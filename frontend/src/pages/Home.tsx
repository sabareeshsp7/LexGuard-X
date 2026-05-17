import { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { uploadContract, createWebSocket } from '../api/lexguard';
import type { AgentEvent } from '../types';
import UploadZone from '../components/UploadZone';
import AgentFeed from '../components/AgentFeed';
import {
  Shield, Scale, Zap, Brain,
  FileText, CheckCircle, AlertTriangle, Lock
} from 'lucide-react';

export default function Home() {
  const navigate = useNavigate();
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState('');
  const wsRef = useRef<WebSocket | null>(null);

  const handleUpload = async (file: File) => {
    setUploading(true);
    setError('');
    setEvents([]);
    setProgress(0);

    try {
      const { analysis_id } = await uploadContract(file);
      setUploading(false);
      setAnalyzing(true);

      wsRef.current = createWebSocket(
        analysis_id,
        (evt: AgentEvent) => {
          setEvents(prev => {
            const idx = prev.findIndex(e => e.agent_name === evt.agent_name);
            if (idx >= 0) {
              const updated = [...prev];
              updated[idx] = evt;
              return updated;
            }
            return [...prev, evt];
          });
          setProgress(evt.progress);
        },
        (id: string) => navigate(`/analysis/${id}`),
        (msg: string) => { setError(msg); setAnalyzing(false); }
      );
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Upload failed';
      setError((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? msg);
      setUploading(false);
      setAnalyzing(false);
    }
  };

  const features = [
    { icon: <Scale size={22} />, label: '8 Specialized AI Agents', desc: 'Each clause reviewed by purpose-built legal AI agents' },
    { icon: <Shield size={22} />, label: 'Privacy & GDPR Scanner', desc: 'Detect hidden data collection and consent traps' },
    { icon: <Brain size={22} />, label: 'Future Consequence AI', desc: 'Simulate best, realistic & worst-case scenarios' },
    { icon: <Zap size={22} />, label: 'Negotiation Advisor', desc: 'AI drafts counter-clauses you can send directly' },
  ];

  const contractTypes = ['Employment', 'Rental', 'Privacy Policy', 'SaaS Terms', 'Insurance', 'Freelance', 'Vendor', 'NDA'];

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>

      {/* ── Navbar ─────────────────────────────────── */}
      <nav style={{
        background: 'white',
        borderBottom: '1px solid var(--border)',
        padding: '0 2rem',
        height: 64,
        display: 'flex', alignItems: 'center', gap: '1rem',
        position: 'sticky', top: 0, zIndex: 100,
        boxShadow: 'var(--shadow-sm)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 36, height: 36, borderRadius: 10,
            background: 'var(--navy)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 2px 8px rgba(26,46,74,0.3)',
          }}>
            <Scale size={18} color="#c9933a" />
          </div>
          <div>
            <span style={{ fontWeight: 800, fontSize: '1.1rem', color: 'var(--navy)', letterSpacing: '-0.02em' }}>
              LexGuard
            </span>
            <span style={{ fontWeight: 700, fontSize: '1.1rem', color: 'var(--gold)' }}> X</span>
          </div>
        </div>

        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 6 }}>
            <Lock size={12} /> End-to-end secure
          </span>
          <span style={{
            padding: '5px 14px',
            borderRadius: 99,
            background: 'var(--gold-pale)',
            border: '1px solid #e8d5b0',
            fontSize: '0.75rem', fontWeight: 600, color: 'var(--gold)',
          }}>
            Powered by Gemini AI
          </span>
        </div>
      </nav>

      {/* ── Hero ───────────────────────────────────── */}
      <section style={{
        background: 'linear-gradient(160deg, #1a2e4a 0%, #243d60 60%, #1e3558 100%)',
        padding: '5rem 2rem 4rem',
        position: 'relative', overflow: 'hidden',
      }}>
        {/* Decorative background elements */}
        <div style={{
          position: 'absolute', top: -60, right: -60,
          width: 400, height: 400, borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(201,147,58,0.12) 0%, transparent 70%)',
          pointerEvents: 'none',
        }} />
        <div style={{
          position: 'absolute', bottom: -80, left: -80,
          width: 500, height: 500, borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(37,99,235,0.15) 0%, transparent 70%)',
          pointerEvents: 'none',
        }} />

        <div style={{ maxWidth: 780, margin: '0 auto', textAlign: 'center', position: 'relative' }}>
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            {/* Category badge */}
            <div style={{
              display: 'inline-flex', alignItems: 'center', gap: 8,
              padding: '6px 18px', borderRadius: 99,
              background: 'rgba(201,147,58,0.15)',
              border: '1px solid rgba(201,147,58,0.35)',
              marginBottom: '1.75rem',
              fontSize: '0.75rem', fontWeight: 700,
              color: '#e8b86d', letterSpacing: '0.08em',
            }}>
              <Zap size={12} fill="currentColor" />
              AI CONTRACT INTELLIGENCE PLATFORM
            </div>

            <h1 style={{
              fontSize: 'clamp(2.2rem, 5vw, 3.8rem)',
              fontWeight: 800,
              lineHeight: 1.15,
              color: 'white',
              letterSpacing: '-0.03em',
              marginBottom: '1.5rem',
            }}>
              Before you sign,{' '}
              <span style={{
                background: 'linear-gradient(135deg, #c9933a 0%, #e8b86d 50%, #f0c96e 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
              }}>
                AI defends your rights.
              </span>
            </h1>

            <p style={{
              color: 'rgba(255,255,255,0.65)',
              fontSize: '1.1rem',
              lineHeight: 1.75,
              maxWidth: 580, margin: '0 auto 2.5rem',
            }}>
              Upload any legal document. 8 specialized AI agents will scan every clause,
              expose hidden risks, and negotiate better terms — in under 60 seconds.
            </p>

            {/* Contract type pills */}
            <div style={{ display: 'flex', gap: 8, justifyContent: 'center', flexWrap: 'wrap', marginBottom: '3rem' }}>
              {contractTypes.map(t => (
                <span key={t} style={{
                  padding: '5px 14px', borderRadius: 99,
                  background: 'rgba(255,255,255,0.08)',
                  border: '1px solid rgba(255,255,255,0.15)',
                  fontSize: '0.75rem', color: 'rgba(255,255,255,0.7)',
                  display: 'flex', alignItems: 'center', gap: 4,
                }}>
                  <FileText size={10} />
                  {t}
                </span>
              ))}
            </div>
          </motion.div>

          {/* ── Upload / Analysis Box ─────────────── */}
          <AnimatePresence mode="wait">
            {!analyzing ? (
              <motion.div
                key="upload"
                initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                style={{
                  background: 'white',
                  borderRadius: 'var(--radius-xl)',
                  padding: '2rem',
                  boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
                  textAlign: 'left',
                  border: '1px solid rgba(255,255,255,0.15)',
                }}
              >
                <p className="section-label" style={{ marginBottom: '1rem' }}>
                  Upload your contract
                </p>
                <UploadZone onUpload={handleUpload} isUploading={uploading} />
                {error && (
                  <motion.div
                    initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                    style={{
                      marginTop: 12, padding: '10px 14px',
                      background: '#fef2f2',
                      border: '1px solid #fecaca',
                      borderRadius: 'var(--radius-sm)',
                      color: 'var(--critical)', fontSize: '0.85rem',
                      display: 'flex', alignItems: 'center', gap: 8,
                    }}
                  >
                    <AlertTriangle size={14} /> {error}
                  </motion.div>
                )}
              </motion.div>
            ) : (
              <motion.div
                key="analyzing"
                initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                style={{
                  background: 'white',
                  borderRadius: 'var(--radius-xl)',
                  overflow: 'hidden',
                  boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
                }}
              >
                <AgentFeed events={events} progress={progress} />
                {error && (
                  <div style={{ padding: '0 1.5rem 1.5rem', color: 'var(--critical)', fontSize: '0.85rem' }}>
                    {error}
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </section>

      {/* ── Trust Bar ──────────────────────────────── */}
      <div style={{
        background: 'var(--gold-pale)',
        borderBottom: '1px solid #e8d5b0',
        padding: '0.875rem 2rem',
        display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '2rem',
        flexWrap: 'wrap',
      }}>
        {[
          { icon: <Lock size={13} />, label: 'Documents never stored' },
          { icon: <Shield size={13} />, label: 'GDPR compliant analysis' },
          { icon: <CheckCircle size={13} />, label: 'Azure + GCP powered' },
          { icon: <Zap size={13} />, label: 'Results in under 60s' },
        ].map(item => (
          <span key={item.label} style={{
            display: 'flex', alignItems: 'center', gap: 6,
            fontSize: '0.78rem', color: '#7a5c2e', fontWeight: 600,
          }}>
            <span style={{ color: 'var(--gold)' }}>{item.icon}</span>
            {item.label}
          </span>
        ))}
      </div>

      {/* ── Features Section ───────────────────────── */}
      <section style={{ padding: '5rem 2rem', maxWidth: 1100, margin: '0 auto', width: '100%' }}>
        <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
          <p className="section-label" style={{ marginBottom: '0.75rem' }}>How It Works</p>
          <h2 style={{
            fontSize: 'clamp(1.6rem, 3vw, 2.4rem)',
            fontWeight: 800,
            color: 'var(--navy)',
            letterSpacing: '-0.02em',
          }}>
            A full legal team, available instantly
          </h2>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.75rem', maxWidth: 500, margin: '0.75rem auto 0' }}>
            Our multi-agent AI system gives you the expertise of lawyers, analysts, and negotiators — at no hourly rate.
          </p>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
          gap: '1.25rem',
        }}>
          {features.map((f, i) => (
            <motion.div
              key={i}
              className="card"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              whileHover={{ y: -4, boxShadow: 'var(--shadow-lg)' }}
              style={{ cursor: 'default' }}
            >
              <div style={{
                width: 48, height: 48, borderRadius: 12,
                background: 'var(--navy-pale)',
                border: '1px solid #c8d5e8',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                color: 'var(--navy)',
                marginBottom: '1rem',
              }}>
                {f.icon}
              </div>
              <h3 style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--navy)', marginBottom: 6 }}>
                {f.label}
              </h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', lineHeight: 1.65 }}>
                {f.desc}
              </p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ── Agent Roster ───────────────────────────── */}
      <section style={{
        background: 'var(--navy)',
        padding: '4rem 2rem',
      }}>
        <div style={{ maxWidth: 1100, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
            <p className="section-label" style={{ color: '#e8b86d', marginBottom: '0.75rem' }}>
              The AI Legal Team
            </p>
            <h2 style={{ fontSize: '2rem', fontWeight: 800, color: 'white', letterSpacing: '-0.02em' }}>
              8 agents working in parallel
            </h2>
          </div>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '1rem',
          }}>
            {[
              { name: 'Contract Classifier', role: 'Identifies contract type & jurisdiction' },
              { name: 'Legal Risk Analyst', role: 'Flags exploitative clauses' },
              { name: 'Privacy Agent', role: 'GDPR & data collection scanner' },
              { name: 'Financial Agent', role: 'Fee, penalty & renewal scanner' },
              { name: 'Ambiguity Detector', role: 'Finds vague language traps' },
              { name: 'Future Simulator', role: '3-scenario consequence modeling' },
              { name: 'Negotiation Advisor', role: 'AI-drafted counter-clauses' },
              { name: 'Judge Agent', role: 'Final verdict & executive summary' },
            ].map((agent, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 12 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.07 }}
                style={{
                  padding: '1rem 1.25rem',
                  borderRadius: 'var(--radius)',
                  background: 'rgba(255,255,255,0.06)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  backdropFilter: 'blur(4px)',
                }}
              >
                <div style={{
                  width: 8, height: 8, borderRadius: '50%',
                  background: 'var(--gold-light)', marginBottom: 8,
                  boxShadow: '0 0 8px rgba(201,147,58,0.5)',
                }} />
                <p style={{ fontWeight: 700, fontSize: '0.85rem', color: 'white', marginBottom: 4 }}>
                  {agent.name}
                </p>
                <p style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.5)', lineHeight: 1.5 }}>
                  {agent.role}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Footer ─────────────────────────────────── */}
      <footer style={{
        background: 'white',
        borderTop: '1px solid var(--border)',
        padding: '1.5rem 2rem',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        flexWrap: 'wrap', gap: '0.75rem',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Scale size={16} color="var(--navy)" />
          <span style={{ fontWeight: 700, color: 'var(--navy)', fontSize: '0.9rem' }}>LexGuard X</span>
        </div>
        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          AI analysis does not constitute legal advice. Consult a qualified attorney for legal decisions.
        </p>
      </footer>
    </div>
  );
}
