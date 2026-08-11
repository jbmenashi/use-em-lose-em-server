import express from "express";
import mongoose from "mongoose";
import { getRequireClerkAuth } from "../middleware/auth.js";
import Lineup from "../models/Lineup.js";
import Contestant from "../models/Contestant.js";
import League from "../models/League.js";

const router = express.Router();
const requireClerkAuth = getRequireClerkAuth();

router.post("/:contestantId", requireClerkAuth, async (req, res) => {
  const { contestantId } = req.params;
  const { sport, style, season, week, selections, score, locked } = req.body || {};

  if (!mongoose.Types.ObjectId.isValid(contestantId)) {
    return res.status(400).json({ error: "Invalid contestant ID" });
  }

  const existingContestant = await Contestant.findById(contestantId).lean();
  if (!existingContestant) {
    return res.status(404).json({ error: `Contestant ${contestantId} not found` });
  }

  if (existingContestant.userId !== req.auth.userId) {
    return res.status(401).json({ error: "Not authorized to create lineup for this contestant" });
  }

  if (!sport || !style || season === undefined || week === undefined) {
    return res.status(400).json({ error: "Body must include { sport, style, season, week }" });
  }

  const newLineup = await Lineup.create({
    contestantId,
    leagueId: existingContestant.leagueId,
    sport,
    style,
    season,
    week,
    selections: selections ?? [],
    score: score ?? 0,
    locked: locked ?? false,
  });

  const lineupLeague = await League.findById(existingContestant.leagueId).lean();

  let builtSelections = [];
  for (const [position, count] of Object.entries(lineupLeague.roster.positions || {})) {
    builtSelections = builtSelections.concat(Array(count).fill(position));
  }
  builtSelections = builtSelections.map((position, index) => ({ position, locked: false, index }));

  // Raw collection write (bypassing Mongoose schema defaults) so the new
  // selection slots only carry { position, locked, index } - no playerId
  // key at all - matching how update_lineup below distinguishes "never
  // filled" slots from "filled then cleared" slots.
  await Lineup.collection.updateOne(
    { _id: newLineup._id },
    { $set: { selections: builtSelections } }
  );

  const createdLineup = await Lineup.findById(newLineup._id).lean();

  res.status(201).json({ lineup: createdLineup });
});

router.get("/:id", requireClerkAuth, async (req, res) => {
  const { id } = req.params;

  if (!mongoose.Types.ObjectId.isValid(id)) {
    return res.status(400).json({ error: "Invalid lineup ID" });
  }

  const lineup = await Lineup.findById(id).lean();
  if (!lineup) {
    return res.status(404).json({ error: `Lineup ${id} not found` });
  }

  res.json(lineup);
});

router.get("/league/:leagueId", requireClerkAuth, async (req, res) => {
  const { leagueId } = req.params;

  if (!mongoose.Types.ObjectId.isValid(leagueId)) {
    return res.status(400).json({ error: "Invalid league ID" });
  }

  const listOfLineups = await Lineup.find({ leagueId }).lean();
  res.json(listOfLineups);
});

router.get("/contestant/:contestantId", requireClerkAuth, async (req, res) => {
  const { contestantId } = req.params;
  const week = req.query.week !== undefined ? Number(req.query.week) : 1;

  if (!mongoose.Types.ObjectId.isValid(contestantId)) {
    return res.status(400).json({ error: "Invalid contestant ID" });
  }

  const existingLineup = await Lineup.findOne({ contestantId, week }).lean();

  if (!existingLineup) {
    return res.status(404).json({ error: "Lineup not found" });
  }

  res.json(existingLineup);
});

// The trickiest endpoint in the app: updates one selection slot, and keeps
// the owning Contestant's unavailablePlayers/unavailableTeams/teamCount in
// sync. Ported field-for-field from routers/lineup_router.py:update_lineup.
router.put("/:id", requireClerkAuth, async (req, res) => {
  const { id } = req.params;
  const selection = req.body || {};

  if (!mongoose.Types.ObjectId.isValid(id)) {
    return res.status(400).json({ error: "Invalid lineup ID" });
  }

  const existingLineup = await Lineup.findById(id).lean();
  if (!existingLineup) {
    return res.status(404).json({ error: `Lineup ${id} not found` });
  }

  const lineupContestant = await Contestant.findById(existingLineup.contestantId).lean();
  const lineupLeague = await League.findById(existingLineup.leagueId).lean();
  const leagueTeamCount = lineupLeague.teamCount;

  if (!lineupContestant || lineupContestant.userId !== req.auth.userId || existingLineup.locked) {
    return res.status(401).json({ error: `Not authorized to edit Lineup ${id}` });
  }

  for (const sel of existingLineup.selections) {
    const positionMatches =
      typeof sel.position === "string" &&
      typeof selection.position === "string" &&
      sel.position.toUpperCase() === selection.position.toUpperCase();

    if (sel.index !== selection.index || !positionMatches) continue;

    if (sel.locked) {
      return res.status(400).json({ error: "This selection slot is locked" });
    }

    const updatedLineup = await Lineup.findByIdAndUpdate(
      id,
      {
        $set: {
          [`selections.${selection.index}.playerId`]: selection.playerId,
          [`selections.${selection.index}.playerName`]: selection.playerName,
          [`selections.${selection.index}.teamId`]: selection.teamId,
          [`selections.${selection.index}.teamAbbreviation`]: selection.teamAbbreviation,
          [`selections.${selection.index}.opponent`]: selection.opponent,
          [`selections.${selection.index}.gameTime`]: selection.gameTime,
          [`selections.${selection.index}.location`]: selection.location,
        },
      },
      { new: true }
    ).lean();

    // Snapshot taken once, up front - mirrors the original's single read of
    // lineup_contestant['team_count'] reused by both branches below.
    const contestantTeamCount = lineupContestant.teamCount;

    if (selection.playerId !== null && selection.playerId !== undefined) {
      // A player is being placed into this slot: reserve their team/player.
      if (Object.prototype.hasOwnProperty.call(contestantTeamCount, selection.teamAbbreviation)) {
        if (contestantTeamCount[selection.teamAbbreviation] + 1 === leagueTeamCount) {
          await Contestant.findByIdAndUpdate(lineupContestant._id, {
            $push: {
              unavailableTeams: {
                teamId: selection.teamId,
                teamAbbreviation: selection.teamAbbreviation,
              },
            },
          });
        }
      }
      await Contestant.findByIdAndUpdate(lineupContestant._id, {
        $inc: { [`teamCount.${selection.teamAbbreviation}`]: 1 },
      });

      await Contestant.findByIdAndUpdate(lineupContestant._id, {
        $push: {
          unavailablePlayers: {
            playerId: selection.playerId,
            playerName: selection.playerName,
            teamId: selection.teamId,
            teamAbbreviation: selection.teamAbbreviation,
          },
        },
      });
    }

    if (Object.prototype.hasOwnProperty.call(sel, "playerId")) {
      // This slot previously held a player: free up their team/player.
      if (contestantTeamCount[sel.teamAbbreviation] === leagueTeamCount) {
        await Contestant.findByIdAndUpdate(lineupContestant._id, {
          $pull: { unavailableTeams: { teamId: sel.teamId } },
        });
      }
      await Contestant.findByIdAndUpdate(lineupContestant._id, {
        $inc: { [`teamCount.${sel.teamAbbreviation}`]: -1 },
      });

      await Contestant.findByIdAndUpdate(lineupContestant._id, {
        $pull: { unavailablePlayers: { playerId: sel.playerId } },
      });
    }

    return res.json(updatedLineup);
  }

  res.json(selection);
});

export default router;
