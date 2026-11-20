import React, { useState } from 'react';
import axios from 'axios';
import { Upload, ShieldCheck, AlertCircle } from 'lucide-react';

export default function ProtectTab() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError('');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first.');
      return;
    }

    setLoading(true);
    setError('');
    const formData = new FormData();
    formData.append('file', file);
    formData.append('doc_type', 'claim');

    try {
      const backendUrl = window.location.origin.replace('5173', '8000');
      const response = await axios.post(`${backendUrl}/protect/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <h2 className="text-lg font-semibold mb-4">Step 1: Secure Document Intake (pdf/scanned image)</h2>
        <div className="flex items-center gap-4">
          <input
            type="file"
            accept=".txt,.pdf,.png,.jpg,.jpeg"
            onChange={handleFileChange}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-gray-50 file:text-gray-700 hover:file:bg-gray-100"
          />
          <button
            onClick={handleUpload}
            disabled={loading || !file}
            className="flex items-center gap-2 bg-brand text-white px-6 py-2 rounded-md font-medium hover:bg-orange-600 disabled:opacity-50"
          >
            {loading ? 'Scanning...' : 'Protect & Upload'}
            <Upload size={16} />
          </button>
        </div>
        {error && <p className="text-red-500 text-sm mt-3 flex items-center gap-1"><AlertCircle size={14} /> {error}</p>}
      </div>

      {result && (
        <div className="grid grid-cols-3 gap-6">
          {/* Tokenized Output */}
          <div className="col-span-2 bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col">
            <div className="bg-gray-50 border-b border-gray-200 px-4 py-3 font-semibold text-gray-700 flex justify-between">
              <span>Parsed text with PII tokenised</span>
              <span className="text-xs font-mono bg-blue-100 text-blue-700 px-2 py-0.5 rounded">{result.status}</span>
            </div>
            <div className="p-4 flex-grow whitespace-pre-wrap font-mono text-sm text-gray-600">
              {result.tokenized_text}
            </div>
            <div className="bg-green-50 border-t border-green-100 px-4 py-2 text-sm text-green-700 font-medium flex items-center gap-2">
              <ShieldCheck size={16} />
              {result.notice}
            </div>
          </div>

          {/* Privacy Check Card */}
          <div className="col-span-1 bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col">
            <div className="bg-gray-50 border-b border-gray-200 px-4 py-3 font-semibold text-gray-700">
              Privacy check
            </div>
            <div className="p-4 flex flex-col gap-3 text-sm">
              {result.privacy_check && Object.entries(result.privacy_check).map(([key, status]) => (
                <div key={key} className="flex justify-between items-center border-b border-gray-100 pb-2">
                  <span className="capitalize text-gray-600">{key.replace('_', ' ')}</span>
                  <span className="bg-green-100 text-green-800 text-xs font-semibold px-2 py-0.5 rounded">
                    {status}
                  </span>
                </div>
              ))}
            </div>
            <div className="mt-auto bg-gray-50 border-t border-gray-200 px-4 py-2 text-xs text-gray-500 text-center">
              Token map stays in local_token_vault.json
            </div>
          </div>
        </div>
      )}
    </div>
  );
}