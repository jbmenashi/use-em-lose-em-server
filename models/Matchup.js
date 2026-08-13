import mongoose from "mongoose";

const matchupSchema = new mongoose.Schema(
  {
    leagueId: { type: mongoose.Schema.Types.ObjectId, ref: "League", required: true },
    season: { type: Number, required: true },
    week: { type: Number, required: true },
    seasonType: { type: String, required: true },
    team1Id: { type: mongoose.Schema.Types.ObjectId, ref: "Contestant", required: true },
    team1Name: { type: String, required: true },
    team1Score: { type: Number, required: true },
    team2Id: { type: mongoose.Schema.Types.ObjectId, ref: "Contestant", required: true },
    team2Name: { type: String, required: true },
    team2Score: { type: Number, required: true },
    winner: { type: mongoose.Schema.Types.ObjectId, ref: "Contestant", default: null },
    loser: { type: mongoose.Schema.Types.ObjectId, ref: "Contestant", default: null },
    finished: { type: Boolean, required: true },
  },
  { timestamps: true }
);

const Matchup = mongoose.model("Matchup", matchupSchema);

export default Matchup;
