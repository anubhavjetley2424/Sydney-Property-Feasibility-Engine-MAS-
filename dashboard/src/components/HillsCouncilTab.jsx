import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Users, TrendingUp, Briefcase, Building,
  Activity, Landmark, Home,
  FileText, Bot, MessageSquare,
  Map as MapIcon, CheckCircle2
} from 'lucide-react';
import {
  LineChart, Line, BarChart, Bar, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell, ComposedChart
} from 'recharts';
import Map from 'react-map-gl/mapbox';
import 'mapbox-gl/dist/mapbox-gl.css';
import {
  estimatedResidentPopulation,
  populationGrowthRate,
  grossRegionalProduct,
  cumulativeGRPGrowth,
  quarterlyUnemploymentRate,
  employedResidents,
  localJobs,
  employmentByIndustry,
  buildingApprovals,
  landUse,
  kpiSnapshot,
  workerProductivity,
  registeredBusinessesByIndustry,
  consumerPriceIndex,
} from '../data/hillsShireData';

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN;

// --- Palette ---
const COLORS = {
  grid: 'rgba(148,163,184,0.08)',
};
const PIE_COLORS = ['#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe', '#e0e7ff', '#c7d2fe', '#a5b4fc', '#818cf8'];

// --- KPI Card (compact) ---
const KpiCard = ({ icon: Icon, label, value, change, delay = 0 }) => {
  const isPositive = change?.startsWith('+') || change === 'Below Avg';
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
      className="bg-[#111113] border border-white/[0.06] rounded-xl p-3 flex items-center gap-3 hover:border-sky-500/20 transition-colors"
    >
      <div className="w-8 h-8 rounded-lg bg-sky-500/10 flex items-center justify-center shrink-0">
        <Icon className="w-3.5 h-3.5 text-sky-400" />
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <span className="text-base font-semibold text-white tracking-tight truncate">{value}</span>
          {change && (
            <span className={`text-[10px] font-mono font-bold px-1.5 py-0.5 rounded ${isPositive ? 'text-emerald-400 bg-emerald-400/10' : 'text-red-400 bg-red-400/10'}`}>
              {change}
            </span>
          )}
        </div>
        <div className="text-[10px] text-white/35 font-medium uppercase tracking-wider truncate">{label}</div>
      </div>
    </motion.div>
  );
};

// --- Category Badge ---
const Badge = ({ label, color = 'sky' }) => {
  const colors = {
    sky: 'bg-sky-500/10 text-sky-400/70',
    blue: 'bg-blue-500/10 text-blue-400/70',
    amber: 'bg-amber-500/10 text-amber-400/70',
    emerald: 'bg-emerald-500/10 text-emerald-400/70',
    violet: 'bg-violet-500/10 text-violet-400/70',
  };
  return <span className={`text-[7px] uppercase tracking-[0.14em] font-bold font-mono px-1.5 py-0.5 rounded shrink-0 ${colors[color]}`}>{label}</span>;
};

// --- Tooltip ---
const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-[#111113] border border-white/10 rounded-xl px-4 py-3 shadow-2xl">
      <div className="text-[11px] text-white/50 font-mono font-bold mb-2">{label}</div>
      {payload.map((p, i) => (
        <div key={i} className="flex items-center gap-2 text-xs">
          <div className="w-2 h-2 rounded-full" style={{ background: p.color }} />
          <span className="text-white/70">{p.name}:</span>
          <span className="text-white font-bold font-mono">{typeof p.value === 'number' ? p.value.toLocaleString() : p.value}</span>
        </div>
      ))}
    </div>
  );
};

// ===========================================================================
// MAIN COMPONENT — Single scrollable page
// ===========================================================================
export default function HillsCouncilTab() {
  const [selectedProperty, setSelectedProperty] = useState(null);

  const workforceData = employedResidents.map((e, i) => ({
    year: e.year,
    employedResidents: e.count,
    localJobs: localJobs[i]?.count || 0,
  }));

  if (selectedProperty) {
    return (
      <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500 text-white">
        <div className="flex items-center gap-4 mb-6 border-b border-white/10 pb-4">
          <button onClick={() => setSelectedProperty(null)} className="w-10 h-10 rounded-full border border-white/10 hover:bg-white/10 flex items-center justify-center transition-colors">
            <span className="text-white text-lg">←</span>
          </button>
          <div>
            <h2 className="text-xl font-medium">{selectedProperty.address}</h2>
            <p className="text-xs text-white/50 font-mono">{selectedProperty.zoning} • Expected ROI <span className="text-sky-400">{selectedProperty.roi}</span></p>
          </div>
        </div>
        <div className="bg-black border border-white/10 h-[500px] flex items-center justify-center rounded-[24px]">
          <div className="text-center">
            <h3 className="text-2xl font-light mb-2">Feasibility Interface Active</h3>
            <p className="text-white/40 font-mono text-sm">(Property drilldown placeholder)</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3 pb-10">

      {/* ============ HEADER ============ */}
      <motion.div
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-sky-500/10 via-[#111113] to-[#111113] border border-white/[0.06] rounded-xl px-5 py-3 flex items-center justify-between"
      >
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-sky-500/15 rounded-xl flex items-center justify-center">
            <Landmark className="w-5 h-5 text-sky-400" />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-white tracking-tight">The Hills Shire Council</h1>
            <p className="text-[11px] text-white/40">
              LGA profile &bull; <span className="text-sky-400 font-mono">id.com.au</span> data + live agent feeds
            </p>
          </div>
        </div>
        <div className="hidden md:flex items-center gap-3">
          <div className="text-right">
            <div className="text-[9px] uppercase tracking-widest text-white/25 font-bold">Data</div>
            <div className="text-xs font-mono text-sky-400">Apr 2025</div>
          </div>
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
        </div>
      </motion.div>

      {/* ====================================================================
          BENTO GRID LAYOUT - FLEX ROW MAIN + RIGHT SIDEBAR
          ==================================================================== */}
      <div className="flex flex-col xl:flex-row gap-4 items-start pb-4">

        {/* ═══ MAIN CONTENT (Left: 72%) ═══ */}
        <div className="w-full xl:w-[72%] grid grid-cols-1 lg:grid-cols-12 auto-rows-[220px] gap-4" style={{ gridAutoFlow: 'dense' }}>

          {/* ═══ MAP & REGIONAL OVERVIEW (8 cols x 2 rows) ═══ */}
          <div className="lg:col-span-8 lg:row-span-2 bg-[#0d0d0f] border border-white/[0.06] rounded-2xl flex flex-col overflow-hidden relative group">
            <div className="absolute top-4 left-4 z-10 bg-black/70 backdrop-blur-md px-3 py-1.5 rounded-lg border border-white/10 flex items-center gap-2">
              <MapIcon className="w-4 h-4 text-sky-400" />
              <h2 className="text-xs font-bold uppercase tracking-widest text-white/90 font-mono">LGA Map Overview</h2>
              <Badge label="Regional" color="sky" />
            </div>
            
            <div className="absolute top-4 right-4 z-10 bg-black/70 backdrop-blur-md px-4 py-3 rounded-lg border border-white/10 flex flex-col gap-2 max-w-[200px]">
              <h3 className="text-[10px] font-bold uppercase tracking-widest text-sky-400 font-mono">Demographics Target</h3>
              <div className="space-y-1">
                <div className="flex items-center gap-1.5 text-[10px] text-white/80"><CheckCircle2 className="w-3 h-3 text-emerald-400" /> Metro NW corridor</div>
                <div className="flex items-center gap-1.5 text-[10px] text-white/80"><CheckCircle2 className="w-3 h-3 text-emerald-400" /> High-density rezoning</div>
              </div>
            </div>

            <div className="flex-1 w-full h-full relative">
              {MAPBOX_TOKEN ? (
                <Map initialViewState={{ longitude: 150.95, latitude: -33.70, zoom: 11.5 }} mapStyle="mapbox://styles/mapbox/dark-v11" mapboxAccessToken={MAPBOX_TOKEN} attributionControl={false} style={{ width: '100%', height: '100%' }} />
              ) : (
                <div className="w-full h-full bg-[#0a0a0a] flex items-center justify-center"><MapIcon className="w-12 h-12 text-white/10" /></div>
              )}
            </div>
          </div>

          {/* ═══ POPULATION SECTION (4 cols x 2 rows) ═══ */}
          <div className="lg:col-span-4 lg:row-span-2 bg-[#0d0d0f] border border-white/[0.06] rounded-2xl p-4 flex flex-col overflow-hidden hover:border-sky-500/20 transition-colors">
            <div className="flex items-center gap-2 mb-3 shrink-0">
              <Users className="w-4 h-4 text-sky-400/60" />
              <h2 className="text-[11px] font-bold uppercase tracking-widest text-white/50 font-mono">Population & Demographics</h2>
            </div>
            
            {/* KPI Extracted into Subsection */}
            <div className="mb-3 shrink-0">
              <KpiCard icon={Users} label={kpiSnapshot.population.label} value="222,675" change={kpiSnapshot.population.change} delay={0} />
            </div>

            <div className="flex-1 grid grid-rows-2 gap-3 min-h-0">
              {/* Resident Pop Chart */}
              <div className="bg-[#111113] border border-white/[0.05] rounded-xl p-2.5 flex flex-col">
                <h3 className="text-[9px] font-bold uppercase tracking-widest text-white/40 font-mono mb-1">Resident Population</h3>
                <div className="flex-1 min-h-0 w-full relative">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={estimatedResidentPopulation} margin={{ top: 5, right: 0, left: 0, bottom: 0 }}>
                      <defs><linearGradient id="popGrad2" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4} /><stop offset="95%" stopColor="#3b82f6" stopOpacity={0} /></linearGradient></defs>
                      <CartesianGrid strokeDasharray="3 3" stroke={COLORS.grid} />
                      <XAxis dataKey="year" tick={{ fontSize: 8, fill: '#64748b' }} axisLine={false} tickLine={false} />
                      <YAxis tick={{ fontSize: 8, fill: '#64748b' }} axisLine={false} tickLine={false} tickFormatter={v => `${(v/1000).toFixed(0)}k`} width={30} />
                      <Tooltip content={<CustomTooltip />} />
                      <Area type="monotone" dataKey="population" stroke="#3b82f6" strokeWidth={2} fill="url(#popGrad2)" name="Pop" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Growth Analysis Line Chart */}
              <div className="bg-[#e0f2fe] border border-sky-200/50 rounded-xl p-2.5 flex flex-col text-[#0c1e2e] relative overflow-hidden">
                <div className="absolute -top-8 -right-8 w-24 h-24 bg-sky-400/20 rounded-full blur-2xl opacity-50" />
                <h3 className="text-[9px] font-bold uppercase tracking-widest text-sky-900/60 font-mono mb-1 relative z-10">Growth vs AU</h3>
                <div className="flex-1 min-h-0 w-full relative z-10">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={populationGrowthRate} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.06)" />
                      <XAxis dataKey="year" tick={{ fontSize: 8, fill: '#1e3a5f' }} axisLine={false} tickLine={false} />
                      <YAxis tick={{ fontSize: 8, fill: '#1e3a5f' }} axisLine={false} tickLine={false} tickFormatter={v => `${v}%`} width={30} />
                      <Tooltip content={<CustomTooltip />} />
                      <Legend wrapperStyle={{ fontSize: 8, paddingTop: '5px' }} />
                      <Line type="monotone" dataKey="hillsShire" stroke="#1d4ed8" strokeWidth={2} dot={{ r: 2 }} name="Hills %" />
                      <Line type="monotone" dataKey="australia" stroke="#94a3b8" strokeWidth={1.5} strokeDasharray="4 4" dot={false} name="Aus %" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </div>

          {/* ═══ ECONOMY SECTION (6 cols x 2 rows) ═══ */}
          <div className="lg:col-span-6 lg:row-span-2 bg-[#0d0d0f] border border-white/[0.06] rounded-2xl p-4 flex flex-col overflow-hidden">
            <div className="flex items-center justify-between mb-4 shrink-0">
              <div className="flex items-center gap-2">
                <Landmark className="w-4 h-4 text-blue-400/60" />
                <h2 className="text-[11px] font-bold uppercase tracking-widest text-white/50 font-mono">Economic Health</h2>
              </div>
              <Badge label="Economy" color="blue" />
            </div>

            <div className="grid grid-cols-2 gap-3 mb-4 shrink-0">
              <KpiCard icon={TrendingUp} label={kpiSnapshot.grp.label} value={kpiSnapshot.grp.value} change={kpiSnapshot.grp.change} delay={0.03} />
              <KpiCard icon={Activity} label={kpiSnapshot.unemploymentRate.label} value={kpiSnapshot.unemploymentRate.value} change={kpiSnapshot.unemploymentRate.change} delay={0.06} />
            </div>
            
            <div className="flex-1 grid grid-cols-2 gap-4 min-h-0">
              {/* GRP Area Chart */}
              <div className="bg-[#111113] border border-white/[0.05] rounded-xl p-3 flex flex-col hover:bg-white/[0.02] transition-colors">
                <h3 className="text-[9px] font-bold uppercase tracking-widest text-white/40 font-mono mb-2">Gross Regional Product ($M)</h3>
                <div className="flex-1 min-h-0">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={grossRegionalProduct} margin={{ top: 5, right: 0, left: 0, bottom: 0 }}>
                      <defs><linearGradient id="grpGrad2" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#60a5fa" stopOpacity={0.3} /><stop offset="95%" stopColor="#60a5fa" stopOpacity={0} /></linearGradient></defs>
                      <CartesianGrid strokeDasharray="3 3" stroke={COLORS.grid} />
                      <XAxis dataKey="year" tick={{ fontSize: 8, fill: '#64748b' }} axisLine={false} tickLine={false} />
                      <YAxis tick={{ fontSize: 8, fill: '#64748b' }} axisLine={false} tickLine={false} tickFormatter={v => `$${(v/1000).toFixed(0)}B`} width={35} />
                      <Tooltip content={<CustomTooltip />} />
                      <Area type="monotone" dataKey="grp" stroke="#60a5fa" strokeWidth={2} fill="url(#grpGrad2)" name="GRP" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>
              
              <div className="grid grid-rows-2 gap-3">
                {/* Unemployment Line Chart */}
                <div className="bg-[#111113] border border-white/[0.05] rounded-xl p-2.5 flex flex-col hover:bg-white/[0.02] transition-colors">
                  <h3 className="text-[9px] font-bold uppercase tracking-widest text-white/40 font-mono mb-1">Unemployment Rate</h3>
                  <div className="flex-1 min-h-0">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={quarterlyUnemploymentRate.slice(-12)} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke={COLORS.grid} />
                        <XAxis dataKey="quarter" tick={{ fontSize: 7, fill: '#64748b' }} axisLine={false} tickLine={false} />
                        <YAxis tick={{ fontSize: 8, fill: '#64748b' }} axisLine={false} tickLine={false} tickFormatter={v => `${v}%`} width={25} />
                        <Tooltip content={<CustomTooltip />} />
                        <Legend wrapperStyle={{ fontSize: 7, paddingTop: '5px' }} />
                        <Line type="monotone" dataKey="hillsShire" stroke="#3b82f6" strokeWidth={2} dot={{ r: 1 }} name="Hills %" />
                        <Line type="monotone" dataKey="greaterSydney" stroke="#94a3b8" strokeWidth={1} strokeDasharray="4 4" dot={false} name="Syd %" />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* CPI Line Chart */}
                <div className="bg-[#111113] border border-white/[0.05] rounded-xl p-2.5 flex flex-col hover:bg-white/[0.02] transition-colors">
                  <h3 className="text-[9px] font-bold uppercase tracking-widest text-white/40 font-mono mb-1">Consumer Price Index</h3>
                  <div className="flex-1 min-h-0">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={consumerPriceIndex.slice(-12)} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke={COLORS.grid} />
                        <XAxis dataKey="quarter" tick={{ fontSize: 7, fill: '#64748b' }} axisLine={false} tickLine={false} />
                        <YAxis tick={{ fontSize: 8, fill: '#64748b' }} axisLine={false} tickLine={false} tickFormatter={v => `${v}%`} width={25} />
                        <Tooltip content={<CustomTooltip />} />
                        <Legend wrapperStyle={{ fontSize: 7, paddingTop: '5px' }} />
                        <Line type="monotone" dataKey="sydney" stroke="#a78bfa" strokeWidth={2} dot={{ r: 1 }} name="Sydney" />
                        <Line type="monotone" dataKey="australia" stroke="#64748b" strokeWidth={1} strokeDasharray="3 3" dot={false} name="Aus" />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* ═══ BUSINESS & WORKFORCE (6 cols x 2 rows) ═══ */}
          <div className="lg:col-span-6 lg:row-span-2 bg-[#0d0d0f] border border-white/[0.06] rounded-2xl p-4 flex flex-col overflow-hidden">
            <div className="flex items-center justify-between mb-4 shrink-0">
              <div className="flex items-center gap-2">
                <Briefcase className="w-4 h-4 text-amber-400/60" />
                <h2 className="text-[11px] font-bold uppercase tracking-widest text-white/50 font-mono">Business & Workforce</h2>
              </div>
              <Badge label="Industry" color="amber" />
            </div>

            <div className="grid grid-cols-2 gap-3 mb-4 shrink-0">
              <KpiCard icon={Briefcase} label={kpiSnapshot.localJobs.label} value="91,980" change={kpiSnapshot.localJobs.change} delay={0.09} />
              <KpiCard icon={Users} label={kpiSnapshot.employedResidents.label} value="122,531" change={kpiSnapshot.employedResidents.change} delay={0.12} />
            </div>

            <div className="flex-1 grid grid-cols-2 gap-4 min-h-0">
              {/* Workforce Composed Chart */}
              <div className="bg-[#111113] border border-white/[0.05] rounded-xl p-3 flex flex-col hover:bg-white/[0.02] transition-colors">
                <h3 className="text-[9px] font-bold uppercase tracking-widest text-white/40 font-mono mb-2">Workforce Capacity</h3>
                <div className="flex-1 min-h-0">
                  <ResponsiveContainer width="100%" height="100%">
                    <ComposedChart data={workforceData} margin={{ top: 5, right: 0, left: 0, bottom: 0 }}>
                      <defs>
                        <linearGradient id="resGrad2" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#10b981" stopOpacity={0.3} /><stop offset="95%" stopColor="#10b981" stopOpacity={0} /></linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke={COLORS.grid} />
                      <XAxis dataKey="year" tick={{ fontSize: 8, fill: '#64748b' }} axisLine={false} tickLine={false} />
                      <YAxis tick={{ fontSize: 8, fill: '#64748b' }} axisLine={false} tickLine={false} tickFormatter={v => `${(v/1000).toFixed(0)}k`} width={25} />
                      <Tooltip content={<CustomTooltip />} />
                      <Legend wrapperStyle={{ fontSize: 8, paddingTop: '5px' }} />
                      <Area type="monotone" dataKey="employedResidents" stroke="#10b981" strokeWidth={2} fill="url(#resGrad2)" name="Resident" />
                      <Line type="monotone" dataKey="localJobs" stroke="#3b82f6" strokeWidth={2} name="Jobs" />
                    </ComposedChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="grid grid-rows-2 gap-3">
                {/* Worker Prod Bar */}
                <div className="bg-[#111113] border border-white/[0.05] rounded-xl p-2.5 flex flex-col hover:bg-white/[0.02] transition-colors">
                  <h3 className="text-[9px] font-bold uppercase tracking-widest text-white/40 font-mono mb-1">Worker Productivity</h3>
                  <div className="flex-1 min-h-0">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={workerProductivity.slice(0, 4)} layout="vertical" margin={{ top: 0, right: 10, left: 0, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke={COLORS.grid} horizontal={false} />
                        <XAxis type="number" tick={{ fontSize: 7, fill: '#64748b' }} axisLine={false} tickLine={false} tickFormatter={v => `$${(v/1000).toFixed(0)}k`} />
                        <YAxis type="category" dataKey="industry" width={65} tick={{ fontSize: 7, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                        <Tooltip content={<CustomTooltip />} />
                        <Legend wrapperStyle={{ fontSize: 7, paddingTop: '2px' }} />
                        <Bar dataKey="hills" fill="#fbbf24" radius={[0, 2, 2, 0]} name="Hills" barSize={5} />
                        <Bar dataKey="nsw" fill="#fbbf24" fillOpacity={0.3} radius={[0, 2, 2, 0]} name="NSW" barSize={5} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Registered Biz Bar */}
                <div className="bg-[#111113] border border-white/[0.05] rounded-xl p-2.5 flex flex-col hover:bg-white/[0.02] transition-colors">
                  <h3 className="text-[9px] font-bold uppercase tracking-widest text-white/40 font-mono mb-1">Registered Businesses</h3>
                  <div className="flex-1 min-h-0">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={registeredBusinessesByIndustry.slice(0, 4)} layout="vertical" margin={{ top: 0, right: 10, left: 0, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke={COLORS.grid} horizontal={false} />
                        <XAxis type="number" tick={{ fontSize: 7, fill: '#64748b' }} axisLine={false} tickLine={false} tickFormatter={v => `${v}%`} />
                        <YAxis type="category" dataKey="industry" width={65} tick={{ fontSize: 7, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                        <Tooltip content={<CustomTooltip />} />
                        <Legend wrapperStyle={{ fontSize: 7, paddingTop: '2px' }} />
                        <Bar dataKey="hills" fill="#f59e0b" radius={[0, 2, 2, 0]} name="Hills" barSize={5} />
                        <Bar dataKey="nsw" fill="#f59e0b" fillOpacity={0.3} radius={[0, 2, 2, 0]} name="NSW" barSize={5} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* ═══ SUPPLY & DATA INTELLIGENCE (INCREASED TO 8 cols x 2 rows) ═══ */}
          <div className="lg:col-span-8 lg:row-span-2 bg-[#0d0d0f] border border-white/[0.06] rounded-2xl p-4 flex flex-col overflow-hidden">
            <div className="flex items-center justify-between mb-4 shrink-0">
              <div className="flex items-center gap-2">
                <Building className="w-4 h-4 text-violet-400/60" />
                <h2 className="text-[11px] font-bold uppercase tracking-widest text-white/50 font-mono">Supply & Approvals Pipeline</h2>
              </div>
              <Badge label="Supply" color="violet" />
            </div>

            <div className="w-1/2 pr-4 mb-4 shrink-0">
              <KpiCard icon={Building} label={kpiSnapshot.buildingApprovals.label} value={kpiSnapshot.buildingApprovals.value} change={kpiSnapshot.buildingApprovals.change} delay={0.15} />
            </div>

            <div className="flex-1 grid grid-cols-2 gap-4 min-h-0">
              {/* Building Approvals Stacked Bar */}
              <div className="bg-[#111113] border border-white/[0.05] rounded-xl p-3 flex flex-col hover:bg-white/[0.02] transition-colors">
                <h3 className="text-[10px] font-bold uppercase tracking-widest text-white/40 font-mono mb-2">Total Building Approvals ($M)</h3>
                <div className="flex-1 min-h-0">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={buildingApprovals} margin={{ top: 5, right: 0, left: 0, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke={COLORS.grid} />
                      <XAxis dataKey="year" tick={{ fontSize: 9, fill: '#64748b' }} axisLine={false} tickLine={false} />
                      <YAxis tick={{ fontSize: 9, fill: '#64748b' }} axisLine={false} tickLine={false} tickFormatter={v => `$${(v/1e6).toFixed(0)}B`} width={30} />
                      <Tooltip content={<CustomTooltip />} />
                      <Legend wrapperStyle={{ fontSize: 9, paddingTop: '10px' }} />
                      <Bar dataKey="residential" fill="#8b5cf6" radius={[0,0,0,0]} name="Residential" stackId="a" />
                      <Bar dataKey="nonResidential" fill="#c4b5fd" radius={[4,4,0,0]} name="Non-Res" stackId="a" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Land Use Pie Chart */}
              <div className="bg-[#111113] border border-white/[0.05] rounded-xl p-3 flex flex-col hover:bg-white/[0.02] transition-colors">
                <h3 className="text-[10px] font-bold uppercase tracking-widest text-white/40 font-mono mb-2">LGA Land Use Profile</h3>
                <div className="flex-1 min-h-0 relative">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={landUse.filter(d => d.category !== 'Other')} cx="50%" cy="50%" innerRadius={35} outerRadius={60} paddingAngle={2} dataKey="value" nameKey="category">
                        {landUse.filter(d => d.category !== 'Other').map((_, i) => <Cell key={i} fill={['#8b5cf6', '#a78bfa', '#c4b5fd', '#ddd6fe', '#ede9fe'][i % 5]} />)}
                      </Pie>
                      <Tooltip content={<CustomTooltip />} />
                      <Legend layout="vertical" verticalAlign="middle" align="right" wrapperStyle={{ fontSize: 9, right: -10 }} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </div>

          {/* ═══ POLICY ASSISTANT (DECREASED TO 4 cols x 2 rows) ═══ */}
          <div className="lg:col-span-4 lg:row-span-2 bg-[#172033] border border-sky-500/20 rounded-2xl p-4 flex flex-col overflow-hidden relative shadow-[inset_0_0_40px_rgba(14,165,233,0.1)]">
            <div className="absolute top-0 right-0 p-2 opacity-5 pointer-events-none">
              <Bot className="w-32 h-32 text-sky-400" />
            </div>
            
            <div className="flex items-center justify-between mb-4 shrink-0 relative z-10 border-b border-sky-500/20 pb-2">
              <div className="flex items-center gap-2">
                <Bot className="w-4 h-4 text-sky-400" />
                <h2 className="text-[11px] font-bold uppercase tracking-widest text-sky-100 font-mono">DCP Intel AI</h2>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-sky-400 animate-pulse"></span>
                <span className="text-[8px] font-mono text-sky-400/80 uppercase">Online</span>
              </div>
            </div>
            
            <div className="flex-1 flex flex-col gap-3 relative z-10 overflow-y-auto mb-3 pr-2 custom-scrollbar">
              <div className="flex gap-2 max-w-[90%] self-start">
                <div className="bg-sky-900/30 border border-sky-500/20 p-2.5 rounded-xl rounded-tl-sm text-[10px] text-sky-100/90 leading-relaxed font-mono">
                  Granny flat on 400 sqm in Kellyville?
                </div>
              </div>
              
              <div className="flex gap-2 max-w-[90%] self-end flex-row-reverse">
                <div className="bg-sky-500/10 border border-sky-400/20 text-white p-2.5 rounded-xl rounded-tr-sm text-[10px] leading-relaxed shadow-lg backdrop-blur-sm">
                  DCP Part B Sec 2: Minimum lot is <strong>450sqm</strong>. You are below threshold.
                </div>
              </div>
              
              <div className="flex gap-2 max-w-[90%] self-start mt-1">
                <div className="bg-sky-900/30 border border-sky-500/20 p-2.5 rounded-xl rounded-tl-sm text-[10px] text-sky-100/90 leading-relaxed font-mono">
                  Max FSR for R4 zoned site there?
                </div>
               </div>
               
               <div className="flex gap-2 max-w-[90%] self-end flex-row-reverse">
                <div className="bg-sky-500/10 border border-sky-400/20 text-white p-2.5 rounded-xl rounded-tr-sm text-[10px] leading-relaxed shadow-lg backdrop-blur-sm">
                  Typically 0.8:1 - 1.2:1 (subject to 20% landscaping). Run massing model?
                </div>
               </div>
            </div>
            
            <div className="relative z-10 w-full mt-auto bg-[#0f172a] rounded-lg border border-sky-500/20 p-1 flex items-center shadow-lg">
              <input type="text" placeholder="Query DCP..." className="flex-1 bg-transparent border-none px-3 py-2 text-[10px] text-white focus:outline-none placeholder:text-white/30" />
              <button className="w-6 h-6 bg-sky-500 text-white rounded-md flex items-center justify-center hover:bg-sky-400 transition-all shadow-[0_0_10px_rgba(14,165,233,0.4)] shrink-0">
                <MessageSquare className="w-3 h-3" />
              </button>
            </div>
          </div>
        </div>

        {/* ═══ RIGHT SIDEBAR (28%): LIVE REAL ESTATE PROSPECTS ═══ */}
        <div className="w-full xl:w-[28%] flex flex-col bg-[#0d0d0f] border border-white/[0.06] rounded-2xl p-4 overflow-hidden relative shadow-2xl h-[calc(3*220px+2*16px+220px+16px)] xl:sticky top-6">
          <div className="flex items-center justify-between mb-4 shrink-0">
            <div className="flex items-center gap-2 border-b border-emerald-500/20 pb-2 w-full">
              <Home className="w-4 h-4 text-emerald-400" />
              <h2 className="text-[12px] font-bold uppercase tracking-widest text-white/90 font-mono">Live Feasibility Targets</h2>
              <span className="ml-auto text-[9px] text-emerald-400 font-mono bg-emerald-400/10 px-2 py-0.5 rounded shadow-[0_0_10px_rgba(52,211,153,0.2)] animate-pulse">LIVE</span>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto space-y-4 custom-scrollbar pr-2 pb-4">
            {[
              { addr: '14 Church St, Castle Hill', price: '$1.45M', roi: '9.2', zone: 'R4', sqm: '650', img: 'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=500&q=80', desc: 'Prime redevelopment corner site near station.' },
              { addr: '82 George St, Baulkham Hills', price: '$1.20M', roi: '8.8', zone: 'R3', sqm: '580', img: 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=500&q=80', desc: 'Duplex scale opportunity subject to council.' },
              { addr: '150 Victoria Rd, Kellyville', price: '$2.10M', roi: '7.5', zone: 'R4', sqm: '920', img: 'https://images.unsplash.com/photo-1628191140046-248db55aa7ed?w=500&q=80', desc: 'High-density apartment block potential.' },
              { addr: '9 Showground Rd, Castle Hill', price: '$1.85M', roi: '8.1', zone: 'R4', sqm: '710', img: 'https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?w=500&q=80', desc: 'Close proximity to retail and transport.' },
              { addr: '12 Boundary Rd, Rouse Hill', price: '$2.40M', roi: '7.1', zone: 'R3', sqm: '1100', img: 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=500&q=80', desc: 'Large lot subdivision potential.' },
              { addr: '45 Windsor Rd, Kellyville', price: '$3.10M', roi: '6.8', zone: 'R4', sqm: '1450', img: 'https://images.unsplash.com/photo-1583608205776-bfd35f0d9f83?w=500&q=80', desc: 'Ample street frontage for medium density.' },
            ].map((p, i) => (
              <div key={i} className="bg-[#111113] border border-white/[0.04] rounded-xl overflow-hidden cursor-pointer group hover:border-emerald-500/40 transition-all hover:bg-emerald-500/5 relative shadow-lg" onClick={() => setSelectedProperty({ address: p.addr, roi: p.roi, zoning: p.zone })}>
                <div className="h-32 w-full relative overflow-hidden bg-[#1a1a1e]">
                  <img src={p.img} alt="Property" className="object-cover w-full h-full opacity-80 group-hover:opacity-100 group-hover:scale-105 transition-all duration-700" />
                  <div className="absolute top-2 right-2 bg-emerald-500 text-black text-[10px] font-mono font-bold px-1.5 py-0.5 rounded shadow-[0_4px_10px_rgba(52,211,153,0.3)]">ROI {p.roi}%</div>
                  <div className="absolute bottom-2 left-2 bg-black/80 backdrop-blur-md text-white text-[9px] font-mono px-2 py-0.5 rounded border border-white/10 shadow-lg">{p.zone} Zoning</div>
                </div>
                <div className="p-3">
                  <div className="text-sm text-white font-medium mb-1 truncate leading-tight group-hover:text-emerald-400 transition-colors">{p.addr}</div>
                  <div className="flex justify-between items-center text-[10px] text-white/50 mb-1.5 border-b border-white/[0.03] pb-1.5">
                    <span className="font-mono text-emerald-400 font-semibold text-[11px]">{p.price}</span>
                    <span className="font-mono bg-white/5 px-1.5 py-0.5 rounded text-[9px]">{p.sqm} sqm</span>
                  </div>
                  <div className="text-[9px] text-white/40 leading-relaxed line-clamp-2">{p.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* ============ FOOTER ============ */}
      <div className="flex justify-between items-center text-[9px] font-bold font-mono text-white/15 uppercase tracking-widest pt-2 border-t border-white/[0.04]">
        <span>Source: profile.id.com.au/the-hills &bull; economy.id.com.au/the-hills</span>
        <span>MAS Dashboard v2.0</span>
      </div>
    </div>
  );
}
