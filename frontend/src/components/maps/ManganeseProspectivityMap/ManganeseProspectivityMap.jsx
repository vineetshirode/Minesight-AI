/**
 * ManganeseProspectivityMap
 * -------------------------
 * Reusable, page-agnostic GIS map for MineSight AI.
 *
 * Layer stack (bottom → top):
 *   1. Terrain / Satellite / Topographic tile basemap
 *   2. Model 1 prospectivity raster (canvas GridLayer, score-weighted alpha)
 *   3. Study boundary (thin dashed outline, no fill)
 *   4. Historical occurrences (separate evidence markers)
 *   5. Geographic labels (custom pane)
 *
 * The component is visualization-only: it makes no API calls, holds no app
 * state, and never generates or modifies data. All data arrives via props.
 */

import { useEffect, useMemo, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './ManganeseProspectivityMap.css';

import { buildScoredGrid, extractRecords, normalizeRecords } from './gridUtils';
import { createProspectivityLayer } from './prospectivityRenderer';
import { BASEMAPS, renderBoundary, renderOccurrences } from './mapLayers';
import {
  DEFAULT_CITY_LABELS, DEFAULT_STATE_LABELS, renderLabels, esc,
} from './labels';
import { rampGradientCSS } from './colorScale';

const DEFAULT_META_LINES = [
  { k: 'Model', v: 'Model 1 · Manganese Prospectivity' },
  { k: 'Data', v: 'Sentinel-2 · SRTM DEM · GSI' },
];
const DEFAULT_DOMAIN_PERCENTILES = [0.02, 0.98];
const DEFAULT_OCCURRENCES = [];
const DEFAULT_DEFAULT_LAYERS = { prospectivity: true, occurrences: true, labels: true, boundary: true };
const DEFAULT_CENTER = [21.55, 79.85];

export default function ManganeseProspectivityMap({
  // ---- data (all optional; the app owns loading) ----
  explorationData = null,          // records | {cells:[...]} | GeoJSON | prebuilt grid
  occurrences = DEFAULT_OCCURRENCES,
  studyBoundary = null,
  // ---- data key overrides ----
  latKey, lonKey, valueKey,
  colorDomain = null,              // [lo, hi] to override percentile domain
  domainPercentiles = DEFAULT_DOMAIN_PERCENTILES,
  // ---- labels ----
  cityLabels = DEFAULT_CITY_LABELS,
  stateLabels = DEFAULT_STATE_LABELS,
  // ---- view (initial values) ----
  center = DEFAULT_CENTER,
  zoom = 8,
  minZoom = 6,
  maxZoom = 16,
  basemap = 'satellite',
  scrollWheelZoom = true,
  // ---- layer visibility defaults ----
  defaultLayers = DEFAULT_DEFAULT_LAYERS,
  layerControlCollapsed = false,
  // ---- rendering ----
  renderMode = 'auto',             // 'auto' | 'cells' | 'smooth'
  opacity = 1,                     // global multiplier on top of score-weighted alpha
  minAlpha = 0.25,
  maxAlpha = 0.48,
  // ---- controls ----
  showLegend = true,
  showScale = true,
  showNorthArrow = true,
  showMetadata = true,
  metaLines = DEFAULT_META_LINES,
  // ---- callbacks ----
  onMapReady = null,
  onCellClick = null,              // ({lat, lon, score, band}) on surface click
  onGridBuilt = null,              // (grid) — for status readouts
  // ---- misc ----
  className = '',
  style = null,
}) {
  const containerRef = useRef(null);
  const [map, setMap] = useState(null);
  const groupsRef = useRef(null);
  const layersRef = useRef({});
  const gridRef = useRef(null);
  const lastGridRef = useRef(null);
  const identifyRef = useRef(null);
  const onCellClickRef = useRef(onCellClick);
  onCellClickRef.current = onCellClick;

  const dp0 = Array.isArray(domainPercentiles) ? domainPercentiles[0] : 0.02;
  const dp1 = Array.isArray(domainPercentiles) ? domainPercentiles[1] : 0.98;
  const cdKey = colorDomain ? `${colorDomain[0]}_${colorDomain[1]}` : 'none';

  // Build (or accept) the scored grid — pure function of data and domain config.
  const grid = useMemo(() => {
    if (!explorationData) return null;
    if (explorationData.__isGrid) return explorationData;
    try {
      const records = normalizeRecords(extractRecords(explorationData), { latKey, lonKey, valueKey });
      return buildScoredGrid(records, { domain: colorDomain, domainPercentiles: [dp0, dp1] });
    } catch (err) {
      console.error('[MineSightAI] grid build failed:', err);
      return null;
    }
  }, [explorationData, latKey, lonKey, valueKey, cdKey, dp0, dp1]); // eslint-disable-line react-hooks/exhaustive-deps

  // ---------- mount: map + controls ----------
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return undefined;

    const mapInstance = L.map(el, {
      center, zoom, minZoom, maxZoom, scrollWheelZoom,
      zoomControl: true,            // top-left
      attributionControl: true,
      preferCanvas: false,
    });
    mapInstance.attributionControl.setPrefix('');

    // 1. Prospectivity raster pane: strictly above basemap tiles (200), strictly below vector boundary & markers
    mapInstance.createPane('msaProspectivity');
    const prosPane = mapInstance.getPane('msaProspectivity');
    prosPane.style.zIndex = '350';
    prosPane.style.pointerEvents = 'none';

    // 2. Study boundary pane: strictly above prospectivity raster (350), below markers
    mapInstance.createPane('msaBoundary');
    const boundPane = mapInstance.getPane('msaBoundary');
    boundPane.style.zIndex = '380';
    boundPane.style.pointerEvents = 'none';

    // 3. Geographic labels pane: above raster tiles & markers (400), below UI popups (700)
    mapInstance.createPane('msaLabels');
    const labelPane = mapInstance.getPane('msaLabels');
    labelPane.style.zIndex = '460';
    labelPane.style.pointerEvents = 'none';

    // stable overlay groups (children swap when props change)
    const groups = {
      prospectivity: L.layerGroup(),
      occurrences: L.layerGroup(),
      labels: L.layerGroup(),
      boundary: L.layerGroup(),
    };
    groupsRef.current = groups;

    const defaults = { prospectivity: true, occurrences: true, labels: true, boundary: true, ...defaultLayers };
    if (defaults.prospectivity) groups.prospectivity.addTo(mapInstance);
    if (defaults.occurrences) groups.occurrences.addTo(mapInstance);
    if (defaults.labels) groups.labels.addTo(mapInstance);
    if (defaults.boundary) groups.boundary.addTo(mapInstance);

    const baseLayers = {};
    BASEMAPS.forEach((b) => { baseLayers[b.name] = b.make(); });
    const initial = BASEMAPS.find((b) => b.id === basemap) || BASEMAPS[0];
    baseLayers[initial.name].addTo(mapInstance);

    // layer switcher — added first → top of the top-right stack
    L.control.layers(
      baseLayers,
      {
        'Manganese Prospectivity': groups.prospectivity,
        'Historical Occurrences': groups.occurrences,
        'Location Labels': groups.labels,
        'Study Boundary': groups.boundary,
      },
      { position: 'topright', collapsed: layerControlCollapsed }
    ).addTo(mapInstance);

    // legend — added second → stacks directly below the layer control
    if (showLegend) {
      const LegendControl = L.Control.extend({
        options: { position: 'topright' },
        onAdd() {
          const div = L.DomUtil.create('div', 'msa-legend msa-panel');
          div.innerHTML =
            `<div class="msa-legend__title">Manganese Prospectivity</div>` +
            `<div class="msa-legend__body">` +
            `<div class="msa-legend__bar" style="background:${rampGradientCSS()}"></div>` +
            `<div class="msa-legend__bands"><span>HIGH</span><span>MEDIUM</span><span>LOW</span></div>` +
            `</div>` +
            `<div class="msa-legend__range">—</div>`;
          return div;
        },
      });
      const legend = new LegendControl();
      mapInstance.addControl(legend);
      layersRef.current.legendRange = legend.getContainer().querySelector('.msa-legend__range');
    }

    // north arrow — top-left, stacked below zoom, away from the legend
    if (showNorthArrow) {
      const NorthControl = L.Control.extend({
        options: { position: 'topleft' },
        onAdd() {
          const div = L.DomUtil.create('div', 'msa-north');
          div.title = 'North';
          div.innerHTML = `<div class="msa-north__arrow"></div><div class="msa-north__letter">N</div>`;
          return div;
        },
      });
      mapInstance.addControl(new NorthControl());
    }

    // technical metadata — bottom-right
    if (showMetadata) {
      const MetaControl = L.Control.extend({
        options: { position: 'bottomright' },
        onAdd() {
          const div = L.DomUtil.create('div', 'msa-meta msa-panel');
          const rows = metaLines.map(
            (l) => `<div class="msa-meta__row"><span class="msa-meta__k">${esc(l.k)}</span>` +
              `<span class="msa-meta__v">${esc(l.v)}</span></div>`
          ).join('');
          div.innerHTML =
            `<div class="msa-meta__row"><span class="msa-meta__k">Base Map</span>` +
            `<span class="msa-meta__v" data-meta="base">${esc(initial.name)}</span></div>` +
            rows +
            `<div class="msa-meta__row"><span class="msa-meta__k">Grid</span>` +
            `<span class="msa-meta__v" data-meta="grid">—</span></div>` +
            `<div class="msa-meta__foot">Prototype · Demo / Synthetic data</div>`;
          return div;
        },
      });
      const meta = new MetaControl();
      mapInstance.addControl(meta);
      layersRef.current.metaBase = meta.getContainer().querySelector('[data-meta="base"]');
      layersRef.current.metaGrid = meta.getContainer().querySelector('[data-meta="grid"]');
    }

    // real scale bar — bottom-left, updates with zoom
    if (showScale) {
      L.control.scale({ position: 'bottomleft', imperial: false, maxWidth: 160 }).addTo(mapInstance);
    }

    mapInstance.on('baselayerchange', (e) => {
      if (layersRef.current.metaBase) layersRef.current.metaBase.textContent = e.name;
    });

    const onMapClick = (e) => { if (identifyRef.current) identifyRef.current(e); };
    mapInstance.on('click', onMapClick);

    let roTimeout = null;
    const ro = new ResizeObserver(() => {
      if (roTimeout) clearTimeout(roTimeout);
      roTimeout = setTimeout(() => {
        if (mapInstance && mapInstance._container) {
          mapInstance.invalidateSize({ debounceMoveend: true });
        }
      }, 100);
    });
    ro.observe(el);

    setMap(mapInstance);
    if (onMapReady) onMapReady(mapInstance);

    return () => {
      if (roTimeout) clearTimeout(roTimeout);
      ro.disconnect();
      mapInstance.off('click', onMapClick);
      mapInstance.remove();
      setMap(null);
      groupsRef.current = null;
      layersRef.current = {};
    };
    // initial-configuration props are intentionally mount-only
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ---------- identify-on-click (reads the grid, never the occurrences) ----------
  useEffect(() => {
    identifyRef.current = (e) => {
      const g = gridRef.current;
      if (!map || !g) return;
      const v = g.sampleAt(e.latlng.lat, e.latlng.lng);
      if (v == null) return;
      let t = (v - g.domain[0]) / Math.max(1e-9, g.domain[1] - g.domain[0]);
      t = Math.min(1, Math.max(0, t));
      const band = t >= 0.6667 ? 'High' : t >= 0.3334 ? 'Medium' : 'Low';
      const color = band === 'High' ? '#e0684b' : band === 'Medium' ? '#d9b23f' : '#3282c4';
      const html =
        `<div class="msa-id">` +
        `<div class="msa-popup__title">Manganese Prospectivity</div>` +
        `<div class="msa-id__value" style="color:${color}">${band} · ${v.toFixed(3)}</div>` +
        `<div class="msa-id__meta">Model 1 grid cell · ≈ ${g.stepKm.toFixed(1)} km spacing</div>` +
        `<div class="msa-popup__foot">Exploration priority — not a reserve estimate.</div>` +
        `</div>`;
      L.popup({
        className: 'msa-popup msa-popup--identify',
        closeButton: false, autoPan: false, offset: [0, -4],
      }).setLatLng(e.latlng).setContent(html).openOn(map);
      if (onCellClickRef.current) onCellClickRef.current({ lat: e.latlng.lat, lon: e.latlng.lng, score: v, band });
    };
  }, [map]);

  // ---------- grid side-effects: refs, legend range, metadata line ----------
  useEffect(() => {
    gridRef.current = grid;
    if (grid && grid !== lastGridRef.current) {
      lastGridRef.current = grid;
      if (onGridBuilt) onGridBuilt(grid);
    }
    const range = layersRef.current.legendRange;
    if (range) {
      range.textContent = grid
        ? `${grid.domain[0].toFixed(2)} – ${grid.domain[1].toFixed(2)} · Model 1 score`
        : '—';
    }
    const mg = layersRef.current.metaGrid;
    if (mg) {
      mg.textContent = grid
        ? `${grid.cellCount.toLocaleString()} cells · ≈${grid.stepKm.toFixed(1)} km`
        : 'no grid';
    }
  }, [grid, onGridBuilt]);

  // ---------- prospectivity raster layer ----------
  useEffect(() => {
    if (!map || !groupsRef.current) return;
    const group = groupsRef.current.prospectivity;
    if (!group) return;

    if (!grid) {
      group.clearLayers();
      layersRef.current.prosLayer = null;
      return;
    }

    // Reuse existing layer if grid hasn't changed
    const currentLayer = layersRef.current.prosLayer;
    if (currentLayer && currentLayer._grid === grid) {
      if (currentLayer.options.renderMode !== renderMode) {
        currentLayer.setRenderMode(renderMode);
      }
      return;
    }

    group.clearLayers();
    const layer = createProspectivityLayer(grid, {
      pane: 'msaProspectivity',
      renderMode,
      minAlpha,
      maxAlpha,
    });
    group.addLayer(layer);
    if (opacity !== 1) layer.setOpacity(opacity);
    layersRef.current.prosLayer = layer;
  }, [map, grid, renderMode, minAlpha, maxAlpha]); // eslint-disable-line react-hooks/exhaustive-deps

  // ---------- evidence / context layers ----------
  useEffect(() => {
    if (!map || !groupsRef.current) return;
    renderOccurrences(groupsRef.current.occurrences, occurrences);
  }, [map, occurrences]);

  useEffect(() => {
    if (!map || !groupsRef.current) return;
    renderBoundary(groupsRef.current.boundary, studyBoundary);
  }, [map, studyBoundary]);

  useEffect(() => {
    if (!map || !groupsRef.current) return;
    renderLabels(groupsRef.current.labels, cityLabels, stateLabels);
  }, [map, cityLabels, stateLabels]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (map && layersRef.current.prosLayer) layersRef.current.prosLayer.setOpacity(opacity);
  }, [map, opacity]);

  return <div ref={containerRef} className={`msa-map-wrap ${className}`.trim()} style={style} />;
}