import React from 'react';

export const StatusPill = ({ status }) => {
  let pillClass = 'status-pill pending';
  if (status === 'Ready to Commit') pillClass = 'status-pill ready';
  if (status === 'Committed' || status === 'QA Approved') pillClass = 'status-pill committed';
  if (status === 'Pending QA Signoff') pillClass = 'status-pill hitl';
  if (status === 'CAPA Initiated') pillClass = 'status-pill capa';

  return (
    <div className={pillClass}>
      ● {status || 'Pending Triage'}
    </div>
  );
};

export default StatusPill;