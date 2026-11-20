const envUrl = import.meta.env.VITE_API_URL;
const API_BASE = envUrl === undefined ? 'http://localhost:8000' : envUrl;

// Market-ready fetch with timeout and better error handling
async function fetchWithTimeout(url: string, opts: RequestInit = {}, timeoutMs = 15000): Promise<Response> {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(url, { ...opts, signal: controller.signal });
    return res;
  } finally {
    clearTimeout(id);
  }
}

async function fetchJSON(path: string, opts: RequestInit = {}) {
  const url = `${API_BASE}${path}`;
  let res: Response;
  try {
    res = await fetchWithTimeout(url, {
      ...opts,
      headers: {
        'Content-Type': 'application/json',
        ...(opts.headers || {}),
      },
    });
  } catch (e: any) {
    if (e.name === 'AbortError') throw new Error(`API ${path} timeout after 15s`);
    throw new Error(`API ${path} network error: ${e.message}`);
  }
  if (!res.ok) {
    const txt = await res.text().catch(() => '');
    // Provide nicer message
    throw new Error(`API ${path} failed ${res.status}: ${txt.slice(0,500)}`);
  }
  const text = await res.text();
  if (!text) return {};
  try {
    return JSON.parse(text);
  } catch {
    return text as any;
  }
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
    const res = await fetchWithTimeout(`${API_BASE}/api/v1/panels/inspect`, { method: 'POST', body: form }, 30000);
    if (!res.ok) {
      const txt = await res.text().catch(()=> '');
      throw new Error(`inspect failed ${res.status}: ${txt.slice(0,300)}`);
    }
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
