import React, { useState, useEffect } from 'react';
import { X, History } from 'lucide-react';
import { fetchComplaintAudit } from '../../api/complaintsApi';

export const AuditLogModal = ({ complaintId, isOpen, onClose }) => {
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && complaintId) {
      setLoading(true);
      fetchComplaintAudit(complaintId)
        .then((logs) => setAuditLogs(logs))
        .catch((err) => console.error('Error fetching audit logs:', err))
        .finally(() => setLoading(false));
    }
  }, [isOpen, complaintId]);

  const formatISTTimestamp = (isoString) => {
    if (!isoString) return 'N/A';
    try {
      let utcStr = isoString;
      if (!utcStr.endsWith('Z') && !utcStr.includes('+')) {
        utcStr += 'Z';
      }
      const date = new Date(utcStr);
      return date.toLocaleString('en-IN', {
        timeZone: 'Asia/Kolkata',
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
      });
    } catch {
      return isoString;
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="flex items-center gap-2 text-base font-bold text-slate-800" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <History size={18} className="text-blue-600" />
            Field Audit Trail History — Complaint #{complaintId}
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              color: '#64748b',
              cursor: 'pointer'
            }}
          >
            <X size={18} />
          </button>
        </div>

        <div className="modal-body">
          {loading ? (
            <div className="text-center text-slate-500 py-8">Loading audit trail...</div>
          ) : auditLogs.length === 0 ? (
            <div className="text-center text-slate-500 py-8">No AI field mutations recorded yet for this complaint.</div>
          ) : (
            <table className="audit-table">
              <thead>
                <tr>
                  <th>Field Name</th>
                  <th>Old Value</th>
                  <th>New Value</th>
                  <th>Changed By</th>
                  <th>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {auditLogs.map((log) => (
                  <tr key={log.id}>
                    <td className="font-mono text-blue-600 font-semibold">{log.field_name}</td>
                    <td className="text-slate-500">{log.old_value || 'EMPTY'}</td>
                    <td className="text-emerald-600 font-medium">{log.new_value}</td>
                    <td>
                      <span style={{ fontSize: '11px', background: '#dbeafe', color: '#1e40af', padding: '2px 8px', borderRadius: '9999px', fontWeight: '600' }}>
                        {log.changed_by}
                      </span>
                    </td>
                    <td className="text-slate-600 font-mono text-xs font-medium">
                      {formatISTTimestamp(log.changed_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
};

export default AuditLogModal;
