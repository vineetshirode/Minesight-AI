/**
 * Geographic labels — real coordinates, rendered as Leaflet markers in a
 * dedicated pane, so they pan/zoom naturally with the map (no screen-space
 * positioning).
 */

import L from 'leaflet';

export const DEFAULT_CITY_LABELS = [
  { name: 'Balaghat', lat: 21.811, lon: 80.1853 },
  { name: 'Bhandara', lat: 21.1675, lon: 79.6493 },
  { name: 'Nagpur', lat: 21.1458, lon: 79.0882 },
  { name: 'Chhindwara', lat: 22.057, lon: 78.9402 },
  { name: 'Seoni', lat: 22.0938, lon: 79.5322 },
  { name: 'Gondia', lat: 21.4602, lon: 80.192 },
];

// Placed inside the correct states, just outside the study surface.
export const DEFAULT_STATE_LABELS = [
  { name: 'MADHYA PRADESH', lat: 22.48, lon: 78.95 },
  { name: 'MAHARASHTRA', lat: 20.72, lon: 78.95 },
  { name: 'CHHATTISGARH', lat: 21.30, lon: 81.18 },
];

const esc = (s) =>
  String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
export { esc };

function cityIcon(name) {
  return L.divIcon({
    className: 'msa-label',
    iconSize: [0, 0],
    html:
      `<span class="msa-label--city">` +
      `<i class="msa-label-dot"></i>` +
      `<span class="msa-label-text">${esc(name)}</span></span>`,
  });
}

function stateIcon(name) {
  return L.divIcon({
    className: 'msa-label',
    iconSize: [0, 0],
    html: `<span class="msa-label--state">${esc(name)}</span>`,
  });
}

/** Render labels INTO a persistent group. */
export function renderLabels(group, cities = DEFAULT_CITY_LABELS, states = DEFAULT_STATE_LABELS) {
  group.clearLayers();
  const opts = { interactive: false, keyboard: false, pane: 'msaLabels' };
  (cities || []).forEach((c) => {
    if (!Number.isFinite(c.lat) || !Number.isFinite(c.lon)) return;
    group.addLayer(L.marker([c.lat, c.lon], { ...opts, icon: cityIcon(c.name) }));
  });
  (states || []).forEach((s) => {
    if (!Number.isFinite(s.lat) || !Number.isFinite(s.lon)) return;
    group.addLayer(L.marker([s.lat, s.lon], { ...opts, icon: stateIcon(s.name) }));
  });
}