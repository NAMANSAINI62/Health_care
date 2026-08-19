import React from 'react';
import { ShieldCheck, PlusCircle, History, FileText, ClipboardCheck } from 'lucide-react';
import StatusPill from '../StatusPill/StatusPill';

export const Header = ({ 
  activeTab, 
  onTabChange, 
  complaintId, 
  status, 
  onNewComplaint, 
  onOpenAuditModal
}) => {
  return (
    <header className="app-header">
      <div className="brand-section">
        <div className="brand-logo-icon">
          <ShieldCheck size={20} />
        </div>
        <div>
          <div className="brand-name">Pharma QMS Complaint Hub</div>
        </div>

        {/* View Navigation Tabs */}
        <nav className="header-nav-tabs">
          <button 
            className={`nav-tab-btn ${activeTab === 'triage' ? 'active' : ''}`}
            onClick={() => onTabChange('triage')}
          >
            <FileText size={15} /> Complaint Triage & Form
          </button>
          <button 
            className={`nav-tab-btn ${activeTab === 'capa' ? 'active' : ''}`}
            onClick={() => onTabChange('capa')}
          >
            <ClipboardCheck size={15} /> CAPA Module
          </button>
        </nav>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        {complaintId && activeTab === 'triage' && (
          <>
            <span className="complaint-id-tag">
              Complaint #{complaintId}
            </span>
            <button className="btn-pill-secondary" onClick={onOpenAuditModal}>
              <History size={14} /> Audit Log
            </button>
          </>
        )}

        {activeTab === 'triage' && <StatusPill status={status} />}

        <button className="btn-pill-primary" onClick={onNewComplaint}>
          <PlusCircle size={15} /> New Complaint
        </button>
      </div>
    </header>
  );
};

export default Header;
