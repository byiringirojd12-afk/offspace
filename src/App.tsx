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
    onend: (() => void) | null;
    start: () => void;
    stop: () => void;
  }

  interface SpeechRecognitionEvent {
    results: SpeechRecognitionResultList;
  }
}

const initialMessages: ChatMessage[] = [
  {
    role: 'assistant',
    text: 'System online. I can help you manage priorities, automate tasks, and keep your context in sync.',
  },
  {
    role: 'user',
    text: 'Summarize the key action items for the next work session.',
  },
];

function App() {
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [command, setCommand] = useState('');
  const [voiceStatus, setVoiceStatus] = useState('Voice ready');
  const [isListening, setIsListening] = useState(false);
  const [wakeDetected, setWakeDetected] = useState(false);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  const speechRecognitionSupport = useMemo(() => {
    return Boolean(window.SpeechRecognition || window.webkitSpeechRecognition);
  }, []);

  useEffect(() => {
    if (!speechRecognitionSupport) {
      setVoiceStatus('Microphone support unavailable in this browser');
    }
  }, [speechRecognitionSupport]);

  const speak = (text: string) => {
    if (!('speechSynthesis' in window)) {
      return;
    }

    const utterance = new SpeechSynthesisUtterance(text);
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

  const submitCommand = () => {
    const trimmed = command.trim();
    if (!trimmed) {
      return;
    }

    setMessages((current) => [
      ...current,
      { role: 'user', text: trimmed },
      {
        role: 'assistant',
        text: `Command received: ${trimmed}. Safe automation will require confirmation for destructive actions.`,
      },
    ]);
    setCommand('');
    speak('Command received');
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
              <span className="status-pill">Connected</span>
            </div>
            <div className="messages">
              {messages.map((message, index) => (
                <div key={index} className={`message ${message.role}`}>
                  {message.text}
                </div>
              ))}
            </div>
            <div className="composer">
              <input
                value={command}
                onChange={(event) => setCommand(event.target.value)}
                placeholder="Ask Offspace to plan, recall, or automate..."
              />
              <button className="primary-button" onClick={submitCommand}>Send</button>
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
