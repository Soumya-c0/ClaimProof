import React, { useState } from 'react';
import axios from 'axios';
import { CheckCircle, Play, ShieldAlert } from 'lucide-react';

export default function CompileTab() {
  const [policyText, setPolicyText] = useState(
    'Clause 4.2: Flood damage to the insured vehicle is covered.\nClause 4.7: Flood claims are payable only if the loss occurs 30 or more days after the policy start date.\nMaximum coverage is 150000.'
  );
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleCompile = async () => {
    setLoading(true);
    setError('');
    try {
      const backendUrl = window.location.origin.replace('5173', '8000');
      const response = await axios.post(`${backendUrl}/compile/`, {
        policy_id: 'PLC-0001',
        version: 'v3',
        tokenized_text: policyText,
      });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Compilation failed. Is Ollama running?');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <h2 className="text-lg font-semibold mb-4">Step 2: Policy Compiler (Ollama + Pydantic)</h2>
        <textarea
          value={policyText}
          onChange={(e) => setPolicyText(e.target.value)}
          className="w-full h-32 p-3 border border-gray-300 rounded-md mb-4 text-sm font-mono"
          placeholder="Enter tokenized policy clauses here..."
        />
        <button
          onClick={handleCompile}
          disabled={loading}
          className="flex items-center gap-2 bg-brand text-white px-6 py-2 rounded-md font-medium hover:bg-orange-600 disabled:opacity-50"
        >
          {loading ? 'Compiling Rules...' : 'Compile Policy'}
          <Play size={16} />
        </button>
        {error && <p className="text-red-500 mt-2 text-sm">{error}</p>}
      </div>

      {result && (
        <div className="grid grid-cols-2 gap-6">
          {/* Left: Compiled Rules JSON */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col">
            <div className="bg-gray-50 border-b border-gray-200 px-4 py-3 font-semibold text-gray-700 flex justify-between">
              <span>Compiled rules (structured)</span>
              <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded">{result.extracted_by}</span>
            </div>
            <div className="p-4 flex-grow font-mono text-xs text-gray-600 overflow-auto bg-gray-50 border border-gray-100 m-4 rounded max-h-72">
              <pre>{JSON.stringify(result.rules, null, 2)}</pre>
            </div>
            <div className="bg-green-50 border-t border-green-100 px-4 py-2 text-sm text-green-700 font-medium flex justify-between items-center">
              <span className="flex items-center gap-2">
                <CheckCircle size={16} /> Pydantic: {result.pydantic_valid ? 'valid' : 'invalid'}
              </span>
              <span className="bg-green-600 text-white px-2 py-0.5 rounded text-xs">
                Published {result.version}
              </span>
            </div>
          </div>

          {/* Right: Z3 Conflicts + Pytest Generated Tests */}
          <div className="flex flex-col gap-6">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="bg-gray-50 border-b border-gray-200 px-4 py-3 font-semibold text-gray-700 flex items-center gap-2">
                <ShieldAlert size={16} /> Z3 Conflicts ({result.conflicts?.length || 0})
              </div>
              <div className="p-4 text-sm text-gray-600">
                {result.conflicts?.length > 0 ? (
                  result.conflicts.map((c, idx) => (
                    <div key={idx} className="p-2 mb-2 bg-yellow-50 border border-yellow-200 rounded text-xs">
                      {c.reason}
                    </div>
                  ))
                ) : (
                  <p className="text-green-700 text-xs">No overlapping or contradictory rule limits detected.</p>
                )}
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 flex-grow">
              <div className="bg-gray-50 border-b border-gray-200 px-4 py-3 font-semibold text-gray-700">
                Generated Pytest Cases
              </div>
              <div className="p-4 flex flex-col gap-2 text-xs">
                {result.generated_tests?.map((t, idx) => (
                  <div key={idx} className="flex justify-between items-center border-b border-gray-100 pb-2">
                    <span className="text-gray-700">{t.name}</span>
                    <span className={`px-2 py-0.5 rounded font-semibold uppercase ${
                      t.status === 'pass' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                    }`}>
                      {t.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}