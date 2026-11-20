import { useState, useEffect } from 'react';
import KPIStrip from '../components/KPIStrip';
import { api, simulateDaySSE } from '../lib/api';
import { useStore } from '../state/useStore';
import { ForecastChart } from '../components/Chart';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip } from 'recharts';
import { Play, Pause, RotateCcw, Zap, Sun, Battery } from 'lucide-react';

export default function Overview() {
  const { regionCode } = useStore();
  const [ledgerSummary, setLedgerSummary] = useState<any>(null);
  const [solar, setSolar] = useState<any>(null);
  const [demand, setDemand] = useState<any>(null);
  const [simData, setSimData] = useState<any[]>([]);
  const [isSim, setIsSim] = useState(false);
  const [scrub, setScrub] = useState(0);
  const [approvals, setApprovals] = useState<any[]>([]);

  useEffect(()=>{
    api.ledgerSummary().then(setLedgerSummary).catch(()=>{});
    api.ledgerApprovals().then(setApprovals).catch(()=>{});
    api.solarForecastGET(`lat=23.8&lon=90.4&capacity_kw=500&tilt_deg=23&horizon_hours=24`).then(d=>{
      const fd = d.forecast.map((f:any,i:number)=>({ time: new Date(f.timestamp).getHours()+':00', p10: f.p10, p50: f.p50, p90: f.p90 }));
      setSolar(fd);
    }).catch(()=>{});
    api.demandForecastGET(`region_code=${regionCode}&sites=3&horizon_hours=24`).then(d=>{
      const fd = d.forecast.map((f:any)=>({ time: new Date(f.timestamp).getHours()+':00', p10: f.p10, p50: f.p50, p90: f.p90 }));
      setDemand(fd);
    }).catch(()=>{});
  }, [regionCode]);

  const startSim = () => {
    setIsSim(true);
    setSimData([]);
    setScrub(0);
    const es = simulateDaySSE(regionCode, (data)=>{
      setSimData(prev=>[...prev, { hour: data.hour, solar: data.solar_p50, demand: data.demand_p50, price: data.price }]);
      setScrub(data.hour);
    }, ()=>setIsSim(false));
    // @ts-ignore
    window._simES = es;
  };
  const stopSim = ()=> {
    // @ts-ignore close
    if (window._simES) window._simES.close();
    setIsSim(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap justify-between gap-4 items-end">
        <div>
          <h1 className="font-serif text-[36px] font-semibold tracking-tight leading-none">Control Room • Today</h1>
          <p className="mt-3 text-[14px] text-fg-muted max-w-[60ch]">Forecast → Uncertainty → Optimize → Act → Explain → Measure. One loop, seven modules, cross-border tariffs. Charge 42 EVs between 01:00 and 04:30. Saves 118 USD. Confidence 91%.</p>
        </div>
        <div className="flex gap-2">
          <button disabled={isSim} onClick={startSim} className="flex items-center gap-2 px-4 py-2.5 rounded-control bg-amber-signal text-black text-[13px] font-semibold hover:bg-amber-hover disabled:opacity-50">
            <Play className="w-4 h-4" /> Simulate a day (60s)
          </button>
          <button onClick={stopSim} className="px-3 py-2.5 rounded-control hairline text-[13px] flex items-center gap-2"><Pause className="w-4 h-4" /> Pause</button>
          <button onClick={()=>{setSimData([]); setScrub(0);}} className="px-3 py-2.5 rounded-control hairline text-[13px]"><RotateCcw className="w-4 h-4" /></button>
        </div>
      </div>

      <KPIStrip data={ledgerSummary} />

      {/* Timeline */}
      <div className="rounded-control hairline p-4" style={{background:'var(--bg-900)', borderColor:'var(--border)'}}>
        <div className="flex justify-between items-center mb-4">
          <div className="text-[12px] font-mono uppercase tracking-widest text-fg-muted">Next 24h decision timeline • Region {regionCode}</div>
          <div className="flex gap-2 text-[11px] font-mono">
            <span className="flex items-center gap-1"><span className="w-2 h-2 bg-amber-signal rounded-full"></span>Solar</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 bg-moss rounded-full"></span>Demand</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 bg-slate-400 rounded-full"></span>Price</span>
          </div>
        </div>
        {simData.length>0 ? (
          <div className="h-[260px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={simData}>
                <CartesianGrid stroke="#26322C" strokeDasharray="2 4" opacity={0.5} />
                <XAxis dataKey="hour" tick={{fontSize:10}} />
                <YAxis tick={{fontSize:10}} />
                <Tooltip contentStyle={{background:'#131A17', border:'1px solid #26322C'}} />
                <Line dataKey="solar" stroke="#E0A73A" strokeWidth={2} dot={false} />
                <Line dataKey="demand" stroke="#5F8F6B" strokeWidth={2} dot={false} />
                <Line dataKey="price" stroke="#3E7C86" strokeWidth={1} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="space-y-2">
              <div className="text-[11px] font-mono text-fg-muted">SOLAR P50</div>
              {solar ? <div className="h-[220px]"><ForecastChart data={solar} /></div> : <div className="h-[220px] bg-ink-800 animate-pulse rounded" />}
            </div>
            <div className="space-y-2">
              <div className="text-[11px] font-mono text-fg-muted">DEMAND P50</div>
              {demand ? <div className="h-[220px]"><ForecastChart data={demand} /></div> : <div className="h-[220px] bg-ink-800 animate-pulse rounded" />}
            </div>
          </div>
        )}
        <div className="mt-4 flex items-center gap-3">
          <input type="range" min={0} max={23} value={scrub} onChange={e=>setScrub(Number(e.target.value))} className="flex-1" />
          <div className="font-mono text-[12px] text-fg-muted">{scrub}:00 scrubber</div>
        </div>
      </div>

      {/* Asset map / flow */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 rounded-control hairline p-4" style={{background:'var(--bg-900)'}}>
          <div className="text-[12px] font-mono uppercase tracking-widest text-fg-muted mb-4">Live Asset Flow</div>
          <div className="relative h-[300px] border hairline rounded-[8px] p-4 overflow-hidden" style={{borderColor:'var(--border)', background:'var(--bg-800)'}}>
            {/* SVG flow diagram */}
            <svg viewBox="0 0 600 280" className="w-full h-full">
              <defs>
                <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                  <path d="M 0 0 L 10 5 L 0 10 z" fill="#8E9A92" />
                </marker>
              </defs>
              <g>
                <rect x="20" y="30" width="100" height="50" rx="8" fill="#1B2420" stroke="#26322C" />
                <text x="70" y="55" textAnchor="middle" fill="#E0A73A" fontSize="12" fontFamily="monospace">PV 500kW</text>
                <text x="70" y="70" textAnchor="middle" fill="#8E9A92" fontSize="9" fontFamily="monospace">{solar?.[scrub]?.p50?.toFixed(0) || '420'} kW</text>
              </g>
              <g>
                <rect x="20" y="110" width="100" height="50" rx="8" fill="#1B2420" stroke="#26322C" />
                <text x="70" y="135" textAnchor="middle" fill="#5F8F6B" fontSize="12" fontFamily="monospace">Batt 150kWh</text>
                <text x="70" y="150" textAnchor="middle" fill="#8E9A92" fontSize="9">SOC 68%</text>
              </g>
              <g>
                <rect x="20" y="190" width="100" height="50" rx="8" fill="#1B2420" stroke="#26322C" />
                <text x="70" y="215" textAnchor="middle" fill="#8E9A92" fontSize="12" fontFamily="monospace">Grid</text>
                <text x="70" y="230" textAnchor="middle" fill="#8E9A92" fontSize="9">CO₂ 0.68kg/kWh</text>
              </g>
              {/* Central bus */}
              <rect x="240" y="100" width="120" height="80" rx="12" fill="#131A17" stroke="#E0A73A" strokeWidth={1.5} />
              <text x="300" y="130" textAnchor="middle" fill="#ECE8DD" fontSize="12" fontFamily="serif">EMS Bus</text>
              <text x="300" y="150" textAnchor="middle" fill="#E0A73A" fontSize="11" fontFamily="monospace">Decision Engine</text>

              {/* Loads */}
              <rect x="480" y="30" width="100" height="50" rx="8" fill="#1B2420" stroke="#26322C" />
              <text x="530" y="55" textAnchor="middle" fill="#ECE8DD" fontSize="11" fontFamily="monospace">EV Fleet 42</text>
              <text x="530" y="70" textAnchor="middle" fill="#8E9A92" fontSize="9">Chrg 01-04:30</text>

              <rect x="480" y="110" width="100" height="50" rx="8" fill="#1B2420" stroke="#26322C" />
              <text x="530" y="135" textAnchor="middle" fill="#ECE8DD" fontSize="11">Indust 400kW</text>

              <rect x="480" y="190" width="100" height="50" rx="8" fill="#1B2420" stroke="#26322C" />
              <text x="530" y="215" textAnchor="middle" fill="#ECE8DD" fontSize="11">HVAC Flex</text>

              {/* Arrows */}
              <line x1="120" y1="55" x2="240" y2="115" stroke="#8E9A92" strokeDasharray="4 4" markerEnd="url(#arrow)" />
              <line x1="120" y1="135" x2="240" y2="135" stroke="#8E9A92" markerEnd="url(#arrow)" />
              <line x1="120" y1="215" x2="240" y2="165" stroke="#8E9A92" markerEnd="url(#arrow)" />
              <line x1="360" y1="125" x2="480" y2="55" stroke="#E0A73A" strokeWidth={2} markerEnd="url(#arrow)" />
              <line x1="360" y1="140" x2="480" y2="135" stroke="#5F8F6B" markerEnd="url(#arrow)" />
              <line x1="360" y1="155" x2="480" y2="215" stroke="#3E7C86" markerEnd="url(#arrow)" />
            </svg>
          </div>
          <div className="mt-3 text-[11px] font-mono text-fg-muted">SINGLE DECISION LOOP: Forecast (P10/P50/P90) → Uncertainty (variability index) → Optimize (RL+LP) → Act (human approval) → Explain (counterfactual) → Measure $/CO₂/peak</div>
        </div>

        <div className="space-y-4">
          <div className="rounded-control hairline p-4" style={{background:'var(--bg-900)'}}>
            <div className="text-[11px] font-mono uppercase text-fg-muted">Human-in-the-loop approvals</div>
            <div className="mt-3 space-y-2">
              {approvals.slice(0,4).map((a:any)=>(
                <div key={a.id} className="p-3 rounded-[6px] bg-ink-800 border hairline text-[12px]">
                  <div className="font-medium">{a.action}</div>
                  <div className="text-[11px] text-fg-muted mt-1">{a.description}</div>
                  <div className="flex gap-2 mt-2">
                    <button onClick={()=>api.ledgerApprove(a.id,'approve').then(()=>api.ledgerApprovals().then(setApprovals))} className="px-2 py-1 rounded bg-moss text-black text-[11px]">Approve</button>
                    <button onClick={()=>api.ledgerApprove(a.id,'reject').then(()=>api.ledgerApprovals().then(setApprovals))} className="px-2 py-1 rounded border text-[11px]">Reject</button>
                    <span className="ml-auto text-[10px] font-mono text-fg-muted">{a.status}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-control hairline p-4" style={{background:'var(--bg-900)'}}>
            <div className="text-[11px] font-mono uppercase text-fg-muted">Decision explainability</div>
            <div className="mt-3 font-serif text-[14px] leading-[1.4]">Charge 42 EVs between 01:00 and 04:30. Saves 118 USD (BDT 12,400). CO₂ avoided 45 kg. Confidence 91%. If we did immediate charging, cost +18% and peak 210 kW higher. Top driver: night tariff 6.2 vs peak 12.8 BDT.</div>
            <div className="mt-3 flex gap-2">
              <span className="text-[10px] font-mono px-2 py-1 rounded bg-ink-800 border">SoC guarantee 100%</span>
              <span className="text-[10px] font-mono px-2 py-1 rounded bg-ink-800 border">Fairness var 0.02</span>
              <span className="text-[10px] font-mono px-2 py-1 rounded bg-ink-800 border">P10≤P50≤P90 ✓</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
