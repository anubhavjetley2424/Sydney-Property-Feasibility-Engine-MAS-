import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MoreHorizontal, BarChart2, Briefcase, Users, Home, Map as MapIcon, ChevronDown, CheckCircle2 } from 'lucide-react';
import Map from 'react-map-gl/mapbox';
import 'mapbox-gl/dist/mapbox-gl.css';

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN;

// Extremely simple leaderboard row as requested
const SimpleLeaderboardRow = ({ rank, name, roi }) => (
  <div className="flex items-center justify-between py-4 border-b border-white/10 last:border-b-0">
    <div className="flex items-center gap-4">
      <span className="font-mono text-white/50 text-sm w-4">{rank}.</span>
      <span className="text-white font-medium text-lg">{name}</span>
    </div>
    <span className="text-sky-400 font-mono text-sm font-bold tracking-widest">{roi}</span>
  </div>
);

// Expanded Demographic & Economic Compare Module - LIGHT GREEN CARD
const LGAMetricsComparison = () => {
  const [activeTab, setActiveTab] = useState('demographics');

  // Multi-dimensional data for each council to power multiple graphs
  const councilData = [
    { name: 'Parramatta',   pop: 420500,  income: 110,  growth: 15,  jobs: 210, density: 4200, grp: 35.2 },
    { name: 'The Hills',    pop: 290100,  income: 135,  growth: 12,  jobs: 145, density: 1900, grp: 15.4 },
    { name: 'Blacktown',    pop: 495000,  income: 90,   growth: 25,  jobs: 180, density: 2500, grp: 22.8 },
    { name: 'Liverpool',    pop: 345000,  income: 95,   growth: 22,  jobs: 120, density: 2100, grp: 18.5 },
  ];

  const maxPop = Math.max(...councilData.map(d => d.pop));
  const maxIncome = Math.max(...councilData.map(d => d.income));
  const maxGrowth = Math.max(...councilData.map(d => d.growth));
  const maxJobs = Math.max(...councilData.map(d => d.jobs));

  return (
    <div className="flex flex-col h-full text-[#111]">
      <div className="flex justify-between items-start mb-8">
        <div>
          <h2 className="text-3xl font-normal tracking-tight flex items-center gap-3">
             <BarChart2 className="w-8 h-8 opacity-40" /> 
             LGA Profile Comparisons
          </h2>
          <p className="mt-2 opacity-60 text-sm font-medium tracking-wide flex items-center gap-2">
            Detailed region analytics across 4 tracked local government areas <CheckCircle2 className="w-4 h-4 text-blue-600" />
          </p>
        </div>
        <div className="flex gap-4">
          <div className="bg-black/5 hover:bg-black/10 transition-colors border border-black/10 rounded-lg px-4 py-2 flex items-center gap-2 text-sm font-semibold cursor-pointer">
            Target Year: <span className="font-mono">2046</span> <ChevronDown className="w-4 h-4 opacity-50" />
          </div>
          <button className="bg-black text-white px-6 py-2 rounded-lg text-sm font-semibold hover:bg-black/80 transition-colors">
            Generate Report
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-8 mb-8 border-b border-black/10">
        {[
          { id: 'demographics', label: 'Demographics & Growth', icon: Users },
          { id: 'market', label: 'Property Market & Density', icon: Home },
          { id: 'economy', label: 'Economy & Jobs', icon: Briefcase }
        ].map(tab => {
          const Icon = tab.icon;
          return (
            <button 
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`pb-4 text-base font-semibold flex items-center gap-2 border-b-2 transition-colors ${activeTab === tab.id ? 'text-black border-black' : 'text-black/40 border-transparent hover:text-black/80'}`}
            >
              <Icon className="w-5 h-5" /> {tab.label}
            </button>
          )
        })}
      </div>

      {/* Multi-Graph Visualization Area */}
      <AnimatePresence mode="wait">
        <motion.div 
          key={activeTab}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-16"
        >
          {activeTab === 'demographics' && (
            <>
              {/* Left Graph: Population Forecast */}
              <div className="flex flex-col justify-end">
                <h3 className="uppercase tracking-widest text-xs font-bold opacity-50 mb-6 font-mono">Population Forecast (Current vs 2046)</h3>
                <div className="space-y-4">
                  {councilData.map((data, i) => (
                    <div key={`pop-${data.name}`} className="flex items-center gap-6 group">
                      <div className="w-24 text-sm font-bold text-right">{data.name}</div>
                      <div className="flex-1 h-8 bg-black/5 rounded-full overflow-hidden relative">
                        <motion.div 
                          initial={{ width: 0 }}
                          animate={{ width: `${(data.pop / maxPop) * 100}%` }}
                          transition={{ duration: 1, delay: i * 0.1, ease: 'easeOut' }}
                          className={`h-full ${i === 2 ? 'bg-[#111111]' : 'bg-black/40'} rounded-full absolute top-0 left-0`}
                        />
                        <div className="absolute inset-y-0 left-4 flex items-center font-mono text-xs mix-blend-difference text-white">
                          {data.pop.toLocaleString()} residents
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="mt-6 text-xs font-medium opacity-80 pl-32 border-l border-black/20">
                  <span className="font-bold underline decoration-black/20">Blacktown</span> projected to remain highest overall population center.
                </div>
              </div>
              
              {/* Right Graph: Forecasted Growth % */}
              <div className="flex flex-col justify-end">
                <h3 className="uppercase tracking-widest text-xs font-bold opacity-50 mb-6 font-mono">Population Growth % (2021 → 2046)</h3>
                <div className="space-y-4">
                  {councilData.map((data, i) => (
                    <div key={`gr-${data.name}`} className="flex items-center gap-6 group">
                      <div className="w-24 text-sm font-bold text-right">{data.name}</div>
                      <div className="flex-1 h-8 bg-black/5 rounded-full overflow-hidden relative">
                        <motion.div 
                          initial={{ width: 0 }}
                          animate={{ width: `${(data.growth / maxGrowth) * 100}%` }}
                          transition={{ duration: 1, delay: i * 0.1, ease: 'easeOut' }}
                          className={`h-full ${i === 2 ? 'bg-[#111111]' : 'bg-black/30'} rounded-full absolute top-0 left-0`}
                        />
                        <div className="absolute inset-y-0 left-4 flex items-center font-mono text-xs font-bold mix-blend-difference text-white">
                          +{data.growth}%
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="mt-6 text-xs font-medium opacity-80 pl-32 border-l border-black/20">
                   Highest dwelling changes forecasted in <span className="font-bold">Kellyville Ridge</span> & <span className="font-bold">Austral</span>.
                </div>
              </div>
            </>
          )}

          {activeTab === 'market' && (
            <>
              {/* Left Graph: Median Income */}
              <div className="flex flex-col justify-end">
                <h3 className="uppercase tracking-widest text-xs font-bold opacity-50 mb-6 font-mono">Median Household Income ($k/yr)</h3>
                <div className="space-y-4">
                  {councilData.map((data, i) => (
                    <div key={`inc-${data.name}`} className="flex items-center gap-6">
                      <div className="w-24 text-sm font-bold text-right">{data.name}</div>
                      <div className="flex-1 h-8 bg-black/5 rounded-r-lg overflow-hidden relative">
                        <motion.div 
                          initial={{ width: 0 }}
                          animate={{ width: `${(data.income / maxIncome) * 100}%` }}
                          transition={{ duration: 1, delay: i * 0.1, ease: 'easeOut' }}
                          className={`h-full ${i === 1 ? 'bg-black' : 'bg-black/40'}`}
                        />
                        <div className="absolute inset-y-0 left-4 flex items-center font-mono text-xs mix-blend-difference text-white">
                          ${data.income}k
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Right Graph: Density */}
              <div className="flex flex-col justify-end">
                <h3 className="uppercase tracking-widest text-xs font-bold opacity-50 mb-6 font-mono">Avg Population Density (Per SqKm)</h3>
                <div className="space-y-4">
                  {councilData.map((data, i) => (
                    <div key={`den-${data.name}`} className="flex items-center gap-6">
                      <div className="w-24 text-sm font-bold text-right">{data.name}</div>
                      <div className="flex-1 flex gap-1 h-8">
                        {Array.from({length: Math.ceil(data.density / 400)}).map((_, j) => (
                           <motion.div 
                             key={j}
                             initial={{ scaleY: 0 }}
                             animate={{ scaleY: 1 }}
                             transition={{ duration: 0.3, delay: (i*0.1) + (j*0.05) }}
                             className={`w-3 h-full ${i === 0 ? 'bg-black' : 'bg-black/30'}`} 
                           />
                        ))}
                        <div className="ml-2 flex items-center font-mono text-xs font-bold">
                          {data.density}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="mt-4 text-[11px] font-bold opacity-40 text-right">Each bar = 400 people/km²</div>
              </div>
            </>
          )}

          {activeTab === 'economy' && (
            <>
              {/* Left Graph: Jobs */}
              <div className="flex flex-col justify-end">
                <h3 className="uppercase tracking-widest text-xs font-bold opacity-50 mb-6 font-mono">Local Jobs (Thousands)</h3>
                <div className="space-y-4">
                  {councilData.map((data, i) => (
                    <div key={`job-${data.name}`} className="flex items-center gap-6">
                      <div className="w-24 text-sm font-bold text-right">{data.name}</div>
                       <div className="flex-1 h-8 bg-transparent border-b-2 border-black/10 relative flex items-end">
                        <motion.div 
                          initial={{ width: 0 }}
                          animate={{ width: `${(data.jobs / maxJobs) * 100}%` }}
                          transition={{ duration: 1, delay: i * 0.1, ease: 'easeOut' }}
                          className={`h-full ${i === 0 ? 'bg-black' : 'bg-black/30'} border-b-2 border-black`}
                        />
                        <div className="absolute -top-1 left-2 font-mono text-xs mix-blend-difference text-white h-full flex items-center font-bold">
                          {data.jobs}k Local Jobs
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

               {/* Right List: Largest Industry */}
              <div className="flex flex-col justify-end">
                <h3 className="uppercase tracking-widest text-xs font-bold opacity-50 mb-6 font-mono">Highest Job Growth Sector (YoY)</h3>
                <div className="space-y-4">
                  {councilData.map((data, i) => (
                    <div key={`ind-${data.name}`} className="flex items-center gap-6 border-b border-black/10 pb-2">
                       <div className="w-24 text-sm font-bold text-right">{data.name}</div>
                       <div className="flex-1 font-mono text-sm opacity-80">
                         {i===0 ? "Healthcare & Social Assistance" : 
                          i===1 ? "Professional Services" : 
                          i===2 ? "Transport & Warehousing" : "Construction"}
                       </div>
                       <div className="font-bold text-sm">
                          +{i === 0 ? 5.2 : i === 1 ? 4.8 : i === 2 ? 6.1 : 3.9}%
                       </div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}

        </motion.div>
      </AnimatePresence>
      
      <div className="mt-auto pt-6 flex justify-between items-center text-[10px] font-bold font-mono opacity-30 uppercase tracking-widest">
        <span>Powered by profile.id.com.au Integration Engine</span>
        <span>MAS Dashboard v2.0</span>
      </div>
    </div>
  );
};

export default function FeasibilityDashboard({ onSelectSuburb }) {
  return (
    <div className="pb-10 space-y-10">

      {/* Top Row Grid: Mapbox & ROI Leaderboard */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-10 min-h-[580px]">
        
        {/* Council Boundaries Mapbox Space (PURE BLACK WITH BORDER) */}
        <div className="xl:col-span-8 bg-[#0a0a0a] border border-white/[0.06] rounded-[24px] overflow-hidden flex flex-col relative group">
          <div className="absolute top-5 left-5 z-10 bg-black/90 backdrop-blur-md px-4 py-3 rounded-xl border border-white/10 flex items-center gap-3 shadow-2xl">
            <MapIcon className="w-5 h-5 text-sky-400" />
            <div className="flex flex-col">
              <span className="text-[10px] uppercase tracking-widest text-white/50 font-bold">Spatial Overview</span>
              <span className="text-xs font-mono text-white tracking-wide">Council Boundaries Mapbox Overlay</span>
            </div>
          </div>
             
          {/* Map Placeholder, NO GRADIENTS */}
          <div className="flex-1 w-full h-full relative border border-white/5 bg-black rounded-[24px] overflow-hidden">
             {MAPBOX_TOKEN ? (
               <Map
                 initialViewState={{
                   longitude: 151.0012,
                   latitude: -33.8151,
                   zoom: 10
                 }}
                 mapStyle="mapbox://styles/mapbox/dark-v11"
                 mapboxAccessToken={MAPBOX_TOKEN}
                 attributionControl={false}
               />
             ) : (
               <div className="absolute inset-0 flex items-center justify-center flex-col gap-4 pointer-events-none">
                  <div className="w-16 h-16 border border-white/10 rounded-full flex items-center justify-center bg-white/5 disabled-map-icon">
                    <MapIcon className="w-6 h-6 text-white/30" />
                  </div>
                  <p className="font-mono text-xs text-white/40 uppercase tracking-widest">
                    [ Mapbox Integration Ready ]
                  </p>
               </div>
             )}
          </div>
        </div>

        {/* Highest ROI Regions (PURE BLACK WITH BORDER) */}
        <div className="xl:col-span-4 bg-[#111113] border border-white/[0.06] rounded-[24px] flex flex-col p-8">
          <h2 className="text-xl font-normal text-white mb-6 border-b border-white/10 pb-4">Highest ROI Regions</h2>
          <div className="flex flex-col flex-1 pl-2">
             <SimpleLeaderboardRow rank="1" name="Parramatta" roi="9.2 ↑" />
             <SimpleLeaderboardRow rank="2" name="The Hills" roi="8.7 ↑" />
             <SimpleLeaderboardRow rank="3" name="Ryde" roi="7.5 ↓" />
             <SimpleLeaderboardRow rank="4" name="Liverpool" roi="7.1 ↑" />
             <SimpleLeaderboardRow rank="5" name="Blacktown" roi="6.8 ↑" />
          </div>
          <div className="mt-auto pt-6 text-[11px] font-mono uppercase tracking-widest text-white/30">
            Based on Scout Analysis Output
          </div>
        </div>
        
      </div>

      {/* Expanded LGA Comparison Row (LIGHT GREEN) */}
      <div className="w-full bg-[#faf6ef] rounded-[24px] p-12 min-h-[640px]">
         <LGAMetricsComparison />
      </div>

    </div>
  );
}