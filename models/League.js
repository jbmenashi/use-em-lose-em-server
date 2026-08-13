import mongoose from "mongoose";

const rosterSchema = new mongoose.Schema(
  {
    rosterSize: { type: Number, required: true },
    positions: { type: mongoose.Schema.Types.Mixed, default: {} },
  },
  { _id: false }
);

const scoringSchema = new mongoose.Schema(
  {
    statistics: { type: mongoose.Schema.Types.Mixed, default: {} },
  },
  { _id: false }
);

const leagueSchema = new mongoose.Schema(
  {
    commissioner: { type: String, default: null },
    leagueName: { type: String, required: true },
    sport: { type: String, required: true },
    season: { type: Number, required: true },
    style: { type: String, required: true },
    size: { type: Number, required: true },
    regularSeasonWeeks: { type: Number, required: true },
    playoffTeams: { type: Number, required: true },
    playoffWeeks: { type: Number, required: true },
    teamCount: { type: Number, required: true },
    roster: { type: rosterSchema, required: true },
    scoring: { type: scoringSchema, required: true },
    scheduled: { type: Boolean, required: true },
    active: { type: Boolean, required: true },
    full: { type: Boolean, required: true },
    locked: { type: Boolean, default: false },
  },
  { timestamps: true }
);

const League = mongoose.model("League", leagueSchema);

export default League;
