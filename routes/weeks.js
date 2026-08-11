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
  const cursor = mongoose.connection.db.collection("Weeks").find({
    start_date: { $lte: currentDate },
    end_date: { $gte: currentDate },
  });

  for await (const item of cursor) {
    const itemSeason = `${item.sport.toLowerCase()}_season`;
    currentWeeks[itemSeason] = item.season;
    const itemWeek = `${item.sport.toLowerCase()}_week`;
    currentWeeks[itemWeek] = item.week_number;
  }

  res.json(currentWeeks);
});

export default router;
