import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { 
  TrendingUp, 
  BrainCircuit, 
  AlertTriangle, 
  Target, 
  Layers, 
  CheckCircle2, 
  RefreshCw, 
  Zap,
  Building2,
  ChevronRight
} from 'lucide-react';
import { predictTrends } from '../../api/complaintsApi';

export const PredictiveTrendPanel = ({ onSelectComplaint, onReuseSolution }) => {
  const { formData, riskAssessment, complaintId } = useSelector((state) => state.complaint);
  
  const [vectorMatches, setVectorMatches] = useState([]);
  const [clusters, setClusters] = useState([]);
  const [anomalyAlert, setAnomalyAlert] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('matches'); // 'matches' | 'clusters'

  const loadRealVectorTrends = async () => {
    setIsLoading(true);
    try {
      const payload = {
        complaint_id: complaintId || null,
        product_name: formData?.product_name || "",
        complaint_category: formData?.complaint_category || "",
        complaint_description: formData?.complaint_description || "",
        originating_site_block: formData?.originating_site_block || ""
      };

      const res = await predictTrends(payload);
      if (res && res.status === 'success') {
        setVectorMatches(res.vector_matches || []);
        setClusters(res.clusters || []);
        setAnomalyAlert(res.anomaly_alert || null);
      }
    } catch (err) {
      console.error('Failed to fetch real vector trends from ChromaDB:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadRealVectorTrends();
  }, [complaintId, formData?.product_name, formData?.complaint_category]);

  const handleTriggerRescan = () => {
    loadRealVectorTrends();
  };

  return (
    <div className="predictive-trend-card" style={{ background: '#ffffff', borderRadius: '16px', border: '1px solid #e2e8f0', padding: '20px', marginTop: '20px', boxShadow: '0 4px 14px rgba(0, 0, 0, 0.03)' }}>
      {/* Header Row */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
        <div>
          <div style={{ fontSize: '15px', fontWeight: '700', color: '#0f172a', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <TrendingUp size={18} className="text-sky-600" />
            Predictive Quality Trends & Vector Clusters
          </div>
          <p style={{ fontSize: '11px', color: '#64748b', marginTop: '2px' }}>
            Live ChromaDB vector embeddings calculating cosine similarity & defect clusters
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button 
            type="button" 
            onClick={handleTriggerRescan}
            disabled={isLoading}
            style={{ background: '#f0f9ff', color: '#0284c7', border: '1px solid #bae6fd', padding: '5px 10px', borderRadius: '10px', fontSize: '11px', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '5px', cursor: 'pointer' }}
          >
            <RefreshCw size={12} className={isLoading ? "animate-spin" : ""} />
            {isLoading ? "Querying Vector DB..." : "Vector Rescan"}
          </button>

          <span style={{ background: '#f0fdf4', color: '#15803d', border: '1px solid #bbf7d0', padding: '4px 10px', borderRadius: '12px', fontSize: '11px', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <BrainCircuit size={13} className="text-emerald-600" />
            Live ChromaDB Engine
          </span>
        </div>
      </div>

      {/* Emerging Trend Alert Banner */}
      {anomalyAlert && (
        <div style={{ background: 'linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%)', border: '1px solid #fdba74', borderRadius: '12px', padding: '12px 14px', marginBottom: '16px', display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
          <div style={{ background: '#ea580c', color: '#ffffff', padding: '6px', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <AlertTriangle size={18} />
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <strong style={{ fontSize: '13px', color: '#9a3412' }}>
                {anomalyAlert.title}
              </strong>
              <span style={{ background: '#ffedd5', color: '#c2410c', border: '1px solid #fed7aa', padding: '2px 8px', borderRadius: '10px', fontSize: '10px', fontWeight: '700' }}>
                {anomalyAlert.confidence_score}
              </span>
            </div>
            <p style={{ fontSize: '12px', color: '#c2410c', marginTop: '3px', lineHeight: '1.4' }}>
              {anomalyAlert.message}
            </p>
          </div>
        </div>
      )}

      {/* Navigation Sub-Tabs */}
      <div style={{ display: 'flex', gap: '10px', borderBottom: '1px solid #e2e8f0', paddingBottom: '8px', marginBottom: '14px' }}>
        <button
          type="button"
          onClick={() => setActiveTab('matches')}
          style={{
            background: activeTab === 'matches' ? '#e0f2fe' : 'transparent',
            color: activeTab === 'matches' ? '#0369a1' : '#64748b',
            border: 'none',
            padding: '5px 12px',
            borderRadius: '8px',
            fontSize: '12px',
            fontWeight: '600',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}
        >
          <Target size={14} /> Vector Matches ({vectorMatches.length})
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('clusters')}
          style={{
            background: activeTab === 'clusters' ? '#e0f2fe' : 'transparent',
            color: activeTab === 'clusters' ? '#0369a1' : '#64748b',
            border: 'none',
            padding: '5px 12px',
            borderRadius: '8px',
            fontSize: '12px',
            fontWeight: '600',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}
        >
          <Layers size={14} /> Defect Clusters ({clusters.length})
        </button>
      </div>

      {/* Tab 1: Semantic Vector Matches List */}
      {activeTab === 'matches' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {isLoading ? (
            <div style={{ textAlign: 'center', padding: '20px', color: '#64748b', fontSize: '12px' }}>
              Calculating vector similarity embeddings in ChromaDB...
            </div>
          ) : vectorMatches.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '20px', color: '#64748b', fontSize: '12px' }}>
              No historical vector matches found for the current complaint query.
            </div>
          ) : (
            vectorMatches.map((match, idx) => (
              <div key={idx} style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '12px', transition: 'all 0.15s ease' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ background: '#e0f2fe', color: '#0369a1', fontSize: '11px', fontWeight: '800', padding: '2px 8px', borderRadius: '6px' }}>
                      {match.complaint_number}
                    </span>
                    <span style={{ fontSize: '13px', fontWeight: '700', color: '#0f172a' }}>
                      {match.product_name} <span style={{ fontSize: '11px', color: '#64748b', fontWeight: '500' }}>({match.batch_lot_number})</span>
                    </span>
                  </div>

                  {/* Similarity Score Pill */}
                  <div style={{ background: match.similarity_score >= 88 ? '#fee2e2' : '#dbeafe', color: match.similarity_score >= 88 ? '#991b1b' : '#1e40af', border: `1px solid ${match.similarity_score >= 88 ? '#fca5a5' : '#bfdbfe'}`, padding: '2px 10px', borderRadius: '12px', fontSize: '11px', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Zap size={11} /> {match.similarity_score}% Vector Match
                  </div>
                </div>

                <div style={{ fontSize: '12px', color: '#334155', marginBottom: '8px', lineHeight: '1.4' }}>
                  <strong>Symptom Match:</strong> "{match.symptom_summary}"
                </div>

                {/* Proven Solution Box */}
                {match.proven_solution && (
                  <div style={{ background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '8px', padding: '8px 10px', fontSize: '11px', color: '#166534', display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                    <CheckCircle2 size={14} className="text-emerald-600" style={{ flexShrink: 0, marginTop: '2px' }} />
                    <div style={{ flex: 1 }}>
                      <strong>Historical Proven Solution:</strong> {match.proven_solution}
                    </div>
                    {onReuseSolution && (
                      <button 
                        type="button"
                        onClick={() => onReuseSolution(match.proven_solution)}
                        style={{ background: '#166534', color: '#ffffff', border: 'none', padding: '3px 8px', borderRadius: '6px', fontSize: '10px', fontWeight: '600', cursor: 'pointer', whiteSpace: 'nowrap' }}
                      >
                        Reuse Solution
                      </button>
                    )}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}

      {/* Tab 2: Defect Trend Clusters */}
      {activeTab === 'clusters' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '12px' }}>
          {clusters.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '20px', color: '#64748b', fontSize: '12px', gridColumn: '1 / -1' }}>
              No active quality clusters indexed in ChromaDB yet.
            </div>
          ) : (
            clusters.map((cluster, idx) => (
              <div key={idx} style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '12px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                    <span style={{ fontSize: '11px', fontWeight: '800', color: cluster.risk_level.includes('Critical') ? '#991b1b' : '#9a3412', background: cluster.risk_level.includes('Critical') ? '#fee2e2' : '#ffedd5', padding: '2px 8px', borderRadius: '6px' }}>
                      {cluster.risk_level}
                    </span>
                    <span style={{ fontSize: '11px', color: '#64748b', fontWeight: '600' }}>
                      Avg Match: {cluster.avg_similarity}
                    </span>
                  </div>

                  <h5 style={{ fontSize: '13px', fontWeight: '700', color: '#0f172a', marginBottom: '4px' }}>
                    {cluster.cluster_name}
                  </h5>

                  <div style={{ fontSize: '11px', color: '#475569', display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '2px' }}>
                    <Building2 size={12} /> {cluster.primary_block}
                  </div>
                  <div style={{ fontSize: '11px', color: '#475569' }}>
                    <strong>Product:</strong> {cluster.top_affected_product}
                  </div>
                </div>

                <div style={{ marginTop: '10px', paddingTop: '8px', borderTop: '1px dashed #cbd5e1', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '11px' }}>
                  <span style={{ color: '#0369a1', fontWeight: '700' }}>{cluster.count} Linked Complaints</span>
                  <span style={{ color: '#0284c7', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '2px', cursor: 'pointer' }}>
                    View Cluster <ChevronRight size={12} />
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default PredictiveTrendPanel;
