import { useStore } from '../state/useStore';
import { formatCurrency, fmtCO2, fmtKW } from '../lib/format';

export default function KPIStrip({ data }: { data?: any }) {
  const { regionCode, regions } = useStore();
  const items = [
    { label: 'Saved today', value: data ? formatCurrency(data.total_cost_saved || 1284, regionCode, regions) : '৳ 1,284', sub: '+12% vs yesterday' },
    { label: 'CO₂ avoided', value: data ? fmtCO2(data.total_co2_avoided_kg || 420) : '420 kg', sub: 'Method: marginal' },
    { label: 'Peak shaved', value: data ? fmtKW(data.total_peak_shaved_kw || 84) : '84 kW', sub: 'Transformer 1,000 kW' },
    { label: 'Forecast error', value: data?.forecast_error ? `${data.forecast_error}% MAPE` : '7.8% MAPE', sub: 'P50 confidence 91%' },
  ];
  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
      {items.map(it=>(
        <div key={it.label} className="rounded-control hairline p-3 sm:p-4 overflow-hidden min-w-0" style={{background:'var(--bg-900)', borderColor:'var(--border)'}}>
          <div className="text-[10px] sm:text-[11px] font-mono tracking-widest text-fg-muted uppercase truncate">{it.label}</div>
          <div className="font-serif text-[20px] sm:text-[28px] font-semibold mt-2 tracking-tight tabular-nums break-words leading-tight">{it.value}</div>
          <div className="text-[10px] sm:text-[11px] font-mono text-fg-muted mt-1 truncate">{it.sub}</div>
        </div>
      ))}
    </div>
  );
}
