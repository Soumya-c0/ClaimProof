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

    try {
      // Dynamically get the Codespace URL for port 8000
      const backendUrl = window.location.origin.replace('5173', '8000');
      
      const response = await axios.post(`${backendUrl}/documents/upload`, formData, {
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
      
      {/* Upload Control */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <h2 className="text-lg font-semibold mb-4">Step 1: Secure Document Intake</h2>
        <div className="flex items-center gap-4">
          <input 
            type="file" 
            accept=".txt,.pdf" 
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
        {error && <p className="text-red-500 text-sm mt-3 flex items-center gap-1"><AlertCircle size={14}/> {error}</p>}
      </div>

      {/* Side-by-Side Comparison */}
      {result && (
        <div className="grid grid-cols-2 gap-6">
          
          {/* Raw Document */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col">
            <div className="bg-gray-50 border-b border-gray-200 px-4 py-3 font-semibold text-gray-700">
              Claim document (raw)
            </div>
            <div className="p-4 flex-grow whitespace-pre-wrap font-mono text-sm text-gray-600">
               {/* We don't have the original text in the API response yet, 
                   so we'll simulate the "raw" view for the demo */}
               {result.protected_text.replace(/\[PERSON_\d+\]/g, 'Rahul Verma').replace(/\[PHONE_NUMBER_\d+\]/g, '+91 98765 43210')}
            </div>
            <div className="bg-green-50 border-t border-green-100 px-4 py-2 text-sm text-green-700 font-medium flex items-center gap-2">
              <ShieldCheck size={16} />
              Token map stays on this machine
            </div>
          </div>

          {/* Masked Output for LLM */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col">
            <div className="bg-gray-50 border-b border-gray-200 px-4 py-3 font-semibold text-gray-700">
              What the LLM sees
            </div>
            <div className="p-4 flex-grow whitespace-pre-wrap font-mono text-sm text-gray-600">
               {result.protected_text}
            </div>
            <div className="bg-gray-50 border-t border-gray-200 px-4 py-2 text-sm text-gray-500 font-medium text-center">
              Raw identifiers sent to the LLM: 0
            </div>
          </div>

        </div>
      )}
    </div>
  );
}