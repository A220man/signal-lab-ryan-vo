import { BrowserRouter, Routes, Route, Link, useParams } from 'react-router-dom';
import { SignalGenerator, SignalList, SignalDetail } from './components/SignalComponents';
// import './App.css';

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <header className="app-header">
          <h1>Signal Lab</h1>
          <nav>
            <Link to="/">Generate</Link>
            <Link to="/signals">Signals</Link>
          </nav>
        </header>
        <main className="app-main">
          <Routes>
            <Route path="/" element={<SignalGenerator />} />
            <Route path="/signals" element={<SignalList />} />
            <Route path="/signals/:id" element={<SignalDetailPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

function SignalDetailPage() {
  const { id } = useParams<{ id: string }>();
  return <SignalDetail signalId={Number(id)} />;
}

export default App;