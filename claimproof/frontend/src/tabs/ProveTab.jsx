import React, { useEffect, useState } from 'react';
import { FileSearch, Link2, ShieldCheck, AlertCircle } from 'lucide-react';

export default function ProveTab() {
  const [result, setResult] = useState(null);

  useEffect(() => {
    const savedResult = localStorage.getItem('claimResult');
    if (savedResult) {
      setResult(JSON.parse(savedResult));
    }
  }, []);

  if (!result) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-gray-400">
        <FileSearch size={48} className="mb-4 opacity-20" />
        <p>No decision found. Please run the engine in the DECIDE tab first.</p>
      </div>
    );
  }

  // Extract the failed evaluation for citation
  const failedEval = result.evaluations.find(e => e.status === 'FAIL');
  const counterfactual = result.counterfactuals?.[0];

  return (
    <div className="grid grid-cols-3 gap-6">
      
      {/* Left Column: Decision Report */}
      <div className="col-span-1 bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col h-[500px]">
        <div className="bg-gray-50 border-b border-gray-200 px-4 py-3 font-semibold text-gray-700">
          Decision report
        </div>
        <div className="p-6 flex-grow flex flex-col gap-6">
          
          <div>
            <span className={`px-4 py-1.5 rounded uppercase font-bold tracking-wider text-sm ${
              result.status === 'APPROVED' ? 'bg-green-600 text-white' : 
              result.status === 'REJECTED' ? 'bg-red-600 text-white' : 'bg-yellow-500 text-white'
            }`}>
              {result.status}
            </span>
          </div>

          <div>
            <div className="text-xs text-gray-500 font-semibold uppercase mb-1">Reason</div>
            <div className="font-bold text-gray-800 text-lg leading-tight">
              {result.reason.split('(')[0]}
            </div>
            {failedEval && (
              <div className="mt-3 text-sm text-gray-600">
                <span className="font-semibold text-gray-800">Evidence:</span> clause {failedEval.rule_id}
                <div className="mt-2 p-3 bg-gray-50 border border-gray-100 rounded text-xs leading-relaxed">
                  "Flood claims are payable only if the loss occurs 30 or more days after the policy start date."
                </div>
              </div>
            )}
          </div>

          <div className="mt-auto">
            <div className="text-xs text-gray-500 font-semibold uppercase mb-1">Settlement</div>
            <div className="font-bold text-gray-800 text-2xl">
              ₹{result.eligible_payout.toLocaleString()}
            </div>
          </div>
        </div>
      </div>

      {/* Right Column: Counterfactual & Audit */}
      <div className="col-span-2 flex flex-col gap-6 h-[500px]">
        
        {/* Top: Counterfactual Proof */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 flex-grow">
          <div className="bg-gray-50 border-b border-gray-200 px-4 py-3 font-semibold text-gray-700">
            What would change the outcome
          </div>
          <div className="p-6">
            {counterfactual ? (
              <div>
                <div className="relative h-12 w-full bg-gray-100 rounded-full overflow-hidden flex mb-4">
                  {/* Slider visualization */}
                  <div className="w-1/2 h-full bg-red-100 border-r-2 border-red-300 relative">
                     <div className="absolute top-2 left-[60%] flex flex-col items-center">
                        <div className="w-3 h-3 bg-red-600 rounded-full"></div>
                        <span className="text-[10px] font-bold text-red-600 mt-1">Incident: day {counterfactual.original_value}</span>
                     </div>
                  </div>
                  <div className="w-1/2 h-full bg-green-100 relative">
                     <div className="absolute top-2 left-0 flex flex-col items-center -ml-[2px]">
                        <div className="w-1 h-8 bg-green-600 rounded-full -mt-2"></div>
                     </div>
                     <span className="absolute top-2 right-4 text-[10px] font-bold text-green-700">Waiting period ends: day {counterfactual.required_value}</span>
                  </div>
                </div>
                <p className="text-sm text-gray-600 leading-relaxed bg-blue-50 p-4 rounded border border-blue-100">
                  {counterfactual.explanation} If the incident had occurred on day {counterfactual.required_value} or later, the claim would be eligible, subject to deductible and coverage limits.
                </p>
              </div>
            ) : (
              <div className="flex items-center gap-2 text-gray-500 text-sm h-full justify-center">
                <AlertCircle size={16} /> No counterfactuals generated (Claim was {result.status}).
              </div>
            )}
          </div>
        </div>

        {/* Bottom: Audit Trail */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 h-[200px] flex flex-col">
          <div className="bg-gray-50 border-b border-gray-200 px-4 py-3 font-semibold text-gray-700">
            Audit trail (hash-chained)
          </div>
          <div className="p-4 flex-grow flex flex-col justify-center">
            {result.audit ? (
              <div className="font-mono text-xs text-gray-600 flex flex-col gap-2">
                <div className="flex justify-between items-center bg-gray-50 p-2 rounded">
                  <span className="font-semibold">CP1 PROTECT</span>
                  <span className="text-gray-400">policy: {result.audit.policy_hash}</span>
                </div>
                <div className="flex justify-between items-center bg-gray-50 p-2 rounded">
                  <span className="font-semibold">CP2 COMPILE</span>
                  <span className="text-gray-400">claim: {result.audit.claim_hash}</span>
                </div>
                <div className="flex justify-between items-center bg-green-50 text-green-800 p-2 rounded border border-green-200">
                  <span className="font-semibold flex items-center gap-2"><Link2 size={12}/> CP3 DECIDE</span>
                  <span className="font-bold flex items-center gap-2">execution: {result.audit.execution_hash} <ShieldCheck size={14}/></span>
                </div>
              </div>
            ) : (
              <p className="text-gray-400 text-center text-sm">No cryptographic hashes generated.</p>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}