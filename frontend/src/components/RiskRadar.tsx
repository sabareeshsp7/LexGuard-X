import { RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer, Tooltip } from 'recharts';
import type { RiskScore } from '../types';

interface Props {
  riskScore: RiskScore;
}

const levelColors: Record<string, string> = {
  CRITICAL: '#ef4444',
  HIGH: '#f97316',
  MEDIUM: '#f59e0b',
  LOW: '#10b981',
};

const levelLabels: Record<string, string> = {
  CRITICAL: 'Do not sign without lawyer review',
  HIGH: 'Significant concerns — negotiate before signing',
  MEDIUM: 'Review highlighted clauses carefully',
  LOW: 'Minor issues — generally safe to sign',
};

export default function RiskRadar({ riskScore }: Props) {
  const level = riskScore?.level ?? 'MEDIUM';
  const color = levelColors[level] ?? '#94a3b8';
  const overallScore = riskScore?.overall_score ?? 0;

  const radarData = [
    { dimension: 'Legal',      value: riskScore?.legal_score      ?? 0 },
    { dimension: 'Privacy',    value: riskScore?.privacy_score    ?? 0 },
    { dimension: 'Financial',  value: riskScore?.financial_score  ?? 0 },
    { dimension: 'IP Rights',  value: riskScore?.ip_score         ?? 0 },
    { dimension: 'Ambiguity',  value: riskScore?.ambiguity_score  ?? 0 },
    { dimension: 'Employment', value: riskScore?.employment_score ?? 0 },
  ];

  const circumference = 2 * Math.PI * 52;
  const strokeDash = (overallScore / 100) * circumference;

  const breakdownBars = [
    { label: 'Legal',      score: riskScore?.legal_score      ?? 0 },
    { label: 'Privacy',    score: riskScore?.privacy_score    ?? 0 },
    { label: 'Financial',  score: riskScore?.financial_score  ?? 0 },
    { label: 'IP Rights',  score: riskScore?.ip_score         ?? 0 },
    { label: 'Ambiguity',  score: riskScore?.ambiguity_score  ?? 0 },
    { label: 'Employment', score: riskScore?.employment_score ?? 0 },
  ];

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <h3 style={{ fontWeight: 700, fontSize: '1rem' }}>Risk Analysis</h3>

      <div style={{ display: 'flex', gap: '2rem', alignItems: 'center', flexWrap: 'wrap' }}>

        {/* Score Gauge */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
          <div style={{ position: 'relative', width: 130, height: 130 }}>
            <svg width="130" height="130" style={{ transform: 'rotate(-90deg)' }}>
              <circle cx="65" cy="65" r="52" fill="none" stroke="rgba(255,255,255,0.07)" strokeWidth="10" />
              <circle
                cx="65" cy="65" r="52" fill="none"
                stroke={color}
                strokeWidth="10"
                strokeLinecap="round"
                strokeDasharray={`${strokeDash} ${circumference}`}
                style={{ transition: 'stroke-dasharray 1s ease', filter: `drop-shadow(0 0 8px ${color})` }}
              />
            </svg>
            <div style={{
              position: 'absolute', inset: 0,
              display: 'flex', flexDirection: 'column',
              alignItems: 'center', justifyContent: 'center',
            }}>
              <span style={{ fontSize: '2rem', fontWeight: 800, color, lineHeight: 1 }}>
                {Math.round(overallScore)}
              </span>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>/100</span>
            </div>
          </div>
          <div style={{
            padding: '6px 16px', borderRadius: 99,
            background: `${color}20`,
            border: `1px solid ${color}40`,
            fontSize: '0.75rem', fontWeight: 800, color,
            letterSpacing: '0.08em',
          }}>
            {level}
          </div>
          <p style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', textAlign: 'center', maxWidth: 120 }}>
            {levelLabels[level] ?? ''}
          </p>
        </div>

        {/* Radar Chart */}
        <div style={{ flex: 1, minWidth: 200, height: 200 }}>
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart data={radarData} margin={{ top: 10, right: 20, bottom: 10, left: 20 }}>
              <PolarGrid stroke="rgba(255,255,255,0.08)" />
              <PolarAngleAxis
                dataKey="dimension"
                tick={{ fill: 'var(--text-secondary)', fontSize: 11 }}
              />
              <Radar
                name="Risk"
                dataKey="value"
                stroke={color}
                fill={color}
                fillOpacity={0.15}
                strokeWidth={2}
              />
              <Tooltip
                contentStyle={{
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border)',
                  borderRadius: 8, fontSize: '0.8rem',
                  color: 'var(--text-primary)',
                }}
                formatter={(val: unknown) => [`${Number(val ?? 0)}/100`, 'Risk Score']}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Score breakdown bars */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
        {breakdownBars.map(({ label, score }) => {
          const barColor = score >= 75 ? '#ef4444' : score >= 50 ? '#f97316' : score >= 25 ? '#f59e0b' : '#10b981';
          return (
            <div key={label}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4, fontSize: '0.78rem' }}>
                <span style={{ color: 'var(--text-secondary)' }}>{label}</span>
                <span style={{ fontWeight: 700, color: barColor }}>{Math.round(score)}</span>
              </div>
              <div style={{ height: 4, borderRadius: 99, background: 'rgba(255,255,255,0.07)' }}>
                <div style={{
                  height: '100%', borderRadius: 99,
                  width: `${score}%`,
                  background: barColor,
                  transition: 'width 1s ease',
                }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
