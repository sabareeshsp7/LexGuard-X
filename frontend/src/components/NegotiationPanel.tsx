import { motion } from 'framer-motion';
import type { FutureScenario, NegotiationAlternative } from '../types';
import { Clock, TrendingDown, DollarSign, MessageSquare, CheckCircle, Lightbulb } from 'lucide-react';

interface Props {
  scenarios: FutureScenario[];
  negotiations: NegotiationAlternative[];
}

const scenarioMeta = {
  best_case:  { label: 'Best Case',  color: '#10b981', emoji: '🟢' },
  realistic:  { label: 'Realistic',  color: '#f59e0b', emoji: '🟡' },
  worst_case: { label: 'Worst Case', color: '#ef4444', emoji: '🔴' },
};

const likelihoodColor: Record<string, string> = {
  Low: '#10b981', Medium: '#f59e0b', High: '#ef4444',
};

export default function NegotiationPanel({ scenarios, negotiations }: Props) {
  const safeScenarios = scenarios ?? [];
  const safeNegotiations = negotiations ?? [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

      {safeScenarios.length > 0 && (
        <div className="card">
          <h3 style={{ fontWeight: 700, fontSize: '1rem', marginBottom: '0.25rem' }}>
            🔮 Future Consequence Simulation
          </h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', marginBottom: '1.25rem' }}>
            AI-simulated outcomes if you sign this contract
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {safeScenarios.map((scenario, i) => {
              const meta = scenarioMeta[scenario.scenario_type as keyof typeof scenarioMeta]
                ?? { label: scenario.scenario_type, color: '#94a3b8', emoji: '⚪' };
              const probColor = likelihoodColor[scenario.probability] ?? '#94a3b8';

              return (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -16 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                  style={{
                    border: `1px solid ${meta.color}25`,
                    borderLeft: `3px solid ${meta.color}`,
                    borderRadius: 'var(--radius-sm)',
                    padding: '1rem',
                    background: `${meta.color}06`,
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: '0.75rem' }}>
                    <span style={{ fontSize: '1.1rem' }}>{meta.emoji}</span>
                    <span style={{ fontWeight: 700, fontSize: '0.9rem', color: meta.color }}>
                      {meta.label}
                    </span>
                    <span style={{
                      marginLeft: 'auto', fontSize: '0.72rem', padding: '2px 10px',
                      borderRadius: 99,
                      background: `${probColor}15`,
                      border: `1px solid ${probColor}30`,
                      color: probColor, fontWeight: 700,
                    }}>
                      {scenario.probability ?? '—'} probability
                    </span>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.6rem', fontSize: '0.8rem' }}>
                    <div>
                      <div style={{ display: 'flex', gap: 5, color: 'var(--text-muted)', marginBottom: 2, alignItems: 'center' }}>
                        <TrendingDown size={12} /> Trigger
                      </div>
                      <p style={{ color: 'var(--text-secondary)', lineHeight: 1.5 }}>{scenario.trigger}</p>
                    </div>
                    <div>
                      <div style={{ display: 'flex', gap: 5, color: 'var(--text-muted)', marginBottom: 2, alignItems: 'center' }}>
                        <Clock size={12} /> Timeline
                      </div>
                      <p style={{ color: 'var(--text-secondary)', lineHeight: 1.5 }}>{scenario.timeline}</p>
                    </div>
                    <div>
                      <div style={{ display: 'flex', gap: 5, color: 'var(--text-muted)', marginBottom: 2, alignItems: 'center' }}>
                        <MessageSquare size={12} /> What you lose
                      </div>
                      <p style={{ color: meta.color, lineHeight: 1.5, fontWeight: 500 }}>{scenario.user_loss}</p>
                    </div>
                    <div>
                      <div style={{ display: 'flex', gap: 5, color: 'var(--text-muted)', marginBottom: 2, alignItems: 'center' }}>
                        <DollarSign size={12} /> Financial impact
                      </div>
                      <p style={{ color: meta.color, lineHeight: 1.5, fontWeight: 600 }}>{scenario.financial_impact}</p>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      )}

      {safeNegotiations.length > 0 && (
        <div className="card">
          <h3 style={{ fontWeight: 700, fontSize: '1rem', marginBottom: '0.25rem' }}>
            🤝 Negotiation Strategies
          </h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', marginBottom: '1.25rem' }}>
            AI-drafted counter-clauses and negotiation tactics
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {safeNegotiations.map((neg, i) => {
              const likeColor = likelihoodColor[neg.likelihood_accepted] ?? '#94a3b8';
              return (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.1 }}
                  style={{
                    border: '1px solid rgba(6,182,212,0.2)',
                    borderRadius: 'var(--radius-sm)',
                    padding: '1rem',
                    background: 'rgba(6,182,212,0.03)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: '0.75rem' }}>
                    <Lightbulb size={16} color="var(--accent-cyan)" />
                    <span style={{ fontWeight: 700, fontSize: '0.88rem' }}>Strategy #{i + 1}</span>
                    <span style={{
                      marginLeft: 'auto', fontSize: '0.72rem', padding: '2px 10px',
                      borderRadius: 99,
                      background: `${likeColor}15`,
                      border: `1px solid ${likeColor}30`,
                      color: likeColor, fontWeight: 700,
                    }}>
                      {neg.likelihood_accepted ?? '—'} chance of acceptance
                    </span>
                  </div>

                  <div style={{ marginBottom: '0.75rem' }}>
                    <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: 6, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                      Proposed new language
                    </p>
                    <div style={{
                      background: 'rgba(16,185,129,0.06)',
                      border: '1px solid rgba(16,185,129,0.2)',
                      borderRadius: 'var(--radius-sm)',
                      padding: '0.75rem',
                      fontSize: '0.82rem',
                      color: 'var(--text-secondary)',
                      lineHeight: 1.6,
                      fontStyle: 'italic',
                    }}>
                      "{neg.revised_text}"
                    </div>
                  </div>

                  <div style={{ display: 'flex', gap: 5, fontSize: '0.8rem', color: 'var(--accent-green)', alignItems: 'flex-start' }}>
                    <CheckCircle size={14} style={{ flexShrink: 0, marginTop: 2 }} />
                    <span>{neg.why_better}</span>
                  </div>

                  {neg.fallback && (
                    <div style={{ marginTop: '0.6rem', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                      <strong style={{ color: 'var(--text-secondary)' }}>Minimum fallback:</strong> {neg.fallback}
                    </div>
                  )}
                </motion.div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
