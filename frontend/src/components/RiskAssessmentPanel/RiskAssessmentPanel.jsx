import React from 'react';
import { useSelector } from 'react-redux';
import { ShieldAlert, Activity, Lightbulb, ClipboardCheck, ArrowUpRight } from 'lucide-react';

export const RiskAssessmentPanel = ({ onOpenCapaTab, activeComplaintFull }) => {
  const { riskAssessment, status, complaintId } = useSelector((state) => state.complaint);
  const severity = (riskAssessment.severity || 'Minor').toLowerCase();

  const capas = activeComplaintFull?.capas || [];
  const linkedCapa = capas.length > 0 ? capas[0] : null;

  return (
    <div className="risk-card">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div className="section-title" style={{ marginBottom: 0, borderBottom: 'none', paddingBottom: 0 }}>
          <ShieldAlert size={18} className="text-amber-500" />
          Risk Assessment & Regulatory Verification
        </div>
        <span className={`severity-pill ${severity}`}>
          Severity: {riskAssessment.severity || 'Minor'}
        </span>
      </div>

      {/* Linked CAPA Badge */}
      {linkedCapa && (
        <div className="linked-capa-banner" onClick={onOpenCapaTab}>
          <div className="flex items-center gap-2">
            <ClipboardCheck size={18} className="text-sky-600" />
            <div>
              <strong>Linked CAPA Task Spawened: {linkedCapa.capa_number}</strong>
              <div className="text-xs text-sky-800">
                Department: {linkedCapa.owner_department} • Status: {linkedCapa.status}
              </div>
            </div>
          </div>
          <ArrowUpRight size={16} className="text-sky-600" />
        </div>
      )}

      <div className="risk-block">
        <div className="risk-title" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Activity size={15} className="text-blue-600" />
          Prevention & Corrective Solution (Suggested QMS Action)
        </div>
        <div className="risk-text font-medium" style={{ color: '#0369a1', background: '#f0f9ff', padding: '10px 12px', borderRadius: '8px', border: '1px solid #bae6fd' }}>
          {riskAssessment.suggested_next_action || 'Awaiting AI complaint analysis...'}
        </div>
      </div>

      <div className="risk-block">
        <div className="risk-title">Diagnosis & Initial Risk Narrative</div>
        <div className="risk-text">
          {riskAssessment.initial_risk_assessment || 'No risk narrative generated yet.'}
        </div>
      </div>

      <div className="root-cause-banner">
        <div className="risk-title" style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#0369a1' }}>
          <Lightbulb size={15} className="text-amber-500" />
          Predicted Root Cause Recommendation
        </div>
        <div style={{ fontSize: '13px', fontWeight: '500', color: '#0c4a6e', marginTop: '4px', lineHeight: '1.5' }}>
          {riskAssessment.likely_root_cause || 'Root cause will be automatically predicted from complaint details.'}
        </div>
      </div>
    </div>
  );
};

export default RiskAssessmentPanel;
