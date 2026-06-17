export function MatchScoreRing({ score, size = 80 }: { score: number; size?: number }) {
  const radius = (size - 8) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (score / 100) * circumference;

  let color = "var(--accent-emerald)";
  if (score < 50) color = "var(--accent-rose)";
  else if (score < 75) color = "var(--accent-amber)";

  return (
    <div className="score-ring-container" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="var(--border-color)"
          strokeWidth="6"
          fill="none"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth="6"
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{
            transformOrigin: "50% 50%",
            transform: "rotate(-90deg)",
            transition: "stroke-dashoffset 1s ease-in-out",
          }}
        />
      </svg>
      <div className="score-ring-value" style={{ color, fontSize: size * 0.25 }}>
        {Math.round(score)}
      </div>
    </div>
  );
}
