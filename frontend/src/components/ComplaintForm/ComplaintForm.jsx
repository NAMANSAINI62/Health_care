import React from 'react';
import { useSelector } from 'react-redux';
import { FileText, Sparkles } from 'lucide-react';

export const ComplaintForm = () => {
  const { formData, lastUpdatedFields } = useSelector((state) => state.complaint);

  const isFieldUpdated = (fieldName) => {
    return lastUpdatedFields && lastUpdatedFields.includes(fieldName);
  };

  const fieldsConfig = [
    { key: 'complaint_source', label: 'Complaint Source / Channel', placeholder: 'e.g. Hospital Direct Email' },
    { key: 'customer_name', label: 'Customer / Reporting Entity', placeholder: 'e.g. Global Health Clinic' },
    { key: 'product_name', label: 'Product Name', placeholder: 'e.g. Metformin 500mg' },
    { key: 'product_strength', label: 'Dosage / Strength', placeholder: 'e.g. 500mg' },
    { key: 'batch_lot_number', label: 'Batch / Lot Number', placeholder: 'e.g. MFM-8812' },
    { key: 'manufacturing_date', label: 'Manufacturing Date', placeholder: 'e.g. Feb 2026' },
    { key: 'expiry_date', label: 'Expiry Date', placeholder: 'e.g. Feb 2028' },
    { key: 'affected_quantity', label: 'Affected Quantity', placeholder: 'e.g. 1000 tablets' },
    { key: 'complaint_category', label: 'Complaint Category', placeholder: 'e.g. Chipped / Capping Tablets' },
    { key: 'originating_site_block', label: 'Manufacturing Site / Block', placeholder: 'e.g. Block A - Solid Dosage' },
    { key: 'impacted_npm', label: 'Impacted Non-Product Material', placeholder: 'e.g. PVC/PVDC Blister Film' },
  ];

  return (
    <div className="form-card">
      <div className="section-header-row" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <div className="section-title" style={{ margin: 0 }}>
          <FileText size={18} className="text-blue-600" />
          Customer Complaint Form
        </div>
        <div className="ocr-badge" style={{ background: '#f0fdf4', color: '#166534', border: '1px solid #bbf7d0', padding: '4px 10px', borderRadius: '12px', fontSize: '11px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
          <Sparkles size={12} className="text-emerald-600" />
          AI Extraction Active
        </div>
      </div>

      <div className="form-grid">
        {fieldsConfig.map((field) => (
          <div key={field.key} className="form-group">
            <label className="form-label">{field.label}</label>
            <input
              type="text"
              readOnly
              tabIndex={-1}
              className={`form-control-readonly ${isFieldUpdated(field.key) ? 'field-updated-highlight' : ''}`}
              value={formData[field.key] || ''}
              placeholder={field.placeholder}
            />
          </div>
        ))}

        <div className="form-group full-width">
          <label className="form-label">Detailed Complaint Description</label>
          <textarea
            readOnly
            tabIndex={-1}
            className={`form-control-readonly ${isFieldUpdated('complaint_description') ? 'field-updated-highlight' : ''}`}
            value={formData.complaint_description || ''}
            placeholder="e.g. Chipped tablets and capping observed during hospital dispensing..."
            rows={3}
          />
        </div>
      </div>
    </div>
  );
};

export default ComplaintForm;
