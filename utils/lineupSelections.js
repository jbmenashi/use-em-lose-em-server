// Bare { position, locked, index } slots only - no playerId key at all -
// matching how routes/lineups.js distinguishes "never filled" from "filled
// then cleared" selection slots.
export function buildSelections(positions) {
  const flatPositions = [];
  for (const [position, count] of Object.entries(positions || {})) {
    flatPositions.push(...Array(count).fill(position));
  }
  return flatPositions.map((position, index) => ({ position, locked: false, index }));
}

export function buildWeeklyLineups({ contestantId, leagueId, league }) {
  const weeklyLineups = [];
  for (let week = 1; week <= league.regularSeasonWeeks; week++) {
    weeklyLineups.push({
      contestantId,
      leagueId,
      sport: league.sport,
      style: league.style,
      season: league.season,
      week,
      score: 0,
      locked: false,
      selections: buildSelections(league.roster.positions),
    });
  }
  return weeklyLineups;
}
