/**
 * DEMO-ONLY DATA — clearly labeled as synthetic.
 *
 * The map component never generates data. This module exists solely so the
 * standalone /map-demo page renders without the private MineSight dataset.
 * At integration time this file is unused: the real Model 1 export
 * (exploration_scores.json) and the real occurrence dataset are passed via
 * props / fetched from the FastAPI backend.
 *
 * The synthetic field is a smooth spatial function (ridge along the
 * Balaghat–Bhandara manganese belt + multi-octave value noise + hotspot
 * bumps), sampled on a regular 0.01° lattice and masked by the demo study
 * boundary — so it exercises the exact same grid-inference + raster pipeline
 * the real data will go through.
 */

function mulberry32(seed) {
  let a = seed | 0;
  return function () {
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Wrap-around value noise with smoothstep bilinear interpolation. */
function makeNoise(rng) {
  const N = 48;
  const g = new Float32Array(N * N);
  for (let i = 0; i < g.length; i++) g[i] = rng();
  const sm = (t) => t * t * (3 - 2 * t);
  return (u, v) => {
    const x = ((u % 1) + 1) % 1 * N;
    const y = ((v % 1) + 1) % 1 * N;
    const x0 = Math.floor(x), y0 = Math.floor(y);
    const fx = sm(x - x0), fy = sm(y - y0);
    const i0 = x0 % N, i1 = (x0 + 1) % N;
    const j0 = y0 % N, j1 = (y0 + 1) % N;
    const a = g[j0 * N + i0], b = g[j0 * N + i1];
    const c = g[j1 * N + i0], d = g[j1 * N + i1];
    return a + (b - a) * fx + (c - a) * fy + (a - b - c + d) * fx * fy;
  };
}

export const DEMO_NOTE =
  'Demo fallback: synthetic prospectivity field + approximate historical localities. ' +
  'Place exploration_scores.json in public/data/ (or fetch it from the API) to view real Model 1 output.';

// Rough NW–SE trend of the manganese belt through the study districts.
const BELT = [[21.02, 79.02], [21.28, 79.36], [21.52, 79.68], [21.74, 79.98], [21.92, 80.24], [22.05, 80.45]];

function ridge(lat, lon) {
  let dmin = Infinity;
  for (let i = 1; i < BELT.length; i++) {
    const [y1, x1] = BELT[i - 1];
    const [y2, x2] = BELT[i];
    const dy = y2 - y1, dx = x2 - x1;
    const t = Math.max(0, Math.min(1, ((lat - y1) * dy + (lon - x1) * dx) / (dy * dy + dx * dx)));
    const d = Math.hypot(lat - (y1 + t * dy), lon - (x1 + t * dx));
    if (d < dmin) dmin = d;
  }
  return Math.exp(-(dmin * dmin) / (2 * 0.30 * 0.30));
}

const gauss = (lat, lon, la, lo, s) => Math.exp(-((lat - la) ** 2 + (lon - lo) ** 2) / (2 * s * s));

function pointInPolygon(lat, lon, ring) {
  let inside = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const [yi, xi] = ring[i];
    const [yj, xj] = ring[j];
    if (yi > lat !== yj > lat && lon < ((xj - xi) * (lat - yi)) / (yj - yi) + xi) inside = !inside;
  }
  return inside;
}

export const DEMO_STUDY_BOUNDARY = [
  [22.42, 79.30], [22.31, 79.72], [22.18, 80.08], [22.06, 80.38], [21.96, 80.68],
  [21.82, 80.92], [21.62, 80.98], [21.44, 80.82], [21.28, 80.66], [21.10, 80.58],
  [20.94, 80.38], [20.84, 80.08], [20.76, 79.78], [20.70, 79.46], [20.76, 79.12],
  [20.88, 78.86], [21.04, 78.74], [21.24, 78.68], [21.46, 78.68], [21.66, 78.70],
  [21.86, 78.74], [22.06, 78.84], [22.22, 79.00], [22.34, 79.14],
];

// 18 approximate historical Mn localities across the three study districts.
// REPLACE with the real occurrence dataset at integration.
export const DEMO_OCCURRENCES = [
  { id: 1, name: 'Bharweli', district: 'Balaghat', state: 'Madhya Pradesh', lat: 21.895, lon: 80.335, type: 'MOIL underground mine', period: 'Historical working' },
  { id: 2, name: 'Ukwa', district: 'Balaghat', state: 'Madhya Pradesh', lat: 21.867, lon: 80.273, type: 'MOIL mine', period: 'Historical working' },
  { id: 3, name: 'Balaghat', district: 'Balaghat', state: 'Madhya Pradesh', lat: 21.811, lon: 80.192, type: 'MOIL underground mine', period: 'Historical working' },
  { id: 4, name: 'Sitasaongi', district: 'Balaghat', state: 'Madhya Pradesh', lat: 21.716, lon: 80.442, type: 'MOIL mine', period: 'Historical working' },
  { id: 5, name: 'Ramrama', district: 'Balaghat', state: 'Madhya Pradesh', lat: 21.532, lon: 80.409, type: 'GSI occurrence', period: 'Historical working' },
  { id: 6, name: 'Tirodi', district: 'Balaghat', state: 'Madhya Pradesh', lat: 21.452, lon: 80.318, type: 'MOIL mine', period: 'Historical working' },
  { id: 7, name: 'Pipardahi', district: 'Balaghat', state: 'Madhya Pradesh', lat: 21.798, lon: 80.086, type: 'GSI occurrence', period: 'Historical working' },
  { id: 8, name: 'Kodajhiri', district: 'Chhindwara', state: 'Madhya Pradesh', lat: 21.968, lon: 78.982, type: 'GSI occurrence', period: 'Historical occurrence' },
  { id: 9, name: 'Dongargaon', district: 'Chhindwara', state: 'Madhya Pradesh', lat: 21.902, lon: 79.046, type: 'GSI occurrence', period: 'Historical occurrence' },
  { id: 10, name: 'Kandri', district: 'Nagpur', state: 'Maharashtra', lat: 21.342, lon: 79.062, type: 'MOIL underground mine', period: 'Historical working' },
  { id: 11, name: 'Mansar', district: 'Nagpur', state: 'Maharashtra', lat: 21.297, lon: 79.087, type: 'MOIL underground mine', period: 'Historical working' },
  { id: 12, name: 'Ambajhari', district: 'Nagpur', state: 'Maharashtra', lat: 21.243, lon: 79.014, type: 'GSI occurrence', period: 'Historical occurrence' },
  { id: 13, name: 'Bhandal Met', district: 'Nagpur', state: 'Maharashtra', lat: 21.183, lon: 78.992, type: 'GSI occurrence', period: 'Historical occurrence' },
  { id: 14, name: 'Gumgaon', district: 'Nagpur', state: 'Maharashtra', lat: 21.052, lon: 79.141, type: 'MOIL underground mine', period: 'Historical working' },
  { id: 15, name: 'Netargaon', district: 'Bhandara', state: 'Maharashtra', lat: 21.146, lon: 79.417, type: 'GSI occurrence', period: 'Historical occurrence' },
  { id: 16, name: 'Beldongri', district: 'Bhandara', state: 'Maharashtra', lat: 21.061, lon: 79.632, type: 'MOIL mine', period: 'Historical working' },
  { id: 17, name: 'Murmadi', district: 'Bhandara', state: 'Maharashtra', lat: 21.017, lon: 79.552, type: 'GSI occurrence', period: 'Historical occurrence' },
  { id: 18, name: 'Kachurwahi', district: 'Bhandara', state: 'Maharashtra', lat: 20.972, lon: 79.781, type: 'MOIL mine', period: 'Historical working' },
].map((o) => ({ ...o, note: 'Prototype demo dataset — approximate locality.' }));

let _records = null;

/** Build the synthetic scored lattice (~0.01° spacing, masked to the boundary). */
export function getDemoExplorationRecords() {
  if (_records) return _records;
  const rng = mulberry32(20260209);
  const n1 = makeNoise(rng);
  const n2 = makeNoise(rng);
  const n3 = makeNoise(rng);

  const fieldValue = (lat, lon) => {
    const u = (lon - 78.5) / 2.6;
    const v = (lat - 20.5) / 2.1;
    let val = 0.50 * ridge(lat, lon);
    val += 0.30 * n1(u, v);
    val += 0.18 * n2(u * 2.3, v * 2.3);
    val += 0.10 * n3(u * 5.1, v * 5.1);
    val += 0.42 * gauss(lat, lon, 21.88, 80.22, 0.17); // Balaghat corridor
    val += 0.34 * gauss(lat, lon, 21.02, 79.80, 0.15); // south Bhandara
    val += 0.26 * gauss(lat, lon, 21.42, 79.95, 0.12);
    val += 0.20 * gauss(lat, lon, 21.28, 79.14, 0.14);
    val = Math.min(1, Math.max(0, val * 0.92));
    return 0.06 + 0.92 * val;
  };

  const out = [];
  for (let i = 0; i < 175; i++) {
    const lat = 20.70 + i * 0.01;
    for (let j = 0; j < 225; j++) {
      const lon = 78.70 + j * 0.01;
      if (!pointInPolygon(lat, lon, DEMO_STUDY_BOUNDARY)) continue;
      out.push({ lat: Number(lat.toFixed(4)), lon: Number(lon.toFixed(4)), score: Number(fieldValue(lat, lon).toFixed(4)) });
    }
  }
  _records = out;
  return out;
}