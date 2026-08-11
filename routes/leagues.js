import express from "express";
import mongoose from "mongoose";
import { getRequireClerkAuth } from "../middleware/auth.js";
import League from "../models/League.js";
import Contestant from "../models/Contestant.js";
import Matchup from "../models/Matchup.js";

const router = express.Router();
const requireClerkAuth = getRequireClerkAuth();

router.post("/", requireClerkAuth, async (req, res) => {
  const {
    leagueName,
    teamName,
    sport,
    season,
    style,
    size,
    regularSeasonWeeks,
    playoffTeams,
    playoffWeeks,
    teamCount,
    roster,
    scoring,
    scheduled,
    active,
    full,
  } = req.body || {};

  if (!leagueName || typeof leagueName !== "string") {
    return res.status(400).json({ error: "Body must include { leagueName: string }" });
  }
  if (!teamName || typeof teamName !== "string") {
    return res.status(400).json({ error: "Body must include { teamName: string }" });
  }
  if (!roster || typeof roster.rosterSize !== "number") {
    return res.status(400).json({ error: "Body must include { roster: { rosterSize: number } }" });
  }
  if (!scoring || typeof scoring !== "object") {
    return res.status(400).json({ error: "Body must include { scoring: object }" });
  }

  const createdLeague = await League.create({
    leagueName,
    sport,
    season,
    style,
    size,
    regularSeasonWeeks,
    playoffTeams,
    playoffWeeks,
    teamCount,
    roster,
    scoring,
    scheduled: !!scheduled,
    active: !!active,
    full: !!full,
    commissioner: req.auth.userId,
    locked: false,
  });

  const createdContestant = await Contestant.create({
    userId: req.auth.userId,
    leagueId: createdLeague._id,
    teamName,
    unavailablePlayers: [],
    unavailableTeams: [],
    teamCount: {},
    standings: {},
    locked: false,
  });

  res.status(201).json({ league: createdLeague, contestant: createdContestant });
});

router.get("/available", requireClerkAuth, async (req, res) => {
  const openLeagues = await League.find({ scheduled: false, active: false, full: false }).lean();

  const listOfLeagues = [];
  for (const league of openLeagues) {
    const alreadyIn = await Contestant.findOne({
      leagueId: league._id,
      userId: req.auth.userId,
    }).lean();
    if (!alreadyIn) {
      listOfLeagues.push(league);
    }
  }

  res.json(listOfLeagues);
});

router.get("/:id", requireClerkAuth, async (req, res) => {
  const { id } = req.params;

  if (!mongoose.Types.ObjectId.isValid(id)) {
    return res.status(400).json({ error: "Invalid league ID" });
  }

  const league = await League.findById(id).lean();

  if (!league) {
    return res.status(404).json({ error: `League ${id} not found` });
  }

  res.json(league);
});

router.get("/:id/schedule", requireClerkAuth, async (req, res) => {
  const { id } = req.params;

  if (!mongoose.Types.ObjectId.isValid(id)) {
    return res.status(400).json({ error: "Invalid league ID" });
  }

  const listOfMatchups = await Matchup.find({ leagueId: id }).lean();

  if (listOfMatchups.length === 0) {
    return res.status(204).json({ error: `Matchups not found for league ${id}` });
  }

  res.json(listOfMatchups);
});

router.put("/:id", requireClerkAuth, async (req, res) => {
  const { id } = req.params;

  if (!mongoose.Types.ObjectId.isValid(id)) {
    return res.status(400).json({ error: "Invalid league ID" });
  }

  const existingLeague = await League.findById(id).lean();
  if (!existingLeague) {
    return res.status(404).json({ error: `League ${id} not found` });
  }

  if (existingLeague.commissioner !== req.auth.userId) {
    return res.status(401).json({ error: `Not authorized to edit League ${id}` });
  }

  if (existingLeague.locked) {
    return res.status(400).json({ error: "League is locked for changes" });
  }

  const {
    leagueName,
    style,
    size,
    regularSeasonWeeks,
    playoffTeams,
    playoffWeeks,
    teamCount,
    roster,
    scoring,
    locked,
  } = req.body || {};

  const updateData = {};
  if (leagueName !== undefined) updateData.leagueName = leagueName;
  if (style !== undefined) updateData.style = style;
  if (size !== undefined) updateData.size = size;
  if (regularSeasonWeeks !== undefined) updateData.regularSeasonWeeks = regularSeasonWeeks;
  if (playoffTeams !== undefined) updateData.playoffTeams = playoffTeams;
  if (playoffWeeks !== undefined) updateData.playoffWeeks = playoffWeeks;
  if (teamCount !== undefined) updateData.teamCount = teamCount;
  if (roster !== undefined) updateData.roster = roster;
  if (scoring !== undefined) updateData.scoring = scoring;
  if (locked !== undefined) updateData.locked = locked;

  if (Object.keys(updateData).length === 0) {
    return res.json(existingLeague);
  }

  const updateResult = await League.findByIdAndUpdate(id, updateData, {
    new: true,
    runValidators: true,
  }).lean();

  if (updateData.locked) {
    await Contestant.updateMany({ leagueId: id }, { $set: { locked: true } });
  }

  res.json(updateResult);
});

router.delete("/:id", requireClerkAuth, async (req, res) => {
  const { id } = req.params;

  if (!mongoose.Types.ObjectId.isValid(id)) {
    return res.status(400).json({ error: "Invalid league ID" });
  }

  const existingLeague = await League.findById(id).lean();
  if (!existingLeague) {
    return res.status(404).json({ error: `League ${id} not found` });
  }

  if (existingLeague.commissioner !== req.auth.userId) {
    return res.status(401).json({ error: `Not authorized to delete League ${id}` });
  }

  await Contestant.deleteMany({ leagueId: id });
  const deleteResult = await League.deleteOne({ _id: id });

  if (deleteResult.deletedCount === 1) {
    return res.status(204).end();
  }

  res.status(404).json({ error: `League ${id} not found` });
});

export default router;
