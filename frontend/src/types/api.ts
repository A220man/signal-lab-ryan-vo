export type SignalType = 'sine' | 'square' | 'noise' | 'chirp';

export interface SignalGenerateRequest {
  name: string;
  signal_type: SignalType;
  sample_rate: number;
  duration: number;
  frequency?: number;
  amplitude: number;
  parameters?: Record<string, any>;
}

export interface SignalResponse {
  id: number;
  name: string;
  signal_type: SignalType;
  sample_rate: number;
  duration: number;
  frequency?: number;
  amplitude: number;
  parameters?: Record<string, any>;
  data: number[];
  created_at: string;
}

export interface SignalListItem {
  id: number;
  name: string;
  signal_type: SignalType;
  sample_rate: number;
  duration: number;
  frequency?: number;
  amplitude: number;
  created_at: string;
}

export interface AnalysisRequest {
  signal_id: number;
  analysis_type: 'fft' | 'spectrogram' | 'statistics';
  parameters?: Record<string, any>;
}

export interface AnalysisResponse {
  id: number;
  signal_id: number;
  analysis_type: string;
  result_data: Record<string, any>;
  created_at: string;
}

export interface ExportResponse {
  id: number;
  name: string;
  signal_type: SignalType;
  sample_rate: number;
  duration: number;
  frequency?: number;
  amplitude: number;
  parameters?: Record<string, any>;
  data: number[];
  created_at: string;
  analyses?: AnalysisResponse[];
}