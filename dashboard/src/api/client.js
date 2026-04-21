/**
 * MAS Sydney – API Client
 * Fetches data from the FastAPI backend (http://localhost:8000)
 * Falls back to static seed data if the API is unreachable.
 */

const API_BASE = 'http://localhost:8000/api';

async function apiFetch(path, options = {}) {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options,
    });
    if (!res.ok) throw new Error(`API ${res.status}: ${res.statusText}`);
    return await res.json();
  } catch (err) {
    console.warn(`API call failed: ${path}`, err.message);
    return null;
  }
}

// ─── Data Endpoints ───

export async function fetchSuburbs() {
  return apiFetch('/suburbs');
}

export async function fetchSuburb(suburbId) {
  return apiFetch(`/suburbs/${suburbId}`);
}

export async function fetchDARecords(suburbId) {
  return apiFetch(`/suburbs/${suburbId}/da-records`);
}

export async function fetchProperties(suburbId) {
  return apiFetch(`/suburbs/${suburbId}/properties`);
}

export async function fetchHotStreets(suburbId) {
  return apiFetch(`/suburbs/${suburbId}/hot-streets`);
}

export async function fetchPopulation(suburbId) {
  return apiFetch(`/suburbs/${suburbId}/population`);
}

export async function fetchDATrends(suburbId) {
  return apiFetch(`/suburbs/${suburbId}/da-trends`);
}

export async function fetchEconomic(suburbId) {
  return apiFetch(`/suburbs/${suburbId}/economic`);
}

export async function fetchHealth() {
  return apiFetch('/health');
}

export async function fetchScheduler() {
  return apiFetch('/scheduler');
}

export async function fetchAgentRuns() {
  return apiFetch('/agent-runs');
}

export async function fetchLLMLinks() {
  return apiFetch('/llm-links');
}

// ─── Agent Trigger Endpoints ───

export async function triggerPhase(phase, suburbIds = null) {
  return apiFetch(`/run/${phase}`, {
    method: 'POST',
    body: JSON.stringify({ suburb_ids: suburbIds }),
  });
}

// ─── Tool Endpoints ───

export async function fetchPlanning(address) {
  return apiFetch(`/tools/planning/${encodeURIComponent(address)}`);
}

export async function fetchSatellite(lat, lng) {
  return apiFetch(`/tools/satellite?lat=${lat}&lng=${lng}`);
}

export async function fetchHazards(lat, lng) {
  return apiFetch(`/tools/hazards?lat=${lat}&lng=${lng}`);
}

export async function fetchSlope(lat, lng) {
  return apiFetch(`/tools/slope?lat=${lat}&lng=${lng}`);
}
