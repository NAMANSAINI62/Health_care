import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  user: null,
  isAuthenticated: false,
  isCheckingAuth: true,
  authMode: 'login', // 'login' or 'register'
};

export const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setCredentials: (state, action) => {
      state.user = action.payload.user;
      state.isAuthenticated = true;
      state.isCheckingAuth = false;
      localStorage.setItem('user', JSON.stringify(action.payload.user));
    },
    setUser: (state, action) => {
      state.user = action.payload;
      state.isAuthenticated = Boolean(action.payload);
      state.isCheckingAuth = false;
      if (action.payload) {
        localStorage.setItem('user', JSON.stringify(action.payload));
      } else {
        localStorage.removeItem('user');
      }
    },
    logout: (state) => {
      state.user = null;
      state.isAuthenticated = false;
      state.isCheckingAuth = false;
      state.authMode = 'login';
      localStorage.removeItem('user');
    },
    setCheckingAuth: (state, action) => {
      state.isCheckingAuth = action.payload;
    },
    setAuthMode: (state, action) => {
      state.authMode = action.payload;
    },
    toggleAuthMode: (state) => {
      state.authMode = state.authMode === 'login' ? 'register' : 'login';
    },
  },
});

export const {
  setCredentials,
  setUser,
  logout,
  setCheckingAuth,
  setAuthMode,
  toggleAuthMode,
} = authSlice.actions;

export default authSlice.reducer;
