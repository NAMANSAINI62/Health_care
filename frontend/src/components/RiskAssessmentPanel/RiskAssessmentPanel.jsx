import React from 'react';
import { useSelector } from 'react-redux';
import { ShieldAlert, Activity, Lightbulb } from 'lucide-react';

export const RiskAssessmentPanel = () => {
  const { riskAssessment } = useSelector((state) => state.complaint);
  const severity = (riskAssessment.severity || 'Minor').toLowerCase();

  return (
    <div className="risk-card">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div className="section-title" style={{ marginBottom: 0, borderBottom: 'none', paddingBottom: 0 }}>
          <ShieldAlert size={18} className="text-amber-500" />
          Risk Assessment & Root Cause
        </div>
        <span className={`severity-pill ${severity}`}>
          Severity: {riskAssessment.severity || 'Minor'}
        </span>
      </div>

      <div className="risk-block">
        <div className="risk-title">Suggested QMS Action</div>
        <div className="risk-text font-medium flex items-center gap-2">
          <Activity size={15} className="text-blue-600" style={{ display: 'inline', marginRight: '6px' }} />
          {riskAssessment.suggested_next_action || 'Awaiting AI complaint analysis...'}
        </div>
      </div>

      <div className="risk-block">
        <div className="risk-title">Initial Risk Narrative</div>
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
