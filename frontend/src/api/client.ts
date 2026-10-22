import axios from 'axios';
import type {
  SignalGenerateRequest,
  SignalResponse,
  SignalListItem,
  AnalysisRequest,
  AnalysisResponse,
  ExportResponse,
} from '../types/api';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const signalApi = {
  generate: (request: SignalGenerateRequest): Promise<SignalResponse> =>
    api.post('/signals/generate', request).then((res) => res.data),

  list: (params?: { skip?: number; limit?: number; signal_type?: string }): Promise<SignalListItem[]> =>
    api.get('/signals', { params }).then((res) => res.data),

  get: (id: number): Promise<SignalResponse> =>
    api.get(`/signals/${id}`).then((res) => res.data),

  delete: (id: number): Promise<void> =>
    api.delete(`/signals/${id}`).then((res) => res.data),

  analyze: (request: AnalysisRequest): Promise<AnalysisResponse> =>
    api.post('/signals/analyze', request).then((res) => res.data),

  listAnalyses: (signalId: number): Promise<AnalysisResponse[]> =>
    api.get(`/signals/${signalId}/analyses`).then((res) => res.data),

  export: (signalId: number, format: 'json' | 'csv' | 'wav' = 'json', includeAnalysis = false): Promise<ExportResponse> =>
    api.get(`/signals/${signalId}/export`, { params: { format, include_analysis: includeAnalysis } }).then((res) => res.data),
};

export default api;