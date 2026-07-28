import React, { useState, useEffect } from 'react';
import { 
  ClipboardCheck, 
  AlertTriangle, 
  Clock, 
  Building2, 
  UserCheck, 
  Search, 
  Filter, 
  Plus, 
  ArrowUpRight,
  ShieldAlert,
  CheckCircle2,
  BellRing
} from 'lucide-react';
import { fetchCapas, escalateCapa, createCapa } from '../../api/complaintsApi';
import CapaDetailModal from '../CapaDetailModal/CapaDetailModal';

export const CapaDashboard = ({ onSelectComplaint }) => {
  const [capas, setCapas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDepartment, setSelectedDepartment] = useState('All');
  const [selectedStatus, setSelectedStatus] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [activeCapa, setActiveCapa] = useState(null);
  const [isDetailOpen, setIsDetailOpen] = useState(false);
  const [isCreateOpen, setIsCreateOpen] = useState(false);

  // New CAPA Form State
  const [newTitle, setNewTitle] = useState('');
  const [newDepartment, setNewDepartment] = useState('Packaging Line 2');
  const [newSeverity, setNewSeverity] = useState('Major');
  const [newAssignee, setNewAssignee] = useState('Process Specialist');
  const [newDesc, setNewDesc] = useState('');

  const loadCapas = async () => {
    setLoading(true);
    try {
      const data = await fetchCapas();
      setCapas(data);
    } catch (err) {
      console.error('Failed to load CAPAs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCapas();
  }, []);

  const handleEscalate = async (capaId, currentLevel) => {
    const nextLevel = currentLevel.includes('Level 1') ? 'Escalated - Level 2' : 'Escalated - Level 1';
    try {
      await escalateCapa(capaId, nextLevel);
      await loadCapas();
    } catch (err) {
      console.error('Escalation failed:', err);
    }
  };

  const handleCreateCapaSubmit = async (e) => {
    e.preventDefault();
    try {
      await createCapa({
        title: newTitle,
        description: newDesc,
        owner_department: newDepartment,
        severity: newSeverity,
        assignee_name: newAssignee,
        due_days: 30
      });
      setIsCreateOpen(false);
      setNewTitle('');
      setNewDesc('');
      await loadCapas();
    } catch (err) {
      console.error('Failed to create CAPA:', err);
    }
  };

  // Metrics
  const totalCapas = capas.length;
  const openCapas = capas.filter(c => c.status !== 'Completed').length;
  const overdueCapas = capas.filter(c => c.status === 'Overdue' || c.escalation_status !== 'Normal').length;
  const criticalCapas = capas.filter(c => c.severity === 'Critical' || c.severity === 'Major').length;

  // Filtered List
  const filteredCapas = capas.filter(c => {
    const matchesDept = selectedDepartment === 'All' || c.owner_department.toLowerCase().includes(selectedDepartment.toLowerCase());
    const matchesStatus = selectedStatus === 'All' || c.status.toLowerCase() === selectedStatus.toLowerCase();
    const matchesSearch = searchQuery === '' || 
      c.capa_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (c.owner_department && c.owner_department.toLowerCase().includes(searchQuery.toLowerCase()));

    return matchesDept && matchesStatus && matchesSearch;
  });

  return (
    <div className="capa-dashboard-container">
      {/* Header Banner */}
      <div className="capa-header-banner">
        <div>
          <h2 className="capa-dashboard-title">
            <ClipboardCheck size={24} className="text-sky-600" />
            CAPA (Corrective and Preventive Action) Management Module
          </h2>
          <p className="capa-dashboard-subtitle">
            Track site block execution, department action items, and regulatory escalation workflows.
          </p>
        </div>
        <button 
          className="btn-pill-primary"
          onClick={() => setIsCreateOpen(true)}
        >
          <Plus size={16} /> New CAPA Task
        </button>
      </div>

      {/* Metrics Row */}
      <div className="capa-metrics-grid">
        <div className="capa-metric-card blue">
          <div className="metric-icon-box">
            <ClipboardCheck size={20} />
          </div>
          <div>
            <div className="metric-value">{openCapas}</div>
            <div className="metric-label">Active / Open CAPAs</div>
          </div>
        </div>

        <div className="capa-metric-card red">
          <div className="metric-icon-box">
            <AlertTriangle size={20} />
          </div>
          <div>
            <div className="metric-value">{overdueCapas}</div>
            <div className="metric-label">Overdue & Escalated</div>
          </div>
        </div>

        <div className="capa-metric-card orange">
          <div className="metric-icon-box">
            <ShieldAlert size={20} />
          </div>
          <div>
            <div className="metric-value">{criticalCapas}</div>
            <div className="metric-label">High-Risk (Critical/Major)</div>
          </div>
        </div>

        <div className="capa-metric-card emerald">
          <div className="metric-icon-box">
            <CheckCircle2 size={20} />
          </div>
          <div>
            <div className="metric-value">{totalCapas - openCapas}</div>
            <div className="metric-label">Completed CAPAs</div>
          </div>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="capa-filter-bar">
        <div className="search-input-wrapper">
          <Search size={16} className="search-icon" />
          <input
            type="text"
            className="capa-search-input"
            placeholder="Search CAPA #, title, or department..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="filter-group">
          <label className="filter-label">
            <Building2 size={14} /> Department:
          </label>
          <select 
            className="filter-select"
            value={selectedDepartment}
            onChange={(e) => setSelectedDepartment(e.target.value)}
          >
            <option value="All">All Departments</option>
            <option value="Packaging">Packaging Line</option>
            <option value="Sterile Block B">Sterile Block B</option>
            <option value="Quality Assurance">Quality Assurance</option>
            <option value="Quality Control">Quality Control</option>
            <option value="Formulation">Formulation</option>
          </select>
        </div>

        <div className="filter-group">
          <label className="filter-label">
            <Filter size={14} /> Status:
          </label>
          <select 
            className="filter-select"
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
          >
            <option value="All">All Statuses</option>
            <option value="Open">Open</option>
            <option value="In Progress">In Progress</option>
            <option value="Completed">Completed</option>
            <option value="Overdue">Overdue</option>
          </select>
        </div>
      </div>

      {/* CAPA List Grid */}
      {loading ? (
        <div className="capa-loading-state">Loading CAPA database records...</div>
      ) : filteredCapas.length === 0 ? (
        <div className="capa-empty-state">No CAPA tasks match the selected filters.</div>
      ) : (
        <div className="capa-cards-grid">
          {filteredCapas.map((capa) => {
            const completedActions = capa.action_items?.filter(a => a.status === 'Completed').length || 0;
            const totalActions = capa.action_items?.length || 0;
            const progressPercent = totalActions > 0 ? Math.round((completedActions / totalActions) * 100) : 0;
            const isEscalated = capa.escalation_status !== 'Normal';

            return (
              <div key={capa.id} className={`capa-card ${isEscalated ? 'escalated-border' : ''}`}>
                <div className="capa-card-header">
                  <div className="capa-title-group">
                    <span className="capa-number-badge">{capa.capa_number}</span>
                    {capa.complaint_id && (
                      <span className="complaint-link-chip" onClick={() => onSelectComplaint && onSelectComplaint(capa.complaint_id)}>
                        Parent Complaint #{capa.complaint_id} <ArrowUpRight size={12} />
                      </span>
                    )}
                  </div>
                  <span className={`severity-pill ${capa.severity.toLowerCase()}`}>
                    {capa.severity}
                  </span>
                </div>

                <h4 className="capa-card-title">{capa.title}</h4>
                <p className="capa-card-desc">{capa.description || 'No description provided.'}</p>

                <div className="capa-meta-row">
                  <div className="meta-item">
                    <Building2 size={14} />
                    <span><strong>Dept:</strong> {capa.owner_department}</span>
                  </div>
                  <div className="meta-item">
                    <UserCheck size={14} />
                    <span><strong>Assignee:</strong> {capa.assignee_name || 'QA Lead'}</span>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="capa-progress-section">
                  <div className="progress-header">
                    <span>Action Items Completion</span>
                    <span className="progress-value">{completedActions}/{totalActions} ({progressPercent}%)</span>
                  </div>
                  <div className="progress-bar-track">
                    <div 
                      className="progress-bar-fill"
                      style={{ width: `${progressPercent}%` }}
                    />
                  </div>
                </div>

                {/* Status & Escalation Footer */}
                <div className="capa-card-footer">
                  <div className="footer-left">
                    <span className={`capa-status-badge ${capa.status.toLowerCase().replace(/\s+/g, '-')}`}>
                      ● {capa.status}
                    </span>
                    {isEscalated && (
                      <span className="escalation-badge">
                        <BellRing size={12} /> {capa.escalation_status}
                      </span>
                    )}
                  </div>

                  <div className="footer-actions">
                    {capa.status !== 'Completed' && (
                      <button 
                        className="btn-escalate"
                        title="Send Escalation Reminder Notice"
                        onClick={() => handleEscalate(capa.id, capa.escalation_status)}
                      >
                        <BellRing size={14} /> Escalate
                      </button>
                    )}
                    <button 
                      className="btn-pill-secondary btn-sm"
                      onClick={() => {
                        setActiveCapa(capa);
                        setIsDetailOpen(true);
                      }}
                    >
                      View Details & Actions
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* CAPA Detail Modal */}
      {isDetailOpen && activeCapa && (
        <CapaDetailModal
          capaId={activeCapa.id}
          isOpen={isDetailOpen}
          onClose={() => {
            setIsDetailOpen(false);
            setActiveCapa(null);
            loadCapas();
          }}
          onSelectComplaint={onSelectComplaint}
        />
      )}

      {/* Manual Create CAPA Modal */}
      {isCreateOpen && (
        <div className="modal-overlay">
          <div className="modal-card">
            <div className="modal-header">
              <h3 className="modal-title">Create Manual CAPA Task</h3>
              <button className="icon-btn-pill" onClick={() => setIsCreateOpen(false)}>×</button>
            </div>
            <form onSubmit={handleCreateCapaSubmit} className="modal-body">
              <div className="form-group">
                <label className="form-label">CAPA Title *</label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="e.g. Inspect Packaging Line 2 Blister Sealing Parameters"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  required
                />
              </div>

              <div className="form-grid">
                <div className="form-group">
                  <label className="form-label">Owner Department *</label>
                  <select 
                    className="form-control"
                    value={newDepartment}
                    onChange={(e) => setNewDepartment(e.target.value)}
                  >
                    <option value="Packaging Line 2">Packaging Line 2</option>
                    <option value="Sterile Block B">Sterile Block B</option>
                    <option value="Quality Assurance">Quality Assurance</option>
                    <option value="Quality Control">Quality Control</option>
                    <option value="Formulation">Formulation</option>
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Severity Level *</label>
                  <select 
                    className="form-control"
                    value={newSeverity}
                    onChange={(e) => setNewSeverity(e.target.value)}
                  >
                    <option value="Critical">Critical</option>
                    <option value="Major">Major</option>
                    <option value="Minor">Minor</option>
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Assignee Name</label>
                <input
                  type="text"
                  className="form-control"
                  value={newAssignee}
                  onChange={(e) => setNewAssignee(e.target.value)}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Description & Scope</label>
                <textarea
                  className="form-control"
                  rows={3}
                  placeholder="Detailed breakdown of corrective action scope..."
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                />
              </div>

              <div className="modal-actions">
                <button type="button" className="btn-pill-secondary" onClick={() => setIsCreateOpen(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-pill-primary">
                  Create CAPA Task
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default CapaDashboard;
