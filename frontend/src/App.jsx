import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import Header from './components/Header/Header';
import ComplaintForm from './components/ComplaintForm/ComplaintForm';
import RiskAssessmentPanel from './components/RiskAssessmentPanel/RiskAssessmentPanel';

import CopilotChat from './components/CopilotChat/CopilotChat';
import AuditLogModal from './components/AuditLogModal/AuditLogModal';
import CapaDashboard from './components/CapaDashboard/CapaDashboard';
import { resetForm, setComplaintState } from './redux/complaintSlice';
import { clearChat, setMessages } from './redux/chatSlice';
import { fetchComplaintById, updateComplaintStatus } from './api/complaintsApi';

function App() {
  const [activeTab, setActiveTab] = useState('triage');
  const [isAuditModalOpen, setIsAuditModalOpen] = useState(false);
  const [activeComplaintFull, setActiveComplaintFull] = useState(null);
  const [rightPanelWidth, setRightPanelWidth] = useState(480);
  const [isResizing, setIsResizing] = useState(false);
  
  const dispatch = useDispatch();
  const { complaintId, status } = useSelector((state) => state.complaint);
  const leftPanelRef = useRef(null);

  const loadFullComplaint = useCallback(async (idToFetch) => {
    if (!idToFetch) return;
    try {
      const data = await fetchComplaintById(idToFetch);
      setActiveComplaintFull(data);
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
    } catch (err) {
      console.error('Error reloading complaint state:', err);
    }
  }, [dispatch]);

  useEffect(() => {
    const savedId = complaintId || sessionStorage.getItem('active_complaint_id');
    if (savedId) {
      loadFullComplaint(parseInt(savedId, 10));
    }
  }, [complaintId, loadFullComplaint]);

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
    setActiveComplaintFull(null);
    setActiveTab('triage');
    if (leftPanelRef.current) {
      leftPanelRef.current.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };


  const handleSelectComplaintFromCapa = (cId) => {
    setActiveTab('triage');
    loadFullComplaint(cId);
  };

  return (
    <div className="app-shell">
      <Header
        activeTab={activeTab}
        onTabChange={setActiveTab}
        complaintId={complaintId}
        status={status}
        onNewComplaint={handleNewComplaint}
        onOpenAuditModal={() => setIsAuditModalOpen(true)}
      />

      {activeTab === 'triage' ? (
        <main className="main-layout-resizable">
          <div className="left-panel" ref={leftPanelRef}>
            <ComplaintForm />
            <RiskAssessmentPanel
              activeComplaintFull={activeComplaintFull}
              onOpenCapaTab={() => setActiveTab('capa')}
            />

          </div>

          <div
            className={`resizer-handle ${isResizing ? 'is-resizing' : ''}`}
            onMouseDown={handleMouseDown}
            title="Drag to resize left & right panels"
          >
            <div className="resizer-line" />
          </div>

          <div style={{ width: `${rightPanelWidth}px`, minWidth: `${rightPanelWidth}px` }}>
            <CopilotChat />
          </div>
        </main>
      ) : (
        <main className="main-layout-single">
          <CapaDashboard onSelectComplaint={handleSelectComplaintFromCapa} />
        </main>
      )}

      <AuditLogModal
        complaintId={complaintId}
        isOpen={isAuditModalOpen}
        onClose={() => setIsAuditModalOpen(false)}
      />


    </div>
  );
}

export default App;
