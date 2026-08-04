type ChatMessage = {
  role: 'assistant' | 'user';
  text: string;
};

const sampleMessages: ChatMessage[] = [
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
            <div>Wake phrase <strong>"Hey Offspace"</strong></div>
            <div>Voice input <strong>Enabled</strong></div>
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
            <button className="ghost-button">Voice</button>
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
            </div>
          </div>

          <div className="chat-card">
            <div className="panel-title-row">
              <span>Chat System</span>
              <span className="status-pill">Connected</span>
            </div>
            <div className="messages">
              {sampleMessages.map((message, index) => (
                <div key={index} className={`message ${message.role}`}>
                  {message.text}
                </div>
              ))}
            </div>
            <div className="composer">
              <input placeholder="Ask Offspace to plan, recall, or automate..." />
              <button className="primary-button">Send</button>
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
              <span className="status-pill">Ready</span>
            </div>
            <button className="voice-button">Mic</button>
            <p>Tap to activate the wake channel or voice command stream.</p>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
