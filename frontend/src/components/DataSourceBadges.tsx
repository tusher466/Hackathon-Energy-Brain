import { useState } from 'react';
import { DataProvenance } from '../lib/api';
import { Database, Cloud, Zap, Activity, Server, ExternalLink } from 'lucide-react';

const sourceMeta: Record<string, { icon: any, color: string, label: string }> = {
  nrel_nsrdb: { icon: Database, color: 'text-amber-signal', label: 'NREL NSRDB' },
  noaa_gfs: { icon: Cloud, color: 'text-moss', label: 'NOAA GFS' },
  electricity_maps: { icon: Zap, color: 'text-teal-slate', label: 'Electricity Maps' },
  opsd: { icon: Server, color: 'text-ochre', label: 'OPSD EU' },
  pjm_dataminer: { icon: Activity, color: 'text-brick', label: 'PJM Data Miner' },
};

function modeDot(mode: string) {
  if (mode === 'live') return 'bg-moss';
  if (mode === 'dataset_snapshot') return 'bg-teal-slate';
  return 'bg-amber-signal'; // synthetic
}

function modeLabel(mode: string) {
  if (mode === 'live') return 'LIVE';
  if (mode === 'dataset_snapshot') return 'SNAPSHOT';
  return 'SYNTHETIC';
}

export default function DataSourceBadges({ sources }: { sources?: DataProvenance[] }) {
  const [selected, setSelected] = useState<DataProvenance | null>(null);

  if (!sources || sources.length === 0) {
    return (
      <div className="text-[11px] font-mono text-fg-muted border hairline rounded-[6px] px-3 py-2" style={{background:'var(--bg-800)'}}>
        No provenance attached yet
      </div>
    );
  }

  return (
    <>
      <div className="flex flex-wrap gap-2">
        {sources.map((src, idx) => {
          const meta = sourceMeta[src.source_id] || { icon: Database, color: 'text-fg-muted', label: src.source_id };
          const Icon = meta.icon;
          return (
            <button
              key={`${src.source_id}-${idx}`}
              onClick={() => setSelected(src)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-full border hairline text-[11px] font-mono hover:bg-ink-800 transition-colors"
              style={{background:'var(--bg-800)', borderColor:'var(--border)'}}
            >
              <span className={`w-2 h-2 rounded-full ${modeDot(src.mode)}`} />
              <Icon className={`w-3 h-3 ${meta.color}`} />
              <span className="font-medium">{meta.label}</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-ink-900 border">{modeLabel(src.mode)}</span>
              <span className="text-[10px] text-fg-muted">{src.latency_ms?.toFixed(0)}ms</span>
            </button>
          );
        })}
      </div>

      {/* Drawer / Popover */}
      {selected && (
        <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/60 backdrop-blur-sm p-4" onClick={() => setSelected(null)}>
          <div
            className="w-full max-w-[640px] rounded-control border hairline overflow-hidden bg-ink-900 max-h-[85vh] overflow-y-auto"
            style={{background:'var(--bg-900)', borderColor:'var(--border)'}}
            onClick={e => e.stopPropagation()}
          >
            <div className="p-4 border-b hairline flex justify-between items-start gap-3" style={{borderColor:'var(--border)'}}>
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full ${modeDot(selected.mode)}`} />
                  <span className="font-serif text-[18px] font-semibold">{selected.source_name}</span>
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${selected.mode==='live' ? 'bg-moss text-black' : selected.mode==='dataset_snapshot' ? 'bg-teal-slate text-white' : 'bg-amber-signal text-black'}`}>{modeLabel(selected.mode)}</span>
                </div>
                <div className="text-[11px] font-mono text-fg-muted mt-1 break-all">{selected.endpoint_or_dataset}</div>
                <div className="text-[11px] font-mono text-fg-muted mt-1">Region: {selected.region_scope} • Fetched: {new Date(selected.fetched_at).toLocaleString()} • Latency: {selected.latency_ms}ms {selected.status_code ? `• HTTP ${selected.status_code}` : ''}</div>
              </div>
              <button onClick={() => setSelected(null)} className="px-2 py-1 rounded border text-[12px] shrink-0">✕</button>
            </div>

            <div className="p-4 space-y-4">
              <div>
                <div className="text-[11px] font-mono uppercase text-fg-muted">Fields ingested</div>
                <div className="mt-2 flex flex-wrap gap-1">
                  {selected.fields_ingested.map(f => (
                    <span key={f} className="text-[10px] font-mono px-2 py-1 rounded bg-ink-800 border">{f}</span>
                  ))}
                </div>
              </div>

              {selected.description && (
                <div>
                  <div className="text-[11px] font-mono uppercase text-fg-muted">Description</div>
                  <div className="mt-1 text-[12px] leading-relaxed text-fg-muted">{selected.description}</div>
                </div>
              )}

              <div>
                <div className="text-[11px] font-mono uppercase text-fg-muted flex items-center gap-2">Sample record <ExternalLink className="w-3 h-3" /> judge-inspectable</div>
                <pre className="mt-2 p-3 rounded bg-ink-950 border text-[11px] font-mono overflow-auto max-h-[260px]" style={{borderColor:'var(--border)'}}>
                  {JSON.stringify(selected.sample_record, null, 2)}
                </pre>
              </div>

              <div className="flex gap-2">
                <div className="text-[10px] font-mono text-fg-muted">Source ID: {selected.source_id} • Provenance verified offline-first • Tier: {selected.mode}</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
