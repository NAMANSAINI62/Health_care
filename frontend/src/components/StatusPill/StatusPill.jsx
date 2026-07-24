import React from 'react';

export const StatusPill = ({ status }) => {
  let pillClass = 'status-pill pending';
  if (status === 'Ready to Commit') pillClass = 'status-pill ready';
  if (status === 'Committed') pillClass = 'status-pill committed';

  return (
    <div className={pillClass}>
      ● {status || 'Pending Triage'}
    </div>
  );
};

export default StatusPill;
