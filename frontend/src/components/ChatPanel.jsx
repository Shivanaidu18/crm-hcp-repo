import React, { useEffect, useRef, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { addMessage, clearChat, setLoading } from '../store/chatSlice';
import {
  clearFieldHighlights,
  setAISuggestions,
  setFollowupMeta,
  setMissingFields,
  updateFields,
} from '../store/interactionSlice';
import { chatWithAgent } from '../services/api';
import './ChatPanel.css';

const QUICK_PROMPTS = [
  'Met Dr. Smith today, discussed Product X efficacy, positive sentiment, shared brochures',
  'Change only the sentiment to Negative',
  'Add follow-up action: schedule a call next Friday',
  'Suggest follow-up actions for this interaction',
  'Search for Dr. Priya Mehta',
];

function MessageBubble({ msg }) {
  const isUser = msg.role === 'user';
  return (
    <div className={`message-bubble ${isUser ? 'user' : 'assistant'} fade-in`}>
      <div className={`chat-avatar ${isUser ? 'user-avatar-bubble' : 'bot-avatar'}`}>
        {isUser ? 'You' : 'AI'}
      </div>
      <div className={`bubble-content ${isUser ? 'user-bubble' : 'assistant-bubble'}`}>
        <div className="bubble-role">{isUser ? 'You' : 'AI Assistant'}</div>
        <div className="bubble-text">{String(msg.content || '')}</div>
        {msg.timestamp && <div className="bubble-time">{msg.timestamp}</div>}
      </div>
    </div>
  );
}

export default function ChatPanel() {
  const dispatch = useDispatch();
  const messages = useSelector((s) => s.chat.messages);
  const isLoading = useSelector((s) => s.chat.isLoading);
  const form = useSelector((s) => s.interaction);
  const [input, setInput] = useState('');
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const sendMessage = async (text) => {
    const content = (typeof text === 'string' ? text : input).trim();
    if (!content || isLoading) return;

    const userMsg = {
      role: 'user',
      content,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    dispatch(addMessage(userMsg));
    dispatch(setLoading(true));
    setInput('');

    try {
      const history = [...messages, userMsg].map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const currentForm = {
        interaction_uid: form.interaction_uid,
        form_name: form.form_name,
        hcp_name: form.hcp_name,
        interaction_type: form.interaction_type,
        date: form.date,
        time: form.time,
        attendees: form.attendees,
        topics_discussed: form.topics_discussed,
        materials_shared: form.materials_shared,
        samples_distributed: form.samples_distributed,
        sentiment: form.sentiment,
        outcomes: form.outcomes,
        follow_up_actions: form.follow_up_actions,
      };

      const result = await chatWithAgent(history, currentForm);
      const tr = result.tool_result;

      if (tr?.fields && Object.keys(tr.fields).length > 0) {
        dispatch(updateFields(tr.fields));
        window.clearTimeout(window.__crmHighlightTimer);
        window.__crmHighlightTimer = window.setTimeout(() => {
          dispatch(clearFieldHighlights());
        }, 2200);
      }

      if (Array.isArray(tr?.missing_fields)) {
        dispatch(setMissingFields(tr.missing_fields));
      }

      if (tr?.suggestions?.length) {
        dispatch(setAISuggestions(tr.suggestions));
      }

      dispatch(setFollowupMeta({
        priority: tr?.priority,
        nextDate: tr?.next_follow_up_date || tr?.next_meeting,
      }));

      dispatch(addMessage({
        role: 'assistant',
        content: tr?.message || result.response,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        toolAction: tr?.action,
      }));
    } catch (err) {
      const detail = err?.response?.data?.detail;
      dispatch(addMessage({
        role: 'assistant',
        content: detail ? `Request failed: ${detail}` : 'Connection error. Please check that the backend is running and the LLM API key is configured.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }));
    } finally {
      dispatch(setLoading(false));
      inputRef.current?.focus();
    }
  };

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chat-panel">
      <div className="chat-header">
        <div className="chat-header-left">
          <div className="bot-icon">AI</div>
          <div>
            <div className="chat-title">AI Assistant</div>
            <div className="chat-subtitle">Use chat to control the form</div>
          </div>
        </div>
        <div className="chat-header-right">
          <div className="status-dot" />
          <button className="btn-clear" onClick={() => dispatch(clearChat())} title="Clear chat">x</button>
        </div>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-welcome fade-in">
            <div className="welcome-card">
              <div className="welcome-icon">AI</div>
              <p>Describe the HCP interaction, ask for edits, search HCPs, analyze sentiment, or request follow-up suggestions.</p>
            </div>

            <div className="quick-prompts">
              <div className="qp-label">Quick prompts:</div>
              {QUICK_PROMPTS.map((p, i) => (
                <button key={i} className="qp-btn" onClick={() => sendMessage(p)}>
                  {p}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <MessageBubble key={`${msg.role}-${i}-${msg.timestamp || 'na'}`} msg={msg} />
        ))}

        {isLoading && (
          <div className="message-bubble assistant fade-in">
            <div className="chat-avatar bot-avatar">AI</div>
            <div className="assistant-bubble thinking">
              <span /><span /><span />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <div className="chat-input-area">
        <textarea
          ref={inputRef}
          className="chat-input"
          rows={1}
          placeholder="Describe interaction or request an edit..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKey}
        />
        <button className="btn-log" onClick={() => sendMessage()} disabled={!input.trim() || isLoading}>
          {isLoading ? <span className="spinner white" /> : <>
            <span className="log-icon">AI</span>
            <span className="log-label">Send</span>
          </>}
        </button>
      </div>
    </div>
  );
}
