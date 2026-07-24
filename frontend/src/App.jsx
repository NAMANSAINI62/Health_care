import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import Header from './components/Header/Header';
import ComplaintForm from './components/ComplaintForm/ComplaintForm';
import RiskAssessmentPanel from './components/RiskAssessmentPanel/RiskAssessmentPanel';
import CopilotChat from './components/CopilotChat/CopilotChat';
import AuditLogModal from './components/AuditLogModal/AuditLogModal';
import { resetForm, setComplaintState } from './redux/complaintSlice';
import { clearChat, setMessages } from './redux/chatSlice';
import { fetchComplaintById, updateComplaintStatus } from './api/complaintsApi';

function App() {
  const [isAuditModalOpen, setIsAuditModalOpen] = useState(false);
  const [rightPanelWidth, setRightPanelWidth] = useState(480);
  const [isResizing, setIsResizing] = useState(false);
  
  const dispatch = useDispatch();
  const { complaintId, status } = useSelector((state) => state.complaint);
  const leftPanelRef = useRef(null);

  // Persistence on Page Refresh: Reload active complaint state from DB
  useEffect(() => {
    const savedId = complaintId || localStorage.getItem('active_complaint_id');
    if (savedId) {
      const parsedId = parseInt(savedId, 10);
      fetchComplaintById(parsedId)
        .then((data) => {
          dispatch(setComplaintState({
            complaint_id: data.id,
            form_data: {
              complaint_source: data.complaint_source,
              customer_name: data.customer_name,
              product_name: data.product_name,
              product_strength: data.product_strength,
              batch_lot_number: data.batch_lot_number,
              manufacturing_date: data.manufacturing_date,
              expiry_date: data.expiry_date,
              affected_quantity: data.affected_quantity,
              complaint_category: data.complaint_category,
              complaint_description: data.complaint_description,
              originating_site_block: data.originating_site_block,
              impacted_npm: data.impacted_npm,
            },
            risk_assessment: {
              severity: data.severity,
              suggested_next_action: data.suggested_next_action,
              initial_risk_assessment: data.initial_risk_assessment,
              likely_root_cause: data.likely_root_cause,
            },
            status: data.status,
          }));

          if (data.chat_messages && data.chat_messages.length > 0) {
            const formattedMessages = data.chat_messages.map((msg) => ({
              id: msg.id.toString(),
              role: msg.role,
              content: msg.content,
              tool_used: msg.tool_used,
            }));
            dispatch(setMessages(formattedMessages));
          }
        })
        .catch((err) => {
          console.error('Error reloading saved complaint state:', err);
        });
    }
  }, [dispatch]);

  // Resizable Split Panel Logic
  const handleMouseDown = useCallback((e) => {
    e.preventDefault();
    setIsResizing(true);
  }, []);

  const handleMouseMove = useCallback((e) => {
    if (!isResizing) return;
    const newWidth = window.innerWidth - e.clientX;
    if (newWidth >= 300 && newWidth <= 850) {
      setRightPanelWidth(newWidth);
    }
  }, [isResizing]);

  const handleMouseUp = useCallback(() => {
    setIsResizing(false);
  }, []);

  useEffect(() => {
    if (isResizing) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    } else {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    }
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing, handleMouseMove, handleMouseUp]);

  const handleNewComplaint = () => {
    dispatch(resetForm());
    dispatch(clearChat());
    if (leftPanelRef.current) {
      leftPanelRef.current.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handleCommitStatus = async () => {
    if (status === 'Ready to Commit' && complaintId) {
      try {
        await updateComplaintStatus(complaintId, 'Committed');
        dispatch(setComplaintState({ status: 'Committed' }));
      } catch (err) {
        console.error('Error committing complaint status:', err);
      }
    }
  };

  return (
    <div className="app-shell">
      {/* Top Application Header */}
      <Header
        complaintId={complaintId}
        status={status}
        onNewComplaint={handleNewComplaint}
        onOpenAuditModal={() => setIsAuditModalOpen(true)}
        onCommitStatus={handleCommitStatus}
      />

      {/* Main Resizable Two-Panel Layout */}
      <main className="main-layout-resizable">
        {/* Left Panel: Scrollable Complaint Form & Risk Assessment */}
        <div className="left-panel" ref={leftPanelRef}>
          <ComplaintForm />
          <RiskAssessmentPanel />
        </div>

        {/* Draggable Resizer Handle */}
        <div
          className={`resizer-handle ${isResizing ? 'is-resizing' : ''}`}
          onMouseDown={handleMouseDown}
          title="Drag to resize left & right panels"
        >
          <div className="resizer-line" />
        </div>

        {/* Right Panel: Dynamic Resizable Copilot Chat */}
        <div style={{ width: `${rightPanelWidth}px`, minWidth: `${rightPanelWidth}px` }}>
          <CopilotChat />
        </div>
      </main>

      {/* Field Mutation Audit Trail Modal */}
      <AuditLogModal
        complaintId={complaintId}
        isOpen={isAuditModalOpen}
        onClose={() => setIsAuditModalOpen(false)}
      />
    </div>
  );
}

export default App;
