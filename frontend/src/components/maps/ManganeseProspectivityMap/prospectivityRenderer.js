/**
 * Prospectivity raster renderer — a custom Leaflet GridLayer that draws the
 * scored grid into per-tile <canvas> elements.
 *
 * Why this is NOT a point heatmap:
 *   - each scored grid CELL is drawn at its true geographic extent
 *     (extent inferred from real neighbor spacing in gridUtils),
 *   - color comes from a precomputed 256-entry LUT of the continuous ramp,
 *   - alpha is score-weighted (terrain stays visible underneath),
 *   - no radius, no blur, no kernel density, no occurrence-point centers.
 *
 * Resampling modes (GIS-style):
 *   'smooth' — grid → 1px/cell offscreen → bilinear upscale (continuous surface)
 *   'cells'  — nearest-neighbor cell rects (crisp raster)
 *   'auto'   — smooth when a cell is < smoothBelowPx on screen, else cells
 *
 * Tiles are drawn with a ±1 cell halo so bilinear interpolation at tile edges
 * uses real neighbors → seamless stitching across tiles.
 */

import L from 'leaflet';
import { buildColorLut } from './colorScale';

const ProspectivityTileLayer = L.GridLayer.extend({
  initialize(grid, options) {
    L.GridLayer.prototype.initialize.call(this, options);
    this._setGrid(grid);
  },

  _setGrid(grid) {
    this._grid = grid;
    this._lut = buildColorLut({
      minAlpha: this.options.minAlpha,
      maxAlpha: this.options.maxAlpha,
    });
  },

  setGrid(grid) {
    this._setGrid(grid);
    this.redraw();
  },

  setRenderMode(mode) {
    this.options.renderMode = mode;
    this.redraw();
  },

  createTile(coords, done) {
    const size = this.getTileSize();
    const dpr = Math.max(1, Math.min(2, (typeof window !== 'undefined' && window.devicePixelRatio) || 1));
    const canvas = L.DomUtil.create('canvas', 'msa-raster-tile');
    canvas.width = Math.round(size.x * dpr);
    canvas.height = Math.round(size.y * dpr);
    canvas.style.width = `${size.x}px`;
    canvas.style.height = `${size.y}px`;
    const ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);
    try {
      this._drawTile(ctx, coords, size);
    } catch (err) {
      console.error('[MineSightAI] prospectivity tile draw failed:', err);
    }
    // Defer done callback to next frame so Leaflet GridLayer registers this._tiles[key] before _tileReady runs
    L.Util.requestAnimFrame(() => {
      done(null, canvas);
    });
    return canvas;
  },

  _drawTile(ctx, coords, size) {
    const map = this._map;
    const g = this._grid;
    if (!map || !g) return;

    const z = coords.z;
    const ts = size.x;
    const originX = coords.x * ts;
    const originY = coords.y * ts;

    const nw = map.unproject([originX, originY], z);
    const se = map.unproject([originX + ts, originY + ts], z);
    const north = nw.lat, west = nw.lng, south = se.lat, east = se.lng;

    // quick reject — tile is entirely outside the scored area
    if (south > g.maxLat + g.stepLat || north < g.minLat - g.stepLat ||
      west > g.maxLon + g.stepLon || east < g.minLon - g.stepLon) return;

    // cell index range intersecting this tile (±1 halo for seamless edges)
    const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));
    const cStart = clamp(Math.floor((west - g.minLon) / g.stepLon + 0.5) - 1, 0, g.nCols - 1);
    const cEnd = clamp(Math.ceil((east - g.minLon) / g.stepLon + 0.5) + 1, 0, g.nCols - 1);
    const rStart = clamp(Math.floor((south - g.minLat) / g.stepLat + 0.5) - 1, 0, g.nRows - 1);
    const rEnd = clamp(Math.ceil((north - g.minLat) / g.stepLat + 0.5) + 1, 0, g.nRows - 1);
    if (cStart > cEnd || rStart > rEnd) return;

    const dLo = g.domain[0];
    const dSpan = Math.max(1e-9, g.domain[1] - g.domain[0]);
    const lut = this._lut;

    // x is linear in longitude in Web Mercator → closed-form per column
    const p0 = map.project([g.minLat, g.minLon], z);
    const pxPerLon = map.project([g.minLat, g.minLon + 1], z).x - p0.x;
    const xOf = (c) => p0.x + (c - 0.5) * g.stepLon * pxPerLon - originX; // west edge of column c
    const yOfLat = (lat) => map.project([lat, g.minLon], z).y - originY;

    // pick resampling mode
    let mode = this.options.renderMode;
    if (mode === 'auto') {
      const cellPx = Math.abs(g.stepLon * pxPerLon);
      mode = cellPx < this.options.smoothBelowPx ? 'smooth' : 'cells';
    }

    if (mode === 'smooth') {
      // ---- bilinear surface: 1px per cell → smoothed upscale ----
      const w = cEnd - cStart + 1;
      const h = rEnd - rStart + 1;
      const off = document.createElement('canvas');
      off.width = w; off.height = h;
      const octx = off.getContext('2d');
      const img = octx.createImageData(w, h);
      const d = img.data;
      for (let j = 0; j < h; j++) {
        const r = rEnd - j; // image row 0 = northernmost grid row
        const rowOff = r * g.nCols;
        for (let i = 0; i < w; i++) {
          const v = g.values[rowOff + cStart + i];
          if (v === v) { // skip NaN holes
            let t = (v - dLo) / dSpan;
            t = t < 0 ? 0 : t > 1 ? 1 : t;
            const q = ((t * 255) | 0) << 2;
            const o = (j * w + i) << 2;
            d[o] = lut[q]; d[o + 1] = lut[q + 1]; d[o + 2] = lut[q + 2]; d[o + 3] = lut[q + 3];
          }
        }
      }
      octx.putImageData(img, 0, 0);
      const xL = xOf(cStart);
      const xR = xOf(cEnd + 1);
      const yT = yOfLat(g.minLat + (rEnd + 0.5) * g.stepLat);
      const yB = yOfLat(g.minLat + (rStart - 0.5) * g.stepLat);
      ctx.imageSmoothingEnabled = true;
      try { ctx.imageSmoothingQuality = 'high'; } catch (e) { /* optional */ }
      ctx.drawImage(off, xL, yT, xR - xL, yB - yT);
    } else {
      // ---- crisp cells: nearest-neighbor rects at true cell extent ----
      ctx.imageSmoothingEnabled = false;
      const xL0 = xOf(cStart);
      const stepPx = g.stepLon * pxPerLon;
      for (let r = rStart; r <= rEnd; r++) {
        const yT = yOfLat(g.minLat + (r + 0.5) * g.stepLat);
        const yB = yOfLat(g.minLat + (r - 0.5) * g.stepLat);
        const hh = yB - yT + 0.5; // slight overlap kills antialiasing seams
        const rowOff = r * g.nCols;
        for (let c = cStart; c <= cEnd; c++) {
          const v = g.values[rowOff + c];
          if (v !== v) continue;
          let t = (v - dLo) / dSpan;
          t = t < 0 ? 0 : t > 1 ? 1 : t;
          const q = ((t * 255) | 0) << 2;
          ctx.fillStyle = `rgba(${lut[q]},${lut[q + 1]},${lut[q + 2]},${(lut[q + 3] / 255).toFixed(3)})`;
          ctx.fillRect(xL0 + (c - cStart) * stepPx - 0.25, yT - 0.25, stepPx + 0.5, hh);
        }
      }
    }
  },
});

export function createProspectivityLayer(grid, options = {}) {
  return new ProspectivityTileLayer(grid, {
    pane: 'msaProspectivity',
    tileSize: 256,
    className: 'msa-prospectivity-tiles',
    renderMode: 'auto',
    smoothBelowPx: 3.5,
    minAlpha: 0.25,
    maxAlpha: 0.48,
    attribution: 'Prospectivity surface: MineSight AI · Model 1 (prototype)',
    bounds: L.latLngBounds(grid.bounds).pad(0.05), // generous bounds to ensure all edge tiles render
    ...options,
  });
}