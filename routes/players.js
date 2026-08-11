import express from "express";
import mongoose from "mongoose";
import { getRequireClerkAuth } from "../middleware/auth.js";
import Contestant from "../models/Contestant.js";

const router = express.Router();
const requireClerkAuth = getRequireClerkAuth();

router.get("/mlb/:contestantId", requireClerkAuth, async (req, res) => {
  const { contestantId } = req.params;
  const { page = 1, limit = 25, positionFilter, teamFilter, sortCategory } = req.query;

  if (!mongoose.Types.ObjectId.isValid(contestantId)) {
    return res.status(400).json({ error: "Invalid contestant ID" });
  }

  const existingContestant = await Contestant.findById(contestantId).lean();
  if (!existingContestant) {
    return res.status(404).json({ error: `Contestant ${contestantId} not found` });
  }

  const unavailPlayerIds = existingContestant.unavailablePlayers.map((p) => p.playerId);
  const unavailTeamIds = existingContestant.unavailableTeams.map((t) => t.teamId);

  const findQuery = {
    status: "Active",
    player_id: { $nin: unavailPlayerIds },
    team_id: { $nin: unavailTeamIds },
  };

  if (positionFilter) {
    if (positionFilter === "C") {
      findQuery.position = positionFilter;
    } else if (positionFilter === "IF") {
      findQuery.position_category = positionFilter;
      findQuery.position = { $ne: "C" };
    } else {
      findQuery.position_category = positionFilter;
    }
  }

  if (teamFilter) {
    findQuery.team_abbreviation = teamFilter;
  }

  let sortQuery = { season_hits: -1 };
  if (sortCategory === "H") sortQuery = { season_hits: -1 };
  else if (sortCategory === "HR") sortQuery = { season_home_runs: -1 };
  else if (sortCategory === "RBI") sortQuery = { season_runs_batted_in: -1 };

  const pageNum = Number(page);
  const limitNum = Number(limit);

  const results = await mongoose.connection.db
    .collection("MLBPlayerSearchView")
    .find(findQuery)
    .sort(sortQuery)
    .skip((pageNum - 1) * limitNum)
    .limit(limitNum)
    .toArray();

  res.json(results);
});

router.get("/nfl/:contestantId", requireClerkAuth, async (req, res) => {
  const { contestantId } = req.params;
  const { page = 1, limit = 25, position, teamFilter, sortCategory } = req.query;

  if (!mongoose.Types.ObjectId.isValid(contestantId)) {
    return res.status(400).json({ error: "Invalid contestant ID" });
  }

  const existingContestant = await Contestant.findById(contestantId).lean();
  if (!existingContestant) {
    return res.status(404).json({ error: `Contestant ${contestantId} not found` });
  }

  const unavailPlayerIds = existingContestant.unavailablePlayers.map((p) => p.playerId);
  const unavailTeamIds = [];
  for (const t of existingContestant.unavailableTeams) {
    unavailTeamIds.push(Number(t.teamId));
    unavailTeamIds.push(String(t.teamId));
  }

  const findQuery = {
    player_id: { $nin: unavailPlayerIds },
    team_id: { $nin: unavailTeamIds },
  };

  if (position) {
    if (position === "FLEX") {
      findQuery.position = { $in: ["RB", "WR", "TE"] };
    } else {
      findQuery.position = position;
    }
  }

  if (teamFilter) {
    findQuery.team_abbreviation = teamFilter;
  }

  let sortQuery = { "projection.stats.score": -1 };
  if (sortCategory === "SEASON_PTS") sortQuery = { "season_stats.stats.yahoo_pts": -1 };
  else if (sortCategory === "PROJ_PTS") sortQuery = { "projection.stats.score": -1 };

  const pageNum = Number(page);
  const limitNum = Number(limit);

  const results = await mongoose.connection.db
    .collection("NFLPlayerSearchView")
    .find(findQuery)
    .sort(sortQuery)
    .skip((pageNum - 1) * limitNum)
    .limit(limitNum)
    .toArray();

  res.json(results);
});

export default router;
