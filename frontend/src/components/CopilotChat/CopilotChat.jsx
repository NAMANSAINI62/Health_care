import React, { useState, useRef, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Bot, Send, Paperclip, Loader2, Cpu, Sparkles } from 'lucide-react';
import { addMessage, setIsLoading, setCurrentTool } from '../../redux/chatSlice';
import { setComplaintState, setLastUpdatedFields } from '../../redux/complaintSlice';
import { sendChatMessage, uploadDocumentFile } from '../../api/complaintsApi';

export const CopilotChat = () => {
  const [inputText, setInputText] = useState('');
  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);

  const dispatch = useDispatch();
  const { messages, isLoading } = useSelector((state) => state.chat);
  const { complaintId } = useSelector((state) => state.complaint);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const quickPrompts = [
    "Apollo Pharmacy reported discolored capsules in Amoxicillin 500mg, batch BMX-240602, Mfg Jan 2026, Exp Jan 2028, quantity 48 capsules from Block B.",
    "MedPlus Pharmacy reported cracked glass vials in Paracetamol Injection 10mg/mL, batch LOT-9988, quantity 200 vials from Block C.",
    "Global Health Clinic reported chipped and capping tablets in Metformin 500mg, batch MFM-8812, Mfg Feb 2026, Exp Feb 2028, quantity 1000 tablets.",
    "Sun Healthcare Distributor reported misprinted barcode on Azithromycin 250mg carton, batch AZT-4401, affected quantity 50 cartons.",
    "City General Hospital reported white cloudiness in Cough Syrup 100mL, batch CS-1102A, quantity 75 bottles from Liquid Block D.",
    "Care Plus Chemist reported open foil seal in Ibuprofen 400mg blister packs, batch IBU-7733, quantity 120 blisters.",
    "Update batch number to CHG-9981A and set affected quantity to 350 vials.",
    "Change manufacturing site to Block C - Sterile Injectables and update expiry date to Dec 2028.",
    "Update customer name to Fortis Healthcare Hospital and channel to Hospital Email Direct.",
    "Change complaint category to Primary Container Leakage and description to rubber stopper detachment."
  ];

  const handleSendPrompt = async (textToSend) => {
    if (!textToSend || isLoading) return;

    setInputText('');

    dispatch(addMessage({
      id: Date.now().toString(),
      role: 'user',
      content: textToSend,
      tool_used: null
    }));

    dispatch(setIsLoading(true));

    try {
      const response = await sendChatMessage(complaintId, textToSend);

      dispatch(setComplaintState({
        complaint_id: response.complaint_id,
        form_data: response.form_data,
        risk_assessment: response.risk_assessment,
        status: response.status
      }));

      if (response.form_data) {
        const nonNullKeys = Object.keys(response.form_data).filter(k => Boolean(response.form_data[k]));
        dispatch(setLastUpdatedFields(nonNullKeys));
      }

      dispatch(setCurrentTool(response.tool_used));

      dispatch(addMessage({
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.assistant_message,
        tool_used: response.tool_used
      }));
    } catch (error) {
      console.error('Error calling Copilot API:', error);
      dispatch(addMessage({
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: '⚠️ An error occurred while contacting the AI agent service.',
        tool_used: null
      }));
    } finally {
      dispatch(setIsLoading(false));
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file || isLoading) return;

    dispatch(addMessage({
      id: Date.now().toString(),
      role: 'user',
      content: `📎 Uploaded Document: ${file.name}`,
      tool_used: 'document_extraction'
    }));

    dispatch(setIsLoading(true));
    dispatch(setCurrentTool('document_extraction'));

    try {
      const response = await uploadDocumentFile(file, complaintId);

      dispatch(setComplaintState({
        complaint_id: response.complaint_id,
        form_data: response.form_data,
        risk_assessment: response.risk_assessment,
        status: response.status
      }));

      if (response.form_data) {
        const nonNullKeys = Object.keys(response.form_data).filter(k => Boolean(response.form_data[k]));
        dispatch(setLastUpdatedFields(nonNullKeys));
      }

      dispatch(addMessage({
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.assistant_message,
        tool_used: 'document_extraction'
      }));
    } catch (error) {
      console.error('Error uploading file:', error);
      dispatch(addMessage({
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: '⚠️ File extraction failed.',
        tool_used: null
      }));
    } finally {
      dispatch(setIsLoading(false));
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSendPrompt(inputText.trim());
    }
  };

  return (
    <div className="right-panel">
      <div className="chat-header">
        <div className="chat-title">
          <Bot size={18} className="text-blue-600" />
          AI Co-Pilot Chat
        </div>
      </div>

      <div className="messages-container">
        {messages.map((msg) => (
          <div key={msg.id} className={`chat-bubble ${msg.role}`}>
            {msg.tool_used && (
              <div style={{ fontSize: '10px', color: '#2563eb', fontWeight: '700', marginBottom: '4px', textTransform: 'uppercase' }}>
                <Cpu size={11} style={{ display: 'inline', marginRight: '4px' }} />
                Tool: {msg.tool_used}
              </div>
            )}
            <div>{msg.content}</div>
          </div>
        ))}

        {isLoading && (
          <div className="ai-thinking-bubble">
            <div className="ai-thinking-content">
              <div className="ai-sparkle-ring">
                <Sparkles size={16} className="text-sky-500 animate-spin-slow" />
              </div>
              <span className="ai-thinking-text">
                AI Co-pilot is processing complaint & evaluating risk...
              </span>
            </div>
            <div className="thinking-dots">
              <span className="thinking-dot" />
              <span className="thinking-dot" />
              <span className="thinking-dot" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Action Prompt Chips */}
      <div className="quick-chips-row">
        {quickPrompts.map((prompt, idx) => (
          <button key={idx} className="chip-btn" onClick={() => handleSendPrompt(prompt)} disabled={isLoading}>
            <Sparkles size={10} style={{ display: 'inline', marginRight: '4px' }} />
            {prompt.length > 35 ? prompt.substring(0, 35) + '...' : prompt}
          </button>
        ))}
      </div>

      {/* Clean Single-line Chat Input Bar */}
      <div className="chat-input-area">
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center', width: '100%' }}>
          <button
            className="icon-btn-pill"
            title="Upload Document"
            onClick={() => fileInputRef.current?.click()}
            disabled={isLoading}
          >
            <Paperclip size={18} />
          </button>
          <input
            type="file"
            ref={fileInputRef}
            style={{ display: 'none' }}
            accept=".pdf,.txt,.eml,.doc,.docx"
            onChange={handleFileUpload}
          />

          <input
            type="text"
            className="chat-input-field"
            placeholder="Type your complaint narrative or edit request..."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
          />

          <button
            className="send-btn-pill"
            onClick={() => handleSendPrompt(inputText.trim())}
            disabled={!inputText.trim() || isLoading}
          >
            <Send size={15} /> Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default CopilotChat;
