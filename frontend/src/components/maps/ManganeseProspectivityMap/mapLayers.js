/**
 * Basemaps (real tile providers), study boundary, and historical occurrences.
 * Occurrences are an evidence layer ONLY — they are never used to build the
 * prospectivity surface.
 */

import L from 'leaflet';
import { LAT_KEYS, LON_KEYS } from './gridUtils';

export const BASEMAPS = [
  {
    id: 'satellite',
    name: 'Satellite',
    make() {
      return L.tileLayer(
        'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        { maxNativeZoom: 18, maxZoom: 19, attribution: 'Tiles &copy; Esri &mdash; Source: Esri, Maxar, Earthstar Geographics' }
      );
    },
  },
  {
    id: 'terrain',
    name: 'Terrain',
    make() {
      // Esri World Terrain Base + World Hillshade → shaded relief stays visible
      const base = L.tileLayer(
        'https://server.arcgisonline.com/ArcGIS/rest/services/World_Terrain_Base/MapServer/tile/{z}/{y}/{x}',
        { maxNativeZoom: 13, maxZoom: 19, attribution: 'Tiles &copy; Esri &mdash; Source: USGS, Esri, TANA, NOAA' }
      );
      const hillshade = L.tileLayer(
        'https://server.arcgisonline.com/ArcGIS/rest/services/Elevation/World_Hillshade/MapServer/tile/{z}/{y}/{x}',
        { maxNativeZoom: 16, maxZoom: 19, attribution: 'Hillshade &copy; Esri' }
      );
      return L.layerGroup([base, hillshade]);
    },
  },
  {
    id: 'topographic',
    name: 'Topographic',
    make() {
      return L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
        subdomains: 'abc',
        maxNativeZoom: 16,
        maxZoom: 18,
        attribution: '&copy; OpenStreetMap contributors, SRTM &middot; &copy; OpenTopoMap (CC-BY-SA)',
      });
    },
  },
];

const BOUNDARY_STYLE = {
  color: '#f0eee6', weight: 1.4, opacity: 0.8,
  dashArray: '6 6', fill: false, interactive: false,
  pane: 'msaBoundary',
};

/** Render the study boundary INTO a persistent group. Accepts [lat,lon] pairs or GeoJSON. */
export function renderBoundary(group, boundary) {
  group.clearLayers();
  if (!boundary) return;
  if (Array.isArray(boundary)) {
    group.addLayer(L.polygon(boundary, { ...BOUNDARY_STYLE, pane: 'msaBoundary' })); // [[lat, lon], ...]
  } else {
    group.addLayer(L.geoJSON(boundary, { style: () => ({ ...BOUNDARY_STYLE, pane: 'msaBoundary' }), interactive: false, pane: 'msaBoundary' }));
  }
}

function occurrencePopupHTML(o) {
  const rows = [
    ['District', o.district], ['State', o.state],
    ['Type', o.type], ['Period', o.period],
  ].filter((r) => r[1]);
  return (
    `<div class="msa-popup__title">${o.name || 'Manganese occurrence'}</div>` +
    (rows.length
      ? `<table class="msa-popup__table">${rows
        .map((r) => `<tr><td>${r[0]}</td><td>${String(r[1])}</td></tr>`)
        .join('')}</table>`
      : '') +
    (o.note ? `<div class="msa-popup__note">${o.note}</div>` : '') +
    `<div class="msa-popup__foot">Historical evidence layer &mdash; not a reserve estimate.</div>`
  );
}

/** Render historical occurrences INTO a persistent group. */
export function renderOccurrences(group, occurrences = []) {
  group.clearLayers();
  for (const raw of occurrences) {
    if (!raw || typeof raw !== 'object') continue;
    const lower = {};
    for (const k in raw) lower[String(k).toLowerCase()] = raw[k];
    const pick = (keys) => {
      for (const k of keys) if (k in lower && Number.isFinite(Number(lower[k]))) return Number(lower[k]);
      return NaN;
    };
    const lat = pick(LAT_KEYS);
    const lon = pick(LON_KEYS);
    if (!Number.isFinite(lat) || !Number.isFinite(lon)) continue;

    const marker = L.circleMarker([lat, lon], {
      radius: 4.5,
      color: '#ffffff', weight: 1.3, opacity: 0.95,
      fillColor: '#e07b2f', fillOpacity: 0.92,
    });
    const label = raw.name || raw.title || 'Manganese occurrence';
    const district = raw.district ? ` · ${raw.district}` : '';
    marker.bindTooltip(`${label}${district}`, { direction: 'top', offset: [0, -6], className: 'msa-tip' });
    marker.bindPopup(occurrencePopupHTML({ ...raw, name: String(label) }), {
      className: 'msa-popup', maxWidth: 260, minWidth: 190,
    });
    group.addLayer(marker);
  }
}