import { useState, useEffect, useCallback } from 'react';
import * as api from '../api/client';
import * as staticData from '../data/suburbData';

/**
 * React hook for loading data from the FastAPI backend.
 * Falls back to static seed data if the API is unavailable.
 */

// Global cache to avoid re-fetching on tab switches
const cache = {};

function useApiData(key, fetcher, fallback, deps = []) {
  const [data, setData] = useState(cache[key] ?? fallback);
  const [loading, setLoading] = useState(!cache[key]);
  const [error, setError] = useState(null);
  const [source, setSource] = useState(cache[key] ? 'cache' : 'loading');

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetcher();
      if (result !== null && result !== undefined) {
        const resolved = Array.isArray(result) ? result : (typeof result === 'object' ? result : fallback);
        cache[key] = resolved;
        setData(resolved);
        setSource('api');
      } else {
        // API returned null, use fallback
        setData(fallback);
        setSource('fallback');
      }
    } catch (err) {
      console.warn(`useApiData(${key}) failed:`, err);
      setData(fallback);
      setSource('fallback');
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [key, ...deps]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { data, loading, error, source, refresh };
}

// ═══════════════════════════════════════════════
// Exported hooks with fallback to static data
// ═══════════════════════════════════════════════

export function useSuburbs() {
  return useApiData(
    'suburbs',
    api.fetchSuburbs,
    staticData.SUBURBS
  );
}

export function useSuburb(suburbId) {
  const fallback = staticData.SUBURBS.find(s => s.id === suburbId) || {};
  return useApiData(
    `suburb-${suburbId}`,
    () => api.fetchSuburb(suburbId),
    fallback,
    [suburbId]
  );
}

export function useDARecords(suburbId) {
  return useApiData(
    `da-records-${suburbId}`,
    () => api.fetchDARecords(suburbId),
    staticData.DA_RECORDS[suburbId] || [],
    [suburbId]
  );
}

export function useProperties(suburbId) {
  return useApiData(
    `properties-${suburbId}`,
    () => api.fetchProperties(suburbId),
    staticData.SCOUTED_PROPERTIES[suburbId] || [],
    [suburbId]
  );
}

export function useHotStreets(suburbId) {
  return useApiData(
    `hot-streets-${suburbId}`,
    () => api.fetchHotStreets(suburbId),
    staticData.HOT_STREETS[suburbId] || [],
    [suburbId]
  );
}

export function usePopulation(suburbId) {
  return useApiData(
    `population-${suburbId}`,
    () => api.fetchPopulation(suburbId),
    staticData.POPULATION_FORECAST[suburbId] || [],
    [suburbId]
  );
}

export function useDATrends(suburbId) {
  return useApiData(
    `da-trends-${suburbId}`,
    () => api.fetchDATrends(suburbId),
    staticData.DA_MONTHLY_TREND[suburbId] || [],
    [suburbId]
  );
}

export function useHealth() {
  return useApiData(
    'health',
    api.fetchHealth,
    { status: 'unknown', scheduler: { running: false, jobs: [] } }
  );
}

export function useScheduler() {
  return useApiData(
    'scheduler',
    api.fetchScheduler,
    { running: false, jobs: [] }
  );
}

export function useAgentRuns() {
  return useApiData(
    'agent-runs',
    api.fetchAgentRuns,
    []
  );
}

export function useLLMLinks() {
  return useApiData(
    'llm-links',
    api.fetchLLMLinks,
    staticData.LLM_LINKS
  );
}
