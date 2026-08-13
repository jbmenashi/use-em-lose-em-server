import express from "express";
import mongoose from "mongoose";
import { getRequireClerkAuth } from "../middleware/auth.js";

const router = express.Router();
const requireClerkAuth = getRequireClerkAuth();

router.get("/current", requireClerkAuth, async (req, res) => {
  const currentDate = new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/Los_Angeles",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date());

  const currentWeeks = {};
  const cursor = mongoose.connection.db.collection("weeks").find({
    startDate: { $lte: currentDate },
    endDate: { $gte: currentDate },
  });

  for await (const item of cursor) {
    const itemSeason = `${item.sport.toLowerCase()}Season`;
    currentWeeks[itemSeason] = item.season;
    const itemWeek = `${item.sport.toLowerCase()}Week`;
    currentWeeks[itemWeek] = item.weekNumber;
  }

  res.json(currentWeeks);
});

export default router;
