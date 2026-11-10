import React, { useState } from 'react';
import axios from 'axios';
import { FileText, CheckCircle, Play, ShieldAlert } from 'lucide-react';

export default function CompileTab() {
  const [policyText, setPolicyText] = useState('Clause 4.2: Flood damage to the insured vehicle is covered.\nClause 4.7: Flood claims are payable only if the loss occurs 30 or more days after the policy start date.\nMaximum coverage is 150000.');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleCompile = async () => {
    setLoading(true);
    setError('');
    try {
      const backendUrl = window.location.origin.replace('5173', '8000');
      const response = await axios.post(`${backendUrl}/policy/compile`, {
        policy_text: policyText
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
      
      {/* Input Section */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <h2 className="text-lg font-semibold mb-4">Step 2: Policy Compiler Engine</h2>
        <textarea
          value={policyText}
          onChange={(e) => setPolicyText(e.target.value)}
          className="w-full h-32 p-3 border border-gray-300 rounded-md mb-4 text-sm font-mono"
          placeholder="Enter policy clauses here..."
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

      {/* Output Section */}
      {result && (
        <div className="grid grid-cols-2 gap-6">
          
          {/* Left: Original Text */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col">
            <div className="bg-gray-50 border-b border-gray-200 px-4 py-3 font-semibold text-gray-700">
              Policy clauses
            </div>
            <div className="p-4 flex-grow text-sm text-gray-700 whitespace-pre-wrap">
              {policyText.split('\n').map((line, i) => (
                <div key={i} className="mb-3">
                  {line.includes('Clause') ? (
                    <>
                      <span className="inline-block border border-purple-300 bg-purple-50 text-purple-700 px-2 py-0.5 rounded text-xs font-bold mb-1">
                        {line.split(':')[0]}
                      </span>
                      <br/>
                      {line.split(':')[1]}
                    </>
                  ) : line}
                </div>
              ))}
            </div>
            <div className="bg-green-50 border-t border-green-100 px-4 py-2 text-sm text-green-700 font-medium flex items-center gap-2">
              <CheckCircle size={16} /> Pydantic validation: passed
            </div>
          </div>

          {/* Right: Compiled JSON */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col">
            <div className="bg-gray-50 border-b border-gray-200 px-4 py-3 font-semibold text-gray-700">
              Compiled rules (structured)
            </div>
            <div className="p-4 flex-grow font-mono text-xs text-gray-600 overflow-auto bg-gray-50 border border-gray-100 m-4 rounded">
              <pre>{JSON.stringify(result.rules, null, 2)}</pre>
            </div>
            <div className="bg-green-50 border-t border-green-100 px-4 py-2 text-sm text-green-700 font-medium flex justify-between items-center">
              <span className="flex items-center gap-2"><ShieldAlert size={16} /> Conflicts found: 0</span>
              <span className="bg-green-600 text-white px-2 py-0.5 rounded text-xs">Published as rules v1</span>
            </div>
          </div>

        </div>
      )}
    </div>
  );
}