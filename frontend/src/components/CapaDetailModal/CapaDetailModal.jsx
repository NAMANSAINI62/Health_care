import React, { useState, useEffect } from 'react';
import { 
  X, 
  CheckSquare, 
  Square, 
  Plus, 
  Building2, 
  UserCheck, 
  Calendar, 
  BellRing, 
  ArrowUpRight,
  ShieldCheck,
  AlertCircle
} from 'lucide-react';
import { fetchCapaById, addCapaActionItem, toggleCapaActionItem, escalateCapa } from '../../api/complaintsApi';

export const CapaDetailModal = ({ capaId, isOpen, onClose, onSelectComplaint }) => {
  const [capa, setCapa] = useState(null);
  const [loading, setLoading] = useState(true);
  const [newActionType, setNewActionType] = useState('Corrective Action');
  const [newActionDesc, setNewActionDesc] = useState('');
  const [newActionAssignee, setNewActionAssignee] = useState('');
  const [isAddingAction, setIsAddingAction] = useState(false);

  const loadCapaDetail = async () => {
    if (!capaId) return;
    setLoading(true);
    try {
      const data = await fetchCapaById(capaId);
      setCapa(data);
    } catch (err) {
      console.error('Failed to fetch CAPA details:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen && capaId) {
      loadCapaDetail();
    }
  }, [capaId, isOpen]);

  if (!isOpen) return null;

  const handleToggleAction = async (itemId, currentStatus) => {
    const nextStatus = currentStatus === 'Completed' ? 'Pending' : 'Completed';
    try {
      await toggleCapaActionItem(itemId, nextStatus);
      await loadCapaDetail();
    } catch (err) {
      console.error('Action toggle failed:', err);
    }
  };

  const handleAddAction = async (e) => {
    e.preventDefault();
    if (!newActionDesc.trim()) return;
    try {
      await addCapaActionItem(capaId, {
        action_type: newActionType,
        description: newActionDesc,
        assignee: newActionAssignee || capa?.owner_department || 'QA Lead'
      });
      setNewActionDesc('');
      setNewActionAssignee('');
      setIsAddingAction(false);
      await loadCapaDetail();
    } catch (err) {
      console.error('Add action item failed:', err);
    }
  };

  const handleEscalateNotice = async () => {
    if (!capa) return;
    try {
      await escalateCapa(capa.id, 'Escalated - Level 1');
      await loadCapaDetail();
    } catch (err) {
      console.error('Escalation failed:', err);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-card capa-detail-modal">
        <div className="modal-header">
          {capa && (
            <div className="modal-title-group">
              <span className="capa-number-badge lg">{capa.capa_number}</span>
              <div>
                <h3 className="modal-title">{capa.title}</h3>
                {capa.complaint_id && (
                  <span 
                    className="complaint-link-chip" 
                    onClick={() => {
                      onClose();
                      if (onSelectComplaint) onSelectComplaint(capa.complaint_id);
                    }}
                  >
                    Parent Complaint #{capa.complaint_id} <ArrowUpRight size={13} />
                  </span>
                )}
              </div>
            </div>
          )}
          <button className="icon-btn-pill" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        {loading || !capa ? (
          <div className="modal-body">Loading CAPA task details...</div>
        ) : (
          <div className="modal-body">
            {/* Meta bar */}
            <div className="capa-detail-meta-grid">
              <div>
                <span className="meta-label">Owner Department</span>
                <div className="meta-value-box">
                  <Building2 size={16} className="text-sky-600" />
                  <strong>{capa.owner_department}</strong>
                </div>
              </div>

              <div>
                <span className="meta-label">Assigned Lead</span>
                <div className="meta-value-box">
                  <UserCheck size={16} className="text-emerald-600" />
                  <strong>{capa.assignee_name || 'QA Lead'}</strong>
                </div>
              </div>

              <div>
                <span className="meta-label">Target Completion</span>
                <div className="meta-value-box">
                  <Calendar size={16} className="text-orange-500" />
                  <strong>{new Date(capa.due_date).toLocaleDateString()}</strong>
                </div>
              </div>

              <div>
                <span className="meta-label">Status / Escalation</span>
                <div className="meta-value-box">
                  <span className={`capa-status-badge ${capa.status.toLowerCase().replace(/\s+/g, '-')}`}>
                    ● {capa.status}
                  </span>
                  {capa.escalation_status !== 'Normal' && (
                    <span className="escalation-badge ml-2">
                      <BellRing size={12} /> {capa.escalation_status}
                    </span>
                  )}
                </div>
              </div>
            </div>

            {/* Root Cause & Description */}
            <div className="capa-root-box">
              <h4 className="section-subtitle">
                <AlertCircle size={16} className="text-sky-600" /> Root Cause Analysis & Description
              </h4>
              <p className="root-cause-text">
                <strong>Likely Root Cause:</strong> {capa.root_cause || 'Root cause investigation under review by QA.'}
              </p>
              {capa.description && (
                <p className="capa-full-desc">{capa.description}</p>
              )}
            </div>

            {/* Action Items List */}
            <div className="action-items-section">
              <div className="action-items-header">
                <h4 className="section-subtitle">
                  <ShieldCheck size={16} className="text-emerald-600" /> CAPA Execution Action Items ({capa.action_items?.length || 0})
                </h4>
                <button 
                  className="btn-pill-secondary btn-sm"
                  onClick={() => setIsAddingAction(!isAddingAction)}
                >
                  <Plus size={14} /> Add Action Item
                </button>
              </div>

              {/* Inline Add Action Item Form */}
              {isAddingAction && (
                <form onSubmit={handleAddAction} className="inline-action-form">
                  <div className="form-grid">
                    <div className="form-group">
                      <label className="form-label">Action Type</label>
                      <select 
                        className="form-control"
                        value={newActionType}
                        onChange={(e) => setNewActionType(e.target.value)}
                      >
                        <option value="Corrective Action">Corrective Action</option>
                        <option value="Preventive Action">Preventive Action</option>
                      </select>
                    </div>
                    <div className="form-group">
                      <label className="form-label">Assignee</label>
                      <input 
                        type="text"
                        className="form-control"
                        placeholder="e.g. Sterile Block Manager"
                        value={newActionAssignee}
                        onChange={(e) => setNewActionAssignee(e.target.value)}
                      />
                    </div>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Action Description *</label>
                    <input 
                      type="text"
                      className="form-control"
                      placeholder="Specify required corrective/preventive step..."
                      value={newActionDesc}
                      onChange={(e) => setNewActionDesc(e.target.value)}
                      required
                    />
                  </div>
                  <div className="inline-form-actions">
                    <button type="button" className="btn-pill-secondary btn-sm" onClick={() => setIsAddingAction(false)}>
                      Cancel
                    </button>
                    <button type="submit" className="btn-pill-primary btn-sm">
                      Save Action Item
                    </button>
                  </div>
                </form>
              )}

              {/* List */}
              <div className="action-items-list">
                {capa.action_items?.length === 0 ? (
                  <p className="text-muted">No action items created yet.</p>
                ) : (
                  capa.action_items.map((item) => (
                    <div 
                      key={item.id} 
                      className={`action-item-card ${item.status === 'Completed' ? 'completed' : ''}`}
                    >
                      <button 
                        className="toggle-check-btn"
                        onClick={() => handleToggleAction(item.id, item.status)}
                      >
                        {item.status === 'Completed' ? (
                          <CheckSquare size={20} className="text-emerald-600" />
                        ) : (
                          <Square size={20} className="text-slate-400" />
                        )}
                      </button>
                      <div className="action-item-info">
                        <div className="action-type-row">
                          <span className={`action-type-badge ${item.action_type === 'Corrective Action' ? 'corrective' : 'preventive'}`}>
                            {item.action_type}
                          </span>
                          <span className="action-assignee">Assigned to: {item.assignee || 'Department Supervisor'}</span>
                        </div>
                        <p className="action-item-desc">{item.description}</p>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Footer Buttons */}
            <div className="modal-actions">
              {capa.status !== 'Completed' && (
                <button 
                  type="button" 
                  className="btn-escalate-pill"
                  onClick={handleEscalateNotice}
                >
                  <BellRing size={16} /> Send Escalation Notice to Department Head
                </button>
              )}
              <button type="button" className="btn-pill-secondary" onClick={onClose}>
                Close
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CapaDetailModal;
