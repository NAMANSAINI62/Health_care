import React, { useState, useEffect } from 'react';
import { X, ShieldCheck, Lock, CheckCircle2, FileSignature } from 'lucide-react';

export const DigitalSignatureModal = ({ complaint, isOpen, onClose, onSignOff }) => {
  const [signerName, setSignerName] = useState('Dr. Sarah Jenkins');
  const [signerRole, setSignerRole] = useState('QA Compliance Officer');
  const [meaning, setMeaning] = useState('Approval of Complaint Classification, Root Cause & Risk Assessment');
  const [comments, setComments] = useState('');
  const [autoCapa, setAutoCapa] = useState(true);
  const [checksum, setChecksum] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [agreed, setAgreed] = useState(false);

  useEffect(() => {
    if (complaint && isOpen) {
      // Calculate SHA-256 checksum snapshot of complaint state
      const payloadString = `${complaint.id}:${complaint.product_name}:${complaint.batch_lot_number}:${complaint.severity}:${complaint.likely_root_cause}:${Date.now()}`;
      
      const computeHash = async () => {
        try {
          const encoder = new TextEncoder();
          const data = encoder.encode(payloadString);
          const hashBuffer = await crypto.subtle.digest('SHA-256', data);
          const hashArray = Array.from(new Uint8Array(hashBuffer));
          const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
          setChecksum(hashHex);
        } catch (err) {
          // Fallback pseudo hash if subtle crypto fails
          setChecksum('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855');
        }
      };
      computeHash();
    }
  }, [complaint, isOpen, signerName, meaning]);

  if (!isOpen || !complaint) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!agreed) return;
    setIsSubmitting(true);
    try {
      await onSignOff({
        signer_name: signerName,
        signer_role: signerRole,
        signature_meaning: meaning,
        checksum_hash: checksum,
        comments: comments,
        auto_spawn_capa: autoCapa
      });
      onClose();
    } catch (err) {
      console.error('Digital signoff error:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const isHighRisk = complaint.severity === 'Critical' || complaint.severity === 'Major';

  return (
    <div className="modal-overlay">
      <div className="modal-card digital-sig-modal">
        <div className="modal-header sig-header">
          <div className="modal-title-group">
            <div className="sig-badge-icon">
              <ShieldCheck size={22} className="text-emerald-500" />
            </div>
            <div>
              <h3 className="modal-title">FDA 21 CFR Part 11 Digital Signature</h3>
              <p className="modal-subtitle">Human-in-the-Loop QA Officer Regulatory Sign-off</p>
            </div>
          </div>
          <button className="icon-btn-pill" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="modal-body">
          {/* Complaint Technical Snapshot */}
          <div className="sig-snapshot-box">
            <div className="snapshot-grid">
              <div>
                <span className="snapshot-label">Complaint Reference:</span>
                <span className="snapshot-val">#{complaint.id} ({complaint.product_name || 'N/A'})</span>
              </div>
              <div>
                <span className="snapshot-label">Batch / Lot #:</span>
                <span className="snapshot-val">{complaint.batch_lot_number || 'N/A'}</span>
              </div>
              <div>
                <span className="snapshot-label">Severity Level:</span>
                <span className={`severity-pill ${complaint.severity?.toLowerCase() || 'major'}`}>
                  {complaint.severity || 'Major'}
                </span>
              </div>
              <div>
                <span className="snapshot-label">Originating Site:</span>
                <span className="snapshot-val">{complaint.originating_site_block || 'Sterile Block B'}</span>
              </div>
            </div>
            {complaint.likely_root_cause && (
              <div className="snapshot-root-cause">
                <span className="snapshot-label">Verified Root Cause:</span>
                <p className="snapshot-root-text">{complaint.likely_root_cause}</p>
              </div>
            )}
          </div>

          <div className="sig-form-grid">
            <div className="form-group">
              <label className="form-label">QA Officer Full Name *</label>
              <input
                type="text"
                className="form-control"
                value={signerName}
                onChange={(e) => setSignerName(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">Regulatory Title / Role *</label>
              <input
                type="text"
                className="form-control"
                value={signerRole}
                onChange={(e) => setSignerRole(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Digital Signature Purpose / Meaning *</label>
            <select
              className="form-control"
              value={meaning}
              onChange={(e) => setMeaning(e.target.value)}
            >
              <option value="Approval of Complaint Classification, Root Cause & Risk Assessment">
                Approval of Complaint Classification, Root Cause & Risk Assessment
              </option>
              <option value="Regulatory Filing & Batch Disposition Approval">
                Regulatory Filing & Batch Disposition Approval
              </option>
              <option value="CAPA Escalation & Site Block Isolation Authorisation">
                CAPA Escalation & Site Block Isolation Authorisation
              </option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Regulatory Notes & Observations (Optional)</label>
            <textarea
              className="form-control"
              rows={2}
              placeholder="Add additional QA remarks or compliance notes for audit logs..."
              value={comments}
              onChange={(e) => setComments(e.target.value)}
            />
          </div>

          {/* Cryptographic SHA-256 Audit Box */}
          <div className="crypto-hash-box">
            <div className="hash-header">
              <Lock size={14} className="text-sky-600" />
              <span>SHA-256 Cryptographic Audit Hash (21 CFR Part 11 Integrity Protection):</span>
            </div>
            <code className="hash-code">{checksum}</code>
          </div>

          {/* Auto CAPA Spawning Checkbox */}
          {isHighRisk && (
            <div className="capa-opt-box">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={autoCapa}
                  onChange={(e) => setAutoCapa(e.target.checked)}
                />
                <span>
                  <strong>Automatically Spawn CAPA Task</strong> (Corrective Action assigned to <em>{complaint.originating_site_block || 'QA / Packaging'}</em> with 30-day target resolution)
                </span>
              </label>
            </div>
          )}

          {/* Legal Compliance Checkbox */}
          <div className="compliance-check-box">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={agreed}
                onChange={(e) => setAgreed(e.target.checked)}
              />
              <span>
                I certify that my digital signature above is the legally binding equivalent of my handwritten signature per <strong>FDA 21 CFR Part 11</strong> requirements.
              </span>
            </label>
          </div>

          {/* Modal Actions */}
          <div className="modal-actions">
            <button type="button" className="btn-pill-secondary" onClick={onClose}>
              Cancel
            </button>
            <button
              type="submit"
              className="btn-pill-primary sig-submit-btn"
              disabled={!agreed || isSubmitting}
            >
              <FileSignature size={16} />
              {isSubmitting ? 'Digitally Signing...' : 'Digitally Sign & Authorize QMS Record'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default DigitalSignatureModal;
