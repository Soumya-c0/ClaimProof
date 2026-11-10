import React, { useState } from 'react';
import axios from 'axios';
import { Play, CheckCircle, XCircle, AlertTriangle, ShieldX } from 'lucide-react';

export default function DecideTab() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  // Default claim facts matching the video scenario
  const [facts, setFacts] = useState({
    loss_type: 'flood',
    days_since_start: 20,
    claimed_amount: 150000
  });

  const handleDecide = async () => {
    setLoading(true);
    setError('');
    
    try {
      const backendUrl = window.location.origin.replace('5173', '8000');
      
      const payload = {
        policy: {
          rules: [
            {
              rule_id: "FLOOD_COVERAGE",
              rule_type: "coverage",
              description: "Flood damage to the insured vehicle is covered",
              conditions: [{ field: "loss_type", operator: "==", value: "flood" }],
              coverage_limit: 150000.0,
              source_clause: "Clause 4.2"
            },
            {
              rule_id: "WAIT_30D",
              rule_type: "condition",
              description: "Claims payable only if loss occurs 30 or more days after policy start",
              conditions: [{ field: "days_since_start", operator: ">=", value: 30 }],
              source_clause: "Clause 4.7"
            }
          ]
        },
        claim: {
          facts: {
            loss_type: facts.loss_type,
            days_since_start: Number(facts.days_since_start)
          },
          claimed_amount: Number(facts.claimed_amount)
        }
      };

      const response = await axios.post(`${backendUrl}/claim/decide`, payload);
      setResult(response.data);
      
      // Store the result in localStorage so the Prove tab can access it
      localStorage.setItem('claimResult', JSON.stringify(response.data));
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Execution failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 flex justify-between items-center">
        <div>
          <h2 className="text-lg font-semibold">Step 3: Deterministic Rule Execution</h2>
          <p className="text-sm text-gray-500">Evaluating claim facts against compiled policy rules.</p>
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

      <div className="grid grid-cols-2 gap-6">
        
        {/* Left: Claim Facts */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col h-[400px]">
          <div className="bg-gray-50 border-b border-gray-200 px-4 py-3 font-semibold text-gray-700">
            Claim facts (tokenised)
          </div>
          <div className="p-4 flex flex-col gap-4 overflow-y-auto">
            <div>
              <label className="text-xs text-gray-500 font-semibold uppercase tracking-wider">Loss type</label>
              <input 
                type="text" 
                value={facts.loss_type}
                onChange={(e) => setFacts({...facts, loss_type: e.target.value})}
                className="w-full border-b border-gray-300 py-1 font-bold text-gray-800 focus:outline-none focus:border-brand"
              />
            </div>
            <div>
              <label className="text-xs text-gray-500 font-semibold uppercase tracking-wider">Incident day</label>
              <input 
                type="number" 
                value={facts.days_since_start}
                onChange={(e) => setFacts({...facts, days_since_start: e.target.value})}
                className="w-full border-b border-gray-300 py-1 font-bold text-gray-800 focus:outline-none focus:border-brand"
              />
            </div>
            <div>
              <label className="text-xs text-gray-500 font-semibold uppercase tracking-wider">Amount Claimed</label>
              <input 
                type="number" 
                value={facts.claimed_amount}
                onChange={(e) => setFacts({...facts, claimed_amount: e.target.value})}
                className="w-full border-b border-gray-300 py-1 font-bold text-gray-800 focus:outline-none focus:border-brand"
              />
            </div>
          </div>
        </div>

        {/* Right: Rule Engine Trace */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col h-[400px]">
          <div className="bg-gray-50 border-b border-gray-200 px-4 py-3 font-semibold text-gray-700">
            Rule engine trace
          </div>
          <div className="p-4 flex-grow overflow-y-auto flex flex-col gap-3">
            {!result && !loading && (
              <p className="text-sm text-gray-400 text-center mt-10">Run the engine to see the evaluation trace.</p>
            )}
            
            {result?.evaluations.map((evalItem, idx) => (
              <div key={idx} className={`border rounded p-3 flex justify-between items-start ${
                evalItem.status === 'PASS' ? 'border-green-200 bg-green-50/30' : 
                evalItem.status === 'FAIL' ? 'border-red-200 bg-red-50' : 'border-yellow-200 bg-yellow-50'
              }`}>
                <div>
                  <div className="font-bold text-sm text-gray-800 tracking-tight">{evalItem.rule_id}</div>
                  <div className={`text-xs mt-1 ${evalItem.status === 'FAIL' ? 'text-red-600 font-medium' : 'text-gray-500'}`}>
                    {evalItem.reason}
                  </div>
                </div>
                <div className="ml-4">
                  {evalItem.status === 'PASS' && <span className="bg-green-600 text-white text-[10px] font-bold px-2 py-1 rounded uppercase">Pass</span>}
                  {evalItem.status === 'FAIL' && <span className="bg-red-600 text-white text-[10px] font-bold px-2 py-1 rounded uppercase">Fail</span>}
                  {evalItem.status === 'AMBIGUOUS' && <span className="bg-yellow-500 text-white text-[10px] font-bold px-2 py-1 rounded uppercase">Ambiguous</span>}
                </div>
              </div>
            ))}
          </div>

          {/* Decision Banner */}
          {result && (
            <div className={`p-4 border-t ${
              result.status === 'APPROVED' ? 'bg-green-600' :
              result.status === 'REJECTED' ? 'bg-red-600' : 'bg-yellow-500'
            }`}>
              <h3 className="text-white font-bold text-center text-lg uppercase tracking-wider">
                Claim {result.status}: {result.reason.split('(')[0]}
              </h3>
            </div>
          )}
        </div>
      </div>
      
      {/* Fallback Agent Info */}
      {result?.status === 'ESCALATED' && (
        <div className="bg-blue-50 border border-blue-200 rounded p-4 flex gap-3 text-blue-800 text-sm">
          <AlertTriangle className="shrink-0" />
          <div>
            <strong>AI Agent Verification Triggered.</strong> 
            <p className="mt-1">The deterministic engine found ambiguity. The Advocate and Challenger agents debated the claim, resulting in an escalation to human review.</p>
          </div>
        </div>
      )}
    </div>
  );
}