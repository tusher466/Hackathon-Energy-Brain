const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function fetchJSON(path: string, opts: RequestInit = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    ...opts,
    headers: {
      'Content-Type': 'application/json',
      ...(opts.headers || {})
    }
  });
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`API ${path} failed ${res.status}: ${txt}`);
  }
  return res.json();
}

export const api = {
  getRegions: () => fetchJSON('/api/v1/regions'),
  getRegion: (code: string) => fetchJSON(`/api/v1/regions/${code}`),
  getTariff: (code: string) => fetchJSON(`/api/v1/regions/${code}/tariff`),
  solarForecast: (params: any) => fetchJSON('/api/v1/solar/forecast', { method: 'POST', body: JSON.stringify(params) }),
  solarForecastGET: (q: string) => fetchJSON(`/api/v1/solar/forecast?${q}`),
  demandForecast: (params: any) => fetchJSON('/api/v1/demand/forecast', { method: 'POST', body: JSON.stringify(params) }),
  demandForecastGET: (q: string) => fetchJSON(`/api/v1/demand/forecast?${q}`),
  vppDispatch: (params: any) => fetchJSON('/api/v1/vpp/dispatch', { method: 'POST', body: JSON.stringify(params) }),
  vppDefaultFleet: () => fetchJSON('/api/v1/vpp/default-fleet'),
  gridBlackstart: (params: any) => fetchJSON('/api/v1/grid/blackstart', { method: 'POST', body: JSON.stringify(params) }),
  gridScenarios: () => fetchJSON('/api/v1/grid/scenarios'),
  gridCopilot: (params: any) => fetchJSON('/api/v1/grid/copilot', { method: 'POST', body: JSON.stringify(params) }),
  panelSample: (region: string, seed: number) => fetchJSON(`/api/v1/panels/sample?region_code=${region}&seed=${seed}`),
  panelInspect: async (file: File, region_code: string) => {
    const form = new FormData();
    form.append('file', file);
    form.append('region_code', region_code);
    const res = await fetch(`${API_BASE}/api/v1/panels/inspect`, { method: 'POST', body: form });
    if (!res.ok) throw new Error('inspect failed');
    return res.json();
  },
  ledgerSummary: () => fetchJSON('/api/v1/ledger/summary'),
  ledgerEntries: () => fetchJSON('/api/v1/ledger/entries?limit=100'),
  ledgerApprovals: () => fetchJSON('/api/v1/ledger/approvals'),
  ledgerApprove: (id: string, decision: string) => fetchJSON(`/api/v1/ledger/approvals/${id}/${decision}`, { method: 'POST' }),
  ledgerReset: () => fetchJSON('/api/v1/ledger/reset', { method: 'POST' }),
  ledgerExport: () => fetchJSON('/api/v1/ledger/export/csv'),
  modelStatus: () => fetchJSON('/api/v1/models/status'),
  integrations: () => fetchJSON('/api/v1/integrations'),
  health: () => fetchJSON('/health'),
};

// SSE helper
export function simulateDaySSE(region: string, onMessage: (data:any)=>void, onDone: ()=>void) {
  const es = new EventSource(`${API_BASE}/api/v1/simulate/day?region_code=${region}`);
  es.onmessage = (e) => {
    try {
      const data = JSON.parse(e.data);
      if (data.done) { es.close(); onDone(); } else onMessage(data);
    } catch {}
  };
  es.onerror = () => { es.close(); onDone(); };
  return es;
}
