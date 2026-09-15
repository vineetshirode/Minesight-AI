/**
 * Data ingestion + grid inference.
 *
 * The component NEVER hardcodes geography. It receives whatever Model 1
 * export the app passes in, normalizes it to {lat, lon, value} records,
 * then infers the REAL lattice geometry (median neighbor spacing per axis)
 * so visual cell bounds come from the data itself.
 */

export const LAT_KEYS = ['lat', 'latitude', 'y', 'center_lat', 'cell_lat'];
export const LON_KEYS = ['lon', 'lng', 'long', 'longitude', 'x', 'center_lon', 'cell_lon'];
export const VAL_KEYS = [
  'score', 'prospectivity', 'prospectivity_score', 'prospectivityScore',
  'value', 'prob', 'probability', 'prediction', 'p', 'mn_score',
];

const round6 = (v) => Math.round(v * 1e6) / 1e6;

/** Grab the first key that parses as a finite number (case-insensitive). */
function pickNumber(obj, keys) {
  const lower = {};
  for (const k in obj) lower[String(k).toLowerCase()] = obj[k];
  for (const k of keys) {
    if (k in lower) {
      const v = Number(lower[k]);
      if (Number.isFinite(v)) return v;
    }
  }
  return NaN;
}

/** Flatten arbitrary JSON shapes (array | {cells|data|records|...} | GeoJSON) into records. */
export function extractRecords(raw) {
  if (!raw) return [];
  if (Array.isArray(raw)) {
    // [lat, lon, score] triplets
    if (raw.length && Array.isArray(raw[0]) && raw[0].length >= 3 && typeof raw[0][2] === 'number') {
      return raw.map((r) => ({ lat: r[0], lon: r[1], value: r[2] }));
    }
    return raw.filter((o) => o && typeof o === 'object');
  }
  if (typeof raw === 'object') {
    if (Array.isArray(raw.features)) {
      return raw.features
        .filter((f) => f && f.geometry && Array.isArray(f.geometry.coordinates))
        .map((f) => ({ ...(f.properties || {}), lat: f.geometry.coordinates[1], lon: f.geometry.coordinates[0] }));
    }
    for (const k of ['cells', 'data', 'records', 'results', 'points', 'rows', 'items', 'grid', 'scores']) {
      if (Array.isArray(raw[k])) return extractRecords(raw[k]);
    }
  }
  return [];
}

/** Normalize records using flexible key aliases (or explicit key overrides). */
export function normalizeRecords(records, opts = {}) {
  const out = [];
  for (const r of records) {
    if (!r || typeof r !== 'object') continue;
    const lat = opts.latKey ? Number(r[opts.latKey]) : pickNumber(r, LAT_KEYS);
    const lon = opts.lonKey ? Number(r[opts.lonKey]) : pickNumber(r, LON_KEYS);
    const value = opts.valueKey ? Number(r[opts.valueKey]) : pickNumber(r, VAL_KEYS);
    if (Number.isFinite(lat) && Number.isFinite(lon) && Number.isFinite(value)) {
      out.push({ lat, lon, value });
    }
  }
  return out;
}

function median(arr) {
  if (!arr.length) return 0;
  const s = [...arr].sort((a, b) => a - b);
  const m = s.length >> 1;
  return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
}

function percentile(sorted, q) {
  const i = (sorted.length - 1) * q;
  const lo = Math.floor(i);
  const hi = Math.ceil(i);
  return sorted[lo] + (sorted[hi] - sorted[lo]) * (i - lo);
}

/**
 * Build a dense scored lattice from records.
 * - spacing = MEDIAN gap between neighboring unique coordinates (robust to missing cells)
 * - cells with no record stay NaN → transparent (natural holes, no invented data)
 * - duplicate cell writes keep the max score
 * - display domain = percentile-clamped (default p2–p98) so outliers don't stretch the ramp
 */
export function buildScoredGrid(records, opts = {}) {
  if (!records || !records.length) return null;

  const latSet = new Set();
  const lonSet = new Set();
  for (const r of records) {
    latSet.add(round6(r.lat));
    lonSet.add(round6(r.lon));
  }
  const uLats = [...latSet].sort((a, b) => a - b);
  const uLons = [...lonSet].sort((a, b) => a - b);

  const latDiffs = [];
  for (let i = 1; i < uLats.length; i++) { const d = uLats[i] - uLats[i - 1]; if (d > 1e-9) latDiffs.push(d); }
  const lonDiffs = [];
  for (let i = 1; i < uLons.length; i++) { const d = uLons[i] - uLons[i - 1]; if (d > 1e-9) lonDiffs.push(d); }

  const stepLat = latDiffs.length ? median(latDiffs) : 0.01;
  const stepLon = lonDiffs.length ? median(lonDiffs) : 0.01;

  const minLat = uLats[0];
  const maxLat = uLats[uLats.length - 1];
  const minLon = uLons[0];
  const maxLon = uLons[uLons.length - 1];

  const nRows = Math.round((maxLat - minLat) / stepLat) + 1;
  const nCols = Math.round((maxLon - minLon) / stepLon) + 1;

  if (nRows > 6000 || nCols > 6000 || nRows * nCols > 8e6) {
    throw new Error(
      'Grid inference failed: coordinates do not form a regular lattice. ' +
      'Pass a prebuilt grid object (see README → Data contract).'
    );
  }

  const values = new Float32Array(nRows * nCols).fill(NaN);
  let cellCount = 0;
  for (const r of records) {
    const row = Math.min(nRows - 1, Math.max(0, Math.round((round6(r.lat) - minLat) / stepLat)));
    const col = Math.min(nCols - 1, Math.max(0, Math.round((round6(r.lon) - minLon) / stepLon)));
    const idx = row * nCols + col;
    const cur = values[idx];
    if (Number.isNaN(cur)) cellCount++;
    values[idx] = Number.isNaN(cur) ? r.value : Math.max(cur, r.value);
  }

  // display domain
  let domain = null;
  if (Array.isArray(opts.domain) && opts.domain.length === 2 &&
    Number.isFinite(opts.domain[0]) && Number.isFinite(opts.domain[1])) {
    domain = [opts.domain[0], opts.domain[1]];
  } else {
    const finite = [];
    for (let i = 0; i < values.length; i++) if (values[i] === values[i]) finite.push(values[i]);
    if (finite.length) {
      finite.sort((a, b) => a - b);
      const [qLo, qHi] = opts.domainPercentiles || [0.02, 0.98];
      const lo = percentile(finite, qLo);
      const hi = percentile(finite, qHi);
      domain = hi > lo ? [lo, hi] : [finite[0], finite[finite.length - 1]];
    } else {
      domain = [0, 1];
    }
  }

  const half = { lat: stepLat / 2, lon: stepLon / 2 };

  return {
    __isGrid: true,
    nRows, nCols, stepLat, stepLon,
    minLat, maxLat, minLon, maxLon,
    values, cellCount, sourceCount: records.length, domain,
    bounds: [[minLat - half.lat, minLon - half.lon], [maxLat + half.lat, maxLon + half.lon]],
    latOf: (row) => minLat + row * stepLat,
    lonOf: (col) => minLon + col * stepLon,
    stepKm: stepLat * 110.574,
    sampleAt(lat, lon) {
      const row = Math.round((lat - minLat) / stepLat);
      const col = Math.round((lon - minLon) / stepLon);
      if (row < 0 || row >= nRows || col < 0 || col >= nCols) return null;
      const v = values[row * nCols + col];
      return Number.isNaN(v) ? null : v;
    },
  };
}