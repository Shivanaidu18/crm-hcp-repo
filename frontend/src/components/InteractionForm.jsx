import React, { useEffect, useMemo, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  hydrateInteraction,
  resetForm,
  setIsSaving,
  setLastSaved,
  setSavedId,
  updateField,
} from '../store/interactionSlice';
import { getInteraction, listInteractions, saveInteraction } from '../services/api';
import './InteractionForm.css';

const INTERACTION_TYPES = ['Meeting', 'Call', 'Email', 'Conference', 'Visit'];
const SENTIMENTS = ['Positive', 'Neutral', 'Negative'];

function FieldBlock({ label, field, children, highlights, missing }) {
  const isHighlighted = highlights.includes(field);
  const isMissing = missing.includes(field);

  return (
    <div className={`form-group ${isHighlighted ? 'field-highlight' : ''} ${isMissing ? 'field-missing' : ''}`}>
      <label>
        {label}
        {isMissing && <span className="field-flag">Missing</span>}
      </label>
      {children}
    </div>
  );
}

export default function InteractionForm() {
  const dispatch = useDispatch();
  const form = useSelector((s) => s.interaction);
  const [storedItems, setStoredItems] = useState([]);
  const [isDrawerOpen, setIsDrawerOpen] = useState(true);
  const [loadingStored, setLoadingStored] = useState(false);
  const [storedError, setStoredError] = useState('');

  const highlightFields = form.highlightedFields || [];
  const missingFields = form.missing_fields || [];

  const followupSummary = useMemo(() => ({
    priority: form.follow_up_priority,
    nextDate: form.next_follow_up_date,
  }), [form.follow_up_priority, form.next_follow_up_date]);

  const loadStoredItems = async () => {
    setLoadingStored(true);
    try {
      const items = await listInteractions();
      setStoredItems(items);
      setStoredError('');
    } catch (err) {
      setStoredItems([]);
      setStoredError(err?.response?.data?.detail || err?.message || 'Could not load saved interactions.');
    } finally {
      setLoadingStored(false);
    }
  };

  useEffect(() => {
    loadStoredItems();
  }, []);

  const handleSave = async () => {
    dispatch(setIsSaving(true));
    try {
      const result = await saveInteraction({
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
        ai_suggested_followups: form.ai_suggested_followups,
        follow_up_priority: form.follow_up_priority,
        next_follow_up_date: form.next_follow_up_date,
      });
      dispatch(setSavedId(result.id));
      dispatch(hydrateInteraction({
        ...form,
        interaction_uid: result.interaction_uid || form.interaction_uid,
        form_name: result.form_name || form.form_name,
      }));
      dispatch(setLastSaved(new Date().toLocaleTimeString()));
      await loadStoredItems();
    } catch (err) {
      console.error('Save failed:', err);
    } finally {
      dispatch(setIsSaving(false));
    }
  };

  const handleLoadInteraction = async (id) => {
    const item = await getInteraction(id);
    dispatch(hydrateInteraction({
      ...item,
      missing_fields: [],
    }));
  };

  return (
    <div className="form-panel">
      <div className="form-header">
        <div>
          <h2>Log HCP Interaction</h2>
          <div className="ai-lock-note">AI controlled. Use the assistant to populate or edit fields.</div>
        </div>
        <div className="form-actions">
          {form.lastSaved && <span className="saved-badge">Saved {form.lastSaved}</span>}
          <button className="btn-reset" onClick={() => dispatch(resetForm())}>Reset</button>
          <button className="btn-secondary" onClick={() => setIsDrawerOpen((v) => !v)}>
            {isDrawerOpen ? 'Hide Stored' : 'View Stored'}
          </button>
          <button className="btn-save" onClick={handleSave} disabled={form.isSaving}>
            {form.isSaving ? <span className="spinner" /> : 'Save'}
          </button>
        </div>
      </div>

      <div className="form-body">
        {isDrawerOpen && (
          <div className="stored-panel">
            <div className="stored-panel-head">
              <div>
                <div className="section-title">Stored Interactions</div>
                <div className="stored-subtitle">Load previous interaction flows saved in the database.</div>
              </div>
              <button className="btn-secondary" onClick={loadStoredItems} disabled={loadingStored}>
                {loadingStored ? 'Refreshing...' : 'Refresh'}
              </button>
            </div>

            <div className="stored-list">
              {storedError && <div className="stored-error">{storedError}</div>}
              {!storedError && storedItems.length === 0 && <div className="stored-empty">No saved interactions yet.</div>}
              {storedItems.map((item) => (
                <button key={item.id} className="stored-item" onClick={() => handleLoadInteraction(item.id)}>
                  <div className="stored-item-top">
                    <strong>{item.form_name || item.hcp_name || 'Untitled Interaction'}</strong>
                    <span>{item.interaction_uid || `#${item.id}`}</span>
                  </div>
                  <div className="stored-item-meta">
                    <span>{item.hcp_name || 'Unknown HCP'}</span>
                    <span>{item.interaction_type || 'Meeting'}</span>
                    <span>{item.date || 'No date'}</span>
                  </div>
                  <div className="stored-item-summary">{item.topics_discussed || 'No summary saved.'}</div>
                </button>
              ))}
            </div>
          </div>
        )}

        {missingFields.length > 0 && (
          <div className="missing-banner">
            Missing fields: {missingFields.join(', ')}
          </div>
        )}

        <div className="form-section">
          <div className="section-title">Form Identity</div>
          <div className="form-row two-col">
            <FieldBlock label="Form Name" field="form_name" highlights={highlightFields} missing={missingFields}>
              <input
                type="text"
                placeholder="Editable manually or via AI chat"
                value={form.form_name}
                onChange={(e) => dispatch(updateField({ field: 'form_name', value: e.target.value }))}
              />
            </FieldBlock>
            <FieldBlock label="Unique ID" field="interaction_uid" highlights={highlightFields} missing={missingFields}>
              <input type="text" placeholder="Assigned on save" value={form.interaction_uid} readOnly aria-readonly="true" />
            </FieldBlock>
          </div>
        </div>

        <div className="form-section">
          <div className="section-title">Interaction Details</div>

          <div className="form-row two-col">
            <FieldBlock label="HCP Name" field="hcp_name" highlights={highlightFields} missing={missingFields}>
              <input type="text" placeholder="Populated by AI assistant" value={form.hcp_name} readOnly aria-readonly="true" />
            </FieldBlock>

            <FieldBlock label="Interaction Type" field="interaction_type" highlights={highlightFields} missing={missingFields}>
              <select value={form.interaction_type} disabled aria-readonly="true">
                {INTERACTION_TYPES.map((t) => <option key={t}>{t}</option>)}
              </select>
            </FieldBlock>
          </div>

          <div className="form-row two-col">
            <FieldBlock label="Date" field="date" highlights={highlightFields} missing={missingFields}>
              <input type="date" value={form.date} readOnly aria-readonly="true" />
            </FieldBlock>
            <FieldBlock label="Time" field="time" highlights={highlightFields} missing={missingFields}>
              <input type="time" value={form.time} readOnly aria-readonly="true" />
            </FieldBlock>
          </div>

          <FieldBlock label="Attendees" field="attendees" highlights={highlightFields} missing={missingFields}>
            <input type="text" placeholder="Populated by AI assistant" value={form.attendees} readOnly aria-readonly="true" />
          </FieldBlock>
        </div>

        <div className="form-section">
          <div className="section-title">Topics Discussed</div>
          <FieldBlock label="Discussion Summary" field="topics_discussed" highlights={highlightFields} missing={missingFields}>
            <textarea rows={3} placeholder="Populated by AI assistant" value={form.topics_discussed} readOnly aria-readonly="true" />
          </FieldBlock>
          <button className="btn-voice" disabled>Voice note summary unavailable in demo</button>
        </div>

        <div className="form-section">
          <div className="section-title">Materials Shared / Samples Distributed</div>
          <div className="mat-row">
            <span className="mat-label">Materials Shared</span>
            <button className="btn-search-add" disabled>AI only</button>
          </div>
          <FieldBlock label="Materials" field="materials_shared" highlights={highlightFields} missing={missingFields}>
            <input type="text" className="mat-input" placeholder="Populated by AI assistant" value={form.materials_shared} readOnly aria-readonly="true" />
          </FieldBlock>

          <div className="mat-row" style={{ marginTop: 12 }}>
            <span className="mat-label">Samples Distributed</span>
            <button className="btn-search-add" disabled>AI only</button>
          </div>
          <FieldBlock label="Samples" field="samples_distributed" highlights={highlightFields} missing={missingFields}>
            <input type="text" className="mat-input" placeholder="Populated by AI assistant" value={form.samples_distributed} readOnly aria-readonly="true" />
          </FieldBlock>
        </div>

        <div className="form-section">
          <div className="section-title">Observed/Inferred HCP Sentiment</div>
          <div className="sentiment-row">
            {SENTIMENTS.map((s) => (
              <label key={s} className={`sentiment-option ${form.sentiment === s ? 'active' : ''} ${highlightFields.includes('sentiment') ? 'field-highlight-chip' : ''}`}>
                <input type="radio" name="sentiment" value={s} checked={form.sentiment === s} readOnly disabled />
                <span>{s}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="form-section">
          <div className="section-title">Outcomes</div>
          <FieldBlock label="Outcomes" field="outcomes" highlights={highlightFields} missing={missingFields}>
            <textarea rows={2} placeholder="Populated by AI assistant" value={form.outcomes} readOnly aria-readonly="true" />
          </FieldBlock>
        </div>

        <div className="form-section">
          <div className="section-title">Follow-up Actions</div>
          <FieldBlock label="Actions" field="follow_up_actions" highlights={highlightFields} missing={missingFields}>
            <textarea rows={2} placeholder="Populated by AI assistant" value={form.follow_up_actions} readOnly aria-readonly="true" />
          </FieldBlock>

          {(followupSummary.priority || followupSummary.nextDate) && (
            <div className="scheduler-card">
              <div className="scheduler-item">
                <span className="scheduler-label">Priority</span>
                <strong>{followupSummary.priority || 'Not set'}</strong>
              </div>
              <div className="scheduler-item">
                <span className="scheduler-label">Next visit</span>
                <strong>{followupSummary.nextDate || 'Not scheduled'}</strong>
              </div>
            </div>
          )}

          {form.ai_suggested_followups?.length > 0 && (
            <div className="ai-suggestions">
              <div className="ai-suggestions-title">AI Suggested Follow-ups:</div>
              <ul>
                {form.ai_suggested_followups.map((s, i) => <li key={i}>{s}</li>)}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
