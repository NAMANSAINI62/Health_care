import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // It basicakly enables browser to automatically send and receive HttpOnly cookies
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auth API Methods
export const registerUser = async ({ username, email, password }) => {
  const response = await api.post('/api/auth/register', { username, email, password });
  return response.data;
};

export const loginUser = async ({ username, password }) => {
  const response = await api.post('/api/auth/login', { username, password });
  return response.data;
};

export const fetchCurrentUser = async () => {
  const response = await api.get('/api/auth/me');
  return response.data;
};

export const logoutUser = async () => {
  try {
    await api.post('/api/auth/logout');
  } catch (e) {
    // ignore server errors during logout
  }
};

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




