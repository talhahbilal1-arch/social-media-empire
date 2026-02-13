export default function ComparisonTable({ comparison, tool1, tool2 }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse">
        <thead>
          <tr className="bg-gray-50">
            <th className="text-left p-4 font-semibold text-gray-700 border-b">Feature</th>
            <th className="text-center p-4 font-semibold text-primary-700 border-b">{tool1.name}</th>
            <th className="text-center p-4 font-semibold text-primary-700 border-b">{tool2.name}</th>
            <th className="text-center p-4 font-semibold text-gray-700 border-b">Winner</th>
          </tr>
        </thead>
        <tbody>
          {comparison.comparison_points.map((point, idx) => (
            <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
              <td className="p-4 border-b font-medium text-gray-900">{point.feature}</td>
              <td className="p-4 border-b text-center">
                <ScoreBar score={point.tool1_score} isWinner={point.winner === comparison.tools[0]} />
              </td>
              <td className="p-4 border-b text-center">
                <ScoreBar score={point.tool2_score} isWinner={point.winner === comparison.tools[1]} />
              </td>
              <td className="p-4 border-b text-center">
                {point.winner === 'tie' ? (
                  <span className="badge bg-gray-100 text-gray-700">Tie</span>
                ) : point.winner === comparison.tools[0] ? (
                  <span className="badge bg-primary-100 text-primary-700">{tool1.name}</span>
                ) : (
                  <span className="badge bg-primary-100 text-primary-700">{tool2.name}</span>
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
  if (score === 0) return <span className="text-gray-400 text-sm">N/A</span>

  const width = `${(score / 5) * 100}%`

  return (
    <div className="flex items-center justify-center space-x-2">
      <div className="w-20 bg-gray-200 rounded-full h-2">
        <div
          className={`h-2 rounded-full ${isWinner ? 'bg-green-500' : 'bg-primary-400'}`}
          style={{ width }}
        />
      </div>
      <span className={`text-sm font-medium ${isWinner ? 'text-green-600' : 'text-gray-600'}`}>
        {score.toFixed(1)}
      </span>
    </div>
  )
}
