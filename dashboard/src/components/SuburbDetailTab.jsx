import React, { useState } from 'react';
import { Bot, Map as MapIcon, Home, Activity, FileText, ChevronLeft, Building, ChevronDown, CheckCircle2, MessageSquare, History, List, BarChart3, TrendingUp, Search } from 'lucide-react';
import Map from 'react-map-gl/mapbox';
import 'mapbox-gl/dist/mapbox-gl.css';

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN;

// Common sub-component: Dummy Mapbox visual placeholder overlay with real map underneath
const MapPlaceholder = ({ title, subtitle, icon: Icon, colorClass, borderStyle = "border-white/10", bgStyle = "bg-black" }) => (
  <div className={`w-full h-full flex flex-col relative group rounded-[24px] overflow-hidden border ${borderStyle} ${bgStyle}`}>
    <div className={`absolute top-5 left-5 z-10 bg-black/80 backdrop-blur-md px-4 py-2 rounded-xl border border-white/10 flex items-center gap-3`}>
      <Icon className={`w-5 h-5 ${colorClass}`} />
      <div className="flex flex-col">
        <span className="text-[10px] uppercase tracking-wider text-white/50 font-bold">{subtitle}</span>
        <span className="text-xs font-mono text-white/90">{title}</span>
      </div>
    </div>
    
    <div className="flex-1 w-full h-full relative overflow-hidden rounded-[24px]">
      {MAPBOX_TOKEN ? (
        <Map
          initialViewState={{
            longitude: 151.0012,
            latitude: -33.8151,
            zoom: 11
          }}
          mapStyle="mapbox://styles/mapbox/dark-v11"
          mapboxAccessToken={MAPBOX_TOKEN}
          attributionControl={false}
        />
      ) : (
        <div className="w-full h-full relative bg-[#050505]">
           <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTYwIDBMMCAwIDAgNjAiIGZpbGw9Im5vbmUiIHN0cm9rZT0icmdiYSgyNTUsMjU1LDI1NSwwLjAyKSIgc3Ryb2tlLXdpZHRoPSIxIi8+PC9zdmc+')] opacity-100" />
           <div className="absolute inset-0 flex items-center justify-center flex-col gap-4 pointer-events-none">
              <div className="w-16 h-16 border border-white/10 rounded-full flex items-center justify-center bg-white/5 disabled-map-icon">
                <Icon className="w-6 h-6 text-white/30" />
              </div>
           </div>
        </div>
      )}
    </div>
  </div>
);

export default function SuburbDetailTab({ suburbName = "Parramatta" }) {
  const [selectedProperty, setSelectedProperty] = useState(null);

  // When a property is clicked, we "drill down" into feasibility rendering
  if (selectedProperty) {
    return <PropertyDetailedView property={selectedProperty} onBack={() => setSelectedProperty(null)} />;
  }

  return (
    <div className="space-y-16 pb-20">

      {/* SECTION 1: id.com Data & Chloropleth Council Map */}
      <div className="flex flex-col gap-6">
        <div className="flex justify-between items-end border-b border-white/10 pb-4 px-2">
           <h2 className="text-2xl font-normal text-white flex items-center gap-2">
              <MapIcon className="w-6 h-6 text-sky-400" /> Regional Demographics (id.com.au)
           </h2>
           <div className="flex gap-3">
              <button className="bg-black border border-white/10 px-4 py-1.5 rounded-lg text-sm text-white flex items-center gap-2 hover:bg-white/5">
                Metric: <span className="text-sky-400 font-mono">Population Growth</span> <ChevronDown className="w-4 h-4 text-white/40" />
              </button>
           </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 h-[680px]">
          {/* Main Map */}
          <div className="lg:col-span-8 h-full">
            <MapPlaceholder 
               title="Regional Chloropleth" 
               subtitle="Suburb boundaries within Council" 
               icon={MapIcon} 
               colorClass="text-sky-400" 
            />
          </div>
          
          {/* Light-coloured detail tile (Cream/Beige) */}
          <div className="lg:col-span-4 bg-[#faf6ef] rounded-[24px] flex flex-col p-8 text-[#111] border border-black/5 shadow-xl relative overflow-hidden">
             
             {/* Subtle aesthetic shape in BG */}
             <div className="absolute -top-12 -right-12 w-48 h-48 bg-black/5 rounded-full blur-3xl opacity-50" />
             
             <h3 className="text-2xl font-normal tracking-tight mb-6">Demographic Shifts</h3>
             <p className="text-sm font-medium opacity-60 mb-8 leading-relaxed">
               Highlighting exact growth metrics from <span className="font-bold border-b border-black/20">id.com.au</span> mapping integration based on the selected layer.
             </p>
             
             <div className="space-y-6 flex-1">
                <div>
                   <div className="text-[10px] font-bold uppercase tracking-widest opacity-40 font-mono mb-1">Top Expanding Suburb</div>
                   <div className="text-xl font-bold flex items-center gap-4">
                      {suburbName} North <span className="text-sky-600 bg-sky-600/10 px-2 py-0.5 rounded text-sm font-mono">+14.2%</span>
                   </div>
                </div>
                <div className="h-px w-full bg-black/10" />
                <div>
                   <div className="text-[10px] font-bold uppercase tracking-widest opacity-40 font-mono mb-1">2026 Forecast Value</div>
                   <div className="text-3xl font-light">45,102 <span className="text-base text-black/50">residents</span></div>
                </div>
                <div>
                   <div className="text-[10px] font-bold uppercase tracking-widest opacity-40 font-mono mb-3">Key Influencing Factors</div>
                   <div className="space-y-2">
                     <div className="flex items-center gap-2 text-sm font-medium"><CheckCircle2 className="w-4 h-4 text-sky-600" /> High-density overlay approval</div>
                     <div className="flex items-center gap-2 text-sm font-medium"><CheckCircle2 className="w-4 h-4 text-sky-600" /> Light rail infrastructure completion</div>
                   </div>
                </div>
             </div>
             
             <div className="mt-auto pt-6 flex gap-2">
                <div className="h-1 flex-1 bg-black rounded-full" />
                <div className="h-1 flex-[0.3] bg-black/20 rounded-full" />
                <div className="h-1 flex-[0.3] bg-black/20 rounded-full" />
             </div>
          </div>
        </div>
      </div>

      {/* SECTION 2: Scouted Properties List */}
      <div className="flex flex-col gap-6">
        <div className="flex justify-between items-end border-b border-white/10 pb-4 px-2">
           <h2 className="text-2xl font-normal text-white flex items-center gap-2">
              <Home className="w-6 h-6 text-white/50" /> Market Acquisition Stream
           </h2>
           <span className="text-xs text-white/50 font-mono border border-white/20 px-3 py-1 rounded-full bg-white/5">
              Live Scout Connected
           </span>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="bg-black border border-white/10 rounded-[24px] p-5 flex flex-col cursor-pointer group hover:border-white/30 transition-colors" onClick={() => setSelectedProperty({ address: `14 Church St, ${suburbName}`, roi: '9.2', zoning: 'R4 Zoning' })}>
             <div className="h-32 bg-[#0c0c0c] rounded-xl mb-4 border border-white/5 overflow-hidden">
                <img src="/api/placeholder/400/300" className="w-full h-full object-cover opacity-60 group-hover:scale-105 transition-transform duration-700" />
             </div>
             <h3 className="font-medium text-white text-base group-hover:text-sky-400 transition-colors">14 Church St</h3>
             <p className="text-xs text-white/50 mb-3">650 sqm • R4 Zoning</p>
             <div className="mt-auto flex justify-between items-end">
               <span className="text-lg font-light text-white">$1.45M</span>
               <span className="text-xs font-mono font-bold text-sky-400 bg-sky-400/10 px-2 py-1 rounded">ROI 9.2</span>
             </div>
          </div>
          
          <div className="bg-black border border-white/10 rounded-[24px] p-5 flex flex-col cursor-pointer group hover:border-white/30 transition-colors" onClick={() => setSelectedProperty({ address: `82 George St, ${suburbName}`, roi: '8.8', zoning: 'R3 Zoning' })}>
             <div className="h-32 bg-[#0c0c0c] rounded-xl mb-4 border border-white/5 overflow-hidden">
                <img src="/api/placeholder/400/300" className="w-full h-full object-cover opacity-60 group-hover:scale-105 transition-transform duration-700" />
             </div>
             <h3 className="font-medium text-white text-base group-hover:text-sky-400 transition-colors">82 George St</h3>
             <p className="text-xs text-white/50 mb-3">580 sqm • R3 Zoning</p>
             <div className="mt-auto flex justify-between items-end">
               <span className="text-lg font-light text-white">$1.20M</span>
               <span className="text-xs font-mono font-bold text-sky-400 bg-sky-400/10 px-2 py-1 rounded">ROI 8.8</span>
             </div>
          </div>

          <div className="bg-black border border-white/10 rounded-[24px] p-5 flex flex-col cursor-pointer group hover:border-white/30 transition-colors" onClick={() => setSelectedProperty({ address: `150 Victoria Rd, ${suburbName}`, roi: '7.5', zoning: 'R4 Zoning' })}>
             <div className="h-32 bg-[#0c0c0c] rounded-xl mb-4 border border-white/5 overflow-hidden flex items-center justify-center">
                <Search className="w-8 h-8 text-white/20" />
             </div>
             <h3 className="font-medium text-white text-base group-hover:text-sky-400 transition-colors">150 Victoria Rd</h3>
             <p className="text-xs text-white/50 mb-3">920 sqm • R4 Zoning</p>
             <div className="mt-auto flex justify-between items-end">
               <span className="text-lg font-light text-white">$2.10M</span>
               <span className="text-xs font-mono font-bold text-sky-400 bg-sky-400/10 px-2 py-1 rounded">ROI 7.5</span>
             </div>
          </div>

          <div className="bg-black border border-white/10 border-dashed rounded-[24px] p-5 flex flex-col items-center justify-center cursor-pointer group hover:border-sky-400 transition-colors">
             <div className="w-12 h-12 rounded-full border border-white/20 bg-white/5 flex items-center justify-center mb-3 group-hover:bg-sky-400/10 group-hover:border-sky-400/30">
               <List className="w-5 h-5 text-white/50 group-hover:text-sky-400" />
             </div>
             <span className="text-sm font-medium text-white/70 group-hover:text-white">View 12 More Properties</span>
          </div>
        </div>
      </div>

      {/* SECTION 3: Historical Sales & Bubble Map */}
      <div className="flex flex-col gap-6">
        <div className="flex justify-between items-end border-b border-white/10 pb-4 px-2">
           <h2 className="text-2xl font-normal text-white flex items-center gap-2">
              <History className="w-6 h-6 text-sky-300" /> Historical Sales Velocity
           </h2>
           <div className="flex gap-3">
              <button className="bg-black border border-white/10 px-4 py-1.5 rounded-lg text-sm text-white flex items-center gap-2">
                Bedrooms: <span className="font-mono">4 Bed</span> <ChevronDown className="w-4 h-4 text-white/40" />
              </button>
              <button className="bg-black border border-white/10 px-4 py-1.5 rounded-lg text-sm text-white flex items-center gap-2">
                Type: <span className="font-mono">House</span> <ChevronDown className="w-4 h-4 text-white/40" />
              </button>
           </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 h-[560px]">
          {/* Light-coloured numbers tile (Light Blue/Cyan tone) */}
          <div className="lg:col-span-5 bg-[#faf6ef] text-[#0a1520] rounded-[24px] p-8 flex flex-col border border-black/5 shadow-lg relative">
             <h3 className="text-xl font-normal mb-8 border-b border-black/10 pb-4">Sales Analytics</h3>
             <div className="grid grid-cols-2 gap-8 flex-1">
                <div className="flex flex-col justify-center">
                  <div className="text-[10px] font-bold uppercase tracking-widest opacity-50 font-mono mb-2">Total Sales (12M)</div>
                  <div className="text-5xl font-light">482</div>
                </div>
                <div className="flex flex-col justify-center">
                  <div className="text-[10px] font-bold uppercase tracking-widest opacity-50 font-mono mb-2">Avg Sale Time</div>
                  <div className="text-5xl font-light">28<span className="text-xl text-black/40">d</span></div>
                </div>
                <div className="flex flex-col justify-center">
                  <div className="text-[10px] font-bold uppercase tracking-widest opacity-50 font-mono mb-2">Median Price Growth</div>
                  <div className="text-4xl font-light text-sky-600">+8.4%</div>
                </div>
                <div className="flex flex-col justify-center">
                  <div className="text-[10px] font-bold uppercase tracking-widest opacity-50 font-mono mb-2">Clearance Rate</div>
                  <div className="text-4xl font-light">72%</div>
                </div>
             </div>
          </div>
          
          {/* Bubble map */}
          <div className="lg:col-span-7 h-full">
            <MapPlaceholder 
               title="Sales Price & Volume Density" 
               subtitle="Bubble Map Integration" 
               icon={MapIcon} 
               colorClass="text-sky-300" 
            />
          </div>
        </div>
      </div>

      {/* SECTION 4: DA Applications & Charts */}
      <div className="flex flex-col gap-6">
        <div className="flex justify-between items-end border-b border-white/10 pb-4 px-2">
           <h2 className="text-2xl font-normal text-white flex items-center gap-2">
              <Activity className="w-6 h-6 text-sky-400" /> Development Applications Pipeline
           </h2>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 h-[500px]">
          {/* DA Table */}
          <div className="lg:col-span-7 bg-black border border-white/10 rounded-[24px] overflow-hidden flex flex-col p-8">
             <h3 className="text-base text-white/80 font-medium mb-6 flex items-center gap-2"><List className="w-4 h-4 opacity-50" /> Latest Live Submissions</h3>
             <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar space-y-2">
                {[
                  { addr: '45 Windsor Rd', type: 'Residential Flat Building', cost: '$4.2M', stat: 'Under Review' },
                  { addr: '12 Church St', type: 'Secondary Dwelling', cost: '$180k', stat: 'Approved' },
                  { addr: '82 Market St', type: 'Major Additions', cost: '$450k', stat: 'Awaiting Info' },
                  { addr: '109 Victoria Rd', type: 'Shop Top Housing', cost: '$2.8M', stat: 'Under Review' },
                  { addr: '51 Macarthur St', type: 'Demolition', cost: '$45k', stat: 'Approved' },
                  { addr: '8 Fleet St', type: 'Backyard Reno', cost: '$90k', stat: 'Lodged' },
                ].map((da, i) => (
                  <div key={i} className="flex justify-between items-center py-3 border-b border-white/5 last:border-0 hover:bg-white/5 px-2 rounded-lg transition-colors cursor-pointer">
                    <div className="flex flex-col">
                      <span className="text-sm font-medium text-white">{da.addr}</span>
                      <span className="text-[11px] text-white/40">{da.type}</span>
                    </div>
                    <div className="flex flex-col items-end">
                      <span className="text-[11px] font-mono font-bold text-white/50">{da.cost}</span>
                      <span className={`text-[10px] uppercase font-bold tracking-wider ${da.stat === 'Approved' ? 'text-sky-400' : 'text-sky-400'}`}>{da.stat}</span>
                    </div>
                  </div>
                ))}
             </div>
          </div>

          {/* Bar Chart Summary */}
          <div className="lg:col-span-5 bg-black border border-white/10 rounded-[24px] p-8 flex flex-col">
             <h3 className="text-base text-white/80 font-medium mb-8 flex items-center gap-2"><BarChart3 className="w-4 h-4 opacity-50" /> Application Types</h3>
             
             <div className="flex-1 flex flex-col justify-end gap-5 font-mono">
                {[
                  { label: "Backyard/Pool Reno", val: 85, color: "bg-white" },
                  { label: "Kitchen/Internal", val: 70, color: "bg-white/70" },
                  { label: "New Single Dwelling", val: 40, color: "bg-white/50" },
                  { label: "Multi-Dwelling/Flats", val: 20, color: "bg-sky-400" },
                  { label: "Commercial Fitout", val: 15, color: "bg-white/20" },
                ].map((item, i) => (
                  <div key={i} className="flex items-center gap-4">
                    <span className="text-[10px] text-white/50 uppercase tracking-widest w-36 text-right truncate">
                      {item.label}
                    </span>
                    <div className="flex-1 h-3 bg-white/5 rounded-r">
                      <div className={`h-full ${item.color} rounded-r`} style={{ width: `${item.val}%` }} />
                    </div>
                    <span className="text-xs text-white right-0 w-8">{item.val}</span>
                  </div>
                ))}
             </div>
          </div>
        </div>
      </div>

      {/* SECTION 5: DCP Rules & Chatbot */}
      <div className="flex flex-col gap-6">
        <div className="flex justify-between items-end border-b border-white/10 pb-4 px-2">
           <h2 className="text-2xl font-normal text-white flex items-center gap-2">
              <FileText className="w-6 h-6 text-sky-300" /> Council Policy & Zoning (DCP)
           </h2>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 h-[500px]">
          {/* Core Rules Table */}
          <div className="lg:col-span-7 bg-black border border-white/10 rounded-[24px] p-8 flex flex-col">
             <h3 className="text-base text-white/80 font-medium mb-6">Core Regulatory Guidelines</h3>

             <div className="grid grid-cols-2 gap-6 flex-1">
                <div className="border border-white/5 bg-[#0a0a0a] p-5 rounded-2xl flex flex-col justify-center">
                  <div className="text-[10px] uppercase tracking-wider mb-2 font-mono text-white/40">FSR Limits (R3/R4)</div>
                  <div className="text-lg font-medium text-white mb-2">0.8:1 <span className="opacity-40 px-2 text-sm">to</span> 1.2:1</div>
                  <div className="text-[10px] text-sky-300 font-mono">Requires exact parcel size lookup</div>
                </div>
                <div className="border border-white/5 bg-[#0a0a0a] p-5 rounded-2xl flex flex-col justify-center">
                  <div className="text-[10px] uppercase tracking-wider mb-2 font-mono text-white/40">Min Lot Size</div>
                  <div className="text-lg font-medium text-white mb-2">600 <span className="opacity-40 text-sm">sqm (dual occ)</span></div>
                  <div className="text-[10px] text-white/40 font-mono">Frontage &gt; 15m</div>
                </div>
                <div className="border border-white/5 bg-[#0a0a0a] p-5 rounded-2xl flex flex-col justify-center">
                  <div className="text-[10px] uppercase tracking-wider mb-2 font-mono text-white/40">Height of Building</div>
                  <div className="text-lg font-medium text-white mb-2">9m <span className="opacity-40 text-sm">to</span> 14m</div>
                  <div className="text-[10px] text-white/40 font-mono">Subject to local overlays</div>
                </div>
                <div className="border border-white/5 bg-[#0a0a0a] p-5 rounded-2xl flex flex-col justify-center">
                  <div className="text-[10px] uppercase tracking-wider mb-2 font-mono text-white/40">Setback Requirements</div>
                  <div className="text-lg font-medium text-white mb-2">Front 6m <span className="opacity-40 text-sm">| Side 1.5m</span></div>
                  <div className="text-[10px] text-white/40 font-mono">Balconies vary</div>
                </div>
             </div>
          </div>

          {/* Light-coloured Chatbot Tile (Pale Yellow/Cream for distinction) */}
          <div className="lg:col-span-5 bg-[#faf6ef] text-[#111] rounded-[24px] p-8 flex flex-col border border-black/5 shadow-lg relative">
             <div className="absolute top-0 right-0 p-4 opacity-5">
                <MessageSquare className="w-32 h-32 text-black" />
             </div>
             
             <h3 className="font-bold text-lg mb-1 relative z-10 flex items-center gap-2">
               <Bot className="w-5 h-5" /> Local Policy Assistant
             </h3>
             <p className="text-sm font-medium opacity-60 mb-6 relative z-10 border-b border-black/10 pb-4">Query Qdrant RAG docs for {suburbName}</p>
             
             <div className="flex-1 flex flex-col gap-3 relative z-10 overflow-y-auto">
               <div className="bg-black/5 text-black p-3 rounded-xl rounded-tl-sm text-[13px] self-start max-w-[85%] font-medium">
                 Can I build a granny flat if my block is 400 sqm?
               </div>
               <div className="bg-black text-white p-3 rounded-xl rounded-tr-sm text-[13px] self-end max-w-[85%] shadow-md">
                 Under the current rules for {suburbName}, a secondary dwelling requires a minimum lot size of 450 sqm. Your block is too small based on the DCP standard.
               </div>
             </div>

             <div className="relative z-10 flex gap-2 mt-4 pt-4 border-t border-black/10">
               <input 
                 type="text" 
                 placeholder="Search policy rules..." 
                 className="flex-1 bg-white border border-black/10 rounded-full px-5 py-2 text-sm text-black focus:outline-none focus:border-black/50 transition-colors shadow-sm"
               />
               <button className="w-10 h-10 bg-black text-white rounded-full flex items-center justify-center hover:bg-black/80 transition-colors">
                 ↑
               </button>
             </div>
          </div>
        </div>
      </div>

    </div>
  );
}

// Minimal placeholder component for property drilldown as instructed earlier
function PropertyDetailedView({ property, onBack }) {
  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500 text-white">
      <div className="flex items-center gap-4 mb-6 border-b border-white/10 pb-4">
        <button onClick={onBack} className="w-10 h-10 rounded-full border border-white/10 hover:bg-white/10 flex items-center justify-center transition-colors">
          <ChevronLeft className="w-5 h-5 text-white" />
        </button>
        <div>
          <h2 className="text-xl font-medium">{property.address}</h2>
          <p className="text-xs text-white/50 font-mono">{property.zoning} • Expected ROI <span className="text-sky-400">{property.roi}</span></p>
        </div>
      </div>
      <div className="bg-black border border-white/10 h-[500px] flex items-center justify-center rounded-[24px]">
         <div className="text-center">
            <h3 className="text-2xl font-light mb-2">Feasibility Interface Active</h3>
            <p className="text-white/40 font-mono text-sm">(Placeholder for property drilldown views)</p>
         </div>
      </div>
    </div>
  );
}