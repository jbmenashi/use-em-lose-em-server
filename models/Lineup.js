import mongoose from "mongoose";

const selectionSchema = new mongoose.Schema(
  {
    playerId: { type: Number, default: null },
    playerName: { type: String, default: null },
    teamId: { type: Number, default: null },
    teamAbbreviation: { type: String, default: null },
    opponent: { type: String, default: null },
    gameTime: { type: String, default: null },
    location: { type: String, default: null },
    position: { type: String, required: true },
    fantasyStats: { type: mongoose.Schema.Types.Mixed, default: null },
    totalPoints: { type: Number, default: 0 },
    locked: { type: Boolean, default: false },
    index: { type: Number, default: null },
  },
  { _id: false }
);

const lineupSchema = new mongoose.Schema(
  {
    contestantId: { type: mongoose.Schema.Types.ObjectId, ref: "Contestant", default: null },
    leagueId: { type: mongoose.Schema.Types.ObjectId, ref: "League", default: null },
    sport: { type: String, required: true },
    style: { type: String, required: true },
    season: { type: Number, required: true },
    week: { type: Number, required: true },
    selections: { type: [selectionSchema], required: true },
    score: { type: Number, default: 0 },
    locked: { type: Boolean, default: false },
  },
  { timestamps: true }
);

const Lineup = mongoose.model("Lineup", lineupSchema);

export default Lineup;
