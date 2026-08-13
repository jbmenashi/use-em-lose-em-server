// Circle-method round robin: each week, pair contestant i with the
// contestant "opposite" it in the current rotation, then rotate everyone
// except the first contestant by one seat. Ported from
// use-em-lose-em-scripts/nfl/schedule.py's generate_schedule(), but driven
// directly by the target week count instead of its cycle/round bookkeeping -
// that version breaks out of only its innermost loop when the week count is
// reached, which (e.g. an 8-team league at 14 weeks) can leave an extra
// unwanted cycle running and generate matchups past the regular season.
// Assumes an even contestant count (guaranteed by the client's league-size
// picker).
export function buildRoundRobinMatchups({ league, contestants }) {
  const halfSize = Math.floor(league.size / 2);
  const contestantIds = contestants.map((c) => c._id);
  const contestantNames = contestants.map((c) => c.teamName);

  const matchups = [];

  for (let week = 1; week <= league.regularSeasonWeeks; week++) {
    for (let i = 0; i < halfSize; i++) {
      matchups.push({
        leagueId: league._id,
        season: league.season,
        week,
        seasonType: "REG",
        team1Id: contestantIds[i],
        team1Name: contestantNames[i],
        team1Score: 0,
        team2Id: contestantIds[contestantIds.length - 1 - i],
        team2Name: contestantNames[contestantNames.length - 1 - i],
        team2Score: 0,
        winner: null,
        loser: null,
        finished: false,
      });
    }

    contestantIds.splice(1, 0, contestantIds.pop());
    contestantNames.splice(1, 0, contestantNames.pop());
  }

  return matchups;
}
