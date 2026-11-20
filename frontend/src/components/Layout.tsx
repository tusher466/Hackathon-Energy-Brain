import { NavLink, Outlet, useLocation } from 'react-router-dom';
import { useStore } from '../state/useStore';
import { api } from '../lib/api';
import { useEffect } from 'react';
import { Sun, BarChart3, Zap, Shield, ScanEye, BookOpenCheck, ShieldCheck, Settings, Command, Moon, SunMedium, Activity, LayoutDashboard } from 'lucide-react';

const nav = [
  { to: '/', label: 'Overview', icon: LayoutDashboard },
  { to: '/solar', label: 'Forecast', icon: Sun },
  { to: '/demand', label: 'Demand', icon: BarChart3 },
  { to: '/vpp', label: 'Dispatch', icon: Zap },
  { to: '/grid', label: 'Recovery', icon: Shield },
  { to: '/panels', label: 'Panels', icon: ScanEye },
  { to: '/ledger', label: 'Ledger', icon: BookOpenCheck },
  { to: '/trust', label: 'Trust', icon: ShieldCheck },
  { to: '/settings', label: 'Settings', icon: Settings },
];

export default function Layout() {
  const { regionCode, setRegion, regions, setRegions, darkMode, toggleDark, setCommandOpen } = useStore();
  const loc = useLocation();

  useEffect(() => {
    api.getRegions().then(setRegions).catch(()=>{});
    const handleK = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase()==='k') {
        e.preventDefault();
        setCommandOpen(true);
      }
    };
    window.addEventListener('keydown', handleK);
    return ()=>window.removeEventListener('keydown', handleK);
  }, []);

  return (
    <div className={`min-h-screen grain ${darkMode ? 'dark' : 'light'} overflow-x-hidden`} style={{background: 'var(--bg-950)'}}>
      <div className="flex min-h-screen overflow-hidden">
        {/* Sidebar */}
        <aside className="w-[260px] shrink-0 border-r hairline hidden lg:flex flex-col sticky top-0 h-screen overflow-y-auto z-20" style={{background: 'var(--bg-900)', borderColor: 'var(--border)'}}>
          <div className="p-6 border-b hairline" style={{borderColor: 'var(--border)'}}>
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-[8px] flex items-center justify-center" style={{background: '#E0A73A'}}>
                <Activity className="w-5 h-5 text-black" />
              </div>
              <div>
                <div className="font-serif text-[18px] font-semibold leading-none tracking-tight">Energy Brain</div>
                <div className="text-[11px] font-mono text-fg-muted mt-1">CONTROL ROOM • v1</div>
              </div>
            </div>
          </div>
          <div className="p-3 flex-1">
            <div className="text-[11px] font-mono tracking-widest text-fg-muted px-3 py-2">DECISION LOOP</div>
            <nav className="space-y-[2px] mt-2">
              {nav.map(n => (
                <NavLink key={n.to} to={n.to} className={({isActive}) => `flex items-center gap-3 px-3 py-2.5 rounded-control text-[13px] font-medium transition-colors ${isActive ? 'text-ink-950' : 'text-fg-muted hover:text-[var(--fg-strong)]'}`} style={({isActive})=> isActive ? {background: '#E0A73A', color: '#0D1210'} : {}}>
                  <n.icon className="w-4 h-4" />
                  {n.label}
                </NavLink>
              ))}
            </nav>

            <div className="mt-8 p-3 rounded-control hairline" style={{background: 'var(--bg-800)'}}>
              <div className="text-[11px] font-mono text-fg-muted">REGION</div>
              <select value={regionCode} onChange={e=>setRegion(e.target.value)} className="mt-2 w-full bg-transparent border hairline rounded-[6px] px-2 py-2 text-[13px]" style={{borderColor:'var(--border)'}}>
                {regions.map((r:any)=> <option key={r.code} value={r.code} className="bg-black text-white">{r.name} — {r.currency}</option>)}
                {regions.length===0 && <>
                  <option value="BD">Bangladesh - Taka</option>
                  <option value="DE">Germany - Euro</option>
                  <option value="US">USA - USD</option>
                </>}
              </select>
              <div className="mt-3 text-[11px] font-mono text-fg-muted">SAVINGS TODAY</div>
              <div className="font-mono text-[18px] font-medium mt-1">৳ 1,284 • 12.4 kg CO₂ • 84 kW peak</div>
            </div>
          </div>
          <div className="p-3 border-t hairline" style={{borderColor:'var(--border)'}}>
            <div className="flex gap-2">
              <button onClick={toggleDark} className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-[6px] hairline text-[12px] font-medium hover:bg-ink-800">
                {darkMode ? <SunMedium className="w-4 h-4" /> : <Moon className="w-4 h-4" />} {darkMode ? 'Light' : 'Dark'}
              </button>
              <button onClick={()=>setCommandOpen(true)} className="flex items-center gap-2 px-3 py-2 rounded-[6px] hairline text-[12px] font-medium">
                <Command className="w-4 h-4" /> K
              </button>
            </div>
            <div className="mt-3 text-[10px] font-mono text-fg-muted">FORECAST → OPTIMIZE → ACT → EXPLAIN → MEASURE</div>
          </div>
        </aside>

        {/* Main */}
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
          {/* Top bar mobile */}
          <div className="lg:hidden flex items-center justify-between p-4 border-b hairline sticky top-0 z-10" style={{background: 'var(--bg-900)'}}>
            <div className="font-serif font-semibold truncate">Energy Brain</div>
            <div className="flex gap-2 shrink-0">
              <select value={regionCode} onChange={e=>setRegion(e.target.value)} className="bg-transparent border hairline rounded px-2 py-1 text-[12px] max-w-[80px]"><option value="BD">BD</option><option value="DE">DE</option><option value="US">US</option></select>
              <button onClick={toggleDark} className="px-2 py-1 border rounded text-[12px] shrink-0">{darkMode?'Light':'Dark'}</button>
            </div>
          </div>
          {/* Mobile nav */}
          <div className="lg:hidden flex gap-1 p-2 overflow-x-auto border-b hairline scrollbar-hide">
            {nav.map(n=> <NavLink key={n.to} to={n.to} className={({isActive})=> `px-3 py-2 rounded text-[12px] whitespace-nowrap shrink-0 ${isActive ? 'bg-amber-signal text-black' : 'bg-ink-800 text-fg-muted'}`}>{n.label}</NavLink>)}
          </div>

          <main className="flex-1 p-3 sm:p-4 lg:p-8 overflow-y-auto overflow-x-hidden">
            <div className="max-w-[1600px] mx-auto w-full">
              <Outlet />
            </div>
          </main>

          <footer className="p-3 sm:p-4 border-t hairline text-[10px] sm:text-[11px] font-mono text-fg-muted flex flex-col sm:flex-row gap-1 sm:gap-0 sm:justify-between" style={{borderColor:'var(--border)'}}>
            <span className="truncate">Energy Brain • Control room at dusk • Offline-first • Synthetic fallback live</span>
            <span className="shrink-0">{loc.pathname}</span>
          </footer>
        </div>
      </div>

      {/* Command palette */}
      <CommandPalette />
    </div>
  );
}

function CommandPalette() {
  const { commandOpen, setCommandOpen } = useStore();
  if (!commandOpen) return null;
  const items = [
    { k: 'G O', label: 'Go to Overview', to: '/' },
    { k: 'G S', label: 'Go to Forecast / Solar', to: '/solar' },
    { k: 'G D', label: 'Go to Demand', to: '/demand' },
    { k: 'G V', label: 'Go to Dispatch VPP', to: '/vpp' },
    { k: 'G R', label: 'Go to Recovery', to: '/grid' },
    { k: 'G P', label: 'Go to Panels', to: '/panels' },
  ];
  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[20vh] bg-black/60 backdrop-blur-sm" onClick={()=>setCommandOpen(false)}>
      <div className="w-[560px] max-w-[90vw] rounded-control border hairline overflow-hidden bg-ink-900" onClick={e=>e.stopPropagation()}>
        <div className="px-4 py-3 border-b hairline text-[12px] font-mono text-fg-muted">COMMAND • Ctrl/Cmd+K</div>
        <div className="p-2">
          <input autoFocus placeholder="Type command, region, or ask..." className="w-full bg-ink-800 border hairline rounded px-3 py-2 text-[14px] outline-none" />
        </div>
        <div className="p-2 space-y-1">
          {items.map(it=>(
            <button key={it.k} onClick={()=>{window.location.hash=''; window.location.pathname=it.to; setCommandOpen(false);}} className="w-full text-left flex justify-between px-3 py-2 rounded hover:bg-ink-800 text-[13px]">
              <span>{it.label}</span><span className="font-mono text-[11px] text-fg-muted">{it.k}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
