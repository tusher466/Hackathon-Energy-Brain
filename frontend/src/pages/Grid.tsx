import { useEffect, useState } from 'react';
import { api } from '../lib/api';
import { useStore } from '../state/useStore';
import { Shield, MessageSquare, Zap } from 'lucide-react';

export default function Grid() {
  const { regionCode } = useStore();
  const [scenario, setScenario] = useState('cloud_collapse');
  const [scenarios, setScenarios] = useState<any[]>([]);
  const [data, setData] = useState<any>(null);
  const [question, setQuestion] = useState('How to handle black start if hydro fails?');
  const [copilotResp, setCopilotResp] = useState<any>(null);
  const [stepIdx, setStepIdx] = useState(0);

  useEffect(()=>{
    api.gridScenarios().then(setScenarios).catch(()=>{});
    fetchPlan();
  }, [scenario, regionCode]);

  const fetchPlan = async () => {
    const res = await api.gridBlackstart({ region_code: regionCode, scenario });
    setData(res);
    setStepIdx(0);
  };

  const askCopilot = async () => {
    const res = await api.gridCopilot({ question, scenario, region_code: regionCode });
    setCopilotResp(res);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between">
        <div>
          <h1 className="font-serif text-[32px] font-semibold">Grid Operator Copilot • Black Start Simulator</h1>
          <p className="text-[13px] text-fg-muted mt-1 max-w-[70ch]">Scenario engine with synthetic renewable failure data. Deterministic recovery sequence with islands, cranking power, load pickup steps, frequency/voltage checks. Copilot RAG over local knowledge base; LLM never controls grid.</p>
        </div>
        <div className="text-[11px] font-mono px-3 py-1 rounded-full bg-ink-800 border">Human-in-the-loop • Approve each step</div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-1 rounded-control hairline p-4 space-y-4" style={{background:'var(--bg-900)'}}>
          <div className="text-[11px] font-mono uppercase text-fg-muted">Scenario</div>
          <select value={scenario} onChange={e=>setScenario(e.target.value)} className="w-full bg-ink-800 border rounded px-3 py-2 text-[13px]">
            {scenarios.map((s:any)=><option key={s.id} value={s.id}>{s.name} • {s.severity}</option>)}
            {scenarios.length===0 && <>
              <option value="cloud_collapse">Cloud Collapse</option>
              <option value="wind_lull">Wind Lull</option>
              <option value="line_trip">Line Trip</option>
              <option value="cyber_outage">Cyber Outage</option>
            </>}
          </select>
          <button onClick={fetchPlan} className="w-full py-2.5 rounded bg-amber-signal text-black font-semibold text-[13px]">Load recovery plan</button>

          {data && (
            <div className="mt-4">
              <div className="text-[11px] font-mono uppercase text-fg-muted">Events</div>
              <div className="mt-2 space-y-2">
                {data.events.map((e:any,i:number)=>(
                  <div key={i} className="p-2 rounded bg-ink-800 border text-[11px]">
                    <div className="font-medium flex justify-between"><span>{e.type}</span><span className={`px-1 rounded text-[10px] ${e.severity==='critical'?'bg-brick text-white': e.severity==='high'?'bg-ochre text-black':'bg-ink-700'}`}>{e.severity}</span></div>
                    <div className="text-fg-muted mt-1">{e.description}</div>
                  </div>
                ))}
              </div>
              <div className="mt-4 text-[11px] font-mono">Est recovery {data.estimated_recovery_minutes} min</div>
            </div>
          )}
        </div>

        <div className="lg:col-span-3 space-y-4">
          {data ? (
            <>
              <div className="rounded-control hairline p-4" style={{background:'var(--bg-900)'}}>
                <div className="flex justify-between items-center mb-4">
                  <div className="text-[11px] font-mono uppercase text-fg-muted">Recovery timeline • SVG network re-energization</div>
                  <div className="flex gap-2">
                    <button onClick={()=>setStepIdx(s=>Math.max(0,s-1))} className="px-3 py-1 rounded border text-[12px]">Prev</button>
                    <button onClick={()=>setStepIdx(s=>Math.min(data.recovery_plan.length-1,s+1))} className="px-3 py-1 rounded bg-amber-signal text-black text-[12px]">Next step</button>
                    <span className="font-mono text-[12px] px-2 py-1">Step {stepIdx+1}/{data.recovery_plan.length}</span>
                  </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                  <div className="lg:col-span-2">
                    {/* Simple network graph visualization */}
                    <svg viewBox="0 0 400 300" className="w-full h-[300px] border rounded bg-ink-800" style={{borderColor:'var(--border)'}}>
                      {data.network_graph.edges.map((ed:any,i:number)=>{
                        const energized = data.recovery_plan[stepIdx]?.energized_nodes || [];
                        const active = energized.includes(ed.from) && energized.includes(ed.to);
                        return <line key={i} x1={pos(ed.from).x} y1={pos(ed.from).y} x2={pos(ed.to).x} y2={pos(ed.to).y} stroke={active ? '#E0A73A' : '#26322C'} strokeWidth={active?3:1} strokeDasharray={active?'':'4 4'} />;
                      })}
                      {data.network_graph.nodes.map((n:any,i:number)=>{
                        const energized = data.recovery_plan[stepIdx]?.energized_nodes?.includes(n.id);
                        return (
                          <g key={i}>
                            <circle cx={pos(n.id).x} cy={pos(n.id).y} r={18} fill={energized ? '#E0A73A' : '#1B2420'} stroke="#26322C" />
                            <text x={pos(n.id).x} y={pos(n.id).y+4} textAnchor="middle" fontSize="8" fill={energized ? 'black' : '#8E9A92'} fontFamily="monospace">{n.id.slice(0,6)}</text>
                          </g>
                        );
                      })}
                    </svg>
                    <div className="mt-3 grid grid-cols-3 gap-2 text-[11px] font-mono">
                      <div className="p-2 rounded bg-ink-800 border">Freq {data.recovery_plan[stepIdx]?.frequency_hz} Hz</div>
                      <div className="p-2 rounded bg-ink-800 border">Volt {data.recovery_plan[stepIdx]?.voltage_pu} pu</div>
                      <div className="p-2 rounded bg-ink-800 border">Load {data.recovery_plan[stepIdx]?.load_mw} MW</div>
                    </div>
                  </div>
                  <div className="space-y-2">
                    {data.recovery_plan.map((st:any,i:number)=>(
                      <div key={i} className={`p-3 rounded border text-[12px] ${i===stepIdx ? 'bg-amber-signal text-black border-amber-signal' : i<stepIdx ? 'bg-moss/20 border-moss' : 'bg-ink-800 border-ink-700'}`}>
                        <div className="flex justify-between"><span className="font-mono text-[10px]">{st.timestamp}</span><span className="text-[10px]">{st.status}</span></div>
                        <div className="font-medium mt-1">{st.action}</div>
                        <div className="text-[11px] mt-1 opacity-80">Energized: {st.energized_nodes.join(', ')}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="rounded-control hairline p-4" style={{background:'var(--bg-900)'}}>
                <div className="text-[11px] font-mono uppercase text-fg-muted flex items-center gap-2"><MessageSquare className="w-4 h-4" /> Copilot chat • RAG over knowledge base</div>
                <div className="mt-3 flex gap-2">
                  <input value={question} onChange={e=>setQuestion(e.target.value)} placeholder="Ask about black start..." className="flex-1 bg-ink-800 border rounded px-3 py-2 text-[13px]" />
                  <button onClick={askCopilot} className="px-4 py-2 rounded bg-ink-800 border text-[13px]">Ask</button>
                </div>
                {copilotResp && (
                  <div className="mt-4 p-3 rounded bg-ink-800 border text-[13px] leading-relaxed">
                    <div>{copilotResp.answer}</div>
                    <div className="mt-3 flex gap-2 text-[11px] font-mono">
                      <span>Citations: {copilotResp.citations.join(', ')}</span>
                      <span>Steps: {copilotResp.referenced_steps.join(', ')}</span>
                      <span className={`px-2 py-0.5 rounded ${copilotResp.source==='llm'?'bg-teal-slate text-white':'bg-ink-700'}`}>{copilotResp.source}</span>
                    </div>
                    <div className="mt-3 text-[11px] text-fg-muted">LLM never controls grid. Operator must approve. Human-in-the-loop badge shown per procedure IEC 61850.</div>
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="rounded-control hairline p-10 text-center" style={{background:'var(--bg-900)'}}>
              <Shield className="w-8 h-8 mx-auto text-fg-muted" />
              <div className="mt-3 font-serif text-[18px]">Select scenario to simulate black start</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function pos(id: string) {
  const map: any = {
    'G1-Hydro': {x:60,y:60},
    'G2-Gas': {x:60,y:120},
    'S1-Sub': {x:150,y:90},
    'S2-Sub': {x:250,y:90},
    'S3-Sub': {x:340,y:90},
    'L1-Indust': {x:250,y:180},
    'L2-Commercial': {x:340,y:180},
    'L3-Residential': {x:340,y:240},
    'Batt-1': {x:150,y:180},
    'EV-Fleet': {x:150,y:240},
  };
  return map[id] || {x:200,y:150};
}
