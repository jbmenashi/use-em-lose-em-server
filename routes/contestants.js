import express from "express";
import mongoose from "mongoose";
import { getRequireClerkAuth } from "../middleware/auth.js";
import Contestant from "../models/Contestant.js";
import League from "../models/League.js";

const router = express.Router();
const requireClerkAuth = getRequireClerkAuth();

router.post("/:leagueId", requireClerkAuth, async (req, res) => {
  const { leagueId } = req.params;
  const { teamName } = req.query;

  if (!mongoose.Types.ObjectId.isValid(leagueId)) {
    return res.status(400).json({ error: `League ${leagueId} not found` });
  }

  const leagueToJoin = await League.findById(leagueId).lean();
  if (!leagueToJoin) {
    return res.status(404).json({ error: `League ${leagueId} not found` });
  }

  const leagueSize = leagueToJoin.size;
  const contestantsCount = await Contestant.countDocuments({ leagueId });

  if (contestantsCount >= leagueSize) {
    return res.status(400).json({ error: "League is full" });
  }

  const alreadyInLeague = await Contestant.findOne({
    leagueId,
    userId: req.auth.userId,
  }).lean();

  if (alreadyInLeague) {
    return res.status(400).json({ error: "User is already in this league" });
  }

  const createdContestant = await Contestant.create({
    userId: req.auth.userId,
    leagueId,
    teamName: teamName ?? "",
    unavailablePlayers: [],
    unavailableTeams: [],
    teamCount: {},
    standings: {},
    locked: false,
  });

  if (contestantsCount + 1 === leagueSize) {
    await League.findByIdAndUpdate(leagueId, { $set: { full: true } });
  }

  res.status(201).json({ contestant: createdContestant });
});

router.get("/me", requireClerkAuth, async (req, res) => {
  const listOfContestants = await Contestant.aggregate([
    { $match: { userId: req.auth.userId } },
    {
      $lookup: {
        from: "leagues",
        localField: "leagueId",
        foreignField: "_id",
        as: "leagueInfo",
      },
    },
    { $unwind: "$leagueInfo" },
    {
      $project: {
        _id: 1,
        contestantId: "$_id",
        userId: 1,
        leagueId: 1,
        teamName: 1,
        locked: 1,
        leagueName: "$leagueInfo.leagueName",
        commissionerId: "$leagueInfo.commissioner",
        sport: "$leagueInfo.sport",
        style: "$leagueInfo.style",
        leagueLocked: "$leagueInfo.locked",
        leagueActive: "$leagueInfo.active",
      },
    },
  ]);

  res.json(listOfContestants);
});

router.get("/league/:leagueId", requireClerkAuth, async (req, res) => {
  const { leagueId } = req.params;

  if (!mongoose.Types.ObjectId.isValid(leagueId)) {
    return res.status(400).json({ error: "Invalid league ID" });
  }

  const listOfContestants = await Contestant.find({ leagueId }).lean();
  res.json(listOfContestants);
});

router.get("/:id", requireClerkAuth, async (req, res) => {
  const { id } = req.params;

  if (!mongoose.Types.ObjectId.isValid(id)) {
    return res.status(400).json({ error: "Invalid contestant ID" });
  }

  const contestant = await Contestant.findById(id).lean();
  if (!contestant) {
    return res.status(404).json({ error: `Contestant ${id} not found` });
  }

  res.json(contestant);
});

router.put("/:id", requireClerkAuth, async (req, res) => {
  const { id } = req.params;

  if (!mongoose.Types.ObjectId.isValid(id)) {
    return res.status(400).json({ error: "Invalid contestant ID" });
  }

  const existingContestant = await Contestant.findById(id).lean();
  if (!existingContestant) {
    return res.status(404).json({ error: `Contestant ${id} not found` });
  }

  if (existingContestant.userId !== req.auth.userId) {
    return res.status(401).json({ error: `Not authorized to edit Contestant ${id}` });
  }

  if (existingContestant.locked) {
    return res.status(400).json({ error: "Contestant is locked for changes" });
  }

  const { teamName, locked, unavailablePlayers, unavailableTeams, standings, teamCount } =
    req.body || {};

  const updateData = {};
  if (teamName !== undefined) updateData.teamName = teamName;
  if (locked !== undefined) updateData.locked = locked;
  if (unavailablePlayers !== undefined) updateData.unavailablePlayers = unavailablePlayers;
  if (unavailableTeams !== undefined) updateData.unavailableTeams = unavailableTeams;
  if (standings !== undefined) updateData.standings = standings;
  if (teamCount !== undefined) updateData.teamCount = teamCount;

  if (Object.keys(updateData).length === 0) {
    return res.json(existingContestant);
  }

  const updateResult = await Contestant.findByIdAndUpdate(id, updateData, {
    new: true,
    runValidators: true,
  }).lean();

  res.json(updateResult);
});

router.delete("/:id", requireClerkAuth, async (req, res) => {
  const { id } = req.params;

  if (!mongoose.Types.ObjectId.isValid(id)) {
    return res.status(400).json({ error: "Invalid contestant ID" });
  }

  const existingContestant = await Contestant.findById(id).lean();
  if (!existingContestant) {
    return res.status(404).json({ error: `Contestant ${id} not found` });
  }

  if (existingContestant.userId !== req.auth.userId) {
    return res.status(401).json({ error: `Not authorized to delete contestant ${id}` });
  }

  const deleteResult = await Contestant.deleteOne({ _id: id });

  const conIsCommissh = await League.findOne({
    _id: existingContestant.leagueId,
    commissioner: req.auth.userId,
  }).lean();

  if (conIsCommissh) {
    await Contestant.deleteMany({ leagueId: existingContestant.leagueId });
    await League.deleteOne({ _id: existingContestant.leagueId });
    await League.findByIdAndUpdate(existingContestant.leagueId, { $set: { full: false } });
  }

  if (deleteResult.deletedCount === 1) {
    return res.status(204).end();
  }

  res.status(404).json({ error: `contestant ${id} not found` });
});

export default router;
