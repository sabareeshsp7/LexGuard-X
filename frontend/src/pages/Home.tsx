import { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { uploadContract, createWebSocket } from '../api/lexguard';
import type { AgentEvent } from '../types';
import UploadZone from '../components/UploadZone';
import AgentFeed from '../components/AgentFeed';
import { Scale, Shield, Zap, Brain, FileText, CheckCircle, AlertTriangle, Lock, Star } from 'lucide-react';

const scrollTo = (id: string) => document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });

export default function Home() {
  const navigate = useNavigate();
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState('');
  const wsRef = useRef<WebSocket | null>(null);

  const handleUpload = async (file: File) => {
    setUploading(true); setError(''); setEvents([]); setProgress(0);
    try {
      const { analysis_id } = await uploadContract(file);
      setUploading(false); setAnalyzing(true);
      wsRef.current = createWebSocket(
        analysis_id,
        (evt: AgentEvent) => {
          setEvents(prev => {
            const idx = prev.findIndex(e => e.agent_name === evt.agent_name);
            if (idx >= 0) { const u = [...prev]; u[idx] = evt; return u; }
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
      setUploading(false); setAnalyzing(false);
    }
  };

  const features = [
    { icon: <Scale size={20} />, label: 'Clause Extraction & Classification', desc: '8 specialized AI agents extract and classify every clause by risk type and severity.' },
    { icon: <Shield size={20} />, label: 'Privacy & Compliance Audit', desc: 'GDPR/CCPA compliance check and hidden data collection clause detection.' },
    { icon: <Brain size={20} />, label: 'Scenario Consequence Simulation', desc: 'Simulate best-case, realistic, and worst-case outcomes for each risk finding.' },
    { icon: <Zap size={20} />, label: 'Negotiation Recommendations', desc: 'AI drafts counter-clauses and redlines ready to send back to the other party.' },
    { icon: <FileText size={20} />, label: 'Multi-Format Document Support', desc: 'PDF, DOCX, scanned images — Cloud Vision OCR handles any format.' },
    { icon: <CheckCircle size={20} />, label: 'Risk Score & Plain Explanations', desc: 'Weighted 0–100 risk score with plain-English explanations for non-lawyers.' },
  ];

  const agents = [
    { num: '01', name: 'Contract Classifier', role: 'Identifies contract type & jurisdiction' },
    { num: '02', name: 'Legal Risk Analyst', role: 'Flags exploitative and harmful clauses' },
    { num: '03', name: 'Privacy Agent', role: 'GDPR & data collection scanner' },
    { num: '04', name: 'Financial Agent', role: 'Fee, penalty & auto-renewal traps' },
    { num: '05', name: 'Ambiguity Detector', role: 'Vague and contradictory language' },
    { num: '06', name: 'Future Simulator', role: '3-scenario consequence modeling' },
    { num: '07', name: 'Negotiation Advisor', role: 'AI-drafted counter-clauses' },
    { num: '08', name: 'Judge Agent', role: 'Final verdict & executive summary' },
  ];

  const navLinks = [
    { label: 'Analyze', action: () => scrollTo('analyze') },
    { label: 'Features', action: () => scrollTo('features') },
    { label: 'How It Works', action: () => scrollTo('how') },
    { label: 'AI Agents', action: () => scrollTo('agents') },
    { label: 'About', action: () => scrollTo('about') },
  ];

  return (
    <div style={{ minHeight: '100vh', background: '#fff', display: 'flex', flexDirection: 'column', fontFamily: 'Inter, system-ui, sans-serif' }}>

      {/* ── Navbar ── */}
      <nav style={{ background: '#fff', borderBottom: '1px solid #e5e7eb', padding: '0 2rem', height: 60, display: 'flex', alignItems: 'center', gap: '2rem', position: 'sticky', top: 0, zIndex: 100 }}>
        {/* Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0 }}>
          <div style={{ width: 32, height: 32, borderRadius: 8, background: 'linear-gradient(135deg,#1e3a8a,#1d4ed8)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Scale size={17} color="#fff" />
          </div>
          <span style={{ fontWeight: 800, fontSize: '1.1rem', color: '#1a2e4a', letterSpacing: '-0.02em' }}>Lexi</span>
          <span style={{ fontWeight: 800, fontSize: '1.1rem', color: '#1d4ed8', letterSpacing: '-0.02em', marginLeft: -6 }}>Ware</span>
          <span style={{ fontSize: '0.62rem', color: '#9ca3af', marginLeft: 4, fontWeight: 500 }}>AI Contract Intelligence</span>
        </div>

        {/* Nav links */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 2, marginLeft: 'auto' }}>
          {navLinks.map(l => (
            <button key={l.label} onClick={l.action} style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '0.83rem', fontWeight: 500, color: '#374151', padding: '6px 12px', borderRadius: 6, transition: 'background 0.15s', fontFamily: 'inherit' }}
              onMouseEnter={e => (e.currentTarget.style.background = '#f3f4f6')}
              onMouseLeave={e => (e.currentTarget.style.background = 'none')}
            >{l.label}</button>
          ))}
        </div>

        {/* CTA */}
        <button onClick={() => scrollTo('analyze')} style={{ background: 'linear-gradient(135deg,#1e3a8a,#1d4ed8)', color: '#fff', border: 'none', borderRadius: 8, padding: '8px 20px', fontSize: '0.83rem', fontWeight: 700, cursor: 'pointer', flexShrink: 0, fontFamily: 'inherit' }}>
          Analyze a Contract
        </button>
      </nav>

      {/* ── Sub-nav ── */}
      <div style={{ background: '#fff', borderBottom: '1px solid #e5e7eb', padding: '0 2rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 4, height: 38 }}>
        {['Employment Contracts', 'NDA', 'Rental Agreements', 'SaaS Terms', 'Insurance Policies', 'Privacy Policies', 'Vendor Agreements', 'Freelance Contracts'].map(item => (
          <button key={item} onClick={() => scrollTo('analyze')} style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '0.77rem', color: '#1d4ed8', fontWeight: 500, padding: '3px 10px', borderRadius: 4, fontFamily: 'inherit', transition: 'background 0.15s' }}
            onMouseEnter={e => (e.currentTarget.style.background = '#eff6ff')}
            onMouseLeave={e => (e.currentTarget.style.background = 'none')}
          >{item}</button>
        ))}
      </div>

      {/* ── Hero ── */}
      <section id="analyze" style={{ padding: '4.5rem 2rem 3rem', textAlign: 'center', background: '#fff' }}>
        <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.55 }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: 6, background: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: 99, padding: '4px 14px', marginBottom: '1.25rem' }}>
            <Zap size={11} color="#1d4ed8" fill="#1d4ed8" />
            <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#1d4ed8', letterSpacing: '0.08em' }}>POWERED BY GOOGLE VERTEX AI GEMINI</span>
          </div>

          <h1 style={{ fontSize: 'clamp(2.2rem,5.5vw,3.8rem)', fontWeight: 800, lineHeight: 1.15, letterSpacing: '-0.03em', marginBottom: '1rem', color: '#1a2e4a' }}>
            AI-Powered{' '}
            <span style={{ background: 'linear-gradient(135deg,#1d4ed8 0%,#8b5cf6 50%,#ec4899 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
              Contract Analysis
            </span>
          </h1>

          <p style={{ fontSize: '1.05rem', color: '#4b5563', maxWidth: 540, margin: '0 auto 2.5rem', lineHeight: 1.75 }}>
            Upload any legal document. 8 specialized AI agents will analyze every clause, expose hidden risks, and generate negotiation strategies — in under 60 seconds.
          </p>

          {/* Upload Card */}
          <div style={{ maxWidth: 660, margin: '0 auto' }}>
            <AnimatePresence mode="wait">
              {!analyzing ? (
                <motion.div key="upload" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} style={{ background: '#fff', border: '1.5px solid #e5e7eb', borderRadius: 14, boxShadow: '0 8px 40px rgba(0,0,0,0.07)', overflow: 'hidden', textAlign: 'left' }}>
                  <div style={{ padding: '1.5rem' }}>
                    <div style={{ display: 'inline-flex', alignItems: 'center', gap: 6, background: '#f9fafb', border: '1px solid #e5e7eb', borderRadius: 99, padding: '5px 14px', fontSize: '0.79rem', fontWeight: 600, color: '#374151', marginBottom: '1rem' }}>
                      <FileText size={12} color="#6b7280" /> Add Contract File
                    </div>
                    <UploadZone onUpload={handleUpload} isUploading={uploading} />
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.9rem 1.5rem', borderTop: '1px solid #f3f4f6' }}>
                    <span style={{ fontSize: '0.73rem', color: '#9ca3af' }}>LexiWare does not store your documents after analysis.</span>
                    <button onClick={() => scrollTo('analyze')} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: 34, height: 34, borderRadius: '50%', background: 'linear-gradient(135deg,#1e3a8a,#1d4ed8)', border: 'none', cursor: 'pointer' }}>
                      <Scale size={15} color="#fff" />
                    </button>
                  </div>
                  {error && (
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ margin: '0 1.5rem 1rem', padding: '9px 13px', background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 8, color: '#dc2626', fontSize: '0.82rem', display: 'flex', alignItems: 'center', gap: 7 }}>
                      <AlertTriangle size={13} /> {error}
                    </motion.div>
                  )}
                </motion.div>
              ) : (
                <motion.div key="analyzing" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} style={{ background: '#fff', borderRadius: 14, overflow: 'hidden', border: '1.5px solid #e5e7eb', boxShadow: '0 8px 40px rgba(0,0,0,0.07)' }}>
                  <AgentFeed events={events} progress={progress} />
                  {error && <div style={{ padding: '0 1.5rem 1.5rem', color: '#dc2626', fontSize: '0.84rem' }}>{error}</div>}
                </motion.div>
              )}
            </AnimatePresence>

            {!analyzing && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }} style={{ display: 'flex', gap: 10, justifyContent: 'center', marginTop: '1.25rem', flexWrap: 'wrap' }}>
                <button onClick={() => scrollTo('analyze')} style={{ background: 'linear-gradient(135deg,#1e3a8a,#1d4ed8)', color: '#fff', border: 'none', borderRadius: 8, padding: '11px 26px', fontSize: '0.9rem', fontWeight: 700, cursor: 'pointer', boxShadow: '0 4px 14px rgba(29,78,216,0.3)', fontFamily: 'inherit' }}>
                  Start Free Analysis
                </button>
                <button onClick={() => scrollTo('how')} style={{ background: '#fff', color: '#1a2e4a', border: '1.5px solid #d1d5db', borderRadius: 8, padding: '11px 26px', fontSize: '0.9rem', fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit' }}>
                  How It Works
                </button>
              </motion.div>
            )}
          </div>
        </motion.div>
      </section>

      {/* ── Trust Bar ── */}
      <div style={{ background: '#f9fafb', borderTop: '1px solid #e5e7eb', borderBottom: '1px solid #e5e7eb', padding: '0.8rem 2rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '2.5rem', flexWrap: 'wrap' }}>
        {[
          { icon: <Lock size={12} />, label: 'Documents never stored' },
          { icon: <Shield size={12} />, label: 'GDPR compliant analysis' },
          { icon: <Star size={12} />, label: 'Google Gemini AI powered' },
          { icon: <Zap size={12} />, label: 'Results in under 60 seconds' },
          { icon: <CheckCircle size={12} />, label: '8 specialized AI agents' },
        ].map(item => (
          <span key={item.label} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.77rem', color: '#6b7280', fontWeight: 500 }}>
            <span style={{ color: '#1d4ed8' }}>{item.icon}</span>{item.label}
          </span>
        ))}
      </div>

      {/* ── How It Works ── */}
      <section id="how" style={{ padding: '4.5rem 2rem', background: '#fff', maxWidth: 900, margin: '0 auto', width: '100%' }}>
        <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
          <p style={{ fontSize: '0.7rem', fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', color: '#1d4ed8', marginBottom: '0.6rem' }}>How It Works</p>
          <h2 style={{ fontSize: 'clamp(1.5rem,3vw,2.2rem)', fontWeight: 800, color: '#1a2e4a', letterSpacing: '-0.02em' }}>From upload to insights in 4 steps</h2>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(190px,1fr))', gap: '1.5rem' }}>
          {[
            { step: '1', title: 'Upload Document', desc: 'Upload PDF, DOCX, or scanned image contracts up to 20 MB.' },
            { step: '2', title: 'AI Extraction', desc: 'Cloud Vision OCR and NLP extract every clause with semantic understanding.' },
            { step: '3', title: 'Multi-Agent Analysis', desc: '8 specialized agents analyze risks, privacy, finances, and ambiguity in parallel.' },
            { step: '4', title: 'Actionable Report', desc: 'Get a plain-English risk report with negotiation advice and a final verdict.' },
          ].map((s, i) => (
            <motion.div key={i} initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.1 }} style={{ textAlign: 'center', padding: '1.5rem 1rem' }}>
              <div style={{ width: 48, height: 48, borderRadius: '50%', background: '#eff6ff', border: '2px solid #bfdbfe', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1rem', fontSize: '1.1rem', fontWeight: 800, color: '#1d4ed8' }}>{s.step}</div>
              <h3 style={{ fontWeight: 700, fontSize: '0.92rem', color: '#1a2e4a', marginBottom: 6 }}>{s.title}</h3>
              <p style={{ color: '#6b7280', fontSize: '0.82rem', lineHeight: 1.6 }}>{s.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ── Features ── */}
      <section id="features" style={{ padding: '4.5rem 2rem', background: '#f9fafb', borderTop: '1px solid #e5e7eb', borderBottom: '1px solid #e5e7eb' }}>
        <div style={{ maxWidth: 1100, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
            <p style={{ fontSize: '0.7rem', fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', color: '#1d4ed8', marginBottom: '0.6rem' }}>Features</p>
            <h2 style={{ fontSize: 'clamp(1.5rem,3vw,2.2rem)', fontWeight: 800, color: '#1a2e4a', letterSpacing: '-0.02em' }}>A full legal intelligence system</h2>
            <p style={{ color: '#6b7280', marginTop: '0.6rem', fontSize: '0.9rem' }}>Powered by Google Vertex AI Gemini — no legal background required.</p>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(300px,1fr))', gap: '1.1rem' }}>
            {features.map((f, i) => (
              <motion.div key={i} initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.07 }}
                style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 10, padding: '1.25rem', display: 'flex', gap: '1rem', alignItems: 'flex-start', boxShadow: '0 1px 4px rgba(0,0,0,0.04)', cursor: 'default' }}
              >
                <div style={{ width: 42, height: 42, borderRadius: 10, background: '#eff6ff', border: '1px solid #bfdbfe', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#1d4ed8', flexShrink: 0 }}>{f.icon}</div>
                <div>
                  <h3 style={{ fontWeight: 700, fontSize: '0.88rem', color: '#1a2e4a', marginBottom: 4 }}>{f.label}</h3>
                  <p style={{ color: '#6b7280', fontSize: '0.81rem', lineHeight: 1.6 }}>{f.desc}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Agents ── */}
      <section id="agents" style={{ padding: '4.5rem 2rem', background: '#fff' }}>
        <div style={{ maxWidth: 1100, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
            <p style={{ fontSize: '0.7rem', fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', color: '#1d4ed8', marginBottom: '0.6rem' }}>AI Agents</p>
            <h2 style={{ fontSize: 'clamp(1.5rem,3vw,2.2rem)', fontWeight: 800, color: '#1a2e4a', letterSpacing: '-0.02em' }}>8 specialist agents — one pipeline</h2>
            <p style={{ color: '#6b7280', marginTop: '0.6rem', fontSize: '0.9rem' }}>Each agent is a domain expert with a focused legal responsibility.</p>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(220px,1fr))', gap: '1rem' }}>
            {agents.map((a, i) => (
              <motion.div key={i} initial={{ opacity: 0, y: 12 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.06 }}
                style={{ padding: '1.1rem 1.25rem', borderRadius: 10, background: '#fafafa', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.04)' }}
              >
                <span style={{ fontSize: '0.62rem', fontWeight: 800, color: '#1d4ed8', letterSpacing: '0.1em' }}>{a.num}</span>
                <p style={{ fontWeight: 700, fontSize: '0.87rem', color: '#1a2e4a', marginTop: 4, marginBottom: 3 }}>{a.name}</p>
                <p style={{ fontSize: '0.75rem', color: '#9ca3af', lineHeight: 1.5 }}>{a.role}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── About ── */}
      <section id="about" style={{ padding: '4.5rem 2rem', background: '#f9fafb', borderTop: '1px solid #e5e7eb' }}>
        <div style={{ maxWidth: 760, margin: '0 auto', textAlign: 'center' }}>
          <p style={{ fontSize: '0.7rem', fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', color: '#1d4ed8', marginBottom: '0.6rem' }}>About LexiWare</p>
          <h2 style={{ fontSize: 'clamp(1.5rem,3vw,2.2rem)', fontWeight: 800, color: '#1a2e4a', letterSpacing: '-0.02em', marginBottom: '1.25rem' }}>
            Know your rights{' '}
            <span style={{ background: 'linear-gradient(135deg,#1d4ed8,#8b5cf6,#ec4899)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>before you sign.</span>
          </h2>
          <p style={{ color: '#4b5563', lineHeight: 1.8, fontSize: '0.95rem', marginBottom: '1rem' }}>
            LexiWare is an AI-powered contract intelligence platform that helps individuals and organizations understand the legal implications of agreements before signing. Millions of people sign contracts every day without fully understanding what they agree to — employment terms, rental leases, SaaS subscriptions, insurance policies, and NDAs often contain hidden risks.
          </p>
          <p style={{ color: '#6b7280', lineHeight: 1.8, fontSize: '0.88rem', marginBottom: '2rem' }}>
            Built on Google Vertex AI Gemini, Cloud Vision OCR, Cloud Natural Language, and a RAG-powered multi-agent pipeline — LexiWare delivers legal clarity without requiring a lawyer.
          </p>
          <button onClick={() => scrollTo('analyze')} style={{ background: 'linear-gradient(135deg,#1e3a8a,#1d4ed8)', color: '#fff', border: 'none', borderRadius: 8, padding: '13px 32px', fontSize: '0.95rem', fontWeight: 700, cursor: 'pointer', boxShadow: '0 4px 14px rgba(29,78,216,0.3)', fontFamily: 'inherit' }}>
            Analyze Your Contract Now
          </button>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer style={{ background: '#fff', borderTop: '1px solid #e5e7eb', padding: '1.25rem 2rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
          <Scale size={15} color="#1a2e4a" />
          <span style={{ fontWeight: 800, color: '#1a2e4a', fontSize: '0.9rem' }}>LexiWare</span>
          <span style={{ color: '#9ca3af', fontSize: '0.73rem' }}>— AI Contract Intelligence</span>
        </div>
        <p style={{ fontSize: '0.72rem', color: '#9ca3af' }}>AI analysis is not legal advice. Consult a qualified attorney for important decisions.</p>
        <div style={{ display: 'flex', gap: '1rem' }}>
          {['Privacy', 'Terms', 'GitHub'].map(l => (
            <a key={l} href={l === 'GitHub' ? 'https://github.com/sabareeshsp7/LexGuard-X' : '#'} style={{ fontSize: '0.77rem', color: '#6b7280', textDecoration: 'none' }} target={l === 'GitHub' ? '_blank' : undefined} rel="noreferrer">{l}</a>
          ))}
        </div>
      </footer>
    </div>
  );
}
