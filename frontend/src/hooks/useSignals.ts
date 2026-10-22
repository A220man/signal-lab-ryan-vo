import { useState, useCallback, useEffect } from 'react';
import { signalApi } from '../api/client';
import type { SignalListItem, SignalResponse, AnalysisResponse, ExportResponse } from '../types/api';

export function useSignals() {
  const [signals, setSignals] = useState<SignalListItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSignals = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await signalApi.list();
      setSignals(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch signals');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSignals();
  }, [fetchSignals]);

  const generateSignal = useCallback(async (request: Parameters<typeof signalApi.generate>[0]): Promise<SignalResponse | null> => {
    setLoading(true);
    setError(null);
    try {
      const signal = await signalApi.generate(request);
      await fetchSignals();
      return signal;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate signal');
      return null;
    } finally {
      setLoading(false);
    }
  }, [fetchSignals]);

  const deleteSignal = useCallback(async (id: number): Promise<boolean> => {
    setLoading(true);
    setError(null);
    try {
      await signalApi.delete(id);
      await fetchSignals();
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete signal');
      return false;
    } finally {
      setLoading(false);
    }
  }, [fetchSignals]);

  return { signals, loading, error, fetchSignals, generateSignal, deleteSignal };
}

export function useSignal(id: number | null) {
  const [signal, setSignal] = useState<SignalResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSignal = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const data = await signalApi.get(id);
      setSignal(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch signal');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchSignal();
  }, [fetchSignal]);

  return { signal, loading, error, refetch: fetchSignal };
}

export function useAnalysis(signalId: number | null) {
  const [analyses, setAnalyses] = useState<AnalysisResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalyses = useCallback(async () => {
    if (!signalId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await signalApi.listAnalyses(signalId);
      setAnalyses(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch analyses');
    } finally {
      setLoading(false);
    }
  }, [signalId]);

  useEffect(() => {
    fetchAnalyses();
  }, [fetchAnalyses]);

  const runAnalysis = useCallback(async (request: Parameters<typeof signalApi.analyze>[0]): Promise<AnalysisResponse | null> => {
    setLoading(true);
    setError(null);
    try {
      const analysis = await signalApi.analyze(request);
      await fetchAnalyses();
      return analysis;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to run analysis');
      return null;
    } finally {
      setLoading(false);
    }
  }, [fetchAnalyses]);

  return { analyses, loading, error, runAnalysis, refetch: fetchAnalyses };
}

export function useExport() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const exportSignal = useCallback(async (
    signalId: number,
    format: 'json' | 'csv' | 'wav' = 'json',
    includeAnalysis = false
  ): Promise<ExportResponse | null> => {
    setLoading(true);
    setError(null);
    try {
      const data = await signalApi.export(signalId, format, includeAnalysis);
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to export signal');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return { exportSignal, loading, error };
}