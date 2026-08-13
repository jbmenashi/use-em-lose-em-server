import express from "express";
import mongoose from "mongoose";
import { getRequireClerkAuth } from "../middleware/auth.js";
import { snakeToCamel } from "../utils/caseTransform.js";

const router = express.Router();
const requireClerkAuth = getRequireClerkAuth();

router.get("/nfl", requireClerkAuth, async (req, res) => {
  const results = await mongoose.connection.db
    .collection("teams")
    .find({ sport: "NFL" })
    .toArray();

  res.json(snakeToCamel(results));
});

export default router;
