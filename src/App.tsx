import { useEffect, useMemo, useRef, useState } from 'react';

type ChatMessage = {
  role: 'assistant' | 'user';
  text: string;
};

type SpeechRecognitionCtor = new () => SpeechRecognition;

declare global {
  interface Window {
    SpeechRecognition?: SpeechRecognitionCtor;
    webkitSpeechRecognition?: SpeechRecognitionCtor;
  }

  interface SpeechRecognition extends EventTarget {
    lang: string;
    interimResults: boolean;
    continuous: boolean;
    onresult: ((event: SpeechRecognitionEvent) => void) | null;
      onerror: ((event: SpeechRecognitionErrorEvent) => void) | null;
    onend: (() => void) | null;
    start: () => void;
    stop: () => void;
  }

  interface SpeechRecognitionEvent {
    results: SpeechRecognitionResultList;
  }

  interface SpeechRecognitionErrorEvent {
    error: string;
  }
}

const initialMessages: ChatMessage[] = [
  { role: 'assistant', text: 'System ready. Sign in to connect to OFFSPACE.' },
];

function App() {
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [command, setCommand] = useState('');
  const [voiceStatus, setVoiceStatus] = useState('Voice ready');
  const [isListening, setIsListening] = useState(false);
  const [wakeDetected, setWakeDetected] = useState(false);
  const [authToken, setAuthToken] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [backendReady, setBackendReady] = useState(false);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  const speechRecognitionSupport = useMemo(() => {
    return Boolean(window.SpeechRecognition || window.webkitSpeechRecognition);
  }, []);

  useEffect(() => {
    if (!speechRecognitionSupport) {
      setVoiceStatus('Microphone support unavailable in this browser');
    }
  }, [speechRecognitionSupport]);

  useEffect(() => {
    let cancelled = false;
    let attempts = 0;

    const waitForBackend = async () => {
      while (!cancelled && attempts < 40) {
        attempts += 1;
        try {
          const response = await fetch('http://127.0.0.1:8000/api/v1/health', { cache: 'no-store' });
          if (response.ok) {
            if (!cancelled) {
              setBackendReady(true);
              setError('');
              setMessages([{ role: 'assistant', text: 'Backend connected. System ready.' }]);
            }
            return;
          }
        } catch {
          // Retry until the Tauri lifecycle reports a readiness timeout.
        }
        await new Promise((resolve) => window.setTimeout(resolve, 250));
      }
      if (!cancelled) {
        setBackendReady(false);
        setError('OFFSPACE backend did not become ready. Restart the application or check %LOCALAPPDATA%\\Offspace\\backend.log.');
      }
    };

    void waitForBackend();
    return () => {
      cancelled = true;
    };
  }, []);

  const speak = (text: string) => {
    if (!('speechSynthesis' in window)) {
      setVoiceStatus('Text-to-speech is unavailable in this browser');
      return;
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.onerror = () => setVoiceStatus('Text-to-speech failed');
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
  };

  const startVoiceCapture = () => {
    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!Recognition) {
      setVoiceStatus('Speech recognition unsupported by this browser');
      return;
    }

    const recognition = new Recognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.continuous = false;
    recognition.onresult = (event) => {
      const transcript = Array.from(event.results)
        .map((result) => result[0]?.transcript ?? '')
        .join(' ')
        .trim();

      if (!transcript) {
        setVoiceStatus('No speech was recognized');
        return;
      }

      setCommand(transcript);
      const lowerTranscript = transcript.toLowerCase();

      if (lowerTranscript.includes('hey offspace')) {
        setWakeDetected(true);
        setVoiceStatus('Wake phrase detected. Listening for command.');
        speak('Hey Offspace. I am ready.');
      } else {
        setVoiceStatus(`Captured: ${transcript}`);
      }
    };

    recognition.onerror = (event) => {
      setIsListening(false);
      const message = event.error === 'not-allowed' || event.error === 'service-not-allowed'
        ? 'Microphone permission was denied'
        : event.error === 'audio-capture'
          ? 'No microphone is available'
          : event.error === 'no-speech'
            ? 'No speech was detected'
            : 'Speech recognition failed; check the browser speech service';
      setVoiceStatus(message);
      setError(message);
    };

    recognition.onend = () => {
      setIsListening(false);
      if (!wakeDetected) {
        setVoiceStatus('Voice capture stopped');
      }
    };

    recognitionRef.current = recognition;
    recognition.start();
    setIsListening(true);
    setVoiceStatus('Listening for “Hey Offspace”');
  };

  const stopVoiceCapture = () => {
    recognitionRef.current?.stop();
    setIsListening(false);
    setVoiceStatus('Voice channel muted');
  };

  const apiRequest = async (path: string, init: RequestInit = {}) => {
    const headers = new Headers(init.headers);
    headers.set('Content-Type', 'application/json');
    if (authToken) {
      headers.set('Authorization', `Bearer ${authToken}`);
    }
    const response = await fetch(`http://127.0.0.1:8000${path}`, { ...init, headers });
    const body = await response.json().catch(() => ({ error: 'The server returned an invalid response.' }));
    if (!response.ok) {
      throw new Error(body.error || body.detail || 'OFFSPACE request failed.');
    }
    return body;
  };

  const signIn = async () => {
    if (!backendReady) {
      setError('OFFSPACE backend is not ready yet.');
      return;
    }
    if (!email.trim() || !password) {
      setError('Email and password are required.');
      return;
    }
    setIsSubmitting(true);
    setError('');
    try {
      const body = await apiRequest('/api/v1/users/login', {
        method: 'POST',
        body: JSON.stringify({ email: email.trim(), password }),
      });
      setAuthToken(body.access_token);
      setMessages([{ role: 'assistant', text: 'Connected to OFFSPACE.' }]);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Sign-in failed.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const submitCommand = async () => {
    const trimmed = command.trim();
    if (!trimmed) {
      return;
    }
    if (!authToken) {
      setError('Sign in before sending a command.');
      return;
    }
    setIsSubmitting(true);
    setError('');
    setMessages((current) => [...current, { role: 'user', text: trimmed }]);
    setCommand('');
    try {
      const body = await apiRequest('/api/v1/chat/message', {
        method: 'POST',
        body: JSON.stringify({ prompt: trimmed }),
      });
      setMessages((current) => [...current, { role: 'assistant', text: body.response }]);
      speak(body.response);
    } catch (caught) {
      const message = caught instanceof Error ? caught.message : 'OFFSPACE could not process the command.';
      setError(message);
      setMessages((current) => [...current, { role: 'assistant', text: message }]);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="app-shell">
      <aside className="sidebar-panel">
        <div className="brand-block">
          <div className="brand-signal" />
          <div>
            <p className="eyebrow">PRIVATE AI CORE</p>
            <h1>OFFSPACE</h1>
          </div>
        </div>

        <nav className="side-nav">
          <button className="nav-item active">Dashboard</button>
          <button className="nav-item">Live Session</button>
          <button className="nav-item">Agents</button>
          <button className="nav-item">Workflows</button>
        </nav>

        <div className="panel-card settings-card">
          <div className="panel-title-row">
            <span>Settings</span>
            <span className="status-pill">Synced</span>
          </div>
          <div className="settings-list">
            <div>Wake phrase <strong>“Hey Offspace”</strong></div>
            <div>Voice input <strong>{speechRecognitionSupport ? 'Enabled' : 'Unavailable'}</strong></div>
            <div>Memory mode <strong>Local-first</strong></div>
          </div>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div>
            <p className="eyebrow">AI CORE ANIMATION</p>
            <h2>Autonomous command engine</h2>
          </div>
          <div className="topbar-actions">
            <button className="ghost-button" onClick={isListening ? stopVoiceCapture : startVoiceCapture}>
              {isListening ? 'Mute Mic' : 'Voice'}
            </button>
            <button className="primary-button">Start Session</button>
          </div>
        </header>

        <section className="hero-grid">
          <div className="ai-core-card">
            <div className="pulse-ring">
              <div className="pulse-center">AI</div>
            </div>
            <div className="ai-core-copy">
              <p className="eyebrow">CORE OUTPUT</p>
              <h3>Realtime reasoning matrix</h3>
              <p>
                Context layering, workflow orchestration, and personalized memory routing are all streaming through
                the shielded neural surface.
              </p>
              <div className="voice-status">{voiceStatus}</div>
            </div>
          </div>

          <div className="chat-card">
            <div className="panel-title-row">
              <span>Chat System</span>
              <span className="status-pill">{backendReady ? 'Connected' : 'Offline'}</span>
            </div>
            <div className="messages">
              {messages.map((message, index) => (
                <div key={index} className={`message ${message.role}`}>
                  {message.text}
                </div>
              ))}
            </div>
            {error && <div className="voice-status" role="alert">{error}</div>}
            <div className="composer">
              {!authToken ? (
                <>
                  <input
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    placeholder="Email"
                    type="email"
                  />
                  <input
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    placeholder="Password"
                    type="password"
                  />
                  <button className="primary-button" onClick={signIn} disabled={isSubmitting}>
                    {isSubmitting ? 'Signing in...' : 'Sign in'}
                  </button>
                </>
              ) : (
                <>
                  <input
                    value={command}
                    onChange={(event) => setCommand(event.target.value)}
                    placeholder="Ask Offspace to plan, recall, or automate..."
                  />
                  <button className="primary-button" onClick={submitCommand} disabled={isSubmitting}>
                    {isSubmitting ? 'Sending...' : 'Send'}
                  </button>
                </>
              )}
            </div>
          </div>
        </section>

        <section className="bottom-grid">
          <div className="panel-card memory-card">
            <div className="panel-title-row">
              <span>Memory Panel</span>
              <span className="status-pill">3 entries</span>
            </div>
            <ul>
              <li>Personal workflow preference: async deep work blocks</li>
              <li>Owner location: Rwanda</li>
              <li>Recent goal: prepare a desktop AI launch</li>
            </ul>
          </div>

          <div className="panel-card voice-card">
            <div className="panel-title-row">
              <span>Voice Button</span>
              <span className="status-pill">{wakeDetected ? 'Wake phrase detected' : 'Ready'}</span>
            </div>
            <button className="voice-button" onClick={isListening ? stopVoiceCapture : startVoiceCapture}>
              {isListening ? 'Stop' : 'Mic'}
            </button>
            <p>Tap to activate the wake channel or voice command stream.</p>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
