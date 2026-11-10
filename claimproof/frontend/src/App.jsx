import React, { useState } from 'react';
import ProtectTab from './tabs/ProtectTab';
import CompileTab from './tabs/CompileTab';
import DecideTab from './tabs/DecideTab';
import ProveTab from './tabs/ProveTab';

export default function App() {
  const [activeTab, setActiveTab] = useState('protect');

  const tabs = [
    { id: 'protect', label: 'PROTECT', color: 'bg-blue-600' },
    { id: 'compile', label: 'COMPILE', color: 'bg-purple-600' },
    { id: 'decide', label: 'DECIDE', color: 'bg-orange-600' },
    { id: 'prove', label: 'PROVE', color: 'bg-green-600' }
  ];

  return (
    <div className="min-h-screen bg-gray-100 font-sans text-gray-800">
      
      {/* Top Navigation */}
      <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center shadow-sm">
        <div className="flex items-center gap-8">
          <h1 className="text-2xl font-bold text-orange-600 tracking-tight">ClaimProof</h1>
          
          <nav className="flex space-x-1 bg-gray-50 p-1 rounded-sm border border-gray-200">
            {tabs.map((tab) => {
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-5 py-1.5 text-sm font-bold transition-all duration-200 border rounded-sm
                    ${isActive 
                      ? `${tab.color} text-white border-transparent shadow` 
                      : 'border-transparent text-gray-500 hover:bg-gray-200 hover:border-gray-300'}`}
                >
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="max-w-5xl mx-auto mt-8 p-6">
        {activeTab === 'protect' && <ProtectTab />}
        {activeTab === 'compile' && <CompileTab />}
        {activeTab === 'decide' && <DecideTab />}
        {activeTab === 'prove' && <ProveTab />}
      </main>
    </div>
  );
}