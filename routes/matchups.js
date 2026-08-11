import express from "express";
import mongoose from "mongoose";
import { getRequireClerkAuth } from "../middleware/auth.js";
import Matchup from "../models/Matchup.js";

const router = express.Router();
const requireClerkAuth = getRequireClerkAuth();

router.get("/:id", requireClerkAuth, async (req, res) => {
  const { id } = req.params;

  if (!mongoose.Types.ObjectId.isValid(id)) {
    return res.status(400).json({ error: "Invalid matchup ID" });
  }

  const results = await Matchup.aggregate([
    { $match: { _id: new mongoose.Types.ObjectId(id) } },
    {
      $lookup: {
        from: "lineups",
        let: {
          matchupTeam1Id: "$team1Id",
          matchupSeason: "$season",
          matchupWeek: "$week",
        },
        pipeline: [
          {
            $match: {
              $expr: {
                $and: [
                  { $eq: ["$$matchupTeam1Id", "$contestantId"] },
                  { $eq: ["$$matchupSeason", "$season"] },
                  { $eq: ["$$matchupWeek", "$week"] },
                ],
              },
            },
          },
        ],
        as: "team1Lineup",
      },
    },
    {
      $lookup: {
        from: "lineups",
        let: {
          matchupTeam2Id: "$team2Id",
          matchupSeason: "$season",
          matchupWeek: "$week",
        },
        pipeline: [
          {
            $match: {
              $expr: {
                $and: [
                  { $eq: ["$$matchupTeam2Id", "$contestantId"] },
                  { $eq: ["$$matchupSeason", "$season"] },
                  { $eq: ["$$matchupWeek", "$week"] },
                ],
              },
            },
          },
        ],
        as: "team2Lineup",
      },
    },
    {
      $project: {
        _id: 1,
        leagueId: 1,
        season: 1,
        week: 1,
        seasonType: 1,
        team1Id: 1,
        team1Name: 1,
        team1Score: 1,
        team1Lineup: { $arrayElemAt: ["$team1Lineup", 0] },
        team2Id: 1,
        team2Name: 1,
        team2Score: 1,
        team2Lineup: { $arrayElemAt: ["$team2Lineup", 0] },
        winner: 1,
        loser: 1,
        finished: 1,
      },
    },
  ]);

  const matchup = results[0];

  if (!matchup) {
    return res.status(404).json({ error: `Matchup ${id} not found` });
  }

  res.json(matchup);
});

export default router;
