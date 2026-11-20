import React, { useState } from 'react';
import axios from 'axios';
import { Play, AlertTriangle } from 'lucide-react';

export default function DecideTab({ claimId = 'CLM-1042', setClaimId }) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const [facts, setFacts] = useState({
    claim_type: 'flood_damage',
    days_since_policy_start: '20',
    claim_amount: '150000',
  });

  const loadNormalCase = () => {
    if (setClaimId) setClaimId('CLM-1042');
    setFacts({ claim_type: 'flood_damage', days_since_policy_start: '20', claim_amount: '150000' });
    setResult(null);
  };

  const loadAmbiguousCase = () => {
    if (setClaimId) setClaimId('CLM-1043');
    // Leaving days_since_policy_start blank marks WAIT_30D as AMBIGUOUS -> triggers LangGraph agents
    setFacts({ claim_type: 'flood_damage', days_since_policy_start: '', claim_amount: '150000' });
    setResult(null);
  };

  const handleDecide = async () => {
    setLoading(true);
    setError('');
    try {
      const backendUrl = window.location.origin.replace('5173', '8000');
      const payload = {
        claim_id: claimId,
        facts: {
          claim_type: facts.claim_type || null,
          days_since_policy_start: facts.days_since_policy_start === '' ? null : Number(facts.days_since_policy_start),
          claim_amount: facts.claim_amount === '' ? null : Number(facts.claim_amount),
        },
      };

      const response = await axios.post(`${backendUrl}/decide/`, payload);
      setResult(response.data);
      localStorage.setItem('claimResult', JSON.stringify(response.data));
    } catch (err) {
      setError(err.response?.data?.detail || 'Execution failed. Compile a policy first.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 flex justify-between items-center">
        <div>
          <h2 className="text-lg font-semibold">Step 3: Deterministic Rule Engine & LangGraph Agents</h2>
          <p className="text-sm text-gray-500">Evaluating {claimId} against compiled policy rules.</p>
        </div>
        <button
          onClick={handleDecide}
          disabled={loading}
          className="flex items-center gap-2 bg-brand text-white px-6 py-2 rounded-md font-medium hover:bg-orange-600 disabled:opacity-50"
        >
          {loading ? 'Evaluating...' : 'Execute Claim'}
          <Play size={16} />
        </button>
      </div>

      {error && <p className="text-red-500 text-sm">{error}</p>}

      <div className="grid grid-cols-2 gap-6">
        {/* Left: Claim Facts + Settlement */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col">
          <div className="bg-gray-50 border-b border-gray-200 px-4 py-3 font-semibold text-gray-700">
            Claim facts (tokenised)
          </div>
          <div className="p-4 flex flex-col gap-4">
            <div>
              <label className="text-xs text-gray-500 font-semibold uppercase">Loss type</label>
              <input
                type="text"
                value={facts.claim_type}
                onChange={(e) => setFacts({ ...facts, claim_type: e.target.value })}
                className="w-full border-b border-gray-300 py-1 font-bold text-gray-800 focus:outline-none"
              />
            </div>
            <div>
              <label className="text-xs text-gray-500 font-semibold uppercase">Incident day (leave blank for missing fact)</label>
              <input
                type="number"
                placeholder="Missing / unknown"
                value={facts.days_since_policy_start}
                onChange={(e) => setFacts({ ...facts, days_since_policy_start: e.target.value })}
                className="w-full border-b border-gray-300 py-1 font-bold text-gray-800 focus:outline-none"
              />
            </div>
            <div>
              <label className="text-xs text-gray-500 font-semibold uppercase">Amount Claimed (₹)</label>
              <input
                type="number"
                value={facts.claim_amount}
                onChange={(e) => setFacts({ ...facts, claim_amount: e.target.value })}
                className="w-full border-b border-gray-300 py-1 font-bold text-gray-800 focus:outline-none"
              />
            </div>

            {result?.settlement && (
              <div className="mt-2 pt-3 border-t border-gray-200 text-xs flex flex-col gap-1">
                <div className="flex justify-between"><span>Deductible:</span><strong>₹{result.settlement.deductible.toLocaleString()}</strong></div>
                <div className="flex justify-between"><span>Coverage limit:</span><strong>₹{result.settlement.coverage_limit.toLocaleString()}</strong></div>
                <div className="flex justify-between text-sm text-gray-900 mt-1"><span>Eligible payout:</span><strong>₹{result.settlement.eligible_payout.toLocaleString()}</strong></div>
              </div>
            )}
          </div>
        </div>

        {/* Right: Rule Engine Trace */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col">
          <div className="bg-gray-50 border-b border-gray-200 px-4 py-3 font-semibold text-gray-700">
            Rule engine trace
          </div>
          <div className="p-4 flex-grow overflow-y-auto flex flex-col gap-3">
            {!result && !loading && (
              <p className="text-sm text-gray-400 text-center mt-10">Run the engine to see the evaluation trace.</p>
            )}

            {result?.rule_trace?.map((item, idx) => (
              <div key={idx} className={`border rounded p-3 flex justify-between items-start ${
                item.status === 'pass' ? 'border-green-200 bg-green-50/30' :
                item.status === 'fail' ? 'border-red-200 bg-red-50' : 'border-yellow-200 bg-yellow-50'
              }`}>
                <div>
                  <div className="font-bold text-sm text-gray-800">{item.rule_id} ({item.clause})</div>
                  <div className="text-xs mt-1 text-gray-600">{item.reason}</div>
                </div>
                <span className={`text-white text-[10px] font-bold px-2 py-1 rounded uppercase ${
                  item.status === 'pass' ? 'bg-green-600' :
                  item.status === 'fail' ? 'bg-red-600' : 'bg-yellow-500'
                }`}>
                  {item.status}
                </span>
              </div>
            ))}
          </div>

          {result && (
            <div className={`p-4 border-t ${
              result.verdict === 'APPROVED' ? 'bg-green-600' :
              result.verdict === 'REJECTED' ? 'bg-red-600' : 'bg-yellow-500'
            }`}>
              <h3 className="text-white font-bold text-center text-lg uppercase tracking-wider">
                Verdict: {result.verdict}
              </h3>
            </div>
          )}
        </div>
      </div>

      {/* Counterfactual & Agent Review */}
      {result && (
        <div className="grid grid-cols-2 gap-6">
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200 text-sm">
            <h4 className="font-semibold text-gray-700 mb-2">What would change the outcome</h4>
            <p className="text-gray-600">
              {result.counterfactual ? result.counterfactual.explanation : 'No counterfactual needed for this verdict.'}
            </p>
          </div>

          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200 text-sm">
            <h4 className="font-semibold text-gray-700 mb-2 flex items-center gap-2">
              <AlertTriangle size={16} /> Agent review (Advocate / Challenger / Judge)
            </h4>
            {result.agents_triggered ? (
              <div className="text-xs text-gray-600 flex flex-col gap-2 max-h-60 overflow-y-auto">
                <div className="p-2 bg-green-50 border border-green-200 rounded">
                  <strong className="text-green-800">Advocate:</strong> {result.agent_arguments?.advocate}
                </div>
                <div className="p-2 bg-red-50 border border-red-200 rounded">
                  <strong className="text-red-800">Challenger:</strong> {result.agent_arguments?.challenger}
                </div>
                <div className="p-2 bg-blue-50 border border-blue-200 rounded">
                  <strong className="text-blue-800">Judge Decision:</strong> {result.verdict}
                </div>
              </div>
            ) : (
              <p className="text-gray-500 text-xs">Not triggered for this claim (rules were unambiguous).</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}