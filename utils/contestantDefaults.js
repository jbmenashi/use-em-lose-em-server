// Matches the shape use-em-lose-em-scripts/nfl/standings.py rebuilds on every
// run, and what Standings.jsx reads client-side - keep these field names in
// sync with both.
export function defaultStandings() {
  return {
    wins: 0,
    losses: 0,
    winPct: 0,
    totalPointsFor: 0,
    totalPointsAg: 0,
  };
}
