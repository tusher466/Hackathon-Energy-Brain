import { useEffect, useState } from 'react';
import { api } from '../lib/api';
import { useStore } from '../state/useStore';
import { ScanEye, Upload } from 'lucide-react';

export default function Panels() {
  const { regionCode, regions } = useStore();
  const [data, setData] = useState<any>(null);
  const [seed, setSeed] = useState(0);
  const [file, setFile] = useState<File|null>(null);

  const loadSample = async () => {
    const res = await api.panelSample(regionCode, seed);
    setData(res);
  };
  useEffect(()=>{ loadSample(); }, [regionCode, seed]);

  const handleUpload = async () => {
    if (!file) return;
    const res = await api.panelInspect(file, regionCode);
    setData(res);
  };

  const curr = regions.find((r:any)=>r.code===regionCode);

  return (
    <div className="space-y-6 overflow-x-hidden">
      <div className="flex flex-col sm:flex-row sm:justify-between gap-3">
        <div className="min-w-0 flex-1">
          <h1 className="font-serif text-[24px] sm:text-[32px] font-semibold break-words">Panel Health Inspector • Thermography</h1>
          <p className="text-[12px] sm:text-[13px] text-fg-muted mt-1 max-w-[70ch] leading-relaxed">Upload drone thermal image or use synthetic samples generated at startup. OpenCV pipeline: normalize, threshold hot regions, connected components, classify defect by shape/temp delta.</p>
        </div>
        <div className="text-[11px] font-mono px-3 py-1 rounded-full bg-ink-800 border shrink-0 h-fit">Loss est in {curr?.currency || 'BDT'}</div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 rounded-control hairline p-4 space-y-4" style={{background:'var(--bg-900)'}}>
          <div className="text-[11px] font-mono uppercase text-fg-muted">Controls</div>
          <div className="flex gap-2">
            <button onClick={()=>setSeed(s=>s+1)} className="flex-1 py-2 rounded bg-amber-signal text-black font-semibold text-[12px]">New synthetic sample</button>
            <button onClick={loadSample} className="px-3 py-2 rounded border text-[12px]">Reload</button>
          </div>
          <div>
            <label className="text-[12px]">Upload thermal JPG/PNG</label>
            <input type="file" accept="image/*" onChange={e=>setFile(e.target.files?.[0]||null)} className="mt-1 w-full text-[12px]" />
            <button disabled={!file} onClick={handleUpload} className="mt-2 w-full py-2 rounded bg-ink-800 border text-[13px] disabled:opacity-50 flex items-center justify-center gap-2"><Upload className="w-4 h-4" /> Inspect uploaded</button>
          </div>

          {data && (
            <div className="mt-4 space-y-3">
              <div className="text-[11px] font-mono uppercase text-fg-muted">Summary</div>
              <div className="text-[13px] leading-relaxed">{data.summary}</div>
              <div className="grid grid-cols-2 gap-2 text-[11px] font-mono">
                <div className="p-2 rounded bg-ink-800 border">Eff loss {data.total_efficiency_loss_pct.toFixed(1)}%</div>
                <div className="p-2 rounded bg-ink-800 border">Yearly {data.total_yearly_loss_kwh.toFixed(0)} kWh</div>
                <div className="p-2 rounded bg-ink-800 border col-span-2">Money {curr?.currency_symbol}{data.total_money_loss.toFixed(1)}</div>
              </div>
            </div>
          )}
        </div>

        <div className="lg:col-span-2 space-y-4">
          <div className="rounded-control hairline p-4" style={{background:'var(--bg-900)'}}>
            <div className="text-[11px] font-mono uppercase text-fg-muted mb-3">Annotated thermal overlay</div>
            {data?.annotated_image_b64 ? (
              <img src={`data:image/jpeg;base64,${data.annotated_image_b64}`} alt="thermal annotated" className="w-full rounded border" style={{borderColor:'var(--border)'}} />
            ) : (
              <div className="h-[400px] bg-ink-800 animate-pulse rounded" />
            )}
            <div className="mt-3 text-[11px] text-fg-muted">Color map JET: blue cold, red hot. Boxes: high=brick, medium=amber, low=moss. Shape heuristic classifies hotspot cell vs bypass diode vs soiling vs string fault.</div>
          </div>

          <div className="rounded-control hairline p-4" style={{background:'var(--bg-900)'}}>
            <div className="text-[11px] font-mono uppercase text-fg-muted mb-3">Defects ({data?.defects?.length || 0})</div>
            <div className="space-y-2">
              {data?.defects?.map((d:any)=>(
                <div key={d.id} className="flex gap-3 p-3 rounded bg-ink-800 border text-[12px]">
                  <div className={`w-2 h-auto rounded ${d.severity==='high'?'bg-brick': d.severity==='medium'?'bg-ochre':'bg-moss'}`} />
                  <div className="flex-1">
                    <div className="flex justify-between"><span className="font-medium">{d.type} • {d.severity}</span><span className="font-mono text-[11px]">Δ {d.temp_delta_c.toFixed(1)}°C</span></div>
                    <div className="text-fg-muted text-[11px] mt-1">Loss {d.efficiency_loss_pct}% • {d.yearly_loss_kwh.toFixed(0)}kWh/yr • {curr?.currency_symbol}{d.money_loss.toFixed(1)}</div>
                    <div className="mt-1 text-[11px]">{d.recommendation}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
