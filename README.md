# ClaimProof

ClaimProof is an AI-powered insurance policy compilation and claim assessment system that transforms complex, unstructured insurance policies into structured, validated and executable rules.

Instead of relying on Large Language Models (LLMs) to independently make every claim decision, ClaimProof uses LLMs to extract and compile policy rules, which are subsequently validated, tested and executed through a deterministic rule engine. Ambiguous cases are handled through conditional multi-agent reasoning, ensuring evidence-backed and explainable decisions.

## Problem Statement

Insurance claim assessment requires interpreting complex policy documents containing coverage conditions, exclusions, deductibles and waiting periods.

For example, vehicle flood damage may be covered under an insurance policy, but a waiting-period clause or another exclusion could make the claim ineligible.

Traditional manual assessment is time-consuming, while conventional LLM-based approaches introduce several challenges:

- **Hallucinated Coverage:** LLMs may invent coverage conditions or overlook exclusions that exist in the actual policy.
- **Data Privacy Risks:** Sensitive customer information, including names, identification numbers and medical details, may be exposed to external LLM services.
- **Lack of Explainability:** Generated decisions do not inherently provide verifiable evidence linking the outcome to exact policy clauses.
- **Unpredictable Costs:** Repeated LLM calls and complex reasoning workflows make token consumption and processing costs difficult to control.

## Our Approach: LLM as a Compiler, Not a Judge

ClaimProof separates policy understanding from claim execution through two independent stages:

**1. Policy Compilation (Once per Policy)**

Insurance policy documents are processed using LLMs to extract structured rules representing coverage conditions, exclusions, waiting periods, deductibles and coverage limits.

The extracted rules undergo schema validation, conflict detection and automated testing before being stored as versioned, executable policy configurations.

**2. Claim Execution (Per Claim)**

Incoming claims are evaluated against previously compiled policy rules using a deterministic rule engine. Eligibility and settlement calculations are performed programmatically.

LLM-powered agents are invoked only when ambiguous or conflicting policy interpretations require additional reasoning.

This approach reduces unnecessary LLM calls while improving consistency, traceability and decision reliability.

## Key Features

### 1. Secure Document Intake and Privacy
- Upload insurance policies and claim documents through FastAPI.
- Extract text from digital and scanned PDF documents.
- Detect and anonymize Personally Identifiable Information (PII).
- Maintain a local token vault for secure information mapping.

### 2. AI-Powered Policy Compilation
- Extract structured policy rules using LLMs.
- Validate extracted rules using Pydantic schemas.
- Preserve clause-level references and source information.
- Convert natural-language policy provisions into executable configurations.
- Maintain versioned policy rules.

### 3. Policy Conflict Detection and Automated Testing
- Identify contradictory and overlapping policy conditions.
- Use constraint-based validation for rule consistency.
- Automatically generate test cases from compiled rules.
- Execute positive, negative and boundary-value tests.
- Flag ambiguous or unsupported rules for human verification.

### 4. Deterministic Claim Evaluation
- Evaluate structured claim facts against compiled policy rules.
- Check coverage conditions, exclusions and waiting periods.
- Calculate eligible settlements using deterministic logic.
- Apply deductibles and coverage limits programmatically.

### 5. Conditional Multi-Agent Reasoning
For ambiguous cases, ClaimProof uses LangGraph to orchestrate specialized agents:

- **Advocate Agent:** Constructs arguments supporting claim approval.
- **Challenger Agent:** Identifies exclusions and arguments against approval.
- **Judge Agent:** Evaluates both arguments against the available policy evidence.

Clear claims bypass unnecessary LLM reasoning and proceed through deterministic evaluation.

### 6. Counterfactual Analysis
- Identify conditions that would change a claim outcome.
- Modify relevant claim variables and reevaluate compiled rules.
- Explain what would need to change for a rejected claim to satisfy specific eligibility conditions.

### 7. Explainability and Auditability
- Link decisions to exact policy clauses and supporting claim facts.
- Generate evidence-based decision reports.
- Maintain workflow checkpoints for execution recovery and replay.
- Maintain hash-chained audit records for tamper detection.
- Preserve policy versions to reproduce historical decisions.

## System Architecture

ClaimProof follows a modular, five-layer architecture supported by a cross-cutting trust layer.

| Layer | Responsibility |
|---|---|
| Intake – Protect | Document processing, PII detection and anonymization |
| Policy Compiler – Compile | Rule extraction, validation, conflict detection and automated testing |
| Claim Evaluator – Decide | Deterministic claim evaluation and conditional multi-agent reasoning |
| Output – Prove | Decision reports, evidence references and settlement explanations |
| Model Layer | LLM routing, hybrid retrieval and standardized tool integration |

**Trust Layer:**
- Langfuse for LLM tracing and cost monitoring.
- LangGraph checkpoints for workflow persistence and replay.
- Hash-chained audit records and policy version history.

## Technology Stack

| Category | Technologies |
|---|---|
| Backend | Python, FastAPI |
| Document Processing | PyMuPDF, PaddleOCR |
| Privacy | Microsoft Presidio |
| Policy Compilation | LangChain, Pydantic |
| Rule Validation | Z3 Solver, Pytest |
| Agent Orchestration | LangGraph |
| Model Infrastructure | LiteLLM, Ollama |
| Retrieval | ChromaDB, Embeddings, BM25, BGE Reranker |
| Tool Integration | MCP |
| Database | PostgreSQL |
| Observability | Langfuse |
| Frontend | React.js |

## Example: Vehicle Flood Damage Claim

Consider a motor insurance policy with the following provisions:

- Flood damage is covered under the comprehensive protection plan.
- Claims arising within the first 30 days from policy inception are excluded.
- Maximum flood coverage is ₹2,00,000.
- A deductible of ₹10,000 applies.

A customer submits a flood damage claim for ₹1,50,000.

**Claim Details:**
- Policy inception: 1 October
- Incident date: 20 October
- Claimed amount: ₹1,50,000

**ClaimProof Evaluation:**

1. The policy is compiled into structured rules, including the flood coverage provision and waiting-period exclusion.
2. The claim details are converted into structured facts.
3. The deterministic rule engine identifies that the incident occurred within the 30-day waiting period.
4. The claim is rejected based on the applicable exclusion.
5. The decision report references the exact supporting policy clause.
6. Counterfactual analysis demonstrates how satisfying the waiting-period condition could change the eligibility outcome, assuming other conditions are met.

## Evaluation and Benchmarking

ClaimProof aims to evaluate its performance against conventional approaches using a synthetic insurance claim dataset.

The proposed comparison includes:

| Approach | Description |
|---|---|
| Plain LLM | Direct claim assessment using an LLM |
| Basic RAG | Retrieval of relevant policy clauses followed by LLM-based assessment |
| ClaimProof | Policy compilation, rule validation and deterministic claim evaluation with conditional agent reasoning |

**Evaluation Metrics:**
- Claim decision accuracy
- Incorrect approval rate
- Policy citation accuracy
- Rule extraction accuracy
- Conflict detection precision and recall
- PII exposure to external models
- Average cost per claim
- Human escalation rate
- Counterfactual consistency

All performance metrics will be based on measured experimental results.

## Project Structure

```text
ClaimProof/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── ingestion/
│   │   ├── privacy/
│   │   ├── compiler/
│   │   ├── validation/
│   │   ├── rule_engine/
│   │   ├── agents/
│   │   ├── evaluation/
│   │   ├── counterfactual/
│   │   ├── audit/
│   │   ├── retrieval/
│   │   ├── database/
│   │   └── main.py
│   │
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.jsx
│   └── package.json
│
├── sample_data/
│   ├── policies/
│   └── claims/
│
├── docs/
│   └── architecture/
│
├── docker-compose.yml
└── README.md
```

*The directory structure represents the proposed modular organization and may evolve during implementation.*

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js and npm
- PostgreSQL
- Ollama (for local LLM inference)
- Git

### 1. Clone the Repository

```bash
git clone <https://github.com/Soumya-c0/ClaimProof>
cd ClaimProof
```

### 2. Backend Setup

```bash
cd backend

python -m venv venv
```

Activate the virtual environment:

Windows:
```bash
venv\Scripts\activate
```

Linux / macOS:
```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure environment variables using `.env.example` and provide the required database credentials and model configuration.

Start the backend:

```bash
uvicorn app.main:app --reload
```

Backend API documentation:

```text
http://localhost:8000/docs
```

### 3. Frontend Setup

```bash
cd frontend

npm install
npm run dev
```

### 4. Local Model Setup

Install Ollama and pull a compatible model:

```bash
ollama pull llama3.1
```

Configure the local model endpoint through the application environment variables.

*The exact model and configuration will depend on the structured-output and reasoning requirements.*

## Future Scope

- Extend policy compilation to additional insurance categories.
- Improve semantic and logical policy conflict detection.
- Introduce advanced constraint solving using Z3.
- Support policy change impact analysis across existing claims.
- Integrate additional document formats and multilingual policy processing.
- Improve fraud detection and anomaly identification.
- Introduce enterprise integrations with insurance management systems.

