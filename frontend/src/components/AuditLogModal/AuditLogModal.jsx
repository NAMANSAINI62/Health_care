import React, { useState, useEffect } from 'react';
import { X, History, Sparkles, Edit3, ArrowRight, Clock, ShieldCheck, Layers, ChevronDown, ChevronUp } from 'lucide-react';
import { fetchComplaintAudit } from '../../api/complaintsApi';

// Friendly labels for form fields
const FIELD_LABELS = {
  complaint_source: "Complaint Source",
  customer_name: "Customer / Entity",
  product_name: "Product Name",
  product_strength: "Dosage / Strength",
  batch_lot_number: "Batch / Lot Number",
  manufacturing_date: "Manufacturing Date",
  expiry_date: "Expiry Date",
  affected_quantity: "Affected Quantity",
  complaint_category: "Complaint Category",
  complaint_description: "Complaint Description",
  originating_site_block: "Manufacturing Site / Block",
  impacted_npm: "Impacted Material (NPM)",
  status: "Complaint Status",
  severity: "Risk Severity",
  suggested_next_action: "Suggested Next Action"
};

export const AuditLogModal = ({ complaintId, isOpen, onClose }) => {
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [expandedEvents, setExpandedEvents] = useState({});

  // 1. Fetch all the audit logs from backend whenever modal opens
  useEffect(() => {
    if (isOpen && complaintId) {
      setLoading(true);
      fetchComplaintAudit(complaintId)
        .then((logs) => {
          setAuditLogs(logs);
          setExpandedEvents({}); //  it is a key-value dictionary that tracks which camplaint is open
        })
        .catch((err) => console.error('Error fetching audit logs:', err))
        .finally(() => setLoading(false));
    }
  }, [isOpen, complaintId]);

  // 2. Toggle card is used to open and close when user clicks a camplaint
  const toggleEventExpand = (eventId) => {
    setExpandedEvents((prev) => ({
      ...prev,
      [eventId]: !prev[eventId]
    }));
  };

  // 3. Format timestamp to friendly Indian Standard Time (IST) format
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

  // 4. Intent & Category-Based Logic: Group logs into Initial Extraction vs. Field Modifications
  const groupLogsByEvent = (logs) => {
    if (!logs || logs.length === 0) return [];

    const sortedLogs = [...logs].sort(
      (a, b) => new Date(a.changed_at || 0) - new Date(b.changed_at || 0)
    );

    const initialItems = [];
    const updateItems = [];

    const initialTimestamp = sortedLogs.length > 0 ? new Date(sortedLogs[0].changed_at || 0).getTime() : 0;

    for (const log of sortedLogs) {
      const logTime = new Date(log.changed_at || 0).getTime();
      // Initial extracting log old_value and new_value both are blank or empty or maybe it was logged during initial creation window within 2s
      const isInitialBatch = (!log.old_value || !log.old_value.trim()) || Math.abs(logTime - initialTimestamp) < 2000;
      
      if (isInitialBatch) {
        initialItems.push(log);
      } else {
        updateItems.push(log);
      }
    }

    const resultGroups = [];

    // Category Card 1: Initial Extraction & Form Auto-Fill
    if (initialItems.length > 0) {
      const latestInitialTime = initialItems[initialItems.length - 1].changed_at || initialItems[0].changed_at;
      resultGroups.push({
        id: 'group_initial',
        isInitialLog: true,
        changed_at: latestInitialTime,
        changed_by: 'User',
        eventTitle: 'Initial Complaint Extraction & Form Auto-Fill',
        items: initialItems
      });
    }

    // Category Card 2: Complaint Field Modifications & Updates
    if (updateItems.length > 0) {
      const latestUpdateTime = updateItems[updateItems.length - 1].changed_at || updateItems[0].changed_at;
      resultGroups.push({
        id: 'group_updates',
        isInitialLog: false,
        changed_at: latestUpdateTime,
        changed_by: 'User',
        eventTitle: `Complaint Field Modifications & Updates (${updateItems.length} ${updateItems.length === 1 ? 'field' : 'fields'} modified)`,
        items: updateItems
      });
    }

    return resultGroups;
  };

  // 5. Simple Human Logic: Create a 1-line plain English summary for collapsed headers
  const getHeaderSummary = (items, isInitialLog) => {
    if (!items || items.length === 0) return '';

    const getFieldValue = (key) => {
      const found = items.find((item) => item.field_name === key);
      return found ? found.new_value : null;
    };

    // Case A: Initial Form Auto-Fill Card Summary
    if (isInitialLog) {
      const productName = getFieldValue('product_name') || 'Product';
      const batchNumber = getFieldValue('batch_lot_number');
      const customerName = getFieldValue('customer_name');

      let text = `Auto-filled ${productName}`;
      if (batchNumber) text += ` (Batch: ${batchNumber})`;
      if (customerName) text += ` for ${customerName}`;
      return text;
    }

    // Case B: Field Modifications & Updates Card Summary
    const changeSummaryList = [];
    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      const friendlyName = FIELD_LABELS[item.field_name] || item.field_name;

      if (item.old_value && item.old_value.trim()) {
        changeSummaryList.push(`${friendlyName}: ${item.old_value} → ${item.new_value}`);
      } else {
        changeSummaryList.push(`${friendlyName}: ${item.new_value}`);
      }
    }

    if (changeSummaryList.length <= 3) {
      return changeSummaryList.join(' • ');
    } else {
      return `${changeSummaryList[0]} • ${changeSummaryList[1]} + ${changeSummaryList.length - 2} more`;
    }
  };

  if (!isOpen) return null;

  const eventGroups = groupLogsByEvent(auditLogs);

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card audit-modal-card" onClick={(e) => e.stopPropagation()}>
        {/* Modal Header */}
        <div className="modal-header flex justify-between items-center">
          <div className="flex items-center gap-2">
            <div className="p-2 bg-blue-50 text-blue-600 rounded-lg">
              <History size={20} />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-800">
                Audit Trail & History Log — Complaint #{complaintId}
              </h3>
              <p className="text-xs text-slate-500">
                Grouped timeline of AI extraction & user modification events
              </p>
            </div>
          </div>
          <button onClick={onClose} className="modal-close-btn">
            <X size={18} />
          </button>
        </div>

        {/* Modal Body */}
        <div className="modal-body audit-modal-body">
          {loading ? (
            <div className="text-center text-slate-500 py-12 flex flex-col items-center gap-2">
              <div className="spinner-blue"></div>
              <span>Loading audit trail events...</span>
            </div>
          ) : eventGroups.length === 0 ? (
            <div className="text-center text-slate-500 py-12 bg-slate-50 rounded-xl border border-dashed border-slate-200">
              <ShieldCheck size={32} className="mx-auto text-slate-400 mb-2" />
              <p className="font-semibold text-slate-700">No Field Audit Events Recorded</p>
              <p className="text-xs text-slate-400 mt-1">Changes made to complaint fields will appear grouped here.</p>
            </div>
          ) : (
            <div className="audit-events-container">
              {eventGroups.map((event, index) => {
                const eventKey = event.id || index;
                const isExpanded = Boolean(expandedEvents[eventKey]);
                const isInitialLog = event.isInitialLog;
                const eventTitle = event.eventTitle;
                
                const summarySubtitle = getHeaderSummary(event.items, isInitialLog);

                return (
                  <div key={eventKey} className={`audit-event-card ${isExpanded ? 'expanded' : 'collapsed'}`}>
                    {/* Event Card Header (Click to expand/collapse) */}
                    <div 
                      className="audit-event-header clickable" 
                      onClick={() => toggleEventExpand(eventKey)}
                      title={isExpanded ? "Click to collapse details" : "Click to expand details"}
                    >
                      <div className="audit-event-title-box">
                        {isInitialLog ? (
                          <span className="audit-icon-badge initial">
                            <Sparkles size={15} />
                          </span>
                        ) : (
                          <span className="audit-icon-badge update">
                            <Edit3 size={15} />
                          </span>
                        )}
                        <div>
                          <h4 className="audit-event-title">{eventTitle}</h4>
                          {summarySubtitle && (
                            <p className="audit-event-summary-text">
                              {summarySubtitle}
                            </p>
                          )}
                          <div className="audit-event-meta">
                            <span className="audit-actor-pill">
                              <ShieldCheck size={12} />
                              User
                            </span>
                            <span className="audit-timestamp">
                              <Clock size={12} />
                              {formatISTTimestamp(event.changed_at)}
                            </span>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-3" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <span className="audit-count-badge">
                          <Layers size={13} />
                          {event.items.length} {event.items.length === 1 ? 'Change' : 'Changes'}
                        </span>
                        <button className="audit-chevron-btn" aria-label="Toggle Expand">
                          {isExpanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                        </button>
                      </div>
                    </div>

                    {/* Event Card Body (Shows delta chips only when expanded) */}
                    {isExpanded && (
                      <div className="audit-event-body animate-fadeIn">
                        <div className="audit-chips-grid">
                          {event.items.map((item) => {
                            const friendlyName = FIELD_LABELS[item.field_name] || item.field_name;
                            const hasPreviousValue = Boolean(item.old_value && item.old_value.trim());

                            return (
                              <div key={item.id} className="audit-field-chip">
                                <div className="chip-header">
                                  <span className="chip-label">{friendlyName}</span>
                                  <span className="chip-key font-mono">{item.field_name}</span>
                                </div>
                                <div className="chip-delta">
                                  {hasPreviousValue ? (
                                    <span className="val-old" title={item.old_value}>
                                      {item.old_value}
                                    </span>
                                  ) : (
                                    <span className="val-added">
                                      + Initial Entry
                                    </span>
                                  )}
                                  <ArrowRight size={13} className="delta-arrow" />
                                  <span className="val-new" title={item.new_value}>
                                    {item.new_value || 'EMPTY'}
                                  </span>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AuditLogModal;
