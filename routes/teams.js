import express from "express";
import mongoose from "mongoose";
import { getRequireClerkAuth } from "../middleware/auth.js";

const router = express.Router();
const requireClerkAuth = getRequireClerkAuth();

router.get("/nfl", requireClerkAuth, async (req, res) => {
  const results = await mongoose.connection.db
    .collection("Teams")
    .find({ sport: "NFL" })
    .toArray();

  res.json(results);
});

export default router;
