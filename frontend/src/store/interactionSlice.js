import { createSlice } from '@reduxjs/toolkit';

const buildInitialState = () => ({
  interaction_uid: '',
  form_name: '',
  hcp_name: '',
  interaction_type: 'Meeting',
  date: new Date().toISOString().split('T')[0],
  time: new Date().toTimeString().slice(0, 5),
  attendees: '',
  topics_discussed: '',
  materials_shared: '',
  samples_distributed: '',
  sentiment: 'Neutral',
  outcomes: '',
  follow_up_actions: '',
  ai_suggested_followups: [],
  follow_up_priority: '',
  next_follow_up_date: '',
  missing_fields: [],
  highlightedFields: [],
  savedId: null,
  isSaving: false,
  lastSaved: null,
});

const initialState = buildInitialState();

const interactionSlice = createSlice({
  name: 'interaction',
  initialState,
  reducers: {
    updateField: (state, action) => {
      const { field, value } = action.payload;
      if (field in state) {
        state[field] = value;
      }
    },
    updateFields: (state, action) => {
      const fields = action.payload || {};
      const changed = [];

      Object.entries(fields).forEach(([key, value]) => {
        if (value !== null && value !== undefined && key in state && state[key] !== value) {
          state[key] = value;
          changed.push(key);
        }
      });

      state.highlightedFields = changed;
    },
    clearFieldHighlights: (state) => {
      state.highlightedFields = [];
    },
    setMissingFields: (state, action) => {
      state.missing_fields = action.payload || [];
    },
    setFollowupMeta: (state, action) => {
      state.follow_up_priority = action.payload?.priority || '';
      state.next_follow_up_date = action.payload?.nextDate || '';
    },
    setAISuggestions: (state, action) => {
      state.ai_suggested_followups = action.payload || [];
    },
    hydrateInteraction: (state, action) => {
      const nextState = { ...buildInitialState(), ...action.payload };
      return {
        ...state,
        ...nextState,
        highlightedFields: [],
        missing_fields: action.payload?.missing_fields || [],
      };
    },
    setSavedId: (state, action) => {
      state.savedId = action.payload;
    },
    setIsSaving: (state, action) => {
      state.isSaving = action.payload;
    },
    setLastSaved: (state, action) => {
      state.lastSaved = action.payload;
    },
    resetForm: () => buildInitialState(),
  },
});

export const {
  updateField,
  updateFields,
  clearFieldHighlights,
  setMissingFields,
  setFollowupMeta,
  setAISuggestions,
  hydrateInteraction,
  setSavedId,
  setIsSaving,
  setLastSaved,
  resetForm,
} = interactionSlice.actions;

export default interactionSlice.reducer;
