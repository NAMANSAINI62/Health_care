import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const sendChatMessage = async (complaintId, message) => {
  const response = await api.post('/api/complaints/chat', {
    complaint_id: complaintId,
    message: message,
  });
  return response.data;
};

export const uploadDocumentFile = async (file, complaintId) => {
  const formData = new FormData();
  formData.append('file', file);
  if (complaintId && !isNaN(parseInt(complaintId, 10))) {
    formData.append('complaint_id', parseInt(complaintId, 10));
  }

  const response = await api.post('/api/complaints/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};


export const fetchComplaints = async () => {
  const response = await api.get('/api/complaints');
  return response.data;
};

export const fetchComplaintById = async (id) => {
  const response = await api.get(`/api/complaints/${id}`);
  return response.data;
};

export const fetchComplaintAudit = async (id) => {
  const response = await api.get(`/api/complaints/${id}/audit`);
  return response.data;
};

export const updateComplaintStatus = async (id, status) => {
  const response = await api.post(`/api/complaints/${id}/status?status=${encodeURIComponent(status)}`);
  return response.data;
};



export const fetchCapas = async (params = {}) => {
  const response = await api.get('/api/capas', { params });
  return response.data;
};

export const fetchCapaById = async (id) => {
  const response = await api.get(`/api/capas/${id}`);
  return response.data;
};

export const createCapa = async (payload) => {
  const response = await api.post('/api/capas', payload);
  return response.data;
};

export const updateCapa = async (id, payload) => {
  const response = await api.put(`/api/capas/${id}`, payload);
  return response.data;
};

export const addCapaActionItem = async (capaId, actionPayload) => {
  const response = await api.post(`/api/capas/${capaId}/action-items`, actionPayload);
  return response.data;
};

export const toggleCapaActionItem = async (itemId, status) => {
  const response = await api.put(`/api/capas/action-items/${itemId}?status=${encodeURIComponent(status)}`);
  return response.data;
};

export const escalateCapa = async (capaId, level = 'Escalated - Level 1') => {
  const response = await api.post(`/api/capas/${capaId}/escalate?level=${encodeURIComponent(level)}`);
  return response.data;
};

