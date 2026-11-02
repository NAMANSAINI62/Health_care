import { configureStore } from '@reduxjs/toolkit';
import complaintReducer from './complaintSlice';
import chatReducer from './chatSlice';
import authReducer from './authSlice';

export const store = configureStore({
  reducer: {
    complaint: complaintReducer,
    chat: chatReducer,
    auth: authReducer,
  },
});
