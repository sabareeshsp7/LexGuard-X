import { motion, AnimatePresence } from 'framer-motion';
import type { AgentEvent } from '../types';
import {
  Scale, Shield, DollarSign, AlertTriangle,
  Telescope, Handshake, Gavel, Cpu, CheckCircle2,
  Loader2, XCircle, Database
} from 'lucide-react';

interface Props {
  events: AgentEvent[];
  progress: number;
}

const agentMeta: Record<string, { icon: React.ReactNode; color: string }> = {
  'Document Parser':     { icon: <Cpu size={16} />,          color: '#06b6d4' },
  'RAG Engine':          { icon: <Database size={16} />,      color: '#8b5cf6' },
  'Contract Classifier': { icon: <Scale size={16} />,         color: '#3b82f6' },
  'Legal Risk Agent':    { icon: <Scale size={16} />,         color: '#ef4444' },
  'Privacy Agent':       { icon: <Shield size={16} />,        color: '#8b5cf6' },
  'Financial Agent':     { icon: <DollarSign size={16} />,    color: '#10b981' },
  'Ambiguity Detector':  { icon: <AlertTriangle size={16} />, color: '#f59e0b' },
  'Future Simulator':    { icon: <Telescope size={16} />,     color: '#f97316' },
  'Negotiation Advisor': { icon: <Handshake size={16} />,     color: '#06b6d4' },
  'Judge Agent':         { icon: <Gavel size={16} />,         color: '#a78bfa' },
  'System':              { icon: <CheckCircle2 size={16} />,  color: '#10b981' },
};

function StatusIcon({ status }: { status: string }) {
  if (status === 'running') {
    return <Loader2 size={14} style={{ animation: 'spin 1s linear infinite', color: 'var(--accent-blue)' }} />;
  }
  if (status === 'done') {
    return <CheckCircle2 size={14} style={{ color: 'var(--accent-green)' }} />;
  }
  if (status === 'error') {
    return <XCircle size={14} style={{ color: 'var(--critical)' }} />;
  }
  return <div style={{ width: 14, height: 14, borderRadius: '50%', background: 'var(--text-muted)' }} />;
}

export default function AgentFeed({ events, progress }: Props) {
  const safeEvents = events ?? [];

  return (
    <div className="card" style={{ padding: '1.5rem' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
        <div>
          <h3 style={{ fontWeight: 700, fontSize: '1rem', marginBottom: 2 }}>
            ⚡ AI Agent War Room
          </h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
            Live multi-agent analysis feed
          </p>
        </div>
        <div style={{
          padding: '6px 14px',
          borderRadius: 99,
          background: 'rgba(59,130,246,0.1)',
          border: '1px solid rgba(59,130,246,0.3)',
          fontSize: '0.8rem',
          fontWeight: 700,
          color: 'var(--accent-blue)',
        }}>
          {progress ?? 0}%
        </div>
      </div>

      {/* Progress bar */}
      <div style={{
        height: 4, borderRadius: 99,
        background: 'rgba(255,255,255,0.08)',
        marginBottom: '1.5rem', overflow: 'hidden',
      }}>
        <motion.div
          style={{ height: '100%', borderRadius: 99, background: 'var(--gradient-brand)' }}
          initial={{ width: 0 }}
          animate={{ width: `${progress ?? 0}%` }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
        />
      </div>

      {/* Events list */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem', maxHeight: 320, overflowY: 'auto' }}>
        <AnimatePresence>
          {safeEvents.map((evt, i) => {
            const meta = agentMeta[evt.agent_name] ?? { icon: <Cpu size={16} />, color: '#94a3b8' };
            return (
              <motion.div
                key={`${evt.agent_name}-${i}`}
                initial={{ opacity: 0, x: -16 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3 }}
                style={{
                  display: 'flex', alignItems: 'flex-start', gap: '0.75rem',
                  padding: '0.75rem',
                  borderRadius: 'var(--radius-sm)',
                  background: evt.status === 'running' ? 'rgba(59,130,246,0.06)' : 'rgba(255,255,255,0.02)',
                  border: `1px solid ${evt.status === 'running' ? 'rgba(59,130,246,0.2)' : 'transparent'}`,
                }}
              >
                {/* Agent icon */}
                <div style={{
                  width: 32, height: 32, borderRadius: '50%',
                  background: `${meta.color}20`,
                  border: `1px solid ${meta.color}40`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  flexShrink: 0,
                  color: meta.color,
                }}>
                  {meta.icon}
                </div>

                {/* Content */}
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 2 }}>
                    <span style={{ fontWeight: 600, fontSize: '0.82rem', color: meta.color }}>
                      {evt.agent_name}
                    </span>
                    <StatusIcon status={evt.status} />
                    {(evt.findings_count ?? 0) > 0 && (
                      <span style={{
                        fontSize: '0.7rem', padding: '1px 8px',
                        background: 'rgba(239,68,68,0.15)',
                        color: 'var(--critical)',
                        borderRadius: 99,
                        border: '1px solid rgba(239,68,68,0.3)',
                      }}>
                        {evt.findings_count} risks
                      </span>
                    )}
                  </div>
                  <p style={{
                    color: 'var(--text-secondary)', fontSize: '0.78rem',
                    whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
                  }}>
                    {evt.message}
                  </p>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>

        {safeEvents.length === 0 && (
          <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '2rem', fontSize: '0.85rem' }}>
            Agents deploying...
          </div>
        )}
      </div>
    </div>
  );
}
