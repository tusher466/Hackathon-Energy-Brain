import { useEffect, useState } from 'react';
import { api } from '../lib/api';
import { useStore } from '../state/useStore';

export default function Settings() {
  const { regionCode, setRegion, regions, darkMode, toggleDark } = useStore();
  const [models, setModels] = useState<any[]>([]);
  const [integrations, setIntegrations] = useState<any[]>([]);
  const [tariff, setTariff] = useState<any>(null);

  useEffect(()=>{
    api.modelStatus().then(setModels).catch(()=>{});
    api.integrations().then(setIntegrations).catch(()=>{});
  }, []);
  useEffect(()=>{
    if (regionCode) api.getTariff(regionCode).then(setTariff).catch(()=>{});
  }, [regionCode]);

  return (
    <div className="space-y-6">
      <h1 className="font-serif text-[32px] font-semibold">Settings • Integrations & Demo</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="rounded-control hairline p-4" style={{background:'var(--bg-900)'}}>
          <div className="text-[11px] font-mono uppercase text-fg-muted">Region profile • cross-border</div>
          <select value={regionCode} onChange={e=>setRegion(e.target.value)} className="mt-3 w-full bg-ink-800 border rounded px-3 py-2 text-[13px]">
            {regions.map((r:any)=><option key={r.code} value={r.code}>{r.name} — {r.currency} — {r.tariff_structure}</option>)}
          </select>
          {tariff && (
            <div className="mt-4">
              <div className="text-[12px] font-medium">{tariff.region.name} tariff hourly</div>
              <div className="mt-2 grid grid-cols-12 gap-1 font-mono text-[10px]">
                {tariff.hourly_tariff.map((p:number,i:number)=><div key={i} className="p-1 rounded bg-ink-800 border text-center"><div>{i}h</div><div>{p.toFixed(2)}</div></div>)}
              </div>
              <div className="mt-3 text-[11px] text-fg-muted">Carbon avg {tariff.region.carbon_factor_avg_kg_per_kwh} kg/kWh, marginal {tariff.region.carbon_factor_marginal_kg_per_kwh}. Peak hours {tariff.region.peak_hours.join(',')}.</div>
            </div>
          )}
          <button onClick={toggleDark} className="mt-4 px-3 py-2 rounded border text-[12px]">{darkMode ? 'Switch to Light' : 'Switch to Dark'} • Control room at dusk theme</button>
        </div>

        <div className="rounded-control hairline p-4" style={{background:'var(--bg-900)'}}>
          <div className="text-[11px] font-mono uppercase text-fg-muted">Demo controls</div>
          <div className="mt-3 space-y-2">
            <button onClick={()=>{api.ledgerReset().then(()=>alert('Ledger reset'));}} className="w-full py-2 rounded bg-ink-800 border text-[13px]">Reset ledger & approvals</button>
            <button onClick={()=>{localStorage.clear(); alert('Local cache cleared');}} className="w-full py-2 rounded bg-ink-800 border text-[13px]">Clear local storage</button>
            <a href="http://localhost:8000/docs" target="_blank" className="block w-full text-center py-2 rounded bg-amber-signal text-black font-semibold text-[13px]">Open API docs (Swagger)</a>
          </div>
          <div className="mt-6">
            <div className="text-[11px] font-mono uppercase text-fg-muted">Premium checklist</div>
            <ul className="mt-2 text-[12px] space-y-1 list-disc ml-4 text-fg-muted">
              <li>Live demo mode: Simulate a day 60s scrubber – Overview</li>
              <li>Scenario compare: save two configs side-by-side (use browser storage – coming)</li>
              <li>Counterfactual explainer on every decision – VPP page</li>
              <li>Uncertainty bands everywhere – Solar/Demand</li>
              <li>Region switch currency/tariff/carbon instant – all pages</li>
              <li>Human-in-loop approvals – Overview + Grid</li>
              <li>Savings ledger methodology tooltip + export – Ledger</li>
              <li>Black-start timeline SVG animation – Grid</li>
              <li>Thermal annotated overlay + money loss – Panels</li>
              <li>Command palette Cmd+K, keyboard nav, dark/light, print – Layout</li>
            </ul>
          </div>
        </div>

        <div className="rounded-control hairline p-4" style={{background:'var(--bg-900)'}}>
          <div className="text-[11px] font-mono uppercase text-fg-muted">Model status</div>
          <div className="mt-3 space-y-2">
            {models.map((m:any)=><div key={m.name} className="flex justify-between p-2 rounded bg-ink-800 border text-[12px]"><span>{m.name} {m.version}</span><span className="font-mono text-[11px]">{m.status} • {m.accuracy ? (m.accuracy*100).toFixed(0)+'%' : ''}</span></div>)}
          </div>
        </div>

        <div className="rounded-control hairline p-4" style={{background:'var(--bg-900)'}}>
          <div className="text-[11px] font-mono uppercase text-fg-muted">Integrations – live vs synthetic provenance</div>
          <div className="mt-3 space-y-2">
            {integrations.map((i:any)=><div key={i.name} className="flex justify-between p-2 rounded bg-ink-800 border text-[12px]"><span>{i.name}</span><span className={`px-2 py-0.5 rounded text-[10px] ${i.status==='live'?'bg-moss text-black':'bg-ink-700'}`}>{i.status} {i.requires_key?'• needs key':''}</span></div>)}
          </div>
          <div className="mt-3 text-[11px] text-fg-muted">Set keys in backend .env: NREL_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, ELECTRICITYMAPS_API_KEY. App auto falls back to synthetic offline.</div>
        </div>
      </div>
    </div>
  );
}
