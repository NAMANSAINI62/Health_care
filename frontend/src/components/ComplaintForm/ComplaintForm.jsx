import React, { useRef, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { FileText, Camera, UploadCloud, Sparkles, Loader2, X, CheckCircle2, AlertTriangle, Image as ImageIcon, ScanLine } from 'lucide-react';
import { scanPackagingImage } from '../../api/complaintsApi';
import { setComplaintState, setLastUpdatedFields, setScannedImagePreview, setDetectedDefects, setIsScanningImage } from '../../redux/complaintSlice';
import { addMessage, setCurrentTool } from '../../redux/chatSlice';

export const ComplaintForm = () => {
  const fileInputRef = useRef(null);
  const dispatch = useDispatch();

  const { formData, lastUpdatedFields, complaintId, scannedImagePreview, detectedDefects, isScanningImage } = useSelector((state) => state.complaint);
  const [imageFileName, setImageFileName] = useState('');
  const [scanSuccessMessage, setScanSuccessMessage] = useState('');

  const isFieldUpdated = (fieldName) => {
    return lastUpdatedFields && lastUpdatedFields.includes(fieldName);
  };

  const fieldsConfig = [
    { key: 'complaint_source', label: 'Complaint Source / Channel', placeholder: 'e.g. XYZ Image / ABC Scan' },
    { key: 'customer_name', label: 'Customer / Reporting Entity', placeholder: 'e.g. XYZ Pharmacy' },
    { key: 'product_name', label: 'Product Name', placeholder: 'e.g. ABC 000mg' },
    { key: 'product_strength', label: 'Dosage / Strength', placeholder: 'e.g. 000mg' },
    { key: 'batch_lot_number', label: 'Batch / Lot Number', placeholder: 'e.g. ABC-000000' },
    { key: 'manufacturing_date', label: 'Manufacturing Date', placeholder: 'e.g. Jan 0000' },
    { key: 'expiry_date', label: 'Expiry Date', placeholder: 'e.g. Jan 0000' },
    { key: 'affected_quantity', label: 'Affected Quantity', placeholder: 'e.g. 000 capsules' },
    { key: 'complaint_category', label: 'Complaint Category', placeholder: 'e.g. ABC Defect / ABC Damage' },
    { key: 'originating_site_block', label: 'Manufacturing Site / Block', placeholder: 'e.g. ABC Block' },
    { key: 'impacted_npm', label: 'Impacted Non-Product Material', placeholder: 'e.g. ABC Foil / ABC Glass' },
  ];

  const handleImageFileSelect = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const validFormats = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp'];
    if (!validFormats.includes(file.type)) {
      alert('Invalid image format. Please upload a PNG, JPG, JPEG, or WEBP packaging photo.');
      return;
    }

    const previewUrl = URL.createObjectURL(file);
    dispatch(setScannedImagePreview(previewUrl));
    setImageFileName(file.name);
    dispatch(setIsScanningImage(true));
    setScanSuccessMessage('');

    dispatch(addMessage({
      id: Date.now().toString(),
      role: 'user',
      content: `📷 Uploaded packaging image for AI OCR & defect analysis: ${file.name}`,
      tool_used: 'multimodal_image_ocr'
    }));

    try {
      const response = await scanPackagingImage(file, complaintId);

      dispatch(setComplaintState({
        complaint_id: response.complaint_id,
        form_data: response.form_data,
        risk_assessment: response.risk_assessment,
        status: response.status,
        detected_defects: response.detected_defects || []
      }));

      if (response.form_data) {
        const nonNullKeys = Object.keys(response.form_data).filter(k => Boolean(response.form_data[k]));
        dispatch(setLastUpdatedFields(nonNullKeys));
      }

      dispatch(setCurrentTool('multimodal_image_ocr'));
      setScanSuccessMessage(response.assistant_message || 'Vision OCR scan completed successfully!');

      dispatch(addMessage({
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.assistant_message || `Vision LLM processed packaging image ${file.name}. Form auto-filled.`,
        tool_used: 'multimodal_image_ocr'
      }));

    } catch (err) {
      console.error('Error scanning packaging image:', err);
      dispatch(addMessage({
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: '⚠️ Failed to extract OCR details from image. Please ensure image is clear.',
        tool_used: 'multimodal_image_ocr'
      }));
    } finally {
      dispatch(setIsScanningImage(false));
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleClearImage = () => {
    dispatch(setScannedImagePreview(null));
    dispatch(setDetectedDefects([]));
    setImageFileName('');
    setScanSuccessMessage('');
  };

  return (
    <div className="form-card">
      <div className="section-header-row" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <div className="section-title" style={{ margin: 0 }}>
          <FileText size={18} className="text-blue-600" />
          Customer Complaint Form
        </div>
        <div className="ocr-badge" style={{ background: '#f0fdf4', color: '#166534', border: '1px solid #bbf7d0', padding: '4px 10px', borderRadius: '12px', fontSize: '11px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
          <Sparkles size={12} className="text-emerald-600" />
          OCR Enabled
        </div>
      </div>

      {/* Multimodal OCR Image Scanning Dropzone & Card */}
      <div className="ocr-scanner-banner">
        <input
          type="file"
          ref={fileInputRef}
          accept="image/png, image/jpeg, image/jpg, image/webp"
          style={{ display: 'none' }}
          onChange={handleImageFileSelect}
        />

        {!scannedImagePreview ? (
          <div
            className="ocr-upload-dropzone"
            onClick={() => fileInputRef.current?.click()}
          >
            <div className="ocr-dropzone-icon">
              <Camera size={24} className="text-blue-600" />
            </div>
            <div className="ocr-dropzone-text">
              <span className="ocr-dropzone-title">Scan Packaging Image (AI Vision OCR & Defect Detection)</span>
              <span className="ocr-dropzone-subtitle">Click or drop packaging photo (.png, .jpg, .jpeg) to extract the data</span>
            </div>
            <button type="button" className="btn-scan-action">
              <ScanLine size={14} /> Upload & Scan
            </button>
          </div>
        ) : (
          <div className="ocr-preview-container">
            <div className="ocr-preview-thumbnail-wrapper">
              <img src={scannedImagePreview} alt="Packaging scan" className="ocr-preview-thumbnail" />
              {isScanningImage && (
                <div className="ocr-scanner-laser-line" />
              )}
            </div>

            <div className="ocr-preview-info">
              <div className="ocr-file-header">
                <span className="ocr-filename"><ImageIcon size={14} /> {imageFileName || 'packaging_photo.jpg'}</span>
                <button type="button" className="ocr-btn-close" onClick={handleClearImage} title="Remove image">
                  <X size={14} />
                </button>
              </div>

              {isScanningImage ? (
                <div className="ocr-scanning-status">
                  <Loader2 size={16} className="animate-spin text-blue-600" />
                  <span>Groq Vision LLM inspecting packaging & extracting text...</span>
                </div>
              ) : (
                <>
                  <div className="ocr-scan-success">
                    <CheckCircle2 size={15} className="text-emerald-600" />
                    <span>Visual defect & text extraction complete</span>
                  </div>

                  {detectedDefects && detectedDefects.length > 0 && (
                    <div className="ocr-defects-tags">
                      <span className="defect-tag-label"><AlertTriangle size={11} /> Detected Anomalies:</span>
                      {detectedDefects.map((defect, idx) => (
                        <span key={idx} className="defect-pill">{defect}</span>
                      ))}
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        )}
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
            placeholder="e.g. Discolored capsules, damaged blister pack foil seal..."
            rows={3}
          />
        </div>
      </div>
    </div>
  );
};

export default ComplaintForm;
