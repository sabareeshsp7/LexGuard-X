import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { getAnalysis } from '../api/lexguard';
import type { AnalysisResult } from '../types';
import RiskRadar from '../components/RiskRadar';
import ClauseViewer from '../components/ClauseViewer';
import NegotiationPanel from '../components/NegotiationPanel';
import {
  Scale, ArrowLeft, FileText, Clock,
  CheckCircle, AlertTriangle, XCircle, Info
} from 'lucide-react';

const verdictMeta: Record<string, { icon: React.ReactNode; color: string; bg: string }> = {
  'SIGN':               { icon: <CheckCircle size={20} />, color: '#059669', bg: '#f0fdf4' },
  'NEGOTIATE':          { icon: <AlertTriangle size={20} />, color: '#d97706', bg: '#fffbeb' },
  'DO NOT SIGN':        { icon: <XCircle size={20} />, color: '#dc2626', bg: '#fef2f2' },
  'REVIEW WITH LAWYER': { icon: <Info size={20} />, color: '#7c3aed', bg: '#faf5ff' },
};

export default function Analysis() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState<'overview' | 'clauses' | 'scenarios' | 'agents'>('overview');

  useEffect(() => {
    if (!id) return;

    const load = async () => {
      try {
        const data = await getAnalysis(id);
        if (data.status === 'processing') {
          // Poll every 3 seconds
          setTimeout(load, 3000);
          return;
        }
        setResult(data);
        setLoading(false);
      } catch (err: any) {
        setError(err?.response?.data?.detail || 'Failed to load analysis');
        setLoading(false);
      }
    };
    load();
  }, [id]);

  if (loading) return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: '1rem' }}>
      <div className="spinner" style={{ width: 48, height: 48, borderWidth: 4 }} />
      <p style={{ color: 'var(--text-secondary)' }}>Loading analysis results...</p>
    </div>
  );

  if (error) return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: '1rem' }}>
      <XCircle size={48} color="var(--critical)" />
      <p style={{ color: 'var(--critical)', fontWeight: 600 }}>{error}</p>
      <button className="btn btn-ghost" onClick={() => navigate('/')}>
        <ArrowLeft size={16} /> Go Back
      </button>
    </div>
  );

  if (!result) return null;

  const verdict = verdictMeta[result.one_liner_verdict?.toUpperCase()] ||
    verdictMeta['REVIEW WITH LAWYER'];

  // Determine recommendation from executive summary context
  const recommendation = result.agent_results?.find(a => a.agent_name === 'Judge Agent')?.summary || 'REVIEW WITH LAWYER';
  const recMeta = verdictMeta[recommendation] || verdictMeta['REVIEW WITH LAWYER'];

  const tabs = [
    { key: 'overview', label: 'Overview' },
    { key: 'clauses', label: `Clauses (${result.findings.length})` },
    { key: 'scenarios', label: 'Scenarios' },
    { key: 'agents', label: 'Agent Report' },
  ];

  return (
    <div style={{ minHeight: '100vh' }}>

      {/* ── Navbar ─────────────────────────────────── */}
      <nav style={{
        background: 'white',
        borderBottom: '1px solid var(--border)',
        padding: '0 1.5rem',
        height: 60,
        display: 'flex', alignItems: 'center', gap: '1rem',
        position: 'sticky', top: 0, zIndex: 100,
        boxShadow: 'var(--shadow-sm)',
      }}>
        <button className="btn btn-ghost" style={{ padding: '6px 12px' }} onClick={() => navigate('/')}>
          <ArrowLeft size={16} /> Home
        </button>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Scale size={18} color="var(--navy)" />
          <span style={{ fontWeight: 800, color: 'var(--navy)', fontSize: '1rem', letterSpacing: '-0.02em' }}>LexGuard <span style={{ color: 'var(--gold)' }}>X</span></span>
        </div>
        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 8 }}>
          <FileText size={14} color="var(--text-muted)" />
          <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>{result.file_name}</span>
          <span className="badge badge-navy">{result.contract_type}</span>
        </div>
      </nav>

      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '2rem 1.5rem' }}>

        {/* ── Verdict Banner ─────────────────────────── */}
        <motion.div
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          style={{
            padding: '1.25rem 1.5rem',
            borderRadius: 'var(--radius)',
            background: `${recMeta.bg}`,
            border: `1px solid ${recMeta.color}30`,
            display: 'flex', alignItems: 'flex-start', gap: '1rem',
            marginBottom: '2rem',
          }}
        >
          <div style={{ color: recMeta.color, flexShrink: 0, marginTop: 2 }}>
            {recMeta.icon}
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
              <span style={{ fontWeight: 800, fontSize: '1rem', color: recMeta.color }}>
                AI Recommendation: {recommendation}
              </span>
            </div>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', lineHeight: 1.6 }}>
              {result.executive_summary}
            </p>
            {result.one_liner_verdict && (
              <p style={{ color: 'var(--text-primary)', fontWeight: 600, fontSize: '0.875rem', marginTop: 8, fontStyle: 'italic' }}>
                Judge's Verdict: "{result.one_liner_verdict}"
              </p>
            )}
          </div>
        </motion.div>

        {/* ── Tabs ───────────────────────────────────── */}
        <div className="tab-bar">
          {tabs.map(tab => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as 'overview' | 'clauses' | 'scenarios' | 'agents')}
              className={`tab-btn ${activeTab === tab.key ? 'active' : ''}`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* ── Tab Content ────────────────────────────── */}
        <motion.div key={activeTab} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.25 }}>

          {activeTab === 'overview' && (
            <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0,1fr) minmax(0,1fr)', gap: '1.5rem' }}>
              <div style={{ gridColumn: 'span 2' }}>
                <RiskRadar riskScore={result.risk_score} />
              </div>
              {/* Stats row */}
              {[
                { label: 'Contract Type', value: result.contract_type, color: 'var(--accent-blue)' },
                { label: 'Total Clauses Scanned', value: result.total_clauses_found, color: 'var(--accent-cyan)' },
                { label: 'Risks Found', value: result.findings.length, color: 'var(--critical)' },
                { label: 'Negotiation Strategies', value: result.negotiation_recommendations.length, color: 'var(--accent-green)' },
              ].map(stat => (
                <div key={stat.label} className="card" style={{ textAlign: 'center' }}>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.78rem', marginBottom: 6 }}>{stat.label}</p>
                  <p style={{ fontSize: '1.5rem', fontWeight: 800, color: stat.color }}>{stat.value}</p>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'clauses' && (
            <ClauseViewer findings={result.findings} />
          )}

          {activeTab === 'scenarios' && (
            <NegotiationPanel
              scenarios={result.future_scenarios}
              negotiations={result.negotiation_recommendations}
            />
          )}

          {activeTab === 'agents' && (
            <div className="card">
              <h3 style={{ fontWeight: 700, fontSize: '1rem', marginBottom: '1.25rem' }}>
                Agent Execution Report
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                {result.agent_results?.map((agent, i) => (
                  <div key={i} style={{
                    display: 'flex', alignItems: 'center', gap: '1rem',
                    padding: '0.75rem 1rem',
                    borderRadius: 'var(--radius-sm)',
                    background: 'var(--bg-primary)',
                    border: '1px solid var(--border)',
                  }}>
                    <CheckCircle size={16} color="var(--accent-green)" />
                    <div style={{ flex: 1 }}>
                      <p style={{ fontWeight: 600, fontSize: '0.875rem' }}>{agent.agent_name}</p>
                      <p style={{ color: 'var(--text-secondary)', fontSize: '0.78rem' }}>{agent.summary}</p>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 4, color: 'var(--text-muted)', fontSize: '0.75rem' }}>
                      <Clock size={12} />
                      {agent.processing_time_seconds}s
                    </div>
                    {agent.findings?.length > 0 && (
                      <span className="badge badge-high">{agent.findings.length} risks</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}
