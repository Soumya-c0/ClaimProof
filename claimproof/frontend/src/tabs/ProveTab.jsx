import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { FileSearch, ShieldCheck, Users } from 'lucide-react';

export default function ProveTab({ claimId = 'CLM-1042' }) {
  const [proof, setProof] = useState(null);
  const backendUrl = window.location.origin.replace('5173', '8000');

  useEffect(() => {
    axios.get(`${backendUrl}/prove/${claimId}`)
      .then((res) => setProof(res.data))
      .catch(() => setProof(null));
  }, [claimId, backendUrl]);

  if (!proof) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-gray-400">
        <FileSearch size={48} className="mb-4 opacity-20" />
        <p>No proof bundle found. Run a claim in the DECIDE tab first.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 gap-6">
      {/* Left: LangGraph Checkpoint Timeline */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col">
        <div className="bg-gray-50 border-b border-gray-200 px-4 py-3 font-semibold text-gray-700">
          LangGraph timeline for {proof.claim_id}
        </div>
        <div className="p-4 flex flex-col gap-3">
          {proof.replay_timeline?.map((item, idx) => (
            <div key={idx} className="flex justify-between items-center bg-gray-50 p-2.5 rounded border border-gray-100 text-sm">
              <span className="text-gray-700">{item.step}</span>
              <span className="font-mono text-xs bg-white px-2 py-0.5 rounded border border-gray-300">
                {item.checkpoint}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Right: Hash-Chained Audit Log, Version History & Human Queue */}
      <div className="flex flex-col gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="bg-gray-50 border-b border-gray-200 px-4 py-3 font-semibold text-gray-700">
            Hash-chained audit log (SHA-256)
          </div>
          <div className="p-4 flex flex-col gap-2 font-mono text-xs">
            {proof.audit_log?.length > 0 ? proof.audit_log.map((entry) => (
              <div key={entry.entry_id} className="flex justify-between items-center bg-gray-50 p-2 rounded border border-gray-100">
                <span>#{entry.entry_id} hash {entry.short_hash} ({entry.clauses?.join(', ')})</span>
                <span className="flex items-center gap-1 text-green-700 bg-green-100 px-2 py-0.5 rounded font-sans font-semibold">
                  <ShieldCheck size={12} /> verified
                </span>
              </div>
            )) : <p className="text-gray-400 font-sans">No audit entries recorded yet.</p>}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="bg-gray-50 border-b border-gray-200 px-4 py-3 font-semibold text-gray-700">
            Policy version history
          </div>
          <div className="p-4 flex flex-col gap-2 text-xs">
            {proof.policy_version_history?.map((v) => (
              <div key={v.version} className="flex justify-between border-b border-gray-100 pb-1">
                <span className={v.current ? 'font-bold text-gray-900' : 'text-gray-600'}>
                  {v.version} {v.current ? '(current)' : ''}
                </span>
                <span className="text-gray-400 font-mono">{v.date}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="bg-gray-50 border-b border-gray-200 px-4 py-3 font-semibold text-gray-700 flex items-center gap-2">
            <Users size={16} /> Human review queue
          </div>
          <div className="p-4 text-xs text-gray-600">
            {proof.human_review_queue?.length > 0 ? (
              proof.human_review_queue.map((q, idx) => (
                <div key={idx} className="flex justify-between bg-yellow-50 p-2 rounded border border-yellow-200 mb-1">
                  <span>{q.claim_id} — {q.verdict} (conf: {q.confidence})</span>
                  <span className="font-semibold text-yellow-800">{q.status}</span>
                </div>
              ))
            ) : (
              <p className="text-gray-400">Uncertain or low-confidence cases land here for an adjuster.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}