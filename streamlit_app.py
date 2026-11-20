"""ClaimProof: Streamlit demo.

Runs the same backend modules as the FastAPI app, in "light" mode for small free hosts
(small spaCy model, BM25-only retrieval). Sample data only.
"""
import json
import os
import random
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).parent
BACKEND = ROOT / "claimproof" / "backend"
os.environ.setdefault("CLAIMPROOF_LIGHT", "1")
os.environ.setdefault("CLAIMPROOF_SPACY_MODEL", "en_core_web_sm")
sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)

import streamlit as st

st.set_page_config(page_title="ClaimProof", layout="wide")

try:  # Streamlit Cloud secrets -> environment (used by LiteLLM)
    if "GROQ_API_KEY" in st.secrets:
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
except Exception:
    pass

POLICY_FILE = Path("compiled_policies.json")
SAMPLE_CLAIM = "Claimant: Rahul Verma. Phone: +91 98765 43210. Loss: Flood damage."
SAMPLE_POLICY = (
    "Clause 4.2: Flood damage to the insured vehicle is covered.\n"
    "Clause 4.7: Flood claims are payable only if the loss occurs 30 or more days after the policy start date.\n"
    "Maximum coverage is 150000."
)
VERDICT_OF_OUTCOME = {"approve": "APPROVED", "reject": "REJECTED", "needs_review": "AMBIGUOUS"}


@st.cache_resource(show_spinner="Loading privacy engine (first run only)...")
def load_privacy():
    from app.privacy.anonymizer import anonymize_text
    from app.privacy.vault import vault

    return anonymize_text, vault


@st.cache_resource(show_spinner="Loading claim workflow...")
def load_workflow():
    from app.agents.workflow import claim_workflow

    return claim_workflow


def read_policy():
    from app.compiler.schema import CompiledPolicy

    return CompiledPolicy(**json.loads(POLICY_FILE.read_text(encoding="utf-8")))


def parse_value(v: str):
    v = v.strip()
    for cast in (int, float):
        try:
            return cast(v)
        except ValueError:
            pass
    return v


st.title("ClaimProof")
st.caption(
    "Policy compilation and evidence-based claim assessment. "
    "Demo with sample data only: please do not upload real personal documents."
)

with st.sidebar:
    st.subheader("Status")
    st.write("LLM key: " + ("configured" if os.getenv("GROQ_API_KEY") else "not set (compile and agent steps unavailable)"))
    st.write("Retrieval: " + ("BM25 only (light mode)" if os.getenv("CLAIMPROOF_LIGHT") == "1" else "hybrid + reranker"))
    st.write("Privacy NER model: " + os.getenv("CLAIMPROOF_SPACY_MODEL", "default"))

tab_protect, tab_compile, tab_decide, tab_prove = st.tabs(["1 Protect", "2 Compile", "3 Decide", "4 Prove"])

# ---------------------------------------------------------------- Protect
with tab_protect:
    st.subheader("Protect: tokenise personal data before any LLM sees it")
    kind = st.radio("Document type", ["claim", "policy"], horizontal=True)
    up = st.file_uploader("Upload a .txt or .pdf (optional)", type=["txt", "pdf"])
    text = st.text_area("...or paste text", SAMPLE_CLAIM, height=120)
    if st.button("Protect", type="primary", key="btn_protect"):
        raw = text
        if up is not None:
            data = up.read()
            if up.name.lower().endswith(".pdf"):
                import fitz

                raw = "\n".join(p.get_text() for p in fitz.open(stream=data, filetype="pdf"))
            else:
                raw = data.decode("utf-8", errors="ignore")
        if not raw.strip():
            st.warning("No text found.")
        else:
            anonymize_text, vault = load_privacy()
            tokenized, token_map, check = anonymize_text(raw)
            doc_id = uuid.uuid4().hex[:8]
            vault.save_map(doc_id, token_map)
            leaks = sum(1 for v in token_map.values() if v and v in tokenized)
            st.session_state["protect"] = dict(
                doc_id=doc_id, kind=kind, raw=raw, tokenized=tokenized, token_map=token_map, leaks=leaks
            )
            if kind == "policy":
                st.session_state["policy_text"] = tokenized
    p = st.session_state.get("protect")
    if p:
        c1, c2 = st.columns(2)
        c1.markdown("**Original (stays on this server)**")
        c1.code(p["raw"], language=None)
        c2.markdown("**What the LLM sees**")
        c2.code(p["tokenized"], language=None)
        m1, m2 = st.columns(2)
        m1.metric("Values tokenised", len(p["token_map"]))
        m2.metric("Raw values still in tokenised text", p["leaks"])
        with st.expander("Token map (kept local, never sent to the LLM)"):
            st.json(p["token_map"])

# ---------------------------------------------------------------- Compile
with tab_compile:
    st.subheader("Compile: policy text into validated, executable rules")
    pol = read_policy()
    st.caption(f"Active policy: {pol.policy_id} {pol.version}")
    st.dataframe(
        [{**r.model_dump(), "value": str(r.value)} for r in pol.rules],
        column_order=["rule_id", "rule_type", "field", "operator", "value", "source_clause", "description"],
        width="stretch",
    )
    if pol.conflicts:
        st.warning("Conflicts found by Z3: " + "; ".join(f"{c.rule_a} vs {c.rule_b}: {c.reason}" for c in pol.conflicts))
    else:
        st.success("No rule conflicts found by the Z3 check.")

    st.markdown("**Generated tests, run live against the rule engine**")
    from app.engine.evaluator import evaluate_rules

    rows = []
    for t in pol.generated_tests:
        verdict, _, _ = evaluate_rules(t.claim_input, pol.rules)
        expected = VERDICT_OF_OUTCOME[t.expected_outcome]
        rows.append(
            {"test": t.name, "expected": expected, "actual": verdict, "result": "pass" if verdict == expected else "FAIL"}
        )
    st.dataframe(rows, width="stretch")

    with st.expander("Compile a new policy with the LLM (needs GROQ_API_KEY)"):
        pid = st.text_input("Policy ID", pol.policy_id)
        ver = st.text_input("Version", pol.version)
        ptxt = st.text_area("Tokenised policy text", st.session_state.get("policy_text", SAMPLE_POLICY), height=140)
        if st.button("Compile policy", key="btn_compile"):
            try:
                from app.compiler.extractor import extract_rules
                from app.compiler.schema import CompiledPolicy
                from app.compiler.validator import detect_conflicts_z3, generate_policy_tests
                from app.services.retrieval import index_policy_clauses

                with st.spinner("Extracting rules..."):
                    rules = extract_rules(ptxt)
                index_policy_clauses([f"{r.source_clause}: {r.description}" for r in rules])
                compiled = CompiledPolicy(
                    policy_id=pid,
                    version=ver,
                    rules=rules,
                    conflicts=detect_conflicts_z3(rules),
                    generated_tests=generate_policy_tests(rules),
                )
                POLICY_FILE.write_text(compiled.model_dump_json(indent=2), encoding="utf-8")
                st.success("Compiled and saved as the active policy.")
                st.rerun()
            except Exception as e:  # noqa: BLE001
                st.error(f"Compile failed (is GROQ_API_KEY set?): {e}")

# ---------------------------------------------------------------- Decide
with tab_decide:
    st.subheader("Decide: evaluate a claim against the compiled rules")
    pol = read_policy()
    fields = list(dict.fromkeys(r.field for r in pol.rules))
    defaults = {"claim_type": "flood_damage", "days_since_policy_start": "20", "claim_amount": "150000"}
    cid = st.text_input("Claim ID", st.session_state.setdefault("cid_default", f"CLM-{random.randint(1000, 9999)}"))
    st.caption("Leave a field empty to simulate a missing fact. That routes the claim to the LLM agents (needs GROQ_API_KEY).")
    cols = st.columns(len(fields))
    for col, f in zip(cols, fields):
        col.text_input(f, defaults.get(f, ""), key=f"fact_{f}")
    if st.button("Decide claim", type="primary", key="btn_decide"):
        facts = {f: parse_value(st.session_state[f"fact_{f}"]) for f in fields if st.session_state[f"fact_{f}"].strip()}
        try:
            wf = load_workflow()
            final = wf.invoke(
                {"claim_id": cid, "facts": facts, "policy_version": pol.version, "rules": pol.rules},
                config={"configurable": {"thread_id": cid}},
            )
            st.session_state["result"] = final
            st.session_state["last_cid"] = cid
        except Exception as e:  # noqa: BLE001
            st.session_state.pop("result", None)
            st.error(f"Decision failed (the agent step needs GROQ_API_KEY): {e}")
    res = st.session_state.get("result")
    if res:
        verdict = res["verdict"]
        {"APPROVED": st.success, "REJECTED": st.error}.get(verdict, st.warning)(f"Verdict: {verdict}")
        st.markdown("**Rule trace**")
        st.dataframe([{**r, "expected": str(r.get("expected"))} for r in res["rule_results"]], column_order=["rule_id", "clause", "status", "reason"], width="stretch")
        s = res.get("settlement")
        if s:
            a, b, c = st.columns(3)
            a.metric("Claim amount", f"{s['claim_amount']:,.0f}")
            b.metric("Deductible", f"{s['deductible']:,.0f}")
            c.metric("Eligible payout", f"{s['eligible_payout']:,.0f}")
        cf = res.get("counterfactual")
        if cf:
            st.info("What would change the outcome: " + cf["explanation"])
        if res.get("agents_triggered"):
            for who, arg in res.get("arguments", {}).items():
                with st.expander(f"{who.title()} argument"):
                    st.write(arg)

# ---------------------------------------------------------------- Prove
with tab_prove:
    st.subheader("Prove: checkpoints and audit trail")
    from app.services.audit import get_audit_log, get_human_review_queue

    cid = st.session_state.get("last_cid")
    if cid:
        wf = load_workflow()
        history = list(wf.get_state_history({"configurable": {"thread_id": cid}}))
        st.markdown(f"**Workflow checkpoints for {cid}**")
        st.dataframe(
            [
                {"checkpoint": f"CP{i + 1}", "next step": (list(s.next)[0] if s.next else "done")}
                for i, s in enumerate(reversed(history))
            ],
            width="stretch",
        )
    else:
        st.caption("Run a decision in the Decide tab to see its checkpoints.")

    log = get_audit_log()
    st.markdown("**Audit log**")
    if log:
        linked = all(e["prev_hash"] == (log[i - 1]["hash"] if i else "GENESIS") for i, e in enumerate(log))
        (st.success if linked else st.error)(
            "Hash links intact: every entry points to the previous entry's hash."
            if linked
            else "Hash links broken: an entry was removed or reordered."
        )
        st.caption("This check detects removed or reordered entries. Edits to an entry's content are not detectable yet, because claim facts are not stored in the log.")
        st.dataframe(
            [{k: e.get(k) for k in ("entry_id", "claim_id", "verdict", "short_hash", "confidence", "timestamp")} for e in log[-10:]],
            width="stretch",
        )
    else:
        st.caption("No audit entries yet.")
    queue = get_human_review_queue()
    st.markdown(f"**Human review queue ({len(queue)})**")
    if queue:
        st.dataframe(queue, width="stretch")
