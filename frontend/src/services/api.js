import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

export const chatWithAgent = async (messages, currentForm) => {
  const response = await api.post('/api/chat', {
    messages,
    current_form: currentForm,
  });
  return response.data;
};

export const saveInteraction = async (data) => {
  const response = await api.post('/api/interactions', data);
  return response.data;
};

export const updateInteraction = async (id, data) => {
  const response = await api.put(`/api/interactions/${id}`, data);
  return response.data;
};

export const listInteractions = async () => {
  const response = await api.get('/api/interactions');
  return response.data;
};

export const getInteraction = async (id) => {
  const response = await api.get(`/api/interactions/${id}`);
  return response.data;
};

export const searchHCPs = async (query) => {
  const response = await api.get('/api/hcps/search', { params: { q: query } });
  return response.data;
};

export default api;
