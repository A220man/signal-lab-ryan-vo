import { useState, useRef, useEffect } from 'react';
import { useSignals, useSignal, useAnalysis, useExport } from '../hooks/useSignals';
import type { SignalType, SignalResponse, SignalListItem, AnalysisResponse } from '../types/api';
import { Chart, registerables } from 'chart.js';
import 'chart.js/auto';

Chart.register(...registerables);

export function SignalGenerator() {
  const { generateSignal, loading, error } = useSignals();
  const [name, setName] = useState('My Signal');
  const [signalType, setSignalType] = useState<SignalType>('sine');
  const [sampleRate, setSampleRate] = useState(44100);
  const [duration, setDuration] = useState(1.0);
  const [frequency, setFrequency] = useState(440);
  const [amplitude, setAmplitude] = useState(1.0);
  const [generatedSignal, setGeneratedSignal] = useState<SignalResponse | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const result = await generateSignal({
      name,
      signal_type: signalType,
      sample_rate: sampleRate,
      duration,
      frequency: signalType !== 'noise' ? frequency : undefined,
      amplitude,
      parameters: signalType === 'chirp' ? { f0: 20, f1: 2000, method: 'linear' } : undefined,
    });
    if (result) setGeneratedSignal(result);
  };

  return (
    <div className="card">
      <h2>Generate Signal</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="name">Name</label>
          <input
            id="name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="signalType">Signal Type</label>
          <select
            id="signalType"
            value={signalType}
            onChange={(e) => setSignalType(e.target.value as SignalType)}
          >
            <option value="sine">Sine Wave</option>
            <option value="square">Square Wave</option>
            <option value="noise">Noise</option>
            <option value="chirp">Chirp</option>
          </select>
        </div>
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="sampleRate">Sample Rate (Hz)</label>
            <input
              id="sampleRate"
              type="number"
              value={sampleRate}
              onChange={(e) => setSampleRate(Number(e.target.value))}
              min="1000"
              max="192000"
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="duration">Duration (s)</label>
            <input
              id="duration"
              type="number"
              value={duration}
              onChange={(e) => setDuration(Number(e.target.value))}
              min="0.01"
              max="3600"
              step="0.01"
              required
            />
          </div>
        </div>
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="frequency">Frequency (Hz)</label>
            <input
              id="frequency"
              type="number"
              value={frequency}
              onChange={(e) => setFrequency(Number(e.target.value))}
              min="1"
              max="96000"
              disabled={signalType === 'noise'}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="amplitude">Amplitude</label>
            <input
              id="amplitude"
              type="number"
              value={amplitude}
              onChange={(e) => setAmplitude(Number(e.target.value))}
              min="0.01"
              max="10"
              step="0.01"
              required
            />
          </div>
        </div>
        <button type="submit" disabled={loading}>
          {loading ? 'Generating...' : 'Generate Signal'}
        </button>
      </form>
      {error && <div className="error">{error}</div>}
      {generatedSignal && (
        <div className="success">
          <h3>Signal Generated: {generatedSignal.name}</h3>
          <p>ID: {generatedSignal.id} | Type: {generatedSignal.signal_type} | Samples: {generatedSignal.data.length}</p>
          <SignalChart data={generatedSignal.data} sampleRate={generatedSignal.sample_rate} />
        </div>
      )}
    </div>
  );
}

export function SignalChart({ data, sampleRate }: { data: number[]; sampleRate: number }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const chartRef = useRef<Chart | null>(null);

  useEffect(() => {
    if (!canvasRef.current || data.length === 0) return;

    const maxPoints = 2000;
    const step = Math.max(1, Math.floor(data.length / maxPoints));
    const plotData = data.filter((_, i) => i % step === 0);
    const labels = plotData.map((_, i) => (i * step) / sampleRate);

    if (chartRef.current) {
      chartRef.current.data.labels = labels;
      chartRef.current.data.datasets[0].data = plotData;
      chartRef.current.update('none');
    } else {
      chartRef.current = new Chart(canvasRef.current, {
        type: 'line',
        data: {
          labels,
          datasets: [
            {
              label: 'Amplitude',
              data: plotData,
              borderColor: 'rgb(59, 130, 246)',
              backgroundColor: 'rgba(59, 130, 246, 0.1)',
              borderWidth: 1,
              pointRadius: 0,
              tension: 0.1,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: false,
          interaction: { intersect: false, mode: 'index' },
          scales: {
            x: { title: { display: true, text: 'Time (s)' } },
            y: { title: { display: true, text: 'Amplitude' } },
          },
        },
      });
    }

    return () => {
      chartRef.current?.destroy();
      chartRef.current = null;
    };
  }, [data, sampleRate]);

  return <canvas ref={canvasRef} height={200} />;
}

export function SignalList() {
  const { signals, loading, error, fetchSignals, deleteSignal } = useSignals();

  return (
    <div className="card">
      <div className="card-header">
        <h2>Signals</h2>
        <button onClick={fetchSignals} disabled={loading}>
          {loading ? 'Loading...' : 'Refresh'}
        </button>
      </div>
      {error && <div className="error">{error}</div>}
      {signals.length === 0 && !loading && (
        <div className="empty">No signals generated yet. Create one using the generator.</div>
      )}
      <div className="signal-list">
        {signals.map((signal) => (
          <SignalListItem key={signal.id} signal={signal} onDelete={deleteSignal} />
        ))}
      </div>
    </div>
  );
}

interface SignalListItemProps {
  signal: SignalListItem;
  onDelete: (id: number) => Promise<boolean>;
}

function SignalListItem({ signal, onDelete }: SignalListItemProps) {
  const [deleting, setDeleting] = useState(false);

  const handleDelete = async () => {
    if (!window.confirm(`Delete "${signal.name}"?`)) return;
    setDeleting(true);
    await onDelete(signal.id);
    setDeleting(false);
  };

  return (
    <div className="signal-item">
      <div className="signal-info">
        <strong>{signal.name}</strong>
        <span className="signal-meta">
          {signal.signal_type} • {signal.sample_rate} Hz • {signal.duration}s
          {signal.frequency && ` • ${signal.frequency} Hz`}
        </span>
      </div>
      <div className="signal-actions">
        <button onClick={handleDelete} disabled={deleting} className="btn-danger">
          {deleting ? 'Deleting...' : 'Delete'}
        </button>
      </div>
    </div>
  );
}

export function SignalDetail({ signalId }: { signalId: number }) {
  const { signal, loading, error } = useSignal(signalId);
  const { analyses, runAnalysis, loading: analysisLoading } = useAnalysis(signalId);
  const { exportSignal, loading: exportLoading } = useExport();

  const handleAnalysis = async (type: 'fft' | 'spectrogram' | 'statistics') => {
    await runAnalysis({ signal_id: signalId, analysis_type: type });
  };

  const handleExport = async (format: 'json' | 'csv' | 'wav') => {
    const result = await exportSignal(signalId, format, true);
    if (result) {
      const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${signal?.name || 'signal'}.${format}`;
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  if (loading) return <div className="loading">Loading signal...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!signal) return <div className="error">Signal not found</div>;

  return (
    <div className="card">
      <div className="card-header">
        <h2>{signal.name}</h2>
        <div className="actions">
          <button onClick={() => handleExport('json')} disabled={exportLoading}>Export JSON</button>
          <button onClick={() => handleExport('csv')} disabled={exportLoading}>Export CSV</button>
        </div>
      </div>

      <div className="signal-meta-grid">
        <div><strong>Type:</strong> {signal.signal_type}</div>
        <div><strong>Sample Rate:</strong> {signal.sample_rate} Hz</div>
        <div><strong>Duration:</strong> {signal.duration} s</div>
        <div><strong>Frequency:</strong> {signal.frequency ?? 'N/A'} Hz</div>
        <div><strong>Amplitude:</strong> {signal.amplitude}</div>
        <div><strong>Samples:</strong> {signal.data.length}</div>
      </div>

      <SignalChart data={signal.data} sampleRate={signal.sample_rate} />

      <div className="analysis-section">
        <h3>Analysis</h3>
        <div className="analysis-buttons">
          <button onClick={() => handleAnalysis('fft')} disabled={analysisLoading}>FFT</button>
          <button onClick={() => handleAnalysis('spectrogram')} disabled={analysisLoading}>Spectrogram</button>
          <button onClick={() => handleAnalysis('statistics')} disabled={analysisLoading}>Statistics</button>
        </div>
        {analyses.map((analysis) => (
          <AnalysisResult key={analysis.id} analysis={analysis} />
        ))}
      </div>
    </div>
  );
}

function AnalysisResult({ analysis }: { analysis: AnalysisResponse }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="analysis-result">
      <div className="analysis-header" onClick={() => setExpanded(!expanded)}>
        <strong>{analysis.analysis_type.toUpperCase()}</strong>
        <span>{new Date(analysis.created_at).toLocaleString()}</span>
      </div>
      {expanded && (
        <div className="analysis-data">
          <pre>{JSON.stringify(analysis.result_data, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}