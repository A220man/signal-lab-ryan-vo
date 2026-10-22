import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { SignalGenerator } from './SignalComponents';
import { BrowserRouter } from 'react-router-dom';
import { signalApi } from '../api/client';

// Mock the API client
vi.mock('../api/client', () => ({
  signalApi: {
    generate: vi.fn(),
    list: vi.fn(),
    get: vi.fn(),
    delete: vi.fn(),
    analyze: vi.fn(),
    listAnalyses: vi.fn(),
    export: vi.fn(),
  },
}));

const renderWithRouter = (component: React.ReactNode) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('SignalGenerator', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the signal generator form', () => {
    renderWithRouter(<SignalGenerator />);
    expect(screen.getByText('Generate Signal')).toBeInTheDocument();
    expect(screen.getByLabelText('Name')).toBeInTheDocument();
    expect(screen.getByLabelText('Signal Type')).toBeInTheDocument();
    expect(screen.getByLabelText('Sample Rate (Hz)')).toBeInTheDocument();
    expect(screen.getByLabelText('Duration (s)')).toBeInTheDocument();
  });

  it('renders all signal type options', () => {
    renderWithRouter(<SignalGenerator />);
    const select = screen.getByLabelText('Signal Type') as HTMLSelectElement;
    expect(select.value).toBe('sine');
    expect(screen.getByText('Sine Wave')).toBeInTheDocument();
    expect(screen.getByText('Square Wave')).toBeInTheDocument();
    expect(screen.getByText('Noise')).toBeInTheDocument();
    expect(screen.getByText('Chirp')).toBeInTheDocument();
  });

  it('disables frequency input for noise type', () => {
    renderWithRouter(<SignalGenerator />);
    const select = screen.getByLabelText('Signal Type') as HTMLSelectElement;
    fireEvent.change(select, { target: { value: 'noise' } });
    const freqInput = screen.getByLabelText('Frequency (Hz)') as HTMLInputElement;
    expect(freqInput.disabled).toBe(true);
  });
});