import { createSlice } from '@reduxjs/toolkit';

const chatSlice = createSlice({
  name: 'chat',
  initialState: {
    messages: [
      {
        id: 'welcome',
        role: 'assistant',
        content: 'Hello! I am your AI Co-Pilot and I can help you with logging or tracking your complaint.',
        tool_used: null,
      }
    ],
    isLoading: false,
    currentTool: null,
  },
  reducers: {
    addMessage: (state, action) => {
      state.messages.push(action.payload);
    },
    setMessages: (state, action) => {
      state.messages = action.payload;
    },
    setIsLoading: (state, action) => {
      state.isLoading = action.payload;
    },
    setCurrentTool: (state, action) => {
      state.currentTool = action.payload;
    },
    clearChat: (state) => {
      state.messages = [
        {
          id: 'welcome',
          role: 'assistant',
          content: 'Hello! I am your AI Co-Pilot and I can help you with logging or tracking your complaint.',
          tool_used: null,
        }
      ];
      state.isLoading = false;
      state.currentTool = null;
    }
  }
});

export const { addMessage, setMessages, setIsLoading, setCurrentTool, clearChat } = chatSlice.actions;
export default chatSlice.reducer;
