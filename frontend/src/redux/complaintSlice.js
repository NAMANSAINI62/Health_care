import { createSlice } from '@reduxjs/toolkit';

const initialFormData = {
  complaint_source: '',
  customer_name: '',
  product_name: '',
  product_strength: '',
  batch_lot_number: '',
  manufacturing_date: '',
  expiry_date: '',
  affected_quantity: '',
  complaint_category: '',
  complaint_description: '',
  originating_site_block: '',
  impacted_npm: '',
};

const initialRiskAssessment = {
  severity: 'Minor',
  suggested_next_action: 'Awaiting AI Analysis',
  initial_risk_assessment: 'Provide input via chat co-pilot or upload a document to generate risk evaluation.',
  likely_root_cause: 'N/A',
};

const savedComplaintId = localStorage.getItem('active_complaint_id')
  ? parseInt(localStorage.getItem('active_complaint_id'), 10)
  : null;

const complaintSlice = createSlice({
  name: 'complaint',
  initialState: {
    complaintId: savedComplaintId,
    formData: initialFormData,
    riskAssessment: initialRiskAssessment,
    status: 'Pending Triage',
    lastUpdatedFields: [],
    scannedImagePreview: null,
    detectedDefects: [],
    isScanningImage: false,
  },
  reducers: {
    setComplaintState: (state, action) => {
      const { complaint_id, form_data, risk_assessment, status, scanned_image_preview, detected_defects } = action.payload;
      if (complaint_id) {
        state.complaintId = complaint_id;
        localStorage.setItem('active_complaint_id', complaint_id.toString());
      }
      if (form_data) {
        state.formData = { ...state.formData, ...form_data };
      }
      if (risk_assessment) {
        state.riskAssessment = { ...state.riskAssessment, ...risk_assessment };
      }
      if (status) {
        state.status = status;
      }
      if (scanned_image_preview !== undefined) {
        state.scannedImagePreview = scanned_image_preview;
      }
      if (detected_defects !== undefined) {
        state.detectedDefects = detected_defects;
      }
    },
    setLastUpdatedFields: (state, action) => {
      state.lastUpdatedFields = action.payload;
    },
    setScannedImagePreview: (state, action) => {
      state.scannedImagePreview = action.payload;
    },
    setDetectedDefects: (state, action) => {
      state.detectedDefects = action.payload;
    },
    setIsScanningImage: (state, action) => {
      state.isScanningImage = action.payload;
    },
    resetForm: (state) => {
      state.complaintId = null;
      localStorage.removeItem('active_complaint_id');
      state.formData = initialFormData;
      state.riskAssessment = initialRiskAssessment;
      state.status = 'Pending Triage';
      state.lastUpdatedFields = [];
      state.scannedImagePreview = null;
      state.detectedDefects = [];
      state.isScanningImage = false;
    }
  }
});

export const { setComplaintState, setLastUpdatedFields, setScannedImagePreview, setDetectedDefects, setIsScanningImage, resetForm } = complaintSlice.actions;
export default complaintSlice.reducer;
