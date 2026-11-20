import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart, ComposedChart } from 'recharts';

export function ForecastChart({ data, title }: { data: any[], title?: string }) {
  return (
    <div className="rounded-control hairline p-4" style={{background:'var(--bg-900)', borderColor:'var(--border)'}}>
      {title && <div className="text-[12px] font-mono text-fg-muted mb-3 uppercase tracking-widest">{title}</div>}
      <div className="h-[280px]">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data}>
            <CartesianGrid strokeDasharray="2 4" stroke="#26322C" opacity={0.6} />
            <XAxis dataKey="time" tick={{fontSize:10, fill:'#8E9A92'}} />
            <YAxis tick={{fontSize:10, fill:'#8E9A92'}} />
            <Tooltip contentStyle={{background:'#131A17', border:'1px solid #26322C', borderRadius:8, fontSize:12}} />
            <Area type="monotone" dataKey="p90" stroke="none" fill="#E0A73A" fillOpacity={0.15} />
            <Area type="monotone" dataKey="p10" stroke="none" fill="#0D1210" fillOpacity={0.8} />
            <Line type="monotone" dataKey="p50" stroke="#E0A73A" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="p10" stroke="#5F8F6B" strokeDasharray="4 4" strokeWidth={1} dot={false} />
            <Line type="monotone" dataKey="p90" stroke="#5F8F6B" strokeDasharray="4 4" strokeWidth={1} dot={false} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-3 flex gap-4 text-[10px] font-mono text-fg-muted">
        <span className="flex items-center gap-1"><span className="w-3 h-[2px] bg-[#E0A73A] block"></span>P50 median</span>
        <span className="flex items-center gap-1"><span className="w-3 h-[2px] block" style={{background:'#5F8F6B', borderTop:'1px dashed'}}></span>P10/P90 confidence</span>
      </div>
    </div>
  );
}

export function SimpleLineChart({ data, dataKeys, color="#E0A73A" }: { data: any[], dataKeys: string[], color?: string }) {
  return (
    <div className="h-[240px]">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="2 4" stroke="#26322C" opacity={0.5} />
          <XAxis dataKey="hour" tick={{fontSize:10, fill:'#8E9A92'}} />
          <YAxis tick={{fontSize:10, fill:'#8E9A92'}} />
          <Tooltip contentStyle={{background:'#131A17', border:'1px solid #26322C', borderRadius:8}} />
          {dataKeys.map(k=> <Line key={k} type="monotone" dataKey={k} stroke={color} strokeWidth={1.5} dot={false} />)}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
