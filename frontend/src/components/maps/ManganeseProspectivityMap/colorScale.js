/**
 * Continuous prospectivity colormap — muted scientific ramp.
 * Deep blue → teal → green → yellow → orange → deep red.
 * No neon, no pure rainbow: stops are deliberately desaturated so the
 * surface reads as a geologic raster, not a heatmap.
 */

export const PROSPECTIVITY_STOPS = [
  { t: 0.0, color: [30, 95, 185] },    // Low: Deep blue
  { t: 0.14, color: [25, 135, 195] },  // Steel cyan-blue
  { t: 0.28, color: [20, 168, 172] },  // Teal / Cyan
  { t: 0.44, color: [45, 175, 100] },  // Green
  { t: 0.58, color: [145, 190, 50] },  // Yellow-Green
  { t: 0.72, color: [235, 192, 35] },  // Medium: Golden Yellow
  { t: 0.84, color: [242, 125, 35] },  // Warm Orange
  { t: 0.94, color: [230, 60, 38] },   // Bright Orange-Red
  { t: 1.0, color: [195, 25, 35] },    // High: Deep Crimson Red
];

const clamp01 = (v) => (v < 0 ? 0 : v > 1 ? 1 : v);

/** Sample the ramp at t ∈ [0,1] → [r,g,b] */
export function sampleRamp(t) {
  const x = clamp01(t);
  for (let i = 1; i < PROSPECTIVITY_STOPS.length; i++) {
    const a = PROSPECTIVITY_STOPS[i - 1];
    const b = PROSPECTIVITY_STOPS[i];
    if (x <= b.t) {
      const f = (x - a.t) / (b.t - a.t || 1);
      return [
        Math.round(a.color[0] + (b.color[0] - a.color[0]) * f),
        Math.round(a.color[1] + (b.color[1] - a.color[1]) * f),
        Math.round(a.color[2] + (b.color[2] - a.color[2]) * f),
      ];
    }
  }
  return PROSPECTIVITY_STOPS[PROSPECTIVITY_STOPS.length - 1].color.slice();
}

/**
 * Score-weighted opacity: low scores stay semi-transparent so terrain/satellite
 * details show through; high scores reach ~48% so priority zones stand out.
 */
export function alphaAt(t, { minAlpha = 0.25, maxAlpha = 0.48, curve = 0.90 } = {}) {
  return minAlpha + (maxAlpha - minAlpha) * Math.pow(clamp01(t), curve);
}

/** 256-entry RGBA lookup table — one precomputed table per layer. */
export function buildColorLut(opts = {}) {
  const lut = new Uint8ClampedArray(256 * 4);
  for (let i = 0; i < 256; i++) {
    const t = i / 255;
    const [r, g, b] = sampleRamp(t);
    const a = Math.round(alphaAt(t, opts) * 255);
    const o = i * 4;
    lut[o] = r; lut[o + 1] = g; lut[o + 2] = b; lut[o + 3] = a;
  }
  return lut;
}

/** CSS gradient for the legend (pure ramp, GIS-legend style). */
export function rampGradientCSS() {
  const parts = PROSPECTIVITY_STOPS.map(
    (s) => `rgb(${s.color[0]},${s.color[1]},${s.color[2]}) ${(s.t * 100).toFixed(1)}%`
  );
  return `linear-gradient(to top, ${parts.join(', ')})`;
}