import React, { useState } from 'react';
import SuburbDetailTab from './components/SuburbDetailTab';
import FeasibilityDashboard from './components/FeasibilityDashboard';
import HillsCouncilTab from './components/HillsCouncilTab';
import { Layers } from 'lucide-react';

const SUBURBS = ['Parramatta', 'The Hills', 'Ryde', 'Liverpool'];

export default function App() {
  // activeView can be 'overview' or one of the suburb names
  const [activeView, setActiveView] = useState('overview');

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white font-sans selection:bg-sky-500/20 pb-12">
      {/* Top Navigation */}
      <nav className="flex items-center px-8 py-5 text-sm font-medium border-b border-white/5">
        <div className="flex items-center gap-8">
          <div className="w-8 h-8 bg-sky-500 text-white rounded-lg flex items-center justify-center font-bold">
            <Layers className="w-5 h-5" />
          </div>
          <div className="flex gap-6 text-textMuted">
            <button 
              onClick={() => setActiveView('overview')}
              className={`${activeView === 'overview' ? 'text-white font-bold' : 'hover:text-white'} transition-colors`}
            >
              Council Overview
            </button>
            {SUBURBS.map((suburb) => (
              <button 
                key={suburb}
                onClick={() => setActiveView(suburb)}
                className={`${activeView === suburb ? 'text-white font-bold' : 'hover:text-white'} transition-colors`}
              >
                {suburb}
              </button>
            ))}
          </div>
        </div>
        <div className="ml-auto flex items-center gap-2 text-textMuted">
          Account <span className="text-white ml-2">Marlene Novak ∨</span>
        </div>
      </nav>

      <main className="max-w-[1600px] mx-auto px-8 py-10">
        <header className="mb-10">
          <h1 className="text-3xl font-normal tracking-wide mb-2">
            {activeView === 'overview' ? 'Council Overview' : `${activeView} Feasibility`}
          </h1>
          <p className="text-sm text-textMuted">
            Multi-Agent System connected via FastMCP • All Systems Online
          </p>
        </header>

        {activeView === 'overview' ? (
          <FeasibilityDashboard onSelectSuburb={setActiveView} />
        ) : activeView === 'The Hills' ? (
          <HillsCouncilTab />
        ) : (
          <SuburbDetailTab suburbName={activeView} />
        )}
      </main>
    </div>
  );
}