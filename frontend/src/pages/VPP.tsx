import { useEffect, useState } from 'react';
import { api } from '../lib/api';
import { useStore } from '../state/useStore';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { Zap, Battery, Car } from 'lucide-react';

export default function VPP() {
  const { regionCode, regions } = useStore();
  const [fleet, setFleet] = useState<any>(null);
  const [result, setResult] = useState<any>(null);
  const [lambdaCo2, setLambda] = useState(0.5);
  const [muPeak, setMuPeak] = useState(1.0);
  const [limit, setLimit] = useState(1000);
  const [loading, setLoading] = useState(false);

  useEffect(()=>{
    api.vppDefaultFleet().then(setFleet).catch(()=>{});
  }, []);

  const runDispatch = async () => {
    setLoading(true);
    try {
      const payload = {
        region_code: regionCode,
        evs: fleet?.evs || [],
        batteries: fleet?.batteries || [],
        flexible_loads: fleet?.flexible_loads || [],
        lambda_co2: lambdaCo2,
        mu_peak: muPeak,
        transformer_limit_kw: limit,
        horizon_hours: 24
      };
      const res = await api.vppDispatch(payload);
      setResult(res);
    } catch(e){ console.error(e); }
    setLoading(false);
  };

  const chartData = result ? result.aggregate_before.map((b:any,i:number)=>({
    hour: i,
    baseline: b,
    optimized: result.aggregate_after[i],
  })) : [];

  const currencySym = regions.find((r:any)=>r.code===regionCode)?.currency_symbol || '৳';

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="font-serif text-[32px] font-semibold">VPP Dispatch Agent</h1>
          <p className="text-[13px] text-fg-muted mt-1 max-w-[75ch]">Fleet simulator: N EVs with arrival/departure + SoC constraints, M batteries, flexible loads. Two controllers side-by-side: Baseline immediate charging vs Smart RL+LP optimizer with safety layer guaranteeing 100% SoC.</p>
        </div>
        <div className="flex gap-2">
          <div className="text-[11px] font-mono px-3 py-1 rounded-full bg-ink-800 border">λ CO₂ {lambdaCo2} • μ peak {muPeak}</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-1 rounded-control hairline p-4 space-y-4" style={{background:'var(--bg-900)'}}>
          <div className="text-[11px] font-mono uppercase text-fg-muted">Controls</div>
          <div>
            <label className="text-[12px]">λ CO₂ weight</label>
            <input type="range" min={0} max={2} step={0.1} value={lambdaCo2} onChange={e=>setLambda(Number(e.target.value))} className="w-full" />
            <div className="text-[11px] font-mono">{lambdaCo2}</div>
          </div>
          <div>
            <label className="text-[12px]">μ Peak weight</label>
            <input type="range" min={0} max={3} step={0.1} value={muPeak} onChange={e=>setMuPeak(Number(e.target.value))} className="w-full" />
            <div className="text-[11px] font-mono">{muPeak}</div>
          </div>
          <div>
            <label className="text-[12px]">Transformer limit kW</label>
            <input type="number" value={limit} onChange={e=>setLimit(Number(e.target.value))} className="w-full bg-ink-800 border rounded px-3 py-2 text-[13px]" />
          </div>
          <button onClick={runDispatch} disabled={loading} className="w-full py-2.5 rounded bg-amber-signal text-black font-semibold text-[13px] disabled:opacity-50">{loading ? 'Optimizing…' : 'Run Smart Dispatch'}</button>

          <div className="mt-6">
            <div className="text-[11px] font-mono uppercase text-fg-muted">Fleet</div>
            <div className="mt-2 space-y-2 max-h-[300px] overflow-auto">
              {fleet?.evs?.map((ev:any)=>(
                <div key={ev.id} className="p-2 rounded bg-ink-800 border text-[11px] font-mono">
                  <div className="flex justify-between"><span className="font-semibold"><Car className="w-3 h-3 inline mr-1" />{ev.id}</span><span>{ev.capacity_kwh}kWh</span></div>
                  <div>Arr {ev.arrival_hour} Dep {ev.departure_hour} SoC {ev.initial_soc_kwh.toFixed(0)}→{ev.required_soc_kwh.toFixed(0)}</div>
                </div>
              ))}
            </div>
          </div>

          {result && (
            <div className="mt-6 p-3 rounded bg-ink-800 border text-[12px] space-y-2">
              <div className="font-medium">Fairness check</div>
              <div className="text-fg-muted text-[11px]">Mean delivery {(result.fairness_metrics.mean_soc_delivery*100).toFixed(0)}% • Min {(result.fairness_metrics.min_soc_delivery*100).toFixed(0)}% • Var {result.fairness_metrics.variance.toFixed(3)}</div>
              <div className={`text-[11px] px-2 py-1 rounded ${result.fairness_metrics.all_guaranteed ? 'bg-moss text-black' : 'bg-brick text-white'}`}>{result.fairness_metrics.all_guaranteed ? '✓ SoC guarantee 100%' : '⚠ Guarantee violated'}</div>
            </div>
          )}
        </div>

        <div className="lg:col-span-3 space-y-4">
          {result ? (
            <>
              <div className="grid grid-cols-3 gap-3">
                <div className="rounded-control hairline p-4" style={{background:'var(--bg-900)'}}><div className="text-[11px] font-mono text-fg-muted">COST SAVED</div><div className="font-mono text-[24px] font-semibold mt-1">{currencySym}{result.cost_saved.toFixed(1)}</div><div className="text-[11px] text-fg-muted">Baseline {currencySym}{result.baseline_cost.toFixed(0)} → {currencySym}{result.optimized_cost.toFixed(0)}</div></div>
                <div className="rounded-control hairline p-4" style={{background:'var(--bg-900)'}}><div className="text-[11px] font-mono text-fg-muted">CO₂ SAVED</div><div className="font-mono text-[24px] font-semibold mt-1">{result.co2_saved_kg.toFixed(0)} kg</div><div className="text-[11px] text-fg-muted">Lane: {regionCode} marginal factor</div></div>
                <div className="rounded-control hairline p-4" style={{background:'var(--bg-900)'}}><div className="text-[11px] font-mono text-fg-muted">PEAK SHAVED</div><div className="font-mono text-[24px] font-semibold mt-1">{result.peak_reduction_kw.toFixed(0)} kW</div><div className="text-[11px] text-fg-muted">{result.peak_before_kw.toFixed(0)} → {result.peak_after_kw.toFixed(0)} kW</div></div>
              </div>

              <div className="rounded-control hairline p-4" style={{background:'var(--bg-900)'}}>
                <div className="text-[11px] font-mono uppercase text-fg-muted mb-3">Aggregate load before vs after • Baseline immediate vs Smart</div>
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData}>
                      <CartesianGrid stroke="#26322C" strokeDasharray="2 4" opacity={0.5} />
                      <XAxis dataKey="hour" tick={{fontSize:10}} />
                      <YAxis tick={{fontSize:10}} />
                      <Tooltip contentStyle={{background:'#131A17', border:'1px solid #26322C'}} />
                      <Legend />
                      <Line type="monotone" dataKey="baseline" stroke="#C2503A" strokeWidth={2} dot={false} name="Baseline immediate" />
                      <Line type="monotone" dataKey="optimized" stroke="#E0A73A" strokeWidth={2} dot={false} name="Optimized RL+LP" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
                <div className="mt-4 grid grid-cols-1 lg:grid-cols-2 gap-4 text-[12px]">
                  <div className="p-3 rounded bg-ink-800 border">
                    <div className="font-medium flex items-center gap-2"><Zap className="w-4 h-4 text-amber-signal" /> Decision explain</div>
                    <div className="mt-2 text-fg-muted leading-relaxed">{result.explain.counterfactual}</div>
                    <div className="mt-2 flex flex-wrap gap-1">{result.explain.top_drivers.map((d:any,i:number)=><span key={i} className="text-[10px] font-mono px-2 py-1 rounded bg-ink-900 border">{d}</span>)}</div>
                  </div>
                  <div className="p-3 rounded bg-ink-800 border">
                    <div className="font-medium">Per-asset schedules (first 3 EVs)</div>
                    <div className="mt-2 space-y-1 font-mono text-[11px]">
                      {Object.entries(result.ev_schedules).slice(0,3).map(([id,sched]:any)=>(
                        <div key={id} className="flex gap-1"><span className="w-[50px]">{id}</span><span className="text-fg-muted">{(sched as number[]).map((v:number)=>v>0?'█':'·').join('')}</span><span className="ml-2">{(sched as number[]).reduce((a:number,b:number)=>a+b,0).toFixed(0)}kWh</span></div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="rounded-control hairline p-10 text-center" style={{background:'var(--bg-900)'}}>
              <div className="mx-auto w-12 h-12 rounded-full bg-ink-800 flex items-center justify-center"><Zap className="w-6 h-6 text-amber-signal" /></div>
              <div className="mt-4 font-serif text-[18px]">Ready to dispatch</div>
              <div className="mt-2 text-[13px] text-fg-muted max-w-[50ch] mx-auto">Baseline charges immediately upon arrival. Smart defers to night low-price, low-carbon hours while respecting transformer limit {limit}kW, SoC deadlines, battery cycle limits. Click Run.</div>
            </div>
          )}

          {/* Battery */}
          {result?.battery_schedules && (
            <div className="rounded-control hairline p-4" style={{background:'var(--bg-900)'}}>
              <div className="text-[11px] font-mono uppercase text-fg-muted flex items-center gap-2"><Battery className="w-4 h-4" /> Battery arbitrage</div>
              <div className="mt-3 font-mono text-[11px] grid grid-cols-6 gap-2">
                {Object.entries(result.battery_schedules).map(([id,sched]:any)=>(
                  <div key={id} className="p-2 rounded bg-ink-800 border">
                    <div className="font-semibold">{id}</div>
                    <div className="mt-1">{(sched as number[]).map((v:number,i:number)=> v>0 ? `+${v.toFixed(0)}@${i}` : v<0 ? `${v.toFixed(0)}@${i}` : '').filter(Boolean).slice(0,4).join(' ')}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
