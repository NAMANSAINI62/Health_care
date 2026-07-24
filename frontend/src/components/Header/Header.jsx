import React from 'react';
import { ShieldCheck, PlusCircle, History } from 'lucide-react';
import StatusPill from '../StatusPill/StatusPill';

export const Header = ({ complaintId, status, onNewComplaint, onOpenAuditModal }) => {
  return (
    <header className="app-header">
      <div className="brand-section">
        <div className="brand-logo-icon">
          <ShieldCheck size={20} />
        </div>
        <div>
          <div className="brand-name">Pharma QMS Complaint Hub</div>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        {complaintId && (
          <>
            <span className="complaint-id-tag">
              Complaint #{complaintId}
            </span>
            <button className="btn-pill-secondary" onClick={onOpenAuditModal}>
              <History size={14} /> Audit Log
            </button>
          </>
        )}

        <StatusPill status={status} />

        <button className="btn-pill-primary" onClick={onNewComplaint}>
          <PlusCircle size={15} /> New Complaint
        </button>
      </div>
    </header>
  );
};

export default Header;
