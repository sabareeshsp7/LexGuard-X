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
  'Document Parser':     { icon: <Cpu size={15} />,          color: '#0891b2' },
  'RAG Engine':          { icon: <Database size={15} />,      color: '#7c3aed' },
  'Contract Classifier': { icon: <Scale size={15} />,         color: '#1d4ed8' },
  'Legal Risk Agent':    { icon: <Scale size={15} />,         color: '#dc2626' },
  'Privacy Agent':       { icon: <Shield size={15} />,        color: '#7c3aed' },
  'Financial Agent':     { icon: <DollarSign size={15} />,    color: '#059669' },
  'Ambiguity Detector':  { icon: <AlertTriangle size={15} />, color: '#d97706' },
  'Future Simulator':    { icon: <Telescope size={15} />,     color: '#ea580c' },
  'Negotiation Advisor': { icon: <Handshake size={15} />,     color: '#0891b2' },
  'Judge Agent':         { icon: <Gavel size={15} />,         color: '#8b5cf6' },
  'System':              { icon: <CheckCircle2 size={15} />,  color: '#059669' },
};

function StatusIcon({ status }: { status: string }) {
  if (status === 'running') return <Loader2 size={13} style={{ animation: 'spin 1s linear infinite', color: '#1d4ed8' }} />;
  if (status === 'done') return <CheckCircle2 size={13} style={{ color: '#059669' }} />;
  if (status === 'error') return <XCircle size={13} style={{ color: '#dc2626' }} />;
  return <div style={{ width: 13, height: 13, borderRadius: '50%', background: '#d1d5db' }} />;
}

export default function AgentFeed({ events, progress }: Props) {
  const safeEvents = events ?? [];

  return (
    <div style={{ padding: '1.5rem', background: 'white' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
        <div>
          <h3 style={{ fontWeight: 700, fontSize: '0.95rem', marginBottom: 2, color: '#111827' }}>
            AI Agents Running
          </h3>
          <p style={{ color: '#9ca3af', fontSize: '0.78rem' }}>Live multi-agent analysis feed</p>
        </div>
        <div style={{
          padding: '5px 14px', borderRadius: 99,
          background: '#eff6ff', border: '1px solid #bfdbfe',
          fontSize: '0.8rem', fontWeight: 700, color: '#1d4ed8',
        }}>
          {progress ?? 0}%
        </div>
      </div>

      {/* Progress bar */}
      <div style={{ height: 4, borderRadius: 99, background: '#f3f4f6', marginBottom: '1.25rem', overflow: 'hidden' }}>
        <motion.div
          style={{ height: '100%', borderRadius: 99, background: 'linear-gradient(90deg, #1d4ed8, #8b5cf6)' }}
          initial={{ width: 0 }}
          animate={{ width: `${progress ?? 0}%` }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
        />
      </div>

      {/* Events list */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: 320, overflowY: 'auto' }}>
        <AnimatePresence>
          {safeEvents.map((evt, i) => {
            const meta = agentMeta[evt.agent_name] ?? { icon: <Cpu size={15} />, color: '#9ca3af' };
            const isRunning = evt.status === 'running';
            return (
              <motion.div
                key={`${evt.agent_name}-${i}`}
                initial={{ opacity: 0, x: -12 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.25 }}
                style={{
                  display: 'flex', alignItems: 'flex-start', gap: '0.75rem',
                  padding: '0.65rem 0.75rem',
                  borderRadius: 8,
                  background: isRunning ? '#eff6ff' : '#fafafa',
                  border: `1px solid ${isRunning ? '#bfdbfe' : '#f3f4f6'}`,
                }}
              >
                <div style={{
                  width: 30, height: 30, borderRadius: '50%', flexShrink: 0,
                  background: `${meta.color}18`,
                  border: `1px solid ${meta.color}35`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  color: meta.color,
                }}>
                  {meta.icon}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 7, marginBottom: 2 }}>
                    <span style={{ fontWeight: 600, fontSize: '0.8rem', color: meta.color }}>
                      {evt.agent_name}
                    </span>
                    <StatusIcon status={evt.status} />
                    {(evt.findings_count ?? 0) > 0 && (
                      <span style={{
                        fontSize: '0.68rem', padding: '1px 7px',
                        background: '#fef2f2', color: '#dc2626',
                        borderRadius: 99, border: '1px solid #fecaca',
                      }}>
                        {evt.findings_count} risks
                      </span>
                    )}
                  </div>
                  <p style={{ color: '#6b7280', fontSize: '0.76rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {evt.message}
                  </p>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>

        {safeEvents.length === 0 && (
          <div style={{ textAlign: 'center', color: '#9ca3af', padding: '2rem', fontSize: '0.83rem' }}>
            Agents deploying...
          </div>
        )}
      </div>
    </div>
  );
}
