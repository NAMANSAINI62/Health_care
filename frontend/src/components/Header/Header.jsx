import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { ShieldCheck, PlusCircle, History, LogOut, User } from 'lucide-react';
import { logout } from '../../redux/authSlice';
import { logoutUser } from '../../api/complaintsApi';

export const Header = ({ 
  complaintId, 
  onNewComplaint, 
  onOpenAuditModal
}) => {
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);

  const handleLogout = async () => {
    await logoutUser();
    dispatch(logout());
  };

  return (
    <header className="app-header">
      <div className="brand-section">
        <div className="brand-logo-icon">
          <ShieldCheck size={20} />
        </div>
        <div>
          <div className="brand-name">Pharma Complaint</div>
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

        <button className="btn-pill-primary" onClick={onNewComplaint}>
          <PlusCircle size={15} /> New Complaint
        </button>

        {user && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginLeft: '6px' }}>
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                fontSize: '0.85rem',
                fontWeight: 600,
                color: '#0369a1',
                background: '#f0f9ff',
                padding: '6px 12px',
                borderRadius: '9999px',
                border: '1px solid #bae6fd'
              }}
              title={user.email || user.username}
            >
              <User size={14} />
              {user.username}
            </span>
            <button
              className="btn-pill-secondary"
              onClick={handleLogout}
              title="Sign Out"
              style={{ padding: '6px 10px', display: 'flex', alignItems: 'center', gap: '6px' }}
            >
              <LogOut size={14} />
              <span>Sign Out</span>
            </button>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;

