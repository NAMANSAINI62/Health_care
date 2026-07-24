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
  if (complaintId) {
    formData.append('complaint_id', complaintId);
  }

  const response = await api.post('/api/complaints/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
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
