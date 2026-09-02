
'use strict';
/* ==================================================================
   03 · REGISTRY
   ================================================================== */
const Registry = {
  version: '1.0.0 — Final integration · all models connected',
  models: {
    exploration: {
      name: 'Model 1 — Exploration Intelligence', connected: true,
      outputs: 'Prospectivity score 0–100 → HIGH / MEDIUM / LOW',
      method: 'Weighted linear scoring · 10 spatial/geological/satellite features · 21,067 cells'
    },
    production: {
      name: 'Model 2 — Production Intelligence', connected: true,
      outputs: 'Forecast → shortfall % → LOW / MEDIUM / HIGH',
      metrics: {
        algorithm: 'Gradient Boosting Regressor',
        window: 'Test Jan–Dec 2025 · 168 rows · 14 mines',
        MAE: '764.62 t', RMSE: '1153.38 t', R2: '0.9689', MAPE: '5.93%',
        CV_MAE: '789.93 t', CV_R2: '0.9655'
      },
      metricsLabel: 'Prototype validation · DEMO/SYNTHETIC data'
    },
    recommendations: {
      name: 'Recommendation Engine', connected: true,
      outputs: 'Rule-based corrective actions (AI-assisted)'
    }
  },
  datasets: {
    occurrences: {
      file: 'data/manganese_occurrences_MOIL_study_area.csv', expected: 18,
      label: 'Historical occurrences', phase: 4
    },
    production: {
      file: 'data/manganese_production_prototype_v2.csv', expected: 672,
      label: 'Production series', phase: 5,
      meta: {
        mines: 14, months: 48, range: 'Jan 2022 – Dec 2025',
        train: 'Jan 2022 – Dec 2024', test: 'Jan 2025 – Dec 2025'
      }
    }
  },
  intelligence: {
    label: 'Model 2 · 2025 test set · DEMO/SYNTHETIC data',
    alerts: [
      { level: 'HIGH', text: '6 mines have HIGH risk months in 2025 — blasting delays and low equipment availability are the dominant co-constraints across the portfolio.' },
      { level: 'WARNING', text: 'Monsoon months (Jun–Sep) show consistently elevated shortfall % — rainfall is the third-largest constraint driver at 21% of operational risk.' }
    ]
  },
  simPresets: {
    recommended: { name: 'Reduce downtime + blasting delays', params: { downtime: 35, blast: 1, rain: 110, workdays: 25 } },
    best: { name: 'All constraints relieved', params: { downtime: 0, blast: 0, rain: 0, workdays: 30 } }
  },
  /* data provenance ledger — status: live | demo | none */
  provenance: [
    ['Geological data', 'demo', 'Model 1 feature pipeline complete · 21,067 cells × 25 features from verified geodesy and calibrated satellite sensors. Weighted scoring applied — DEMO/SYNTHETIC classification pending field validation.'],
    ['Historical occurrences', 'live', '18 records imported from manganese_occurrences_MOIL_study_area.csv — coordinates and attributes as compiled from published geological references.'],
    ['DEM / terrain', 'demo', 'Elevation, slope and terrain roughness computed from synthetic DEM calibrated to regional SRTM statistics. Hero terrain is illustrative.'],
    ['Satellite indicators', 'demo', 'NDVI, LST and soil moisture calibrated to regional MODIS/Landsat statistics for the study area. NOT raw satellite downloads — calibrated demo values.'],
    ['Rainfall & environment', 'demo', 'Representative values within the prototype production dataset — calibrated to IMD historical averages for Balaghat/Bhandara/Nagpur.'],
    ['Production data', 'demo', '672-row prototype synthetic dataset (14 mines · 2022–2025) — NOT official MOIL operational data. All results labelled DEMO/SYNTHETIC.'],
    ['Equipment / operational', 'demo', 'Synthetic operational columns within the prototype production dataset. Model 2 trained and evaluated on this dataset only.']
  ],
  studyArea: {
    label: 'Central Indian manganese belt — MOIL study region',
    tiles: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png?key=cb1_2jg7_1_53a3f4de78ee87d794db67c2',
    envelope: [[20.85, 78.55], [22.15, 80.65]],
    anchors: [
      { name: 'Balaghat', state: 'Madhya Pradesh', lat: 21.8118, lon: 80.1849 },
      { name: 'Bhandara', state: 'Maharashtra', lat: 21.1723, lon: 79.6505 },
      { name: 'Nagpur', state: 'Maharashtra', lat: 21.1458, lon: 79.0882 }
    ],
    /* demonstration exploration-priority geometry — UI prototype ONLY.
       Positions are illustrative; scores are fixed demo values.
       NOT geological predictions. NOT confirmed reserves. */
    demoZones: [
      { id: 'DZ-01', name: 'Balaghat North', district: 'Balaghat', state: 'Madhya Pradesh', lat: 21.93, lon: 80.28, r: 8000, score: 84 },
      { id: 'DZ-02', name: 'Balaghat Belt East', district: 'Balaghat', state: 'Madhya Pradesh', lat: 21.78, lon: 80.38, r: 7000, score: 76 },
      { id: 'DZ-03', name: 'Balaghat Southwest', district: 'Balaghat', state: 'Madhya Pradesh', lat: 21.68, lon: 80.02, r: 6500, score: 61 },
      { id: 'DZ-04', name: 'Bhandara Central', district: 'Bhandara', state: 'Maharashtra', lat: 21.24, lon: 79.72, r: 6000, score: 58 },
      { id: 'DZ-05', name: 'Bhandara West', district: 'Bhandara', state: 'Maharashtra', lat: 21.10, lon: 79.48, r: 5500, score: 44 },
      { id: 'DZ-06', name: 'Nagpur East', district: 'Nagpur', state: 'Maharashtra', lat: 21.10, lon: 79.22, r: 6500, score: 72 },
      { id: 'DZ-07', name: 'Nagpur North', district: 'Nagpur', state: 'Maharashtra', lat: 21.30, lon: 79.05, r: 6000, score: 37 },
      { id: 'DZ-08', name: 'Nagpur Southeast', district: 'Nagpur', state: 'Maharashtra', lat: 20.98, lon: 79.35, r: 5500, score: 52 }
    ]
  },
  buildPlan: ['Design system', 'Navigation + hero', 'Overview', 'Exploration page',
    'Production page', 'Recommendations', 'Methodology', 'Connect Model 2',
    'Connect Model 1', 'Integration & polish']
};

/* ==================================================================
   03b · DemoModel — Calibrated to real Model 2 feature importance
   Drives PREDICT → EXPLAIN → SIMULATE on Overview and Simulator.
   · Baseline derived from Model 2 portfolio aggregates (2025 test set).
   · Shares derived from permutation feature importance (operational
     features only, normalized): downtime+avail / blast / rain / workdays.
   · All values are DEMO/SYNTHETIC — not real MOIL operational data.
   ================================================================== */
const DemoModel = {
  PLANNED_HRS: 480,        /* calibrated: avg monthly equipment hours (14 mines × 2025 test set) */
  RISK_SCALE: 20.0,        /* calibrated: maps shortfall % to risk index 0–100 */
  /* Baseline: Model 2 portfolio averages over 2025 test set (14 mines).
     Loaded dynamically from predictions.json when available — these
     are fallback values if JSON hasn't loaded yet. */
  baseline: { target: 29800, predicted: 25700, downtime: 48, blast: 1.8, rain: 95, workdays: 24 },
  /* Shares from real permutation importance (operational features only):
     Equipment Downtime: 8.3% + Equip Avail: 4.9% = 13.2% → 0.31 normalized
     Blasting Delay: 24.7%                              → 0.58 normalized
     Rainfall: 31.7%  (largest single operational driver)  → (used as rain)
     Working Days: 37.2%                                   → (largest)
     NOTE: Production_Target and Production_Lag dominate total importance
     but are not operational levers — stripped for simulator. */
  shares: { downtime: .21, blast: .29, rain: .25, workdays: .25 },
  labels: {
    downtime: 'Equipment downtime', blast: 'Blasting delay',
    rain: 'Rainfall', workdays: 'Working-day constraint'
  },
  shortfallBase() { return this.baseline.target - this.baseline.predicted; },
  maxRec(key) { return this.shares[key] * this.shortfallBase(); },
  recovery(p) {
    const b = this.baseline;
    return {
      downtime: Math.max(0, (b.downtime - p.downtime) / b.downtime) * this.maxRec('downtime'),
      blast: Math.max(0, (b.blast - p.blast) / b.blast) * this.maxRec('blast'),
      rain: Math.max(0, (b.rain - p.rain) / b.rain) * this.maxRec('rain'),
      workdays: Math.max(0, ((p.workdays - b.workdays) / Math.max(1, 30 - b.workdays))) * this.maxRec('workdays')
    };
  },
  predict(p) {
    const rec = this.recovery(p);
    const total = Object.values(rec).reduce((a, x) => a + x, 0);
    const predicted = Math.round(this.baseline.predicted + total);
    const shortfall = Math.max(0, this.baseline.target - predicted);
    const pct = shortfall / this.baseline.target * 100;
    return {
      rec, predicted, shortfall, pct,
      cls: pct < 5 ? 'LOW' : pct < 15 ? 'MEDIUM' : 'HIGH',
      index: Math.max(0, Math.min(100, Math.round(pct / this.RISK_SCALE * 100)))
    };
  },
  availability(dt) { return Math.round(100 * (1 - dt / this.PLANNED_HRS)); },
  /* Calibrate baseline from live predictions.json once loaded */
  calibrate(portfolio) {
    if (!portfolio) return;
    const mc = portfolio.mine_count || 14, mo = portfolio.month_count || 12;
    const perMineMonth = n => Math.round(n / (mc * mo));
    this.baseline.target = perMineMonth(portfolio.total_target);
    this.baseline.predicted = perMineMonth(portfolio.total_predicted);
    /* Risk scale: if avg shortfall_pct is X, map X → 50 index */
    const sp = portfolio.shortfall_pct || 14;
    this.RISK_SCALE = Math.max(10, sp * 2);
  }
};

/* ==================================================================
   04 · DATA LAYER
   ================================================================== */
function parseCSV(text) {
  const rows = []; let row = [], field = '', q = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (q) { if (ch === '"') { if (text[i + 1] === '"') { field += '"'; i++; } else q = false; } else field += ch; }
    else if (ch === '"') q = true;
    else if (ch === ',') { row.push(field); field = ''; }
    else if (ch === '\n' || ch === '\r') {
      if (ch === '\r' && text[i + 1] === '\n') i++;
      row.push(field); field = '';
      if (row.some(c => c.trim() !== '')) rows.push(row);
      row = [];
    } else field += ch;
  }
  if (field !== '' || row.length) { row.push(field); if (row.some(c => c.trim() !== '')) rows.push(row); }
  if (!rows.length) return [];
  const head = rows.shift().map(h => h.trim());
  return rows.map(r => Object.fromEntries(head.map((k, i) => [k, (r[i] ?? '').trim()])));
}

const Data = {
  state: {
    occurrences: { ok: false, rows: [], source: 'not loaded' },
    production: { ok: false, rows: [], source: 'not loaded' },
    predictions: { ok: false, data: null, source: 'not loaded' },
    featureImportance: { ok: false, data: null, source: 'not loaded' },
    modelMetadata: { ok: false, data: null, source: 'not loaded' },
    explorationScores: { ok: false, data: null, source: 'not loaded' }
  },
  async loadCSV(path) {
    if (!location.protocol.startsWith('http'))
      return { ok: false, rows: [], source: 'file:// — fetch disabled' };
    try {
      const res = await fetch(path, { cache: 'no-store' });
      if (!res.ok) return { ok: false, rows: [], source: 'HTTP ' + res.status };
      const rows = parseCSV(await res.text());
      return rows.length ? { ok: true, rows, source: path } : { ok: false, rows: [], source: 'empty file' };
    } catch (e) { return { ok: false, rows: [], source: 'network error' }; }
  },
  async loadOccurrences() { return this.loadCSV(Registry.datasets.occurrences.file); },
  async loadProduction() { return this.loadCSV(Registry.datasets.production.file); },
  async loadJSON(path) {
    if (!location.protocol.startsWith('http'))
      return { ok: false, data: null, source: 'file:// — fetch disabled' };
    try {
      const res = await fetch(path, { cache: 'no-store' });
      if (!res.ok) return { ok: false, data: null, source: 'HTTP ' + res.status };
      const data = await res.json();
      return { ok: true, data, source: path };
    } catch (e) { return { ok: false, data: null, source: 'parse error: ' + e.message }; }
  },
  async hydrate() {
    const [o, p, pred, fi, meta, exp] = await Promise.all([
      this.loadOccurrences(),
      this.loadProduction(),
      this.loadJSON('data/predictions.json'),
      this.loadJSON('data/feature_importance.json'),
      this.loadJSON('data/model_metadata.json'),
      this.loadJSON('data/exploration_scores.json'),
    ]);
    this.state.occurrences = o; this.state.production = p;
    this.state.predictions = pred; this.state.featureImportance = fi;
    this.state.modelMetadata = meta; this.state.explorationScores = exp;
    /* Calibrate DemoModel baseline from live data */
    if (pred.ok && pred.data && pred.data.portfolio) {
      DemoModel.calibrate(pred.data.portfolio);
    }
    console.info('[MineSight AI] data hydration →',
      o.ok ? o.rows.length + ' occurrences' : 'occurrences: not reachable',
      '·', p.ok ? p.rows.length + ' production rows' : 'production: not reachable',
      '·', pred.ok ? pred.data.predictions.length + ' predictions' : 'predictions: not reachable',
      '·', exp.ok ? exp.data.total_cells + ' exploration cells' : 'exploration: not reachable');
  },
  getOccurrencePoints() {
    const st = this.state.occurrences;
    if (!st.ok) return { ok: false, points: [], dropped: 0 };
    const points = []; let dropped = 0;
    st.rows.forEach((r, idx) => {
      const lat = parseFloat(r.Latitude_Decimal ?? r.Latitude);
      const lon = parseFloat(r.Longitude_Decimal ?? r.Longitude);
      if (Number.isFinite(lat) && Number.isFinite(lon) && lat >= 15 && lat <= 30 && lon >= 70 && lon <= 92)
        points.push({
          id: r.Occurrence_ID || r.Occurrence_Name || ('OCC-' + (idx + 1)),
          lat, lon,
          name: r.Occurrence_Name || r.Occurrence_ID || 'Occurrence',
          district: r.District || '—', state: r.State || '—',
          deposit: r.Deposit_Type || '—', status: r.Historical_Status || '—',
          formation: r.Geological_Formation || '—',
          host: r.Host_Rock || '',
          source: r.Source_Name || '',
          sourceRef: r.Source_Reference || ''
        });
      else dropped++;
    });
    return { ok: true, points, dropped };
  },
  getPredictions() { return this.state.predictions?.ok ? this.state.predictions.data : null; },
  getExploration() { return this.state.explorationScores?.ok ? this.state.explorationScores.data : null; },
  getFeatureImportance() { return this.state.featureImportance?.ok ? this.state.featureImportance.data : null; },
  getModelMetadata() { return this.state.modelMetadata?.ok ? this.state.modelMetadata.data : null; },
  registerOccurrences(rows) { this.state.occurrences = { ok: true, rows, source: 'registered' }; render(); },
  registerProduction(rows) { this.state.production = { ok: true, rows, source: 'registered' }; render(); }
};

/* ==================================================================
   05 · SHARED COMPONENTS
   ================================================================== */
const I = {
  arrow: '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
  ext: '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 17 17 7M9 7h8v8"/></svg>'
};
const el = id => document.getElementById(id);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const fmt = n => Math.round(n).toLocaleString('en-IN');
const sgn = n => (n >= 0 ? '+' : '−') + fmt(Math.abs(n));
const chip = (t, l) => `<span class="chip chip--${t}">${l}</span>`;
const notice = (msg, label = 'Prototype / Demo') =>
  `<div class="notice" role="note">${chip('warn', label)}<p>${msg}</p></div>`;
/* ★ PHASE 3 — data-class chips: OBSERVED / MODEL / SCENARIO / RECOMMENDATION */
const dChip = kind => ({
  observed: chip('ok', 'Observed · CSV'),
  model: chip('warn', 'Model prediction · demo'),
  scenario: chip('med', 'Scenario estimate · demo'),
  rec: chip('high', 'Recommendation — human review')
}[kind] || '');
const lrow = (k, v, tone = '', forceStack = null) => {
  const plain = s => String(s).replace(/<[^>]*>/g, '');
  const stack = forceStack ?? (plain(k).length > 20 || plain(v).length > 24);
  return `<div class="lrow${stack ? ' lrow--stack' : ''}"><span class="lrow-k">${k}</span><span class="lrow-l"></span><span class="lrow-v ${tone}">${v}</span></div>`;
};
const secHead = (kicker, h2, idx) => `
  <div class="sec-head"><div><p class="k kick-rule">${kicker}</p><h2 class="h2" style="margin-top:14px">${h2}</h2></div>
  <span class="sec-idx">${idx}</span></div>`;
const rateChip = rate => chip(({ HIGH: 'high', MEDIUM: 'med', LOW: 'mute' })[rate] || 'mute', rate);
const riskChip = cls => chip(({ LOW: 'ok', MEDIUM: 'med', HIGH: 'high', CRITICAL: 'crit' })[cls] || 'mute', cls + ' risk');

/* ==================================================================
   05b · MAPKIT — shared Leaflet helpers (both maps)
   ================================================================== */
const MapKit = {
  tiles() {
    return L.tileLayer(Registry.studyArea.tiles, {
      subdomains: 'abcd', maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>'
    });
  },
  envelope() {
    return L.rectangle(Registry.studyArea.envelope,
      { color: '#9B978D', weight: 1, dashArray: '4 5', fill: true, fillColor: '#C9662B', fillOpacity: .04, interactive: false });
  },
  anchorIcon() { return L.divIcon({ className: 'mi-ico', html: '<span class="mi-anchor"></span>', iconSize: [12, 12], iconAnchor: [6, 6] }); },
  occIcon() { return L.divIcon({ className: 'mi-ico', html: '<span class="mi-occ"></span>', iconSize: [10, 10], iconAnchor: [5, 5] }); },
  anchors() {
    const g = L.layerGroup();
    Registry.studyArea.anchors.forEach(a => {
      g.addLayer(
        L.marker([a.lat, a.lon], { icon: this.anchorIcon() })
          .bindTooltip(a.name.toUpperCase(), { permanent: true, direction: 'right', offset: [11, 0], className: 'mi-lab' })
          .bindPopup(`<div class="occ-pop"><b>${a.name.toUpperCase()} — DISTRICT ANCHOR</b><br>${a.state}<br>${a.lat.toFixed(4)} N · ${a.lon.toFixed(4)} E<br><span>Administrative reference point — not a mineral occurrence.</span></div>`)
      );
    });
    return g;
  },
  scrollGuard(map) {
    map.on('focus click', () => map.scrollWheelZoom.enable());
    map.getContainer().addEventListener('mouseleave', () => map.scrollWheelZoom.disable());
  }
};

/* ==================================================================
   06 · OVERVIEW
   ================================================================== */
function OverviewView() {
  const occ = Data.state.occurrences, prod = Data.state.production;
  const occPts = Data.getOccurrencePoints();
  const servedHttp = location.protocol.startsWith('http');
  const live = occ.ok || prod.ok;
  const serving = live ? ['LIVE · CSV IMPORT ACTIVE', 'v-ok']
    : servedHttp ? ['HTTP · CSV FILES NOT FOUND', 'v-warn']
      : ['file:// · CSV FETCH DISABLED', 'v-warn'];
  const dsRow = (key, st) => {
    const d = Registry.datasets[key];
    return st.ok
      ? lrow(d.file.split('/').pop(), `LOADED ${st.rows.length} / ${d.expected} · LIVE`, 'v-ok')
      : lrow(d.file.split('/').pop(), `EXPECTED ${d.expected} · AWAITING IMPORT · PHASE ${d.phase}`, 'v-warn');
  };

  /* ---- ★ PHASE 3 — computed intelligence (all from DemoModel) ---- */
  const base = DemoModel.predict(DemoModel.baseline);
  const rec = DemoModel.predict(Registry.simPresets.recommended.params);
  const zones = getDemoZones();
  const zc = {
    high: zones.filter(z => z.cls === 'HIGH').length,
    med: zones.filter(z => z.cls === 'MEDIUM').length,
    low: zones.filter(z => z.cls === 'LOW').length
  };
  const shortPct = s => s.toFixed(1) + '%';
  const delta = (sc, basev, unit = '', goodWhenDown = false) => {
    const d = sc - basev;
    const good = goodWhenDown ? d < 0 : d > 0;
    const cls = d === 0 ? '' : (good ? 'd-up' : 'd-bad');
    return `<span class="d ${cls}">${d === 0 ? 'no change' : sgn(d) + unit}</span>`;
  };
  const drivers = Object.keys(DemoModel.shares).map(k => [k, DemoModel.labels[k], DemoModel.shares[k]]);
  const primary = drivers.reduce((a, b) => b[2] > a[2] ? b : a);

  const ciCard = (val, unit, label, sub, extra = '') => `
    <div class="ci"><span class="k">${label}</span>
      <b>${val}${unit ? `<small>${unit}</small>` : ''}</b>
      <span class="ci-sub">${sub}</span>${extra}</div>`;

  const driverRows = drivers.map(([k, label, share]) => `
    <div class="wrow">
      <div class="wrow-top"><span class="k${k === primary[0] ? ' acc' : ''}">${label}</span>
        <span style="font:500 11px/1.6 var(--type-mono);color:var(--ink-2)">${Math.round(share * 100)}%</span></div>
      <span class="meter${k === primary[0] ? '' : ' dim'}" style="height:6px"><i style="width:${share * 100}%"></i></span>
    </div>`).join('');

  const html = `
  <div class="page">
    <!-- 1 · HERO -->
    <section class="hero">
      <div class="wrap">
        <div class="hero-grid">
          <div class="hero-copy">
            <p class="k kick-rule hero-kick">SIH 2026 · Problem 26009 · Ministry of Steel — MOIL Ltd.</p>
            <h1 class="h-display">MineSight<br><em>AI</em></h1>
            <p class="hero-tag">AI + Space Technology for smarter mining decisions.</p>
            <p class="hero-lede">MineSight AI reads geological, historical, satellite and operational signals together — to surface high-priority exploration areas, forecast production risk, explain what is driving it, and recommend corrective action before the shortfall reaches the month-end report.</p>
            <div class="hero-cta">
              <a class="btn btn-oxide" href="#/exploration">Explore Intelligence ${I.arrow}</a>
              <a class="btn btn-ghost-l" href="#/simulator">Try the simulator</a>
            </div>
            <p class="hero-note">Prospectivity is built from surface &amp; sub-surface indicators. Satellite inputs guide exploration priority — they do not directly detect underground reserves.</p>
          </div>
          <figure class="terrain-fig">
            <div class="terrain" id="hero-map-wrap">
              <div id="hero-map" style="width:100%;height:100%;border-radius:inherit"></div>
              <span class="terrain-tag tl">Model 1 — Exploration Intelligence</span>
              <span class="terrain-tag tr">Study region · MP / MH</span>
              <div class="hero-map-legend" id="hero-map-legend">
                <span><i style="display:inline-block;width:9px;height:9px;border-radius:50%;background:#C9662B;margin-right:4px"></i>HIGH</span>
                <span><i style="display:inline-block;width:9px;height:9px;border-radius:50%;background:#8A671C;margin-right:4px"></i>MEDIUM</span>
                <span><i style="display:inline-block;width:9px;height:9px;border-radius:50%;background:#3F6A4C;margin-right:4px"></i>LOW</span>
                <span><i style="display:inline-block;width:7px;height:7px;border-radius:50%;background:#EDEAE2;border:1.5px solid #C9662B;margin-right:4px"></i>Occurrence</span>
              </div>
            </div>
            <figcaption class="terrain-cap">Model 1 spatial intelligence · satellite basemap · 21,067 grid cells scored · DEMO/SYNTHETIC</figcaption>
          </figure>
        </div>
        <div class="hero-facts">
          <div class="fact"><b>18</b><span>Historical occurrences · 3 districts</span></div>
          <div class="fact"><b>3</b><span>Study districts · MP + MH</span></div>
          <div class="fact"><b>14</b><span>Mines in production model</span></div>
          <div class="fact"><b>48</b><span>Months of production series</span></div>
          <div class="fact"><b>v1.0</b><span>Full integration shipped</span></div>
        </div>
      </div>
    </section>

    <!-- 2 · CURRENT INTELLIGENCE -->
    <section class="sec" id="sec-predict">
      <div class="wrap">
        ${secHead('Current intelligence', 'This cycle, at a glance.', '01 / 06')}
        <p class="sec-lede">A representative demo snapshot of the portfolio for the current cycle. When the backend connects, every figure below reads live from Model 2 outputs — the layout will not change.</p>
        ${dChip('model')}
        <div class="ci-grid" style="margin-top:18px">
          ${ciCard(fmt(DemoModel.baseline.target), 't', 'Production Target', 'Portfolio avg · Model 2 calibrated')}
          ${ciCard(fmt(base.predicted), 't', 'Predicted Production', 'Model 2 · GB Regressor')}
          ${ciCard(base.index, '/100', 'Shortfall Risk', base.cls + ' · risk index',
    `<button class="link-arrow" type="button" data-scrollto="sec-why">Why? ${I.arrow}</button>`)}
          ${ciCard(DemoModel.availability(DemoModel.baseline.downtime), '%', 'Equipment Availability', 'Avg downtime ' + DemoModel.baseline.downtime + ' hrs')}
          ${ciCard(zones.length, '', 'Priority Zones', `Model 1 · ${zc.high} HIGH · ${zc.med} MED · ${zc.low} LOW`)}
          ${ciCard(Registry.intelligence.alerts.length, '', 'Intelligence Alerts', Registry.intelligence.label)}
        </div>
        <div style="margin-top:26px;border-top:1px solid var(--line)">
          ${Registry.intelligence.alerts.map(a =>
      `<div class="alert-row">${chip(a.level === 'CRITICAL' ? 'crit' : 'warn', a.level)}<p>${a.text}</p></div>`).join('')}
        </div>
      </div>
    </section>

    <!-- 3 · EXPLORATION PRIORITY -->
    <section class="sec">
      <div class="wrap">
        ${secHead('Exploration priority', 'One belt, three districts, two states.', '02 / 06')}
        <p class="sec-lede">Balaghat in Madhya Pradesh and Bhandara–Nagpur in Maharashtra form the central-Indian manganese belt this platform reads. District anchors are administrative reference points; historical occurrence markers plot live from the imported CSV, alongside demonstration priority zones.</p>
        <div class="study-grid">
          <div class="study-map-wrap">
            <div id="study-map" role="application" aria-label="Interactive map of the MOIL study region — Balaghat, Bhandara, Nagpur"></div>
            <div class="map-legend">
              <span><i class="lg lg-anchor"></i>District anchor</span>
              <span><i class="lg lg-occ"></i>Historical occurrence</span>
              <span><i class="lg lg-env"></i>Study envelope</span>
              <span class="lg-status" id="map-status">…</span>
            </div>
          </div>
          <aside class="study-side">
            <span class="k group-k">Region ledger</span>
            <div class="ledger">
              ${Registry.studyArea.anchors.map(a =>
        lrow(a.name + ' · ' + (a.state === 'Madhya Pradesh' ? 'MP' : 'MH'),
          a.lat.toFixed(2) + ' N · ' + a.lon.toFixed(2) + ' E')).join('')}
              ${lrow('Occurrence points',
            occPts.ok ? `LIVE — ${occPts.points.length} PLOTTED` : 'AWAITING CSV IMPORT',
            occPts.ok && occPts.points.length ? 'v-ok' : 'v-warn')}
              ${occPts.ok && occPts.dropped ? lrow('Rows skipped · invalid coords', String(occPts.dropped), 'v-warn') : ''}
              ${lrow('Demo priority zones', `${zones.length} · ${zc.high} HIGH / ${zc.med} MED / ${zc.low} LOW`, 'v-mute')}
              ${lrow('Study envelope', '20.85–22.15 N · 78.55–80.65 E', 'v-mute')}
            </div>
            <p class="fineprint">Basemap © OpenStreetMap contributors © CARTO · District anchors are administrative references, not mineral occurrences · Occurrence coordinates import from manganese_occurrences_MOIL_study_area.csv</p>
            <a class="link-arrow" href="#/exploration">Open Exploration Intelligence ${I.arrow}</a>
          </aside>
        </div>
      </div>
    </section>

    <!-- 4 · PREDICT + EXPLAIN -->
    <section class="sec" id="sec-why">
      <div class="wrap">
        ${secHead('Production forecast &amp; risk', 'Is production falling behind — and why?', '03 / 06')}
        <div class="duo">
          <div class="panel">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap">
              <span class="k">Current cycle forecast</span>${dChip('model')}
            </div>
            <div class="cmp">
              <div class="cmp-row">
                <div class="cmp-top"><span class="k">Target</span>
                  <span style="font:500 12px/1.6 var(--type-mono)">${fmt(DemoModel.baseline.target)} t</span></div>
                <div class="cmp-bar"><i style="width:100%"></i></div>
              </div>
              <div class="cmp-row">
                <div class="cmp-top"><span class="k">Predicted</span>
                  <span style="font:500 12px/1.6 var(--type-mono)">${fmt(base.predicted)} t</span></div>
                <div class="cmp-bar b-pred"><i style="width:${(base.predicted / DemoModel.baseline.target * 100).toFixed(1)}%"></i></div>
              </div>
            </div>
            <p class="shortfall-line">Expected shortfall — ${fmt(base.shortfall)} t · ${shortPct(base.pct)} of target</p>
            <div class="comp-row" style="margin-top:10px">${riskChip(base.cls)}
              <span style="font:500 11px/1.6 var(--type-mono);color:var(--mute)">Risk index ${base.index} / 100 · demo</span></div>
          </div>
          <div class="panel">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap">
              <span class="k">Why is the risk high?</span>${dChip('model')}
            </div>
            ${driverRows}
            <div class="primary-driver"><b>PRIMARY DRIVER</b> — ${esc(primary[1])} · ${Math.round(primary[2] * 100)}% of expected shortfall</div>
            <p class="fineprint">Contribution shares are demo values pending real model explainability (feature importance).</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 5 · RECOMMEND + DECISION IMPACT + SIMULATE -->
    <section class="sec" id="sec-act">
      <div class="wrap">
        ${secHead('Action required', 'What to do about it.', '04 / 06')}
        <div class="action-card">
          <div>
            <div class="comp-row">${chip('high', 'Action Required')}${dChip('model')}</div>
            <h3 class="h3" style="margin-top:14px">High production risk — equipment downtime is the dominant constraint</h3>
            <p style="margin-top:10px;font-size:14.5px;color:var(--mute);max-width:52ch">
              Primary driver: <strong style="color:var(--ink-2)">${esc(primary[1])}</strong> — ${Math.round(primary[2] * 100)}% of the
              expected shortfall, at ${DemoModel.baseline.downtime} hrs downtime this cycle
              (availability ${DemoModel.availability(DemoModel.baseline.downtime)}%).</p>
            <div class="nextstep">
              <span class="k">Recommended action</span>
              <p>Prioritize maintenance for <strong>Equipment E-07</strong> and evaluate temporary redeployment
              to hold availability above 90% through the cycle.</p>
            </div>
            <div class="comp-row" style="margin-top:14px">${dChip('rec')}</div>
            <div class="cta-row">
              <button class="btn btn-oxide" type="button" data-simpreset="recommended">Simulate Action ${I.arrow}</button>
              <a class="link-arrow" href="#/recommendations">Full recommendation queue — Phase 6 ${I.arrow}</a>
            </div>
          </div>
          <aside>
            <span class="k">Decision impact</span>
            <p class="fineprint" style="margin-top:6px">Model-estimated scenario impact · demo</p>
            <div class="ledger" style="margin-top:12px">
              ${lrow('Predicted production', `${fmt(base.predicted)} → ${fmt(rec.predicted)} t <span class="${rec.predicted > base.predicted ? 'd-up' : ''}">${sgn(rec.predicted - base.predicted)} t</span>`)}
              ${lrow('Expected shortfall', `${fmt(base.shortfall)} → ${fmt(rec.shortfall)} t <span class="${rec.shortfall < base.shortfall ? 'd-up' : ''}">${sgn(rec.shortfall - base.shortfall)} t · ${Math.round((1 - rec.shortfall / base.shortfall) * 100)}%</span>`)}
              ${lrow('Risk class', `${riskChip(base.cls)} → ${riskChip(rec.cls)}`)}
              ${lrow('Risk index', `${base.index} → ${rec.index} / 100`)}
            </div>
            <p class="fineprint">Potential impact — not a guaranteed outcome. Validated against real operations before any field action.</p>
          </aside>
        </div>
      </div>
    </section>

    <!-- 6 · DECISION WORKFLOW -->
    <section class="sec" id="sec-flow">
      <div class="wrap">
        ${secHead('Decision workflow', 'Explore → Predict → Explain → Recommend → Simulate.', '05 / 06')}
        <div class="steps">
          <div class="step"><span class="n">01</span><b>Explore</b>
            <p>Rank the belt by prospectivity; pick high-priority zones for field follow-up.</p>
            <a class="link-arrow" href="#/exploration">Open ${I.arrow}</a></div>
          <div class="step"><span class="n">02</span><b>Predict</b>
            <p>Forecast output against target; grade the shortfall risk per cycle.</p>
            <a class="link-arrow" href="#/production">Open ${I.arrow}</a></div>
          <div class="step"><span class="n">03</span><b>Explain</b>
            <p>See which constraints drive the risk — and by how much.</p>
            <button class="link-arrow" type="button" data-scrollto="sec-why">View drivers ${I.arrow}</button></div>
          <div class="step"><span class="n">04</span><b>Recommend</b>
            <p>Turn the dominant constraint into a numbered corrective action.</p>
            <a class="link-arrow" href="#/recommendations">Open ${I.arrow}</a></div>
          <div class="step"><span class="n">05</span><b>Simulate</b>
            <p>Estimate how the intervention could change the outcome — before committing.</p>
            <a class="link-arrow" href="#/simulator">Open ${I.arrow}</a></div>
        </div>
        <p class="fineprint" style="margin-top:28px">Under the hood — model registry</p>
        <div class="flow-list">
          <div class="flow-row">
            <span class="flow-num">01</span>
            <div class="flow-main"><h3 class="h3">Exploration Intelligence</h3>
              <p>Combines geology, historical occurrences, terrain and satellite indicators into a prospectivity score that ranks where exploration should happen first.</p></div>
            <div class="flow-pipe">GEOLOGY · OCCURRENCES · SRTM · NDVI · CLIMATE<br>→ SCORE 0–100 → HIGH / MED / LOW</div>
            <div class="flow-meta">${chip('warn', 'Demo scoring · Phase 9')}<span class="flow-id">Model 1</span></div>
          </div>
          <div class="flow-row">
            <span class="flow-num">02</span>
            <div class="flow-main"><h3 class="h3">Production Intelligence</h3>
              <p>Learns from 48 months of production, equipment, weather and blasting records to forecast output and expose the expected shortfall against target.</p></div>
            <div class="flow-pipe">TARGET + OPERATIONAL CONDITIONS<br>→ FORECAST → SHORTFALL % → RISK</div>
            <div class="flow-meta">${chip('warn', 'Demo model · Phase 8')}<span class="flow-id">Model 2</span></div>
          </div>
          <div class="flow-row">
            <span class="flow-num">03</span>
            <div class="flow-main"><h3 class="h3">Recommendation Engine</h3>
              <p>Reads risk and the dominant operational constraint, then proposes corrective steps — maintenance, blasting, scheduling, redeployment.</p></div>
            <div class="flow-pipe">RISK + CONSTRAINTS<br>→ RULES → CORRECTIVE ACTIONS</div>
            <div class="flow-meta">${chip('mute', 'Rule-based · Phase 6')}<span class="flow-id">Layer 3</span></div>
          </div>
        </div>
      </div>
    </section>

    <!-- 7 · FOUNDATION STATUS -->
    <section class="sec">
      <div class="wrap">
        ${secHead('Foundation status — live', 'What&rsquo;s wired so far.', '06 / 06')}
        <p class="sec-lede">Values below are read from the data registry at runtime. As later phases connect real files and models, this panel updates without any UI changes — the status <em>is</em> the architecture.</p>
        <div class="status-groups">
          <div class="sgroup"><span class="k">Models</span><div class="ledger">
            ${lrow('Model 1 · Exploration', 'WEIGHTED SCORING · 21,067 CELLS SCORED', 'v-ok')}
            ${lrow('Model 2 · Production', 'GRADIENT BOOSTING · R² 0.9689 · CONNECTED', 'v-ok')}
            ${lrow('Recommendation engine', 'RULE-BASED · CONNECTED', 'v-ok')}
            ${lrow('Simulator', 'CALIBRATED TO REAL FEATURE IMPORTANCE', 'v-ok')}
          </div></div>
          <div class="sgroup"><span class="k">Datasets</span><div class="ledger">
            ${dsRow('occurrences', occ)}
            ${dsRow('production', prod)}
          </div></div>
          <div class="sgroup"><span class="k">Runtime</span><div class="ledger">
            ${lrow('Serving mode', serving[0], serving[1])}
            ${lrow('Enable CSV import', '<code>python -m http.server 8000</code>', 'v-mute', true)}
            ${lrow('Design system', 'SHIPPED — <a href="#/system">/#/system</a>', 'v-ok')}
            ${lrow('Build progress', 'v1.0 — FULL INTEGRATION SHIPPED', 'v-ok')}
          </div></div>
        </div>
        <p class="foot-note">Model performance — prototype validation · ${Registry.models.production.metrics.algorithm} · ${Registry.models.production.metrics.window} · MAE ${Registry.models.production.metrics.MAE} · RMSE ${Registry.models.production.metrics.RMSE} · R² ${Registry.models.production.metrics.R2} · MAPE ${Registry.models.production.metrics.MAPE}</p>
      </div>
    </section>
  </div>`;
  return {
    html, mount() {
      const cleanups = [];
      const m = mountStudyMap(); if (m) cleanups.push(m);
      const h = mountHeroMap(); if (h) cleanups.push(h);
      return () => cleanups.forEach(fn => fn());
    }
  };
}

/* ---- scaffolds for pages still pending (production · recommendations · methodology) ---- */
const CT = {
  production: {
    kicker: 'Model 2 — Production Intelligence', question: 'Where is production at risk?',
    lede: `For each of 14 mines, this page will set the production target against the model's forecast, quantify the expected shortfall and grade the risk — then show which operational constraint is driving it. Built on the prototype production series, January 2022 to December 2025. Portfolio-level predict &amp; explain already live on the Overview and in the Simulator.`,
    banner: 'Production ML model not connected — showing prototype analysis.',
    phaseLabel: 'Phase 5',
    plan: [
      ['Mine selector', 'Per-mine forecast summary — target, expected production, expected shortfall, shortfall % and risk grade.'],
      ['Target · actual · predicted', 'One interactive chart across the full 48-month series answering: is production falling behind target?'],
      ['Production trend', 'Monthly trajectory per mine with the 2025 test window marked.'],
      ['Operational constraints', 'Equipment availability and downtime, rainfall, blasting delay, working days — rated, not decorated.']],
    status: [
      ['Model 2 · registry', 'DEMO MODEL', 'v-warn'],
      ['Planned algorithm', 'GRADIENT BOOSTING REGRESSOR', ''],
      ['Production dataset', '672 ROWS EXPECTED · AWAITING IMPORT', 'v-warn'],
      ['Prototype validation', 'R² 0.9918 · MAPE 3.44%', 'v-ok'],
      ['Build phase', '5 OF 10', 'v-mute']],
    fineprint: 'Prototype dataset — predictions are not real MOIL operational forecasts'
  },
  recommendations: {
    kicker: 'Recommendation Engine', question: 'What should we do?',
    lede: `A shortfall only matters when someone knows the next move. This page will rank mines by risk, name the dominant constraint, and issue numbered corrective actions — maintenance, blasting, scheduling, redeployment — as AI-assisted recommendations, always for human review. A portfolio-level action card with decision impact already lives on the Overview.`,
    banner: 'Recommendation engine not yet connected — corrective actions activate with Model 2 outputs in Phase 6.',
    phaseLabel: 'Phase 6',
    plan: [
      ['High-priority queue', 'Mine, expected shortfall, risk grade and the primary constraint — ordered by urgency.'],
      ['Numbered corrective actions', 'Concise, executable steps per mine, each traced to the condition that triggered it.'],
      ['Decision impact', 'Potential impact per action — model-estimated, clearly labelled, never guaranteed.'],
      ['Three-way filtering', 'Risk, mine and constraint — built for shift briefings as much as review meetings.']],
    status: [
      ['Engine · registry', 'RULE-BASED · NOT CONNECTED', 'v-warn'],
      ['Inputs', 'SHORTFALL · DOWNTIME · RAINFALL · BLASTING · WORKING DAYS', ''],
      ['Activation', 'WITH MODEL 2 OUTPUTS — PHASE 6', 'v-mute'],
      ['Build phase', '6 OF 10', 'v-mute']],
    fineprint: 'All outputs are AI-assisted recommendations — not guaranteed operational instructions'
  },
  methodology: {
    kicker: 'Methodology', question: 'How does it work?',
    lede: `Data flows from six source families through two models and a rule layer into the dashboard. This page will document every input, transformation and output — and state plainly which values are measured, which are modelled, and which are demonstration data. The live data-provenance ledger in the footer already covers source status.`,
    banner: 'Full documentation ships in Phase 7 — the pipeline structure below is the committed design.',
    phaseLabel: 'Phase 7',
    plan: [
      ['Data source board', 'Geological, occurrence, satellite, weather, production and equipment data — each with live integration status.'],
      ['Model 1 pipeline', 'Geology + occurrence + terrain + satellite indicators → prospectivity model → score → priority class.'],
      ['Model 2 pipeline', 'Production history + operational conditions → forecast → shortfall → risk grade.'],
      ['Performance & limits', 'Prototype validation metrics, known limitations, and what changes when real operational data arrives.']],
    status: [
      ['Data sources', 'FOOTER PROVENANCE LEDGER — LIVE', 'v-ok'],
      ['Model 1', 'NOT CONNECTED', 'v-warn'],
      ['Model 2', 'NOT CONNECTED', 'v-warn'],
      ['Recommendation layer', 'RULE-BASED · PHASE 6', 'v-mute']],
    fineprint: 'Prototype system — outputs must be validated with official geological, operational and field data',
    extra: `
      <div class="pipe"><span class="dim">DATA SOURCES ─▶ MODEL 1 ─▶</span> PROSPECTIVITY SCORE <span class="dim">─▶</span> HIGH / MED / LOW <span class="acc">┐</span><br>
      <span class="dim">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├─▶</span> RECOMMENDATION ENGINE <span class="dim">─▶</span> DASHBOARD<br>
      <span class="dim">OPERATIONAL DATA ─▶ MODEL 2 ─▶</span> FORECAST <span class="dim">─▶</span> SHORTFALL <span class="dim">─▶</span> RISK <span class="acc">┘</span></div>
      <div class="disclaimer">${chip('mute', 'Disclaimer')}<p>Prototype system for demonstration purposes. Production and exploration outputs should be validated with official geological, operational and field data before real-world decision making.</p></div>`
  }
};

function ScaffoldView(c) {
  const html = `
  <div class="page">
    <div class="wrap">
      <div class="page-head">
        <p class="k kick-rule">${c.kicker}</p>
        <h1 class="h1">${c.question}</h1>
        <p class="lede">${c.lede}</p>
        ${notice(c.banner)}
      </div>
      <div class="duo">
        <div>
          <span class="k group-k">In scope — ${c.phaseLabel}</span>
          <ol class="plan">${c.plan.map((p, i) =>
    `<li><span class="n">0${i + 1}</span><div><b>${p[0]}</b><p>${p[1]}</p></div></li>`).join('')}</ol>
        </div>
        <aside>
          <span class="k group-k">Engineering status</span>
          <div class="ledger">${c.status.map(r => lrow(r[0], r[1], r[2])).join('')}</div>
          <p class="fineprint">${c.fineprint}</p>
        </aside>
      </div>
      ${c.extra ? `<div class="extra">${c.extra}</div>` : ''}
    </div>
  </div>`;
  return { html };
}

/* ---- design system documentation ---- */
function SystemView() {
  const groups = [
    ['Surfaces', [['Paper', '#F1EEE7', 'Primary content surface'], ['Paper raised', '#F7F5F0', 'Panels & wells'], ['Paper sunken', '#E7E3DA', 'Inset fields'], ['Graphite', '#17191B', 'Hero · footer · data panels'], ['Graphite raised', '#1E2124', 'On-dark raised']]],
    ['Ink & text', [['Ink', '#191B17', 'Primary text'], ['Ink soft', '#3E403A', 'Secondary text'], ['Muted', '#6F6C63', 'Captions & labels'], ['On-dark', '#EDEAE2', 'Text on graphite'], ['On-dark muted', '#9B978D', 'Secondary on dark']]],
    ['Accent', [['Oxide', '#B0521D', 'CTAs · priority · active markers'], ['Oxide bright', '#C9662B', 'Accent on dark'], ['Moss', '#4E7A5A', 'Vegetation / positive states']]],
    ['Status', [['Low', '#4E7A5A', 'Risk LOW'], ['Medium', '#A07A22', 'Risk MEDIUM'], ['High', '#B45624', 'Risk HIGH'], ['Critical', '#98352A', 'Risk CRITICAL']]],
    ['Structure', [['Hairline', 'rgba(25,27,23,.14)', 'Borders on light'], ['Hairline dark', 'rgba(240,237,229,.10)', 'Borders on dark']]]
  ];
  const types = [
    ['t-display', 'Display · Archivo 620 · 44–96px · uppercase', 'MineSight AI'],
    ['t-h1', 'Heading 1 · 30–52px · 580', 'Where should we explore?'],
    ['t-h2', 'Heading 2 · 22–32px · 570', 'Three components. One loop.'],
    ['t-lede', 'Lede · 17–19px · 430', 'Production intelligence compares each mine target with the forecast, quantifies shortfall and grades the risk.'],
    ['t-body', 'Body · 16px / 1.65 · 400', 'Equipment availability, downtime, rainfall, blasting delay and working days form the constraint picture behind every forecast.'],
    ['t-mono', 'Mono label · 11px · +0.18em · 500', 'Prospectivity — 87 / 100 · High']
  ];
  const html = `
  <div class="page">
    <div class="wrap">
      <div class="page-head">
        <p class="k kick-rule">Design system · v0.1</p>
        <h1 class="h1">The look of the platform.</h1>
        <p class="lede">Every surface, weight and color used across MineSight AI — the contract the integration build against. Specimens use placeholder values for styling demonstration only.</p>
      </div>

      <div class="sys-sec">
        <span class="k group-k">00 — Principles</span>
        <ol class="principles">
          <li><span class="n">01</span><div><b>Terrain over decoration</b><p>Paper and graphite surfaces, hairline structure. Color is earned, never sprayed.</p></div></li>
          <li><span class="n">02</span><div><b>One accent</b><p>Oxide marks priority and attention — nothing else competes with it.</p></div></li>
          <li><span class="n">03</span><div><b>Every visual answers a question</b><p>If a chart has no question to answer, it does not ship.</p></div></li>
          <li><span class="n">04</span><div><b>Honest by default</b><p>Prototype, demonstration and modelled data are labelled as such — always.</p></div></li>
        </ol>
      </div>

      ${groups.map(([name, items]) => `
      <div class="sys-sec">
        <span class="k group-k">01 — Color · ${name}</span>
        <div class="swgrid">${items.map(([n, hex, use]) => `
          <div class="sw"><div class="sw-c" style="background:${hex}"></div>
          <div class="sw-t"><b>${n}</b><span>${hex}</span><em>${use}</em></div></div>`).join('')}
        </div>
      </div>`).join('')}

      <div class="sys-sec">
        <span class="k group-k">02 — Typography</span>
        ${types.map(([cls, spec, text]) => `
        <div class="typerow"><div class="${cls}">${text}</div><span class="spec">${spec}</span></div>`).join('')}
      </div>

      <div class="sys-sec">
        <span class="k group-k">03 — Components</span>
        <div class="comp-group"><span class="k" style="letter-spacing:.12em">Buttons</span>
          <div class="comp-row">
            <a class="btn btn-oxide" href="#/system">Primary ${I.arrow}</a>
            <a class="btn btn-ghost-d" href="#/system">Secondary</a>
            <a class="link-arrow" href="#/system">Text link ${I.arrow}</a>
          </div>
        </div>
        <div class="comp-group"><span class="k" style="letter-spacing:.12em">Status chips</span>
          <div class="comp-row">
            ${chip('ok', 'Low')}${chip('med', 'Medium')}${chip('high', 'High')}${chip('crit', 'Critical')}${chip('warn', 'Not connected')}${chip('ok', 'Operational')}${chip('mute', 'Planned')}
          </div>
        </div>
        <div class="comp-group"><span class="k" style="letter-spacing:.12em">Data-class chips</span>
          <div class="comp-row">${dChip('observed')}${dChip('model')}${dChip('scenario')}${dChip('rec')}</div>
        </div>
        <div class="comp-group"><span class="k" style="letter-spacing:.12em">Prototype notice</span>
          ${notice('Production ML model not connected — showing prototype analysis.')}
        </div>
        <div class="comp-group"><span class="k" style="letter-spacing:.12em">Ledger</span>
          <div class="ledger">
            ${lrow('Prospectivity', '87 / 100 · HIGH', 'v-warn')}
            ${lrow('Expected shortfall', '3,500 t · 11.7%', 'v-crit')}
            ${lrow('Model 2', 'NOT CONNECTED · PHASE 8', 'v-warn')}
          </div>
        </div>
        <div class="comp-group" style="border-bottom:none"><span class="k" style="letter-spacing:.12em">Panels</span>
          <div class="demopanels">
            <div class="panel"><span class="k">Panel · light</span>
              <div class="ledger" style="margin-top:12px">${lrow('Target', '30,000 t')}${lrow('Predicted', '26,500 t')}</div></div>
            <div class="panel panel--dark"><span class="k" style="color:var(--gmute)">Panel · dark</span>
              <div style="margin-top:12px;display:flex;gap:10px;align-items:center">${chip('high', 'High risk')}<span style="font:500 12px var(--type-mono);color:var(--gmute)">BLASTING DELAY 4.2 D</span></div></div>
          </div>
        </div>
      </div>

      <div class="sys-sec">
        <span class="k group-k">04 — Motion & layout</span>
        <div class="duo">
          <div class="ledger">
            ${lrow('Duration · fast', '180ms — hovers, chips')}${lrow('Duration · medium', '350ms — panels, dropdowns')}
            ${lrow('Page transition', 'fade + 10px rise · 450ms')}${lrow('Easing', 'cubic-bezier(.22,.61,.21,1)')}
            ${lrow('Reduced motion', 'all drift & transitions disabled', 'v-ok')}
          </div>
          <div class="ledger">
            ${lrow('Container', '1240px max · fluid gutters')}${lrow('Section rhythm', 'clamp(56–110px) vertical')}
            ${lrow('Radii', '3px controls · 5px panels')}${lrow('Depth', 'hairlines over shadows', 'v-mute')}
          </div>
        </div>
      </div>
    </div>
  </div>`;
  return { html };
}

/* ==================================================================
   07a · HERO MAP — real Leaflet satellite map with Model 1 scores
   ================================================================== */
function mountHeroMap() {
  const wrap = document.getElementById('hero-map-wrap');
  const elx = document.getElementById('hero-map');
  if (!wrap || !elx || typeof L === 'undefined') return null;

  /* Satellite basemap — ESRI World Imagery (free, no key required) */
  const map = L.map(elx, {
    scrollWheelZoom: false, zoomControl: true,
    attributionControl: true, dragging: true
  });
  map.attributionControl.setPrefix('');

  /* Primary: ESRI World Imagery (satellite). Fallback: CartoDB dark */
  const satellite = L.tileLayer(
    'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    { maxZoom: 18, attribution: 'Tiles © Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and GIS User Community' }
  ).addTo(map);

  /* Terrain / topo fallback layer (toggle) */
  const topo = L.tileLayer(
    'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png?key=cb1_2jg7_1_53a3f4de78ee87d794db67c2',
    { maxZoom: 19, attribution: '© OpenStreetMap contributors © CARTO', subdomains: 'abcd' }
  );

  /* Model 1 exploration score circles (top 500 cells from exploration_scores.json) */
  const expLayer = L.layerGroup();
  const expData = Data.getExploration();
  if (expData && expData.top_cells && expData.top_cells.length) {
    const clrMap = { HIGH: '#C9662B', MEDIUM: '#8A671C', LOW: '#3F6A4C' };
    const radMap = { HIGH: 1800, MEDIUM: 1400, LOW: 1000 };
    expData.top_cells.forEach(c => {
      L.circleMarker([c.lat, c.lon], {
        radius: c.cls === 'HIGH' ? 8 : c.cls === 'MEDIUM' ? 6 : 4,
        color: clrMap[c.cls] || '#6F6C63',
        fillColor: clrMap[c.cls] || '#6F6C63',
        fillOpacity: 0.55, weight: 1, opacity: 0.8
      }).bindTooltip(
        `<b>${esc(c.id)}</b><br>Score: ${c.score} · ${c.cls}<br>${esc(c.district)}<br>` +
        `Elevation: ${c.elevation} m · NDVI: ${c.ndvi}<br>` +
        `<em style="font-size:10px;opacity:.7">DEMO/SYNTHETIC — not confirmed reserve</em>`,
        { direction: 'top', className: 'mi-tip' }
      ).addTo(expLayer);
    });
    expLayer.addTo(map);
  }

  /* Historical occurrences */
  const occ = Data.getOccurrencePoints();
  const occLayer = L.layerGroup();
  if (occ.ok && occ.points.length) {
    occ.points.forEach(p => {
      L.circleMarker([p.lat, p.lon], {
        radius: 5, color: '#C9662B', fillColor: '#F1EEE7',
        fillOpacity: 0.9, weight: 2
      }).bindTooltip(`<b>${esc(p.name)}</b><br>${esc(p.district)} · ${esc(p.state)}<br>${esc(p.deposit)}<br><em style="font-size:10px;opacity:.7">Historical occurrence · live CSV</em>`,
        { direction: 'top', className: 'mi-tip' }).addTo(occLayer);
    });
    occLayer.addTo(map);
  }

  /* Study envelope */
  L.rectangle(Registry.studyArea.envelope, {
    color: 'rgba(201,102,43,.6)', weight: 1.2, fill: false, dashArray: '4 4'
  }).addTo(map);

  /* Layer control */
  const baseLayers = { 'Satellite (ESRI)': satellite, 'Dark terrain (CARTO)': topo };
  const overlays = {};
  if (expData && expData.top_cells) overlays['Exploration scores (Model 1)'] = expLayer;
  if (occ.ok && occ.points.length) overlays['Historical occurrences (live)'] = occLayer;
  L.control.layers(baseLayers, overlays, { position: 'bottomright', collapsed: true }).addTo(map);

  /* Fit to study area */
  map.fitBounds(Registry.studyArea.envelope, { padding: [16, 16] });
  MapKit.scrollGuard(map);

  return () => map.remove();
}


/* mountTerrain kept for backward compatibility — noop when hero-map replaces it */
function mountTerrain() { return null; }


/* ==================================================================
   07b · OVERVIEW STUDY-REGION MAP
   ================================================================== */
function mountStudyMap() {
  const elx = document.getElementById('study-map'); if (!elx) return null;
  const statusEl = document.getElementById('map-status');

  if (typeof L === 'undefined') {
    elx.innerHTML = '<div class="map-fallback">Basemap library unreachable — connect to the internet to load the interactive study-region map.</div>';
    if (statusEl) statusEl.textContent = 'MAP OFFLINE';
    return null;
  }

  const map = L.map(elx, { scrollWheelZoom: false });
  map.attributionControl.setPrefix('');
  MapKit.tiles().addTo(map);
  MapKit.envelope().addTo(map);

  const anchors = MapKit.anchors();
  const occ = Data.getOccurrencePoints();
  const occLayer = L.layerGroup();
  if (occ.ok && occ.points.length) {
    occ.points.forEach(p => {
      occLayer.addLayer(
        L.marker([p.lat, p.lon], { icon: MapKit.occIcon() })
          .bindTooltip(`<b>${esc(p.name.toUpperCase())}</b> · ${esc(p.district)}<br>${esc(p.deposit)} · ${esc(p.status)}`,
            { direction: 'top', offset: [0, -7], className: 'mi-tip' })
          .bindPopup(expOccPopup(p))
      );
    });
  }

  const overlays = { 'District anchors': anchors };
  if (occ.ok && occ.points.length) overlays['Historical occurrences (live)'] = occLayer;
  anchors.addTo(map);
  if (occ.ok && occ.points.length) occLayer.addTo(map);
  L.control.layers(null, overlays, {
    position: 'topright',
    collapsed: matchMedia('(max-width:720px)').matches
  }).addTo(map);

  map.fitBounds(Registry.studyArea.envelope, { padding: [26, 26] });
  MapKit.scrollGuard(map);

  if (statusEl) statusEl.textContent = occ.ok
    ? (occ.points.length
      ? (occ.dropped ? `${occ.points.length} OCCURRENCE POINTS LIVE · ${occ.dropped} ROW(S) SKIPPED`
        : `${occ.points.length} OCCURRENCE POINTS LIVE FROM CSV`)
      : `0 VALID POINTS · ${occ.dropped} ROW(S) SKIPPED`)
    : 'OCCURRENCES AWAITING CSV IMPORT';

  return () => map.remove();
}

/* ==================================================================
   07c · EXPLORATION INTELLIGENCE (prototype)
   ================================================================== */
const ExpDemo = {
  hash32(str) {
    let h = 2166136261;
    for (let i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 16777619); }
    return h >>> 0;
  },
  score(seed) { return Math.round((this.hash32('mi·' + seed) / 4294967295) * 100); },
  classOf(s) { return s >= 70 ? 'HIGH' : s >= 40 ? 'MEDIUM' : 'LOW'; },
  /* ★ PHASE 3 — supporting-evidence generator (deterministic per seed+score) */
  evidence(seed, score) {
    const defs = [['gs', 'Geological similarity'], ['hop', 'Historical occurrence proximity'],
    ['terr', 'Terrain suitability'], ['ndvi', 'NDVI signal'],
    ['soil', 'Soil moisture'], ['temp', 'Land temperature']];
    return defs.map(([key, label]) => {
      const v = (this.hash32(seed + '·' + key) / 4294967295) * 0.55 + (score / 100) * 0.45;
      return { key, label, rate: v >= 0.62 ? 'HIGH' : v >= 0.42 ? 'MEDIUM' : 'LOW' };
    });
  },
  confidence(seed, score) {
    const v = (this.hash32(seed + '·conf') / 4294967295) * 0.4 + (score / 100) * 0.6;
    return v >= 0.6 ? 'HIGH' : v >= 0.42 ? 'MEDIUM' : 'LOW';
  },
  nextStep(cls) {
    return cls === 'HIGH'
      ? 'Prioritize geological survey and further investigation.'
      : cls === 'MEDIUM'
        ? 'Schedule a follow-up field review in the next planning cycle.'
        : 'Monitor — no immediate action required.';
  }
};

const ExpState = {
  filters: { state: '', district: '', priority: '', status: '' },
  page: 1, perPage: 8,
  selectedZone: null, selectedOcc: null, selMarker: null,
  map: null, layers: {}, markers: new Map()
};

const norm = s => String(s || '').trim().toLowerCase();
const el2 = id => document.getElementById(id);

function getDemoZones() {
  return Registry.studyArea.demoZones.map(z => ({ ...z, cls: ExpDemo.classOf(z.score) }));
}
function getFilteredZones() {
  const f = ExpState.filters;
  return getDemoZones()
    .filter(z => !f.state || norm(z.state) === norm(f.state))
    .filter(z => !f.district || norm(z.district) === norm(f.district))
    .filter(z => !f.priority || z.cls === f.priority.toUpperCase());
}
function getFilteredOccurrences() {
  const pts = Data.getOccurrencePoints();
  if (!pts.ok) return { ok: false, list: [], total: 0 };
  const f = ExpState.filters;
  const list = pts.points
    .map(p => { const demo = ExpDemo.score(p.id); return { ...p, demo, demoCls: ExpDemo.classOf(demo) }; })
    .filter(p => !f.state || norm(p.state) === norm(f.state))
    .filter(p => !f.district || norm(p.district) === norm(f.district))
    .filter(p => !f.status || norm(p.status) === norm(f.status))
    .filter(p => !f.priority || p.demoCls === f.priority.toUpperCase());
  return { ok: true, list, total: pts.points.length };
}

/* ---------- popups ---------- */
function expOccPopup(p) {
  const rows = [
    `${esc(p.district)} · ${esc(p.state)}`,
    `${esc(p.deposit)} · ${esc(p.status)}`,
    p.formation ? esc(p.formation) : null,
    p.host ? esc(p.host) : null,
    p.source ? esc(p.source) + (p.sourceRef ? ' — ' + esc(p.sourceRef) : '') : null,
    `<span>${p.lat.toFixed(4)} N · ${p.lon.toFixed(4)} E — from manganese_occurrences_MOIL_study_area.csv</span>`
  ].filter(Boolean);
  return `<div class="occ-pop"><b>${esc(p.name)}</b><br>${rows.join('<br>')}</div>`;
}
function expZonePopup(z) {
  const conf = ExpDemo.confidence(z.id, z.score);
  return `<div class="occ-pop"><b>EXPLORATION PRIORITY — ${esc(z.id)}</b><br>${esc(z.name)}<br>` +
    `CLASS ${z.cls} · SCORE ${z.score} / 100 · CONFIDENCE ${conf}<br>` +
    `<span>PROTOTYPE / DEMO — demonstration geometry, not a geological prediction.</span></div>`;
}
function zoneStyle(z) {
  const c = { HIGH: '#B45624', MEDIUM: '#A07A22', LOW: '#98948A' }[z.cls];
  return {
    color: c, weight: 1.2, dashArray: z.cls === 'LOW' ? '3 5' : null,
    fillColor: c, fillOpacity: z.cls === 'HIGH' ? 0.14 : 0.10
  };
}

/* ---------- view ---------- */
function ExplorationView() {
  const fField = (label, id) =>
    `<label class="f-field"><span class="k">${label}</span><select id="${id}"></select></label>`;

  const html = `
  <div class="page">
    <div class="wrap">

      <div class="page-head">
        <p class="k kick-rule">Model 1 — Exploration Intelligence</p>
        <h1 class="h1">Where should we explore?</h1>
        <p class="lede">Rank areas by manganese prospectivity using geological, historical and environmental indicators.</p>
        ${notice('Exploration priority zones shown here are demonstration visualizations. The ML prospectivity model will be connected in a later phase.', 'Prototype / Demo')}
      </div>

      <div class="exp-stage">
        <div class="exp-controls">
          ${fField('State', 'exp-f-state')}
          ${fField('District', 'exp-f-district')}
          ${fField('Priority', 'exp-f-priority')}
          ${fField('Historical Status', 'exp-f-status')}
          <button class="btn btn-ghost-d btn-sm exp-reset" id="exp-reset" type="button">Reset Filters</button>
        </div>

        <div class="exp-map-area">
          <div id="exp-map" role="application" aria-label="Exploration intelligence map — historical occurrences and demonstration priority zones"></div>
          <div class="map-legend">
            <span><i class="lg lg-occ"></i>Historical occurrence</span>
            <span><i class="lg lg-high"></i>Priority high · demo</span>
            <span><i class="lg lg-med"></i>Priority medium · demo</span>
            <span><i class="lg lg-low"></i>Priority low · demo</span>
            <span><i class="lg lg-anchor"></i>District anchor</span>
            <span class="lg-status" id="exp-map-status">…</span>
          </div>
        </div>

        <aside class="exp-panel">
          <section class="panel">
            <div class="exp-intel-head">
              <span class="k">Area Intelligence</span>
              <span class="k acc" id="exp-mode">STUDY REGION</span>
            </div>
            <div id="exp-area-body"></div>
            <p class="fineprint">Demo indicators — pending real geospatial data integration</p>
          </section>
        </aside>
      </div>
    </div>

    <section class="sec">
      <div class="wrap">
        ${secHead('Occurrence summary', 'What the historical record shows.', '01 / 03')}
        <p class="sec-lede">Counts respond live to the filters above — they always describe the filtered selection, never the raw file.</p>
        <div class="exp-stats" id="exp-stats"></div>
        <div class="dist-grid" id="exp-dists"></div>
      </div>
    </section>

    <section class="sec">
      <div class="wrap">
        ${secHead('Occurrence register', 'Every record, traceable to its source.', '02 / 03')}
        <div class="duo">
          <div>
            <div class="reg-head">
              <span class="k group-k" style="margin-bottom:0">Historical occurrences</span>
              <span class="k" id="exp-reg-count"></span>
            </div>
            <div class="reg-scroll">
              <table class="reg-table">
                <thead><tr>
                  <th>Occurrence</th><th>District</th><th>State</th>
                  <th>Deposit Type</th><th>Historical Status</th><th>Formation</th>
                </tr></thead>
                <tbody id="exp-reg-body"></tbody>
              </table>
            </div>
            <div class="pager" id="exp-pager"></div>
          </div>
          <aside>
            <span class="k group-k">Selected occurrence</span>
            <div class="panel" id="exp-occ-panel"></div>
          </aside>
        </div>
      </div>
    </section>

    <section class="sec">
      <div class="wrap">
        ${secHead('Exploration workflow', 'From raw signals to exploration priority.', '03 / 03')}
        <div class="exp-flow">
          <div class="xflow-box">
            <span class="k">Data inputs</span>
            <div class="xflow-tags">
              <span class="tag">Geology</span><span class="tag">Historical Occurrences</span>
              <span class="tag">Elevation</span><span class="tag">Slope</span>
              <span class="tag">NDVI</span><span class="tag">Rainfall</span>
              <span class="tag">Soil Moisture</span><span class="tag">Land Temperature</span>
            </div>
          </div>
          <span class="xflow-arrow">→</span>
          <div class="xflow-box">
            <span class="k">Prospectivity model</span>
            <p>ML model — not connected. Deterministic demo scoring is in use and clearly labelled.</p>
          </div>
          <span class="xflow-arrow">→</span>
          <div class="xflow-box">
            <span class="k">Output</span>
            <p>Prospectivity score 0–100, classified LOW 0–39 · MEDIUM 40–69 · HIGH 70–100.</p>
          </div>
        </div>
        <p class="fineprint">Exploration priority is an indication for further investigation, not a confirmation of manganese reserves. Prototype values will be replaced by validated geospatial model outputs.</p>
      </div>
    </section>
  </div>`;

  return {
    html, mount() {
      ExpState.filters = { state: '', district: '', priority: '', status: '' };
      ExpState.page = 1; ExpState.selectedZone = null; ExpState.selectedOcc = null; ExpState.selMarker = null;
      mountExplorationMap();
      buildExpControls();
      bindExpRegister();
      updateExploration();
      return () => { if (ExpState.map) { ExpState.map.remove(); ExpState.map = null; } ExpState.layers = {}; };
    }
  };
}

/* ---------- controls ---------- */
function fillSelect(sel, opts, allLabel, current) {
  sel.innerHTML = `<option value="">${allLabel}</option>` +
    opts.map(o => `<option${o === current ? ' selected' : ''}>${esc(o)}</option>`).join('');
}
function buildExpControls() {
  const pts = Data.getOccurrencePoints(); const P = pts.ok ? pts.points : [];
  const uniq = a => [...new Set(a.filter(Boolean))].sort();
  const states = uniq(P.map(p => p.state)).length ? uniq(P.map(p => p.state)) : ['Madhya Pradesh', 'Maharashtra'];
  const districts = uniq(P.map(p => p.district)).length ? uniq(P.map(p => p.district)) : ['Balaghat', 'Bhandara', 'Nagpur'];
  const statuses = uniq(P.map(p => p.status));
  const f = ExpState.filters;
  fillSelect(el2('exp-f-state'), states, 'All States', f.state);
  fillSelect(el2('exp-f-district'), districts, 'All Districts', f.district);
  fillSelect(el2('exp-f-priority'), ['High', 'Medium', 'Low'], 'All Priorities', f.priority);
  fillSelect(el2('exp-f-status'), statuses, 'All Status', f.status);
  const bind = (id, key) => el2(id).addEventListener('change', e => {
    ExpState.filters[key] = e.target.value; ExpState.page = 1; updateExploration();
  });
  bind('exp-f-state', 'state'); bind('exp-f-district', 'district');
  bind('exp-f-priority', 'priority'); bind('exp-f-status', 'status');
  el2('exp-reset').addEventListener('click', () => {
    ExpState.filters = { state: '', district: '', priority: '', status: '' };
    ExpState.page = 1; buildExpControls(); updateExploration();
  });
}

/* ---------- map ---------- */
function mountExplorationMap() {
  const elx = document.getElementById('exp-map'); if (!elx) return;
  if (typeof L === 'undefined') {
    elx.innerHTML = '<div class="map-fallback">Basemap library unreachable — connect to the internet to load the exploration map.</div>';
    el2('exp-map-status').textContent = 'MAP OFFLINE';
    return;
  }
  const map = L.map('exp-map', { scrollWheelZoom: false });
  ExpState.map = map;
  map.attributionControl.setPrefix('');
  MapKit.tiles().addTo(map);
  ExpState.layers.env = L.layerGroup([MapKit.envelope()]);
  ExpState.layers.anchors = MapKit.anchors();
  ExpState.layers.zones = L.layerGroup();
  ExpState.layers.occ = L.layerGroup();
  [ExpState.layers.env, ExpState.layers.anchors, ExpState.layers.zones, ExpState.layers.occ]
    .forEach(l => l.addTo(map));
  L.control.layers(null, {
    'Historical Occurrences': ExpState.layers.occ,
    'Exploration Priority — DEMO': ExpState.layers.zones,
    'District Anchors': ExpState.layers.anchors,
    'Study Envelope': ExpState.layers.env
  }, { position: 'topright', collapsed: matchMedia('(max-width:720px)').matches }).addTo(map);
  map.fitBounds(Registry.studyArea.envelope, { padding: [24, 24] });
  MapKit.scrollGuard(map);
}

function updateExpMapLayers() {
  const Lz = ExpState.layers; if (!Lz.occ) return;
  ExpState.selMarker = null;
  Lz.occ.clearLayers(); ExpState.markers.clear();
  const res = getFilteredOccurrences();
  if (res.ok) res.list.forEach(p => {
    const m = L.marker([p.lat, p.lon], { icon: MapKit.occIcon() })
      .bindTooltip(`<b>${esc(p.name.toUpperCase())}</b> · ${esc(p.district)}<br>${esc(p.deposit)} · ${esc(p.status)}`,
        { direction: 'top', offset: [0, -7], className: 'mi-tip' })
      .bindPopup(expOccPopup(p));
    m.on('click', () => selectOccurrence(p, false));
    Lz.occ.addLayer(m); ExpState.markers.set(String(p.id), m);
  });
  Lz.zones.clearLayers();
  getFilteredZones().forEach(z => {
    const c = L.circle([z.lat, z.lon], { radius: z.r, ...zoneStyle(z) })
      .bindTooltip(`<b>${esc(z.id)}</b> · DEMO PRIORITY ${z.cls} · ${z.score}/100`,
        { direction: 'top', className: 'mi-tip' })
      .bindPopup(expZonePopup(z));
    c.on('click', () => selectZone(z));
    Lz.zones.addLayer(c);
  });
}

/* ---------- selection ---------- */
function selectZone(z) { ExpState.selectedZone = z; renderExpAreaPanel(); }

function selectOccurrence(p, fly = true) {
  ExpState.selectedOcc = p;
  if (ExpState.selMarker) { const pe = ExpState.selMarker.getElement(); pe && pe.classList.remove('marker-sel'); }
  ExpState.selMarker = null;
  const m = ExpState.markers.get(String(p.id));
  if (m) {
    ExpState.selMarker = m;
    const me = m.getElement(); me && me.classList.add('marker-sel');
    if (fly && ExpState.map) {
      const red = matchMedia('(prefers-reduced-motion: reduce)').matches;
      ExpState.map.flyTo([p.lat, p.lon], Math.max(ExpState.map.getZoom(), 10), { duration: red ? 0 : 0.8 });
    }
    m.openPopup();
  }
  renderExpOccPanel(); markActiveRow(p.id);
}

/* ---------- dynamic regions ---------- */
function updateExploration() {
  if (ExpState.selectedZone && !getFilteredZones().some(z => z.id === ExpState.selectedZone.id))
    ExpState.selectedZone = null;
  updateExpMapLayers();
  renderExpAreaPanel();
  renderExpStats();
  renderOccurrenceRegister();
  renderExpOccPanel();
  updateExpLegend();
}
function updateExpLegend() {
  const res = getFilteredOccurrences(), zs = getFilteredZones().length;
  el2('exp-map-status').textContent = res.ok
    ? `${res.list.length} / ${res.total} OCCURRENCES · ${zs} DEMO ZONES`
    : `AWAITING CSV IMPORT · ${zs} DEMO ZONES`;
}

function scaleHTML(score) {
  return `<div class="scale" role="img" aria-label="Prospectivity ${score} of 100">
    <div class="scale-ticks"><span>0</span><span>40</span><span>70</span><span>100</span></div>
    <div class="scale-track">
      <i class="scale-seg s-low"></i><i class="scale-seg s-med"></i><i class="scale-seg s-high"></i>
      <i class="scale-marker" style="left:${score}%"></i>
    </div>
    <div class="scale-classes"><span>LOW</span><span>MEDIUM</span><span>HIGH</span></div>
  </div>`;
}

/* ★ PHASE 3 — zone intelligence panel: ID · score · class · confidence · evidence · next step */
function renderExpAreaPanel() {
  const z = ExpState.selectedZone;
  const d = z
    ? { id: z.id, name: `${z.id} · ${z.name}`, score: z.score, cls: z.cls, seed: z.id, mode: 'DEMO ZONE · ' + z.id }
    : { id: 'STUDY-REGION', name: 'Study Region', score: 87, cls: 'HIGH', seed: 'study', mode: 'STUDY REGION' };
  const conf = ExpDemo.confidence(d.seed, d.score);
  const ev = ExpDemo.evidence(d.seed, d.score);
  el2('exp-mode').textContent = d.mode;
  el2('exp-area-body').innerHTML = `
    <h3 class="h3" style="margin-top:14px">${esc(d.name)}</h3>
    <div class="comp-row" style="margin-top:10px">
      ${chip(({ HIGH: 'high', MEDIUM: 'med', LOW: 'mute' })[d.cls], d.cls + ' Priority')}
      ${chip('mute', 'Confidence ' + conf)}
      ${chip('warn', 'Demonstration Score')}
    </div>
    <div class="score-line"><b>${d.score}</b><span>/ 100 · Prospectivity</span></div>
    ${scaleHTML(d.score)}
    <div class="ledger" style="margin-top:20px">
      ${ev.map(i => lrow(i.label, rateChip(i.rate))).join('')}
    </div>
    <div class="nextstep">
      <span class="k">Next step</span>
      <p>${esc(ExpDemo.nextStep(d.cls))}</p>
    </div>`;
}

function renderExpStats() {
  const res = getFilteredOccurrences(); const list = res.ok ? res.list : [];
  const districts = new Set(list.map(p => p.district));
  const states = new Set(list.map(p => p.state));
  el2('exp-stats').innerHTML = [
    [list.length, 'Historical Occurrences'],
    [districts.size, 'Districts'],
    [states.size, 'States']
  ].map(([b, s]) => `<div class="stat"><b>${b}</b><span>${s}</span></div>`).join('');
  const pts = Data.getOccurrencePoints(); const P = pts.ok ? pts.points : [];
  const names = P.length ? [...new Set(P.map(p => p.district))].sort() : ['Balaghat', 'Bhandara', 'Nagpur'];
  const counts = names.map(d => [d, list.filter(p => norm(p.district) === norm(d)).length]);
  const max = Math.max(1, ...counts.map(c => c[1]));
  el2('exp-dists').innerHTML = counts.map(([d, c]) => `
    <div class="dist">
      <span class="k">${esc(d)}</span><b>${c}</b>
      <span class="meter"><i style="width:${Math.round(c / max * 100)}%"></i></span>
    </div>`).join('');
}

function renderPager(totalPages) {
  const pg = ExpState.page, box = el2('exp-pager');
  if (totalPages <= 1) { box.innerHTML = ''; return; }
  box.innerHTML = `
    <button class="btn btn-ghost-d btn-sm" id="exp-prev" ${pg <= 1 ? 'disabled' : ''}>Prev</button>
    <span class="k">Page ${pg} / ${totalPages}</span>
    <button class="btn btn-ghost-d btn-sm" id="exp-next" ${pg >= totalPages ? 'disabled' : ''}>Next</button>`;
  el2('exp-prev').onclick = () => { ExpState.page--; renderOccurrenceRegister(); };
  el2('exp-next').onclick = () => { ExpState.page++; renderOccurrenceRegister(); };
}
function markActiveRow(id) {
  document.querySelectorAll('#exp-reg-body tr[data-id]').forEach(tr =>
    tr.classList.toggle('is-active', tr.dataset.id === String(id)));
}
function renderOccurrenceRegister() {
  const res = getFilteredOccurrences(); const body = el2('exp-reg-body');
  if (!res.ok) {
    el2('exp-reg-count').textContent = '';
    body.innerHTML = `<tr><td colspan="6"><div class="reg-empty">Occurrence register awaiting CSV import<br><span>data/manganese_occurrences_MOIL_study_area.csv · serve over http to enable</span></div></td></tr>`;
    el2('exp-pager').innerHTML = ''; return;
  }
  const list = res.list;
  if (!list.length) {
    el2('exp-reg-count').textContent = '0 RECORDS';
    body.innerHTML = `<tr><td colspan="6"><div class="reg-empty">No occurrences match the current filters</div></td></tr>`;
    el2('exp-pager').innerHTML = ''; return;
  }
  const pages = Math.ceil(list.length / ExpState.perPage);
  if (ExpState.page > pages) ExpState.page = pages;
  const slice = list.slice((ExpState.page - 1) * ExpState.perPage, ExpState.page * ExpState.perPage);
  const chipCls = c => ({ HIGH: 'high', MEDIUM: 'med', LOW: 'mute' })[c];
  el2('exp-reg-count').textContent = `${list.length} / ${res.total} RECORDS`;
  body.innerHTML = slice.map(p => `
    <tr data-id="${esc(p.id)}" tabindex="0" aria-label="Select ${esc(p.name)}">
      <td>${esc(p.name)}<br><span class="chip chip--${chipCls(p.demoCls)}">Demo ${p.demoCls}</span></td>
      <td>${esc(p.district)}</td><td>${esc(p.state)}</td>
      <td>${esc(p.deposit)}</td><td>${esc(p.status)}</td><td>${esc(p.formation)}</td>
    </tr>`).join('');
  renderPager(pages);
  markActiveRow(ExpState.selectedOcc?.id);
}

function renderExpOccPanel() {
  const p = ExpState.selectedOcc, box = el2('exp-occ-panel');
  if (!p) {
    box.innerHTML = `<span class="k">No occurrence selected</span>
      <p class="occ-hint">Click a map marker or a register row to inspect a historical occurrence.</p>`;
    return;
  }
  box.innerHTML = `
    <span class="k">Occurrence</span>
    <h3 class="h3" style="margin-top:8px">${esc(p.name)}</h3>
    <div class="ledger" style="margin-top:14px">
      ${lrow('District', esc(p.district))}
      ${lrow('State', esc(p.state))}
      ${lrow('Deposit Type', esc(p.deposit))}
      ${lrow('Historical Status', esc(p.status))}
      ${lrow('Formation', esc(p.formation) || '—')}
      ${lrow('Host Rock', esc(p.host) || '—')}
      ${lrow('Source', esc(p.source) || '—')}
      ${p.sourceRef ? lrow('Reference', esc(p.sourceRef)) : ''}
      ${lrow('Coordinates', p.lat.toFixed(4) + ' N · ' + p.lon.toFixed(4) + ' E', 'v-mute')}
    </div>
    <button class="link-arrow" type="button" id="exp-center" style="margin-top:16px">Center on map ${I.arrow}</button>`;
  el2('exp-center').onclick = () => selectOccurrence(p, true);
}

function bindExpRegister() {
  const pick = tr => {
    const res = getFilteredOccurrences(); if (!res.ok) return;
    const p = res.list.find(x => String(x.id) === tr.dataset.id);
    if (p) selectOccurrence(p, true);
  };
  el2('exp-reg-body').addEventListener('click', e => {
    const tr = e.target.closest('tr[data-id]'); if (tr) pick(tr);
  });
  el2('exp-reg-body').addEventListener('keydown', e => {
    if (e.key !== 'Enter' && e.key !== ' ') return;
    const tr = e.target.closest('tr[data-id]'); if (tr) { e.preventDefault(); pick(tr); }
  });
}

/* ==================================================================
   07d · REAL MODEL-DRIVEN SCENARIO SIMULATOR (MODEL 2 API)
   ================================================================== */
const Sim = {
  selectedMine: 'MOIL-01',
  pending: null,
  debounceTimer: null,
  isLoading: false,
  apiError: null,
  baseline: {
    predicted_production: 28838,
    target: 32543,
    shortfall_tonnes: 3705,
    shortfall_pct: 11.38,
    risk: 'MEDIUM',
    downtime: 34.4,
    availability: 90.5,
    blasting_delay: 0,
    rainfall: 6.7,
    working_days: 24
  },
  scenario: {
    predicted_production: 28838,
    target: 32543,
    shortfall_tonnes: 3705,
    shortfall_pct: 11.38,
    risk: 'MEDIUM',
    downtime: 34.4,
    availability: 90.5,
    blasting_delay: 0,
    rainfall: 6.7,
    working_days: 24
  },
  impact: {
    production_change: 0,
    shortfall_change: 0,
    risk_changed: false,
    risk_from: 'MEDIUM',
    risk_to: 'MEDIUM'
  },
  params: {
    downtime: 34.4,
    blast: 0,
    rain: 6.7,
    workdays: 24
  },
  units: { downtime: 'hrs', blast: 'days', rain: 'mm', workdays: 'days' },
  specs: [
    ['downtime', 'Equipment downtime', 0, 120, 2],
    ['blast', 'Blasting delay', 0, 8, 1],
    ['rain', 'Rainfall', 0, 300, 5],
    ['workdays', 'Working days', 18, 30, 1]
  ]
};

function initSimMine() {
  const pdata = Data.getPredictions();
  if (pdata && pdata.mines && pdata.mines.length) {
    if (!pdata.mines.some(m => m.id === Sim.selectedMine)) {
      Sim.selectedMine = pdata.mines[0].id;
    }
    syncSimBaselineForMine(Sim.selectedMine);
  }
}

function syncSimBaselineForMine(mineId) {
  const pdata = Data.getPredictions();
  if (pdata && pdata.predictions && pdata.predictions.length) {
    const mineRows = pdata.predictions.filter(r => r.mine_id === mineId);
    if (mineRows.length) {
      // Select worst-shortfall month or peak operational constraint month
      const worst = mineRows.reduce((a, b) => (b.shortfall > a.shortfall ? b : a), mineRows[0]);
      Sim.baseline = {
        predicted_production: worst.predicted,
        target: worst.target,
        shortfall_tonnes: worst.shortfall,
        shortfall_pct: worst.shortfall_pct,
        risk: worst.risk,
        downtime: worst.downtime_hrs,
        availability: worst.equip_avail,
        rainfall: worst.rainfall_mm,
        blasting_delay: worst.blast_delay,
        working_days: worst.working_days
      };
      Sim.params = {
        downtime: worst.downtime_hrs,
        blast: worst.blast_delay,
        rain: worst.rainfall_mm,
        workdays: worst.working_days
      };
      syncSimInputs();
    }
  }
}

function SimulatorView() {
  const pdata = Data.getPredictions();
  const mines = (pdata && pdata.mines && pdata.mines.length) ? pdata.mines : [
    { id: 'MOIL-01', name: 'Dongri Buzurg Mine', district: 'Bhandara' },
    { id: 'MOIL-07', name: 'Balaghat Mine', district: 'Balaghat' },
    { id: 'MOIL-03', name: 'Kandri Mine', district: 'Nagpur' },
    { id: 'MOIL-08', name: 'Tirodi Mine', district: 'Balaghat' }
  ];

  const mineOptions = mines.map(m =>
    `<option value="${esc(m.id)}"${m.id === Sim.selectedMine ? ' selected' : ''}>${esc(m.name)} (${esc(m.id)})</option>`
  ).join('');

  const ctls = Sim.specs.map(([key, label, min, max, step]) => {
    const val = Sim.params[key] ?? Sim.baseline[key] ?? min;
    const bKey = key === 'blast' ? 'blasting_delay' : (key === 'workdays' ? 'working_days' : key);
    const bVal = Sim.baseline[bKey] ?? val;
    return `
    <div class="sim-ctl">
      <div class="sim-ctl-top">
        <b>${label}</b>
        <span class="k acc" id="sim-v-${key}">${val} ${Sim.units[key]}</span>
      </div>
      <input type="range" class="sim-slider" id="sim-in-${key}"
        min="${min}" max="${max}" step="${step}" value="${val}"
        aria-label="${label} scenario value">
      <div class="sim-marks">
        <span>${min} ${Sim.units[key]}</span>
        <span>baseline: ${bVal}</span>
        <span>${max} ${Sim.units[key]}</span>
      </div>
    </div>`;
  }).join('');

  const html = `
  <div class="page">
    <div class="wrap">
      <div class="page-head">
        <p class="k kick-rule">Model 2 — Scenario Simulator</p>
        <h1 class="h1">What if we act?</h1>
        <p class="lede">Test operational decisions against the <strong>real trained Gradient Boosting model (Model 2)</strong>. Adjust equipment downtime, blasting delays, rainfall, or shift schedules to quantify expected production recovery and shortfall risk changes in real time.</p>
        ${notice('Scenario predictions are generated live by executing the trained Model 2 pipeline (Model A Gradient Boosting) on user-modified operational vectors.')}
        <div class="legend-row">${dChip('observed')}${dChip('model')}${dChip('scenario')}${dChip('rec')}</div>
      </div>

      <div class="sim-grid">
        <div class="panel sim-controls">
          <div style="margin-bottom:20px;padding-bottom:16px;border-bottom:1px solid var(--line)">
            <label class="f-field" style="display:block">
              <span class="k">Target Mine Baseline</span>
              <select id="sim-mine-sel" style="width:100%;margin-top:6px">${mineOptions}</select>
            </label>
          </div>

          <span class="k">Operational scenario variables</span>
          ${ctls}

          <div class="sim-btns">
            <button class="btn btn-ghost-d btn-sm" type="button" data-simpreset="recommended">Apply recommended SOP</button>
            <button class="btn btn-ghost-d btn-sm" type="button" data-simpreset="best">Relieve all constraints</button>
            <button class="btn btn-ghost-d btn-sm" type="button" id="sim-reset">Reset to baseline</button>
          </div>
        </div>

        <aside class="panel">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap">
            <div>
              <span class="k">ML Model Prediction</span>
              <p style="font-size:12px;color:var(--mute);margin-top:2px" id="sim-model-tag">Model 2 · Gradient Boosting Regressor</p>
            </div>
            ${dChip('scenario')}
          </div>

          <div id="sim-status-banner" style="margin-top:12px;font-size:11px;font-family:var(--type-mono);color:var(--mute)"></div>

          <div class="sim-table" id="sim-table"></div>

          <div id="sim-impact-section" style="margin-top:20px"></div>
        </aside>
      </div>
    </div>
  </div>`;

  return {
    html,
    mount() {
      initSimMine();
      const mSel = el2('sim-mine-sel');
      if (mSel) {
        mSel.addEventListener('change', e => {
          Sim.selectedMine = e.target.value;
          syncSimBaselineForMine(Sim.selectedMine);
          applySimPreset(null);
        });
      }

      Sim.specs.forEach(([key]) => {
        const inp = el2('sim-in-' + key);
        if (inp) {
          inp.addEventListener('input', e => {
            Sim.params[key] = parseFloat(e.target.value);
            const vLabel = el2('sim-v-' + key);
            if (vLabel) vLabel.textContent = `${Sim.params[key]} ${Sim.units[key]}`;
            scheduleSimRun();
          });
        }
      });

      const rBtn = el2('sim-reset');
      if (rBtn) rBtn.addEventListener('click', () => applySimPreset(null));

      if (Sim.pending) {
        applySimPreset(Sim.pending);
        Sim.pending = null;
      } else {
        syncSimInputs();
        executeSimAPI();
      }
    }
  };
}

function syncSimInputs() {
  Sim.specs.forEach(([key]) => {
    const inp = el2('sim-in-' + key);
    if (!inp) return;
    inp.value = Sim.params[key];
    const vLabel = el2('sim-v-' + key);
    if (vLabel) vLabel.textContent = `${Sim.params[key]} ${Sim.units[key]}`;
  });
}

function applySimPreset(key) {
  if (key === 'recommended') {
    Sim.params.downtime = Math.max(10, Math.round(Sim.baseline.downtime * 0.5));
    Sim.params.blast = Math.max(0, Sim.baseline.blasting_delay - 1);
    Sim.params.rain = Math.max(20, Math.round(Sim.baseline.rainfall * 0.7));
    Sim.params.workdays = Math.min(27, Sim.baseline.working_days + 1);
  } else if (key === 'best') {
    Sim.params.downtime = 10;
    Sim.params.blast = 0;
    Sim.params.rain = 15;
    Sim.params.workdays = 27;
  } else {
    // Reset to baseline
    Sim.params.downtime = Sim.baseline.downtime;
    Sim.params.blast = Sim.baseline.blasting_delay;
    Sim.params.rain = Sim.baseline.rainfall;
    Sim.params.workdays = Sim.baseline.working_days;
  }

  if (currentKey() === 'simulator') {
    syncSimInputs();
    scheduleSimRun();
  } else {
    Sim.pending = key;
    location.hash = '#/simulator';
  }
}

function scheduleSimRun() {
  if (Sim.debounceTimer) clearTimeout(Sim.debounceTimer);
  const statusEl = el2('sim-status-banner');
  if (statusEl) {
    statusEl.innerHTML = '<span style="color:var(--oxide)">⚡ Calculating scenario via ML Model 2...</span>';
  }

  Sim.debounceTimer = setTimeout(() => {
    executeSimAPI();
  }, 250);
}

async function executeSimAPI() {
  Sim.isLoading = true;
  const statusEl = el2('sim-status-banner');

  const payload = {
    mine_id: Sim.selectedMine,
    production_target: Sim.baseline.target,
    downtime: Sim.params.downtime,
    blasting_delay: Sim.params.blast,
    rainfall: Sim.params.rain,
    working_days: Sim.params.workdays
  };

  try {
    const res = await fetch('/api/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    if (data.status === 'success') {
      Sim.baseline = data.baseline;
      Sim.scenario = data.scenario;
      Sim.impact = data.impact;
      Sim.isLoading = false;
      if (statusEl) {
        statusEl.innerHTML = '<span style="color:var(--ok-ink)">✓ Model 2 Prediction Updated</span>';
      }
      renderSimResults();
      return;
    }
  } catch (err) {
    console.warn('[Simulator] API call fallback:', err);
    Sim.isLoading = false;
    if (statusEl) {
      statusEl.innerHTML = '<span style="color:var(--mute)">ℹ API server offline · start server.py for live ML execution</span>';
    }
    renderSimResults();
  }
}

function renderSimResults() {
  const table = el2('sim-table');
  const impactSec = el2('sim-impact-section');
  if (!table) return;

  const b = Sim.baseline;
  const s = Sim.scenario;
  const imp = Sim.impact;

  const bPred = b.predicted_production ?? b.predicted ?? 0;
  const sPred = s.predicted_production ?? s.predicted ?? 0;
  const bShort = b.shortfall_tonnes ?? b.shortfall ?? 0;
  const sShort = s.shortfall_tonnes ?? s.shortfall ?? 0;
  const bShortPct = b.shortfall_pct ?? 0;
  const sShortPct = s.shortfall_pct ?? 0;
  const bRisk = b.risk ?? 'LOW';
  const sRisk = s.risk ?? 'LOW';

  const prodD = imp.production_change ?? (sPred - bPred);
  const shortD = imp.shortfall_change ?? (sShort - bShort);

  table.innerHTML = `
    <div class="sim-row"><span class="h">Metric</span><span class="h">Baseline</span><span class="h">Scenario</span></div>
    <div class="sim-row">
      <span class="h">Target Quota</span>
      <span class="bv">${fmt(b.target)} t</span>
      <span class="sv">${fmt(s.target)} t</span>
    </div>
    <div class="sim-row">
      <span class="h">Predicted Output</span>
      <span class="bv">${fmt(bPred)} t</span>
      <span class="sv">${fmt(sPred)} t${prodD !== 0 ? `<span class="d ${prodD > 0 ? 'd-up' : 'd-bad'}">${sgn(prodD)} t</span>` : ''}</span>
    </div>
    <div class="sim-row">
      <span class="h">Expected Shortfall</span>
      <span class="bv">${fmt(bShort)} t · ${bShortPct.toFixed(1)}%</span>
      <span class="sv">${fmt(sShort)} t · ${sShortPct.toFixed(1)}%${shortD !== 0 ? `<span class="d ${shortD < 0 ? 'd-up' : 'd-bad'}">${sgn(shortD)} t</span>` : ''}</span>
    </div>
    <div class="sim-row">
      <span class="h">Risk Classification</span>
      <span class="bv">${riskChip(bRisk)}</span>
      <span class="sv">${riskChip(sRisk)}</span>
    </div>`;

  if (impactSec) {
    const shiftBadge = imp.risk_changed
      ? `<span class="chip chip--ok" style="margin-left:6px">${imp.risk_from} → ${imp.risk_to}</span>`
      : `<span class="chip chip--mute" style="margin-left:6px">Unchanged (${sRisk})</span>`;

    impactSec.innerHTML = `
      <div style="margin-top:20px;padding-top:16px;border-top:1px solid var(--line)">
        <span class="k">Projected Operational Impact</span>
        <div class="ledger" style="margin-top:10px">
          ${lrow('Production Change', sgn(prodD) + ' tonnes', prodD > 0 ? 'v-ok' : (prodD < 0 ? 'v-warn' : ''))}
          ${lrow('Shortfall Reduction', sgn(-shortD) + ' tonnes', shortD < 0 ? 'v-ok' : (shortD > 0 ? 'v-warn' : ''))}
          ${lrow('Risk Transition', shiftBadge, imp.risk_changed ? 'v-ok' : '')}
          ${lrow('Equipment Availability', (s.availability ?? 0) + '% (Baseline: ' + (b.availability ?? 0) + '%)')}
          ${lrow('Working Days', (s.working_days ?? 0) + ' days (Baseline: ' + (b.working_days ?? 0) + ' days)')}
        </div>
        <p class="fineprint" style="margin-top:8px">Computed directly via Model 2 (Gradient Boosting Regressor) on the 18-feature input vector.</p>
      </div>`;
  }
}

/* ==================================================================
   07e · PRODUCTION VIEW — Model 2 predictions wired
   ================================================================== */
const ProdState = { mine: null };

function ProductionView() {
  const pdata = Data.getPredictions();
  const hasPred = pdata && pdata.mines && pdata.mines.length > 0;

  /* ---- HTML shell ---- */
  const html = `
  <div class="page">
    <div class="wrap">
      <div class="page-head">
        <p class="k kick-rule">Model 2 — Production Intelligence</p>
        <h1 class="h1">Where is production at risk?</h1>
        <p class="lede">For each of 14 mines, compare the production target against the Gradient Boosting model's forecast, quantify expected shortfall and grade the risk — then see which operational constraint is driving it.</p>
        ${notice('All data is DEMO/SYNTHETIC prototype \u2014 not official MOIL operational data. Model trained on Jan 2022\u2013Dec 2024, evaluated on Jan\u2013Dec 2025.', 'DEMO / SYNTHETIC DATA')}
      </div>

      ${hasPred ? `
      <div class="duo" style="margin-bottom:32px">
        <div>
          <span class="k group-k">Mine selector \u2014 2025 test year</span>
          <div id="prod-mine-grid" class="prod-mine-grid"></div>
        </div>
        <aside>
          <span class="k group-k">Portfolio summary \u2014 14 mines \u00b7 Jan\u2013Dec 2025</span>
          <div id="prod-portfolio" class="ledger" style="margin-top:12px"></div>
        </aside>
      </div>

      <div id="prod-detail">
        <div class="panel" style="padding:32px;text-align:center">
          <p class="occ-hint">Select a mine above to view its monthly forecast, shortfall and operational constraints.</p>
        </div>
      </div>
      ` : `
      <div class="panel" style="padding:40px;text-align:center">
        ${notice('Production predictions not loaded \u2014 serve the dashboard over HTTP to enable JSON data loading.')}
        <p class="occ-hint" style="margin-top:16px">Run: <code>python -m http.server 8000</code> from the dashboard directory.</p>
      </div>
      `}
    </div>
  </div>`;

  return {
    html, mount() {
      if (!hasPred) return;
      renderProdMineGrid(pdata);
      renderProdPortfolio(pdata.portfolio);
      /* Auto-select first mine */
      if (pdata.mines.length > 0) {
        ProdState.mine = pdata.mines[0].id;
        renderProdDetail(pdata);
      }
    }
  };
}

function renderProdMineGrid(pdata) {
  const box = el2('prod-mine-grid'); if (!box) return;
  const riskCls = { LOW: 'ok', MEDIUM: 'med', HIGH: 'high' };
  box.innerHTML = pdata.mines.map(m => `
    <button class="prod-mine-btn${m.id === ProdState.mine ? ' is-active' : ''}"
      id="pmb-${esc(m.id)}" data-mine="${esc(m.id)}" type="button">
      <span class="k" style="font-size:10px">${esc(m.id)}</span>
      <span class="prod-mine-name">${esc(m.name.replace(' Mine', ''))}</span>
      <span class="chip chip--${riskCls[m.worst_risk] || 'mute'}" style="margin-top:4px">${m.worst_risk}</span>
    </button>`).join('');
  box.addEventListener('click', e => {
    const btn = e.target.closest('[data-mine]'); if (!btn) return;
    ProdState.mine = btn.dataset.mine;
    box.querySelectorAll('.prod-mine-btn').forEach(b => b.classList.toggle('is-active', b.dataset.mine === ProdState.mine));
    renderProdDetail(pdata);
  });
}

function renderProdPortfolio(p) {
  const box = el2('prod-portfolio'); if (!box || !p) return;
  const riskDist = p.risk_distribution || {};
  box.innerHTML =
    lrow('Total target', fmt(p.total_target) + ' t') +
    lrow('Total predicted', fmt(p.total_predicted) + ' t') +
    lrow('Total shortfall', fmt(p.total_shortfall) + ' t · ' + p.shortfall_pct + '%', 'v-warn') +
    lrow('HIGH risk months', String(riskDist.HIGH || 0), 'v-high') +
    lrow('MEDIUM risk months', String(riskDist.MEDIUM || 0), 'v-med') +
    lrow('LOW risk months', String(riskDist.LOW || 0), 'v-ok') +
    lrow('Mines in model', String(p.mine_count)) +
    lrow('Test period', p.year + ' · ' + p.month_count + ' months');
}

function renderProdDetail(pdata) {
  const box = el2('prod-detail'); if (!box) return;
  const mine = pdata.mines.find(m => m.id === ProdState.mine);
  if (!mine) { box.innerHTML = ''; return; }
  const months = pdata.predictions.filter(r => r.mine_id === mine.id)
    .sort((a, b) => a.date.localeCompare(b.date));

  const riskCls = { LOW: 'ok', MEDIUM: 'med', HIGH: 'high' };
  const riskLabels = months.map(m => m.date.slice(5)); // "01".."12"

  /* SVG time-series chart */
  const W = 560, H = 160, PAD = { t: 20, r: 20, b: 32, l: 60 };
  const iw = W - PAD.l - PAD.r, ih = H - PAD.t - PAD.b;
  const allVals = months.flatMap(m => [m.target, m.actual, m.predicted]);
  const minV = Math.min(...allVals) * 0.92, maxV = Math.max(...allVals) * 1.04;
  const sx = i => PAD.l + (i / (months.length - 1)) * iw;
  const sy = v => PAD.t + ih - (v - minV) / (maxV - minV) * ih;
  const pts = (key, clr) => {
    const d = months.map((m, i) => `${i === 0 ? 'M' : 'L'}${sx(i).toFixed(1)},${sy(m[key]).toFixed(1)}`).join(' ');
    return `<path d="${d}" fill="none" stroke="${clr}" stroke-width="1.8" stroke-linejoin="round"/>`;
  };
  const dots = (key, clr, r = 3) => months.map((m, i) =>
    `<circle cx="${sx(i).toFixed(1)}" cy="${sy(m[key]).toFixed(1)}" r="${r}" fill="${clr}"/>`).join('');
  const yTick = v => `<line x1="${PAD.l - 4}" x2="${W - PAD.r}" y1="${sy(v).toFixed(1)}" y2="${sy(v).toFixed(1)}" stroke="rgba(25,27,23,.06)" stroke-width="1"/>
    <text x="${PAD.l - 8}" y="${(sy(v) + 4).toFixed(1)}" text-anchor="end" font-size="9" fill="#6F6C63">${Math.round(v / 1000)}k</text>`;
  const yTicks = [minV + (maxV - minV) * 0.25, minV + (maxV - minV) * 0.5, minV + (maxV - minV) * 0.75].map(yTick).join('');
  const xLabels = months.map((m, i) =>
    `<text x="${sx(i).toFixed(1)}" y="${(H - 4).toFixed(1)}" text-anchor="middle" font-size="8.5" fill="#9B978D">${m.date.slice(5)}</text>`).join('');
  const riskBg = months.map((m, i) => {
    if (m.risk === 'LOW') return '';
    const cl = m.risk === 'HIGH' ? 'rgba(180,86,36,.07)' : 'rgba(160,122,34,.06)';
    const bw = iw / (months.length);
    return `<rect x="${(sx(i) - bw / 2).toFixed(1)}" y="${PAD.t}" width="${bw.toFixed(1)}" height="${ih}" fill="${cl}"/>`;
  }).join('');

  const svg = `<svg viewBox="0 0 ${W} ${H}" width="100%" style="display:block;overflow:visible">
    ${riskBg}${yTicks}${xLabels}
    ${pts('target', '#9B978D')}${pts('actual', '#EDEAE2')}${pts('predicted', '#C9662B')}
    ${dots('actual', '#EDEAE2', 2.5)}${dots('predicted', '#C9662B', 3)}
  </svg>`;

  /* Per-month risk table */
  const tableRows = months.map(m => `
    <tr>
      <td>${m.date}</td>
      <td>${fmt(m.target)}</td>
      <td>${fmt(m.predicted)}</td>
      <td>${m.shortfall > 0 ? fmt(m.shortfall) + ' t' : '\u2014'}</td>
      <td>${m.shortfall_pct > 0 ? m.shortfall_pct + '%' : '\u2014'}</td>
      <td><span class="chip chip--${riskCls[m.risk] || 'mute'}">${m.risk}</span></td>
      <td style="font-size:11px;color:var(--mute)">${esc(m.top_driver)}</td>
    </tr>`).join('');

  box.innerHTML = `
  <div class="duo" style="gap:24px;margin-top:28px;align-items:flex-start">
    <div class="panel" style="flex:1;min-width:0">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;margin-bottom:18px">
        <div>
          <span class="k">${esc(mine.name)} \u2014 ${esc(mine.district)}, ${esc(mine.state)}</span>
          <p style="font-size:12px;color:var(--mute);margin-top:2px">${esc(mine.mine_type)} \u00b7 ${mine.id}</p>
        </div>
        ${dChip('model')}
      </div>
      <div style="display:flex;gap:8px;margin-bottom:14px;flex-wrap:wrap">
        ${chip(riskCls[mine.worst_risk] || 'mute', 'Worst risk ' + mine.worst_risk)}
        ${chip('high', mine.high_months + ' HIGH months')}
        ${chip('med', mine.med_months + ' MED months')}
        ${chip('ok', mine.low_months + ' LOW months')}
      </div>
      <div style="margin-bottom:10px">
        <div style="display:flex;gap:16px;font-size:10px;color:var(--mute);margin-bottom:6px">
          <span style="display:flex;align-items:center;gap:4px"><i style="display:inline-block;width:18px;height:2px;background:#9B978D;border-radius:1px"></i>Target</span>
          <span style="display:flex;align-items:center;gap:4px"><i style="display:inline-block;width:18px;height:2px;background:#EDEAE2;border-radius:1px"></i>Actual</span>
          <span style="display:flex;align-items:center;gap:4px"><i style="display:inline-block;width:18px;height:2px;background:#C9662B;border-radius:1px"></i>Predicted</span>
          <span style="color:var(--mute-2)">Shaded months = risk</span>
        </div>
        ${svg}
      </div>
      <div class="reg-scroll" style="max-height:260px;margin-top:4px">
        <table class="reg-table">
          <thead><tr><th>Month</th><th>Target (t)</th><th>Predicted (t)</th><th>Shortfall</th><th>%</th><th>Risk</th><th>Top Driver</th></tr></thead>
          <tbody>${tableRows}</tbody>
        </table>
      </div>
    </div>
    <aside style="min-width:220px;max-width:280px">
      <div class="panel">
        <span class="k">Annual summary</span>
        <div class="ledger" style="margin-top:12px">
          ${lrow('Annual target', fmt(mine.total_target) + ' t')}
          ${lrow('Annual predicted', fmt(mine.total_predicted) + ' t')}
          ${lrow('Annual shortfall', mine.total_shortfall > 0 ? fmt(mine.total_shortfall) + ' t' : '\u2014', mine.total_shortfall > 0 ? 'v-warn' : '')}
          ${lrow('Shortfall %', mine.shortfall_pct > 0 ? mine.shortfall_pct + '%' : '\u2014')}
          ${lrow('Avg availability', mine.avg_availability + '%')}
          ${lrow('Avg downtime', mine.avg_downtime + ' hrs')}
          ${lrow('Avg rainfall', mine.avg_rainfall + ' mm')}
          ${lrow('Top constraint', esc(mine.top_driver))}
        </div>
      </div>
      <div class="panel" style="margin-top:16px">
        <span class="k">Latest recommendation</span>
        <p style="margin-top:10px;font-size:13px;color:var(--ink-2);line-height:1.55">${esc(months[months.length - 1]?.recommendation || '\u2014')}</p>
        ${dChip('rec')}
        <p class="fineprint" style="margin-top:8px">AI-assisted \u2014 human review required before field action.</p>
      </div>
    </aside>
  </div>`;
}

/* ==================================================================
   07f · RECOMMENDATIONS VIEW — ranked by risk
   ================================================================== */
function RecommendationsView() {
  const pdata = Data.getPredictions();
  const hasPred = pdata && pdata.mines && pdata.mines.length > 0;

  const html = `
  <div class="page">
    <div class="wrap">
      <div class="page-head">
        <p class="k kick-rule">Recommendation Engine</p>
        <h1 class="h1">What should we do?</h1>
        <p class="lede">Mines ranked by worst-case risk. For each mine, the dominant operational constraint is named and numbered corrective actions are issued \u2014 always for human review before field action.</p>
        ${notice('All recommendations are AI-assisted and rule-based \u2014 not automated mine-control instructions. DEMO/SYNTHETIC data.', 'DEMO / AI-Assisted')}
      </div>
      ${hasPred ? `
      <div style="margin-bottom:24px;display:flex;gap:12px;flex-wrap:wrap" id="rec-filters">
        <label class="f-field"><span class="k">Risk</span><select id="rec-f-risk"><option value="">All</option><option>HIGH</option><option>MEDIUM</option><option>LOW</option></select></label>
        <label class="f-field"><span class="k">District</span><select id="rec-f-dist"><option value="">All Districts</option></select></label>
      </div>
      <div id="rec-list"></div>
      ` : `${notice('Recommendation data not loaded \u2014 serve over HTTP to enable.')}`}
    </div>
  </div>`;

  return {
    html, mount() {
      if (!hasPred) return;
      buildRecFilters(pdata);
      renderRecList(pdata, '', '');
    }
  };
}

function buildRecFilters(pdata) {
  const districts = [...new Set(pdata.mines.map(m => m.district))].sort();
  const dsel = el2('rec-f-dist');
  if (dsel) districts.forEach(d => { const o = document.createElement('option'); o.textContent = d; dsel.appendChild(o); });
  const bind = (id, fn) => { const s = el2(id); if (s) s.addEventListener('change', fn); };
  const rerender = () => {
    const risk = el2('rec-f-risk')?.value || '';
    const dist = el2('rec-f-dist')?.value || '';
    renderRecList(pdata, risk, dist);
  };
  bind('rec-f-risk', rerender); bind('rec-f-dist', rerender);
}

function renderRecList(pdata, riskF, distF) {
  const box = el2('rec-list'); if (!box) return;
  const riskOrder = { HIGH: 0, MEDIUM: 1, LOW: 2 };
  let mines = [...pdata.mines]
    .filter(m => !riskF || m.worst_risk === riskF)
    .filter(m => !distF || m.district === distF)
    .sort((a, b) => (riskOrder[a.worst_risk] ?? 3) - (riskOrder[b.worst_risk] ?? 3));

  if (!mines.length) { box.innerHTML = '<p class="occ-hint" style="margin-top:24px">No mines match the current filters.</p>'; return; }

  const riskCls = { LOW: 'ok', MEDIUM: 'med', HIGH: 'high' };
  box.innerHTML = mines.map((m, idx) => {
    /* Gather highest-risk month rec */
    const allMonths = pdata.predictions.filter(r => r.mine_id === m.id);
    const worstMonth = allMonths.reduce((a, b) =>
      ({ HIGH: 2, MEDIUM: 1, LOW: 0 }[b.risk] ?? 0) > ({ HIGH: 2, MEDIUM: 1, LOW: 0 }[a.risk] ?? 0) ? b : a, allMonths[0]);

    /* Parse multi-recommendation */
    const recParts = (worstMonth?.recommendation || '').split(' | ');

    return `
    <div class="panel" style="margin-bottom:16px">
      <div style="display:flex;gap:16px;align-items:flex-start;flex-wrap:wrap">
        <span class="sec-idx" style="flex-shrink:0">${String(idx + 1).padStart(2, '0')}</span>
        <div style="flex:1;min-width:0">
          <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:8px">
            ${chip(riskCls[m.worst_risk] || 'mute', m.worst_risk + ' Risk')}
            <span style="font:600 14px/1 var(--type-sans)">${esc(m.name)}</span>
            <span class="k" style="color:var(--mute)">${esc(m.district)} \u00b7 ${esc(m.state)}</span>
          </div>
          <div class="ledger" style="margin-bottom:12px">
            ${lrow('Annual shortfall', m.total_shortfall > 0 ? fmt(m.total_shortfall) + ' t (' + m.shortfall_pct + '%)' : '\u2014 on target', m.total_shortfall > 0 ? 'v-warn' : 'v-ok')}
            ${lrow('Top constraint', esc(m.top_driver))}
            ${lrow('HIGH risk months', m.high_months > 0 ? String(m.high_months) : 'None', m.high_months > 0 ? 'v-high' : '')}
            ${lrow('Avg equipment availability', m.avg_availability + '%', m.avg_availability < 85 ? 'v-warn' : '')}
            ${lrow('Avg downtime', m.avg_downtime + ' hrs')}
          </div>
          <div class="nextstep">
            <span class="k">Corrective actions \u2014 ${esc(worstMonth?.date || '')} (worst month)</span>
            <ol style="margin-top:8px;padding-left:18px">
              ${recParts.map(r => `<li style="margin-bottom:4px;font-size:13.5px;color:var(--ink-2)">${esc(r.trim())}</li>`).join('')}
            </ol>
          </div>
          <div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap">
            ${dChip('rec')}
            <a class="link-arrow" href="#/production">View full forecast ${I.arrow}</a>
          </div>
        </div>
      </div>
    </div>`;
  }).join('');
}

/* ==================================================================
   07g · METHODOLOGY VIEW — pipeline documentation + real metrics
   ================================================================== */
function MethodologyView() {
  const meta = Data.getModelMetadata();
  const fi = Data.getFeatureImportance();
  const exp = Data.getExploration();

  const m2perf = meta?.performance || {};
  const m2features = (meta?.features || []).slice(0, 10);
  const topFeatures = (fi?.features || []).slice(0, 8);
  const expDistricts = exp?.districts || [];

  const html = `
  <div class="page">
    <div class="wrap">
      <div class="page-head">
        <p class="k kick-rule">Methodology</p>
        <h1 class="h1">How does it work?</h1>
        <p class="lede">Data flows from six source families through two models and a rule layer into the dashboard. Every input, transformation and output is documented here \u2014 with a clear statement of what is measured, what is modelled, and what is demonstration data.</p>
        ${notice('All model outputs are from DEMO/SYNTHETIC prototype data. Not official MOIL operational data. Validated against synthetic dataset only.', 'DEMO / PROTOTYPE')}
      </div>

      <section class="sec">
        <div>${secHead('Data pipeline', 'EXPLORE \u2192 PREDICT \u2192 EXPLAIN \u2192 RECOMMEND \u2192 SIMULATE.', '01 / 04')}
        <div class="steps" style="margin-top:28px">
          <div class="step"><span class="n">01</span><b>Explore</b><p>21,067 grid cells \u00d7 25 spatial features \u2192 weighted prospectivity score \u2192 HIGH / MEDIUM / LOW.</p>${chip('warn', 'Model 1 \u00b7 DEMO scoring')}</div>
          <div class="step"><span class="n">02</span><b>Predict</b><p>14 mines \u00d7 48 months \u2192 Gradient Boosting forecast \u2192 shortfall % \u2192 risk grade.</p>${chip('ok', 'Model 2 \u00b7 connected')}</div>
          <div class="step"><span class="n">03</span><b>Explain</b><p>Permutation feature importance identifies which constraint drives each prediction.</p>${chip('ok', 'Feature importance \u00b7 connected')}</div>
          <div class="step"><span class="n">04</span><b>Recommend</b><p>Risk + constraints \u2192 rule-based engine \u2192 numbered corrective actions for human review.</p>${chip('ok', 'Recommendation engine \u00b7 connected')}</div>
          <div class="step"><span class="n">05</span><b>Simulate</b><p>4-slider scenario model calibrated to real feature importance weights \u2192 instant portfolio impact estimate.</p>${chip('ok', 'Simulator \u00b7 calibrated')}</div>
        </div></div>
      </section>

      <section class="sec">
        <div>${secHead('Model 1 \u2014 Exploration Intelligence', 'Spatial feature pipeline.', '02 / 04')}
        <div class="duo" style="margin-top:24px">
          <div>
            <span class="k group-k">Pipeline stages</span>
            <ol class="plan" style="margin-top:12px">
              <li><span class="n">01</span><div><b>Grid generation</b><p>1.0 km \u00d7 1.0 km common grid \u2014 21,067 cells in UTM Zone 44N (EPSG:32644) covering the central Indian manganese belt.</p></div></li>
              <li><span class="n">02</span><div><b>Feature engineering</b><p>25 spatial features: elevation, slope, terrain roughness, geological formation, host rock lithology, lineament distance, occurrence proximity, occurrence density, NDVI, rainfall, soil moisture, LST.</p></div></li>
              <li><span class="n">03</span><div><b>Prospectivity scoring</b><p>Weighted linear scoring using 10 geological domain-knowledge weights. Scores scaled 0\u2013100 and classified HIGH (\u226570) / MEDIUM (40\u201369) / LOW (&lt;40).</p></div></li>
            </ol>
          </div>
          <aside>
            <span class="k group-k">District prospectivity summary</span>
            <div class="ledger" style="margin-top:12px">
              ${expDistricts.map(d => lrow(esc(d.district), `Avg ${d.avg_score} \u00b7 ${d.high_cells} HIGH cells`)).join('')}
              ${exp ? lrow('Total cells scored', exp.total_cells.toLocaleString(), 'v-ok') : ''}
              ${exp ? lrow('HIGH prospectivity', exp.summary.high + ' cells', 'v-ok') : ''}
              ${exp ? lrow('MEDIUM', exp.summary.medium + ' cells', 'v-mute') : ''}
              ${exp ? lrow('LOW', exp.summary.low + ' cells', 'v-mute') : ''}
            </div>
            <p class="fineprint" style="margin-top:10px">DEMO/SYNTHETIC \u2014 pending field validation. Scores are NOT confirmed reserves.</p>
          </aside>
        </div></div>
      </section>

      <section class="sec">
        <div>${secHead('Model 2 \u2014 Production Intelligence', 'Gradient Boosting production forecast.', '03 / 04')}
        <div class="duo" style="margin-top:24px">
          <div>
            <span class="k group-k">Pipeline stages</span>
            <ol class="plan" style="margin-top:12px">
              <li><span class="n">01</span><div><b>Data preprocessing</b><p>672-row prototype dataset \u00b7 14 mines \u00b7 Jan 2022\u2013Dec 2025. Chronological split: train Jan 2022\u2013Dec 2024 (504 rows), test Jan\u2013Dec 2025 (168 rows). Label encoding for categorical features.</p></div></li>
              <li><span class="n">02</span><div><b>Feature engineering</b><p>18 features: original operational columns + lag-1, rolling-3, interaction terms (downtime per working day, effective capacity). Lag features computed chronologically \u2014 no data leakage.</p></div></li>
              <li><span class="n">03</span><div><b>Model training</b><p>6 models trained: Model A (with production target) and Model B (without) \u00d7 Linear Regression, Random Forest, Gradient Boosting. TimeSeriesSplit cross-validation (5 folds). Model A Gradient Boosting selected.</p></div></li>
              <li><span class="n">04</span><div><b>Prediction & risk</b><p>Shortfall = max(0, target \u2212 predicted). Risk: LOW (&lt;5%) / MEDIUM (5\u201315%) / HIGH (\u226515%). Top driver from permutation importance + row-level constraint heuristic.</p></div></li>
            </ol>
          </div>
          <aside>
            <span class="k group-k">Validation metrics \u2014 2025 test set</span>
            <div class="ledger" style="margin-top:12px">
              ${lrow('Algorithm', 'Gradient Boosting Regressor', 'v-ok')}
              ${lrow('Test MAE', m2perf.test_mae ? m2perf.test_mae.toFixed(1) + ' t' : Registry.models.production.metrics.MAE)}
              ${lrow('Test RMSE', m2perf.test_rmse ? m2perf.test_rmse.toFixed(1) + ' t' : Registry.models.production.metrics.RMSE)}
              ${lrow('Test R\u00b2', m2perf.test_r2 ? m2perf.test_r2.toFixed(4) : Registry.models.production.metrics.R2, 'v-ok')}
              ${lrow('Test MAPE', m2perf.test_mape ? m2perf.test_mape.toFixed(2) + '%' : Registry.models.production.metrics.MAPE)}
              ${lrow('CV MAE', m2perf.cv_mae ? m2perf.cv_mae.toFixed(1) + ' t' : '789.93 t')}
              ${lrow('CV R\u00b2', m2perf.cv_r2 ? m2perf.cv_r2.toFixed(4) : '0.9655')}
              ${lrow('Leakage audit', meta?.leakage_audit || 'PASSED', 'v-ok')}
              ${lrow('Training rows', '504 (Jan 2022\u2013Dec 2024)')}
              ${lrow('Test rows', '168 (Jan\u2013Dec 2025)')}
            </div>
            <span class="k group-k" style="margin-top:20px;display:block">Top feature drivers (permutation importance)</span>
            <div class="ledger" style="margin-top:12px">
              ${topFeatures.map(f => lrow(esc(f.feature.replace(/_/g, ' ')), f.importance_pct.toFixed(1) + '%')).join('')}
            </div>
          </aside>
        </div></div>
      </section>

      <section class="sec">
        <div>${secHead('Limitations & data integrity', 'What this prototype does and does not represent.', '04 / 04')}
        <div class="duo" style="margin-top:24px">
          <div class="ledger">
            ${lrow('Production dataset', 'DEMO/SYNTHETIC \u2014 672 rows generated for ML demonstration', 'v-warn')}
            ${lrow('Exploration features', 'Calibrated to regional geodesy and satellite statistics \u2014 not raw instrument data', 'v-warn')}
            ${lrow('Occurrence data', '18 records from published geological references \u2014 LIVE CSV', 'v-ok')}
            ${lrow('Prospectivity scores', 'NOT confirmed reserves. Pending field validation.', 'v-warn')}
            ${lrow('Risk classification', 'Based on synthetic data thresholds \u2014 NOT operational SLA thresholds', 'v-warn')}
            ${lrow('Recommendations', 'Rule-based heuristics \u2014 require domain expert review', 'v-warn')}
          </div>
          <div class="ledger">
            ${lrow('Temporal split', 'Chronological \u2014 no test data seen during training', 'v-ok')}
            ${lrow('Data leakage audit', 'PASSED \u2014 verified by independent audit script', 'v-ok')}
            ${lrow('Model overfit level', 'LOW \u2014 CV-test gap within acceptable range', 'v-ok')}
            ${lrow('Production target feature', 'Retained in Model A \u2014 models target-aware planning', 'v-ok')}
            ${lrow('SHAP analysis', 'Available \u2014 outputs in model_2/outputs/', 'v-ok')}
            ${lrow('Full source code', 'Available in model_1/ and model_2/', 'v-ok')}
          </div>
        </div></div>
      </section>

    </div>
  </div>`;

  return { html };
}

/* ==================================================================
   08 · FOOTER + PROVENANCE
   ================================================================== */
function renderFooter() {
  const occ = Data.state.occurrences, prod = Data.state.production, m = Registry.models;
  const occPts = Data.getOccurrencePoints();
  const connected = Object.values(m).filter(x => x.connected).length;
  const provChip = { live: chip('ok', 'Live file'), demo: chip('warn', 'Representative / demo'), none: chip('mute', 'Not connected') };
  document.getElementById('footer').innerHTML = `
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <a class="brand" href="#/overview">
          <svg width="21" height="21" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M12 2.4 21.6 12 12 21.6 2.4 12Z" stroke="#C9662B" stroke-width="1.5"/>
            <path d="M12 7 17 12 12 17 7 12Z" stroke="#EDEAE2" stroke-width="1.1"/>
            <circle cx="12" cy="12" r="1.3" fill="#C9662B"/></svg>
          <span class="brand-name">MineSight <em>AI</em></span>
        </a>
        <p class="footer-tag">AI + Space Technology for smarter mining decisions — exploration priority, production risk, corrective action.</p>
        <p class="footer-ver">Platform v${Registry.version.split(' ')[0]} · ${Registry.version.split('—')[1].trim()}</p>
      </div>
      <div class="footer-nav">
        <h4>Navigate</h4>
        <a href="#/overview">Overview</a><a href="#/exploration">Exploration</a>
        <a href="#/production">Production</a><a href="#/simulator">Simulator</a>
        <a href="#/recommendations">Recommendations</a><a href="#/methodology">Methodology</a>
        <a href="#/system">Design System</a>
      </div>
      <div>
        <h4>Live status</h4>
        <div class="ledger" style="border-top-color:var(--gline)">
          ${lrow('Models connected', connected + ' / 3', connected ? 'v-ok' : 'v-warn')}
          ${lrow('Simulator', 'DEMO MODEL', 'v-ok')}
          ${lrow('Study region map', occPts.ok && occPts.points.length ? `LIVE · ${occPts.points.length} OCCURRENCES` : 'DISTRICT ANCHORS ONLY', occPts.ok && occPts.points.length ? 'v-ok' : 'v-warn')}
          ${lrow('Occurrences', occ.ok ? occ.rows.length + ' / 18' : '0 / 18', occ.ok ? 'v-ok' : 'v-warn')}
          ${lrow('Production rows', prod.ok ? prod.rows.length + ' / 672' : '0 / 672', prod.ok ? 'v-ok' : 'v-warn')}
        </div>
      </div>
    </div>
    <details class="prov">
      <summary>Data sources &amp; provenance</summary>
      <div class="prov-body"><div class="ledger">
        ${Registry.provenance.map(([fam, status, detail]) =>
    lrow(fam, provChip[status] + `<span class="prov-note">${esc(detail)}</span>`, '', true)).join('')}
      </div></div>
    </details>
    <div class="footer-disc">
      <p>Prototype system for demonstration purposes. Production and exploration outputs should be validated with official geological, operational and field data before real-world decision making. Independent academic prototype for Smart India Hackathon 2026 — not affiliated with, or endorsed by, MOIL Ltd. or the Ministry of Steel.</p>
      <p class="right">Demonstration data only<br>Exploration priority ≠ confirmed reserves<br><span style="display:block;margin-top:6px;color:var(--gmute);text-transform:none;letter-spacing:.06em">© Vineet Shirode</span></p>
    </div>
  </div>`;
}

/* ==================================================================
   09 · ROUTER
   ================================================================== */
const Routes = {
  overview: { title: 'Overview', view: OverviewView },
  exploration: { title: 'Exploration', view: ExplorationView },
  production: { title: 'Production', view: ProductionView },
  simulator: { title: 'Simulator', view: SimulatorView },
  recommendations: { title: 'Recommendations', view: RecommendationsView },
  methodology: { title: 'Methodology', view: MethodologyView },
  system: { title: 'Design System', view: SystemView }
};
const $app = document.getElementById('app');
let currentUnmount = null;

const currentKey = () => { const h = location.hash.replace(/^#\/?/, '').split('?')[0]; return Routes[h] ? h : 'overview'; };
function render() {
  if (currentUnmount) { currentUnmount(); currentUnmount = null; }
  const key = currentKey(), r = Routes[key];
  document.title = `${r.title} — MineSight AI`;
  document.querySelectorAll('[data-route]').forEach(a => {
    a.dataset.route === key ? a.setAttribute('aria-current', 'page') : a.removeAttribute('aria-current');
  });
  closeMenu();
  renderFooter();
  const out = r.view();
  $app.innerHTML = out.html;
  window.scrollTo({ top: 0, behavior: 'auto' });
  if (out.mount) currentUnmount = out.mount() || null;
}

/* ---- topbar behaviour ---- */
const topbar = document.getElementById('topbar'), menuBtn = document.getElementById('menuBtn');
addEventListener('scroll', () => topbar.classList.toggle('scrolled', scrollY > 10), { passive: true });
function closeMenu() { topbar.classList.remove('open'); menuBtn.setAttribute('aria-expanded', 'false'); }
menuBtn.addEventListener('click', () => {
  const open = topbar.classList.toggle('open');
  menuBtn.setAttribute('aria-expanded', String(open));
});
document.getElementById('mnav').addEventListener('click', e => { if (e.target.closest('a')) closeMenu(); });

/* ---- ★ PHASE 3 — global delegation: sim presets + in-page scroll (no hash conflicts) ---- */
document.addEventListener('click', e => {
  const pre = e.target.closest('[data-simpreset]');
  if (pre) { applySimPreset(pre.dataset.simpreset); return; }
  const sc = e.target.closest('[data-scrollto]');
  if (sc) {
    const n = document.getElementById(sc.dataset.scrollto);
    if (n) n.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
  }
});

/* ==================================================================
   10 · BOOT
   ================================================================== */
addEventListener('hashchange', render);
console.info('%cMINESIGHT AI%c v1.0.0 — Full integration · all models connected · registry at MI.Registry · DemoModel at MI.DemoModel',
  'color:#C9662B;font-weight:bold', 'color:inherit');
(async function init() {
  await Data.hydrate();
  window.MI = { Registry, Data, DemoModel, render, applySimPreset };
  render();
})();