import React from 'react';
import { Provider } from 'react-redux';
import { store } from './store/store';
import InteractionForm from './components/InteractionForm';
import ChatPanel from './components/ChatPanel';
import './App.css';

function App() {
  return (
    <Provider store={store}>
      <div className="app-shell">
        <header className="app-nav">
          <div className="nav-brand">
            <div className="nav-logo">Rx</div>
            <span className="nav-title">PharmaSync CRM</span>
            <span className="nav-module">HCP Module</span>
          </div>
          <nav className="nav-links">
            <a href="#0" className="nav-link active">Log Interaction</a>
            <a href="#0" className="nav-link">HCP Directory</a>
            <a href="#0" className="nav-link">Reports</a>
          </nav>
          <div className="nav-user">
            <div className="user-avatar">FR</div>
            <span className="user-name">Field Rep</span>
          </div>
        </header>
        <main className="split-screen">
          <div className="panel-left">
            <InteractionForm />
          </div>
          <div className="panel-right">
            <ChatPanel />
          </div>
        </main>
      </div>
    </Provider>
  );
}

export default App;
