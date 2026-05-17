import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { RiskFinding } from '../types';
import {
  ChevronDown, ChevronUp, AlertTriangle, Shield,
  DollarSign, Scale, HelpCircle, Briefcase, FileWarning, Info
} from 'lucide-react';

interface Props { findings: RiskFinding[] }

const categoryIcons: Record<string, React.ReactNode> = {
  NON_COMPETE:     <Briefcase size={15} />,
  IP_TRANSFER:     <FileWarning size={15} />,
  TERMINATION:     <AlertTriangle size={15} />,
  ARBITRATION:     <Scale size={15} />,
  PRIVACY:         <Shield size={15} />,
  FINANCIAL:       <DollarSign size={15} />,
  LIABILITY:       <AlertTriangle size={15} />,
  DATA_COLLECTION: <Shield size={15} />,
  AMBIGUITY:       <HelpCircle size={15} />,
  OTHER:           <Info size={15} />,
};

const categoryLabels: Record<string, string> = {
  NON_COMPETE: 'Non-Compete',
  IP_TRANSFER: 'IP Transfer',
  TERMINATION: 'Termination',
  ARBITRATION: 'Arbitration',
  PRIVACY: 'Privacy',
  FINANCIAL: 'Financial',
  LIABILITY: 'Liability',
  DATA_COLLECTION: 'Data Collection',
  AMBIGUITY: 'Ambiguity',
  OTHER: 'Other',
};

function FindingCard({ finding, index }: { finding: RiskFinding; index: number }) {
  const [expanded, setExpanded] = useState(index === 0);

  const severityColor = {
    CRITICAL: 'var(--critical)',
    HIGH: 'var(--high)',
    MEDIUM: 'var(--medium)',
    LOW: 'var(--low)',
  }[finding.severity] || 'var(--text-muted)';

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.06 }}
      style={{
        border: `1px solid ${severityColor}30`,
        borderLeft: `3px solid ${severityColor}`,
        borderRadius: 'var(--radius-sm)',
        background: 'rgba(255,255,255,0.02)',
        overflow: 'hidden',
      }}
    >
      {/* Header */}
      <button
        onClick={() => setExpanded(!expanded)}
        style={{
          width: '100%', display: 'flex', alignItems: 'center',
          gap: '0.75rem', padding: '0.9rem 1rem',
          background: 'transparent', border: 'none', cursor: 'pointer',
          color: 'var(--text-primary)', textAlign: 'left',
        }}
      >
        {/* Severity badge */}
        <span className={`badge badge-${finding.severity.toLowerCase()}`}>
          {finding.severity}
        </span>

        {/* Category */}
        <span style={{
          display: 'flex', alignItems: 'center', gap: 4,
          color: 'var(--text-secondary)', fontSize: '0.78rem',
        }}>
          {categoryIcons[finding.category]}
          {categoryLabels[finding.category] || finding.category}
        </span>

        {/* Score */}
        <span style={{
          marginLeft: 'auto', fontSize: '0.75rem',
          color: severityColor, fontWeight: 700,
        }}>
          Impact: {finding.user_impact_score}/10
        </span>

        {/* Toggle */}
        <span style={{ color: 'var(--text-muted)', flexShrink: 0 }}>
          {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </span>
      </button>

      {/* Plain explanation (always visible) */}
      <div style={{ padding: '0 1rem 0.9rem', marginTop: -4 }}>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', lineHeight: 1.6 }}>
          {finding.plain_explanation}
        </p>
      </div>

      {/* Expanded details */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            style={{ overflow: 'hidden' }}
          >
            <div style={{ padding: '0 1rem 1rem', display: 'flex', flexDirection: 'column', gap: '1rem', borderTop: '1px solid var(--border)' }}>

              {/* Problematic language */}
              {finding.problematic_language && (
                <div style={{ marginTop: '1rem' }}>
                  <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: 6, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                    ⚠ Problematic Language
                  </p>
                  <blockquote style={{
                    background: 'rgba(239,68,68,0.06)',
                    border: '1px solid rgba(239,68,68,0.2)',
                    borderLeft: '3px solid var(--critical)',
                    padding: '0.75rem 1rem',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.82rem',
                    color: 'var(--text-secondary)',
                    fontStyle: 'italic', lineHeight: 1.6,
                  }}>
                    "{finding.problematic_language}"
                  </blockquote>
                </div>
              )}

              {/* Industry standard */}
              {finding.industry_standard && (
                <div>
                  <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: 6, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                    ✓ Industry Standard
                  </p>
                  <p style={{ fontSize: '0.82rem', color: 'var(--accent-green)', lineHeight: 1.6 }}>
                    {finding.industry_standard}
                  </p>
                </div>
              )}

              {/* User rights impacted */}
              {finding.user_rights_impacted?.length > 0 && (
                <div>
                  <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: 6, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                    Rights Impacted
                  </p>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                    {(finding.user_rights_impacted || []).map((right, i) => (
                      <span key={i} style={{
                        padding: '3px 10px', borderRadius: 99,
                        background: 'rgba(139,92,246,0.1)',
                        border: '1px solid rgba(139,92,246,0.3)',
                        fontSize: '0.72rem', color: 'var(--accent-purple)',
                      }}>
                        {right}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export default function ClauseViewer({ findings }: Props) {
  const [filter, setFilter] = useState<string>('ALL');

  const severityCounts = (findings || []).reduce((acc, f) => {
    acc[f.severity] = (acc[f.severity] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const filtered = filter === 'ALL'
    ? (findings || [])
    : (findings || []).filter(f => f.severity === filter);

  return (
    <div className="card">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div>
          <h3 style={{ fontWeight: 700, fontSize: '1rem', marginBottom: 2 }}>
            Clause Risk Report
          </h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
            {(findings || []).length} risky clauses detected
          </p>
        </div>

        {/* Filter tabs */}
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
          {(['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'] as const).map(sev => (
            <button
              key={sev}
              onClick={() => setFilter(sev)}
              className={`badge ${sev !== 'ALL' ? `badge-${sev.toLowerCase()}` : ''}`}
              style={{
                cursor: 'pointer', border: 'none',
                background: filter === sev
                  ? (sev === 'ALL' ? 'rgba(255,255,255,0.1)' : undefined)
                  : 'rgba(255,255,255,0.04)',
                opacity: filter === sev ? 1 : 0.6,
                transition: 'all 0.15s ease',
              }}
            >
              {sev} {sev !== 'ALL' && severityCounts[sev] ? `(${severityCounts[sev]})` : ''}
            </button>
          ))}
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
        {filtered.length === 0
          ? <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem', fontSize: '0.85rem' }}>
              No findings at this severity level
            </p>
          : filtered.map((f, i) => <FindingCard key={f.clause_id} finding={f} index={i} />)
        }
      </div>
    </div>
  );
}
