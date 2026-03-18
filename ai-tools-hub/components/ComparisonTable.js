export default function ComparisonTable({ comparison, tool1, tool2 }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse">
        <thead>
          <tr className="bg-dark-surface-hover">
            <th className="text-left p-4 font-semibold text-dt border-b border-dark-border">Feature</th>
            <th className="text-center p-4 font-semibold text-accent border-b border-dark-border">{tool1.name}</th>
            <th className="text-center p-4 font-semibold text-accent border-b border-dark-border">{tool2.name}</th>
            <th className="text-center p-4 font-semibold text-dt border-b border-dark-border">Winner</th>
          </tr>
        </thead>
        <tbody>
          {comparison.comparison_points.map((point, idx) => (
            <tr key={idx} className={idx % 2 === 0 ? 'bg-dark-surface' : 'bg-dark-surface-hover/50'}>
              <td className="p-4 border-b border-dark-border font-medium text-dt">{point.feature}</td>
              <td className="p-4 border-b border-dark-border text-center">
                <ScoreBar score={point.tool1_score} isWinner={point.winner === comparison.tools[0]} />
              </td>
              <td className="p-4 border-b border-dark-border text-center">
                <ScoreBar score={point.tool2_score} isWinner={point.winner === comparison.tools[1]} />
              </td>
              <td className="p-4 border-b border-dark-border text-center">
                {point.winner === 'tie' ? (
                  <span className="badge bg-dark-surface-hover text-dt-muted border border-dark-border">Tie</span>
                ) : point.winner === comparison.tools[0] ? (
                  <span className="badge bg-accent/10 text-accent border border-accent/20">{tool1.name}</span>
                ) : (
                  <span className="badge bg-accent/10 text-accent border border-accent/20">{tool2.name}</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function ScoreBar({ score, isWinner }) {
  if (score === 0) return <span className="text-dt-muted text-sm">N/A</span>

  const width = `${(score / 5) * 100}%`

  return (
    <div className="flex items-center justify-center space-x-2">
      <div className="w-20 bg-dark-border rounded-full h-2">
        <div
          className={`h-2 rounded-full ${isWinner ? 'bg-green-500' : 'bg-accent/60'}`}
          style={{ width }}
        />
      </div>
      <span className={`text-sm font-medium ${isWinner ? 'text-green-400' : 'text-dt-muted'}`}>
        {score.toFixed(1)}
      </span>
    </div>
  )
}
