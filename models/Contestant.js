import mongoose from "mongoose";

const unavailPlayerSchema = new mongoose.Schema(
  {
    playerId: { type: Number, required: true },
    playerName: { type: String, required: true },
    teamId: { type: Number, required: true },
    teamAbbreviation: { type: String, required: true },
  },
  { _id: false }
);

const unavailTeamSchema = new mongoose.Schema(
  {
    teamId: { type: Number, required: true },
    teamAbbreviation: { type: String, required: true },
  },
  { _id: false }
);

const contestantSchema = new mongoose.Schema(
  {
    userId: { type: String, default: null },
    leagueId: { type: mongoose.Schema.Types.ObjectId, ref: "League", default: null },
    teamName: { type: String, default: "" },
    unavailablePlayers: { type: [unavailPlayerSchema], default: [] },
    unavailableTeams: { type: [unavailTeamSchema], default: [] },
    teamCount: { type: mongoose.Schema.Types.Mixed, default: {} },
    standings: { type: mongoose.Schema.Types.Mixed, default: {} },
    locked: { type: Boolean, default: false },
  },
  { timestamps: true, minimize: false }
);

const Contestant = mongoose.model("Contestant", contestantSchema);

export default Contestant;
