import React from 'react';
import { createRoot } from 'react-dom/client';
import ManganeseProspectivityMap from './components/maps/ManganeseProspectivityMap/ManganeseProspectivityMap';
import './components/maps/ManganeseProspectivityMap/ManganeseProspectivityMap.css';
import { extractRecords } from './components/maps/ManganeseProspectivityMap/gridUtils';
import {
  DEMO_OCCURRENCES,
  DEMO_STUDY_BOUNDARY,
  getDemoExplorationRecords,
} from './components/maps/ManganeseProspectivityMap/demo/demoData';

let activeRoot = null;
let cachedRecords = null;

async function loadScores() {
  if (cachedRecords) return cachedRecords;
  try {
    const res = await fetch('data/exploration_scores.json');
    if (res.ok) {
      const json = await res.json();
      const records = extractRecords(json);
      if (records && records.length) {
        cachedRecords = records;
        return records;
      }
    }
  } catch (e) {
    console.warn('[MapMount] Error loading exploration scores, using fallback', e);
  }
  cachedRecords = getDemoExplorationRecords();
  return cachedRecords;
}

export async function mountProspectivityMap(target = 'hero-map-wrap', options = {}) {
  const container = typeof target === 'string' ? document.getElementById(target) : target;
  if (!container) return null;

  // Clear previous root/content in container if re-mounting
  if (activeRoot) {
    try {
      activeRoot.unmount();
    } catch (e) {
      // ignore
    }
    activeRoot = null;
  }
  container.innerHTML = '';

  const explorationData = await loadScores();
  if (!container.isConnected) return null;

  let occurrences = options && options.occurrences && options.occurrences.length ? options.occurrences : null;
  if (!occurrences && typeof window !== 'undefined' && window.MI && window.MI.Data) {
    const occRes = window.MI.Data.getOccurrencePoints();
    if (occRes && occRes.ok && occRes.points && occRes.points.length) {
      occurrences = occRes.points;
    }
  }
  if (!occurrences || !occurrences.length) {
    occurrences = DEMO_OCCURRENCES;
  }

  activeRoot = createRoot(container);
  activeRoot.render(
    <ManganeseProspectivityMap
      explorationData={explorationData}
      occurrences={occurrences}
      studyBoundary={DEMO_STUDY_BOUNDARY}
      center={[21.55, 79.85]}
      zoom={8}
      basemap="satellite"
      showMetadata={false}
      layerControlCollapsed={true}
    />
  );

  return () => {
    if (activeRoot) {
      try {
        activeRoot.unmount();
      } catch (e) {
        // ignore
      }
      activeRoot = null;
    }
  };
}

if (typeof window !== 'undefined') {
  window.mountProspectivityMap = mountProspectivityMap;
}

export default mountProspectivityMap;
