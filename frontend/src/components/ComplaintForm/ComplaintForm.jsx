import React from 'react';
import { useSelector } from 'react-redux';
import { FileText } from 'lucide-react';

export const ComplaintForm = () => {
  const { formData, lastUpdatedFields } = useSelector((state) => state.complaint);

  const isFieldUpdated = (fieldName) => {
    return lastUpdatedFields && lastUpdatedFields.includes(fieldName);
  };

  const fieldsConfig = [
    { key: 'complaint_source', label: 'Complaint Source / Channel', placeholder: 'e.g. Pharmacy / Hospital' },
    { key: 'customer_name', label: 'Customer / Reporting Entity', placeholder: 'e.g. Apollo Pharmacy' },
    { key: 'product_name', label: 'Product Name', placeholder: 'e.g. Amoxicillin' },
    { key: 'product_strength', label: 'Dosage / Strength', placeholder: 'e.g. 500mg' },
    { key: 'batch_lot_number', label: 'Batch / Lot Number', placeholder: 'e.g. BMX-240602' },
    { key: 'manufacturing_date', label: 'Manufacturing Date', placeholder: 'e.g. Jan 2026' },
    { key: 'expiry_date', label: 'Expiry Date', placeholder: 'e.g. Jan 2028' },
    { key: 'affected_quantity', label: 'Affected Quantity', placeholder: 'e.g. 48 capsules' },
    { key: 'complaint_category', label: 'Complaint Category', placeholder: 'e.g. Discoloration' },
    { key: 'originating_site_block', label: 'Manufacturing Site / Block', placeholder: 'e.g. Block B' },
    { key: 'impacted_npm', label: 'Impacted Non-Product Material', placeholder: 'e.g. Blister Foil' },
  ];

  return (
    <div className="form-card">
      <div className="section-title">
        <FileText size={18} className="text-blue-600" />
        Customer Complaint Form
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
            placeholder="e.g. Discolored capsules..."
            rows={3}
          />
        </div>
      </div>
    </div>
  );
};

export default ComplaintForm;
