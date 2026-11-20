export default function Trust() {
  return (
    <div className="space-y-6 max-w-[900px]">
      <h1 className="font-serif text-[32px] font-semibold">Trust • Explainability + Responsible AI</h1>
      <p className="text-[13px] text-fg-muted">Every output has Explain drawer, counterfactual, confidence band, data provenance, model version.</p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="rounded-control hairline p-5" style={{background:'var(--bg-900)'}}>
          <div className="text-[11px] font-mono uppercase text-fg-muted">Data provenance</div>
          <div className="mt-3 text-[13px] leading-relaxed space-y-2">
            <p>Synthetic generators offline-first. Clear-sky model with solar geometry (declination, hour angle, cos zenith) × cloud transmission field 32×32 advected by wind vector. Estimated via phase correlation FFT (numpy) fallback block matching.</p>
            <p>Demand multi-site: weekday/weekend patterns, temperature sensitivity regional, economic indicator sinusoidal.</p>
            <p>Price/carbon forecasts region-specific tariffs: BD BDT 6.2 night/8.5 day/12.8 peak, DE EUR, US USD LMP.</p>
            <p>Live connectors (optional): NREL NSRDB, NOAA GFS, Electricity Maps, OPSD, PJM – each returns same schema as synthetic, flag source live/synthetic for honest UI.</p>
          </div>
        </div>
        <div className="rounded-control hairline p-5" style={{background:'var(--bg-900)'}}>
          <div className="text-[11px] font-mono uppercase text-fg-muted">Bias & fairness</div>
          <div className="mt-3 text-[13px] leading-relaxed space-y-2">
            <p><strong>EV SoC delivery fairness:</strong> All EVs must hit required SoC (100% guarantee via linprog safety layer). Metric: mean/min delivery ratio, variance. If early departure EV would get lower SoC in pure RL, fallback to baseline immediate for that EV. Dashboard shows variance &lt;5%.</p>
            <p><strong>Forecast bias:</strong> Quantile models produce P10/P50/P90 monotonic guaranteed post-sort. Checked in tests.</p>
            <p><strong>Regional fairness:</strong> Region profiles config-driven, currency changes instantly, methodology transparent.</p>
            <p><strong>Failure modes:</strong> Cloud motion estimate error tolerance &lt;2px on synthetic shift. Battery cycle limits enforced. Transformer limit hard constraint.</p>
          </div>
        </div>
        <div className="rounded-control hairline p-5" style={{background:'var(--bg-900)'}}>
          <div className="text-[11px] font-mono uppercase text-fg-muted">Model selection logic</div>
          <div className="mt-3 text-[13px] leading-relaxed">
            <p><strong>Solar:</strong> LSTM PyTorch CPU if available for temporal dependencies, fallback gradient boosting quantile (sklearn) for offline reliability. Reason: irradiance time-series has short memory + cloud proxy, small LSTM overkill but demo plausible; GB faster for hackathon.</p>
            <p><strong>Demand:</strong> Compact Transformer encoder (why) – captures weekly seasonality & attention over past 168h; fallback GB quantile with engineered hour sin/cos, lag features. Attention summary shown as feature importance.</p>
            <p><strong>VPP:</strong> RL (tabular Q-learning) as price threshold policy learner + rolling horizon LP optimizer safety layer. Why both: RL adapts to price volatility, LP guarantees constraints (SoC, transformer). PPO-lite if stable-baselines3 installed – not required.</p>
            <p><strong>Grid copilots:</strong> LLM + RAG only for explanation, never control. TF-IDF retrieval over /knowledge/*.md markdown docs, citations shown. Rule-based fallback when no OPENAI/ANTHROPIC key – still grounded.</p>
            <p><strong>Thermal:</strong> OpenCV pipeline (normalize, threshold hot, connected components, shape/temp delta classification) + optional CNN patch classifier if torch.</p>
          </div>
        </div>
        <div className="rounded-control hairline p-5" style={{background:'var(--bg-900)'}}>
          <div className="text-[11px] font-mono uppercase text-fg-muted">Privacy & human override</div>
          <div className="mt-3 text-[13px] leading-relaxed space-y-2">
            <p>No personal data. EV IDs anonymized (EV-1…). Aggregated load curves. GDPR-friendly approach – data stays locally in SQLite, can be wiped via Reset.</p>
            <p>Human-in-the-loop: Approval queue – charge action, black start step. Operator must approve; logged with timestamp. LLM badge shows "Assistant – not controller".</p>
            <p>Explainability: Every decision ships with plain-language reason, counterfactual (what if immediate), confidence band, data sources, model version.</p>
            <p>Failure modes documented, override log.</p>
          </div>
          <div className="mt-4 p-3 rounded bg-ink-800 border text-[12px] font-mono">Example: "Charge 42 EVs between 01:00 and 04:30. Saves 118 USD. Confidence 91%. If immediate, +210kW peak."</div>
        </div>
      </div>

      <div className="rounded-control hairline p-5" style={{background:'var(--bg-900)'}}>
        <div className="text-[11px] font-mono uppercase text-fg-muted">Architecture workflow – input → processing → output</div>
        <div className="mt-3 font-mono text-[12px] bg-ink-950 p-4 rounded border overflow-auto">
{`[Satellite Cloud Field 32x32] --phase-corr--> wind vector --> advect --> cloud transmission
[Lat/Lon/Tilt] --clear-sky model--> irradiance --> * cloud --> P10/P50/P90
[Regional Load + Temp + Economic] --GB/Transformer--> demand P10/P50/P90 + feature importance + MAPE
[Price + Carbon tariff per region] + [EV fleet arrival/departure/SoC] --> RL tabular Q (price threshold) + LP safety (linprog) --> schedule per asset + aggregate before/after + fairness
[Grid events cloud_collapse/wind_lull/line_trip/cyber] --> deterministic recovery simulator 6 steps --> network graph SVG re-energize --> copilot RAG (TF-IDF over .md) + LLM optional --> citations + referenced steps
[Drone thermal JPG] --OpenCV normalize/threshold/contours--> defects bbox + temp delta + shape classify --> eff loss % yearly kWh money per region
[All decisions] --> SQLite ledger --> summary $/CO2/peak + by module/region + CSV export + printable report`}
        </div>
      </div>
    </div>
  );
}
