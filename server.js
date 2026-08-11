import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import mongoose from "mongoose";
import { createRemoteJWKSet } from "jose";
import { createRequireClerkAuth } from "./middleware/auth.js";
import healthRoutes from "./routes/health.js";
import leaguesRoutes from "./routes/leagues.js";
import contestantsRoutes from "./routes/contestants.js";
import playersRoutes from "./routes/players.js";
import teamsRoutes from "./routes/teams.js";
import lineupsRoutes from "./routes/lineups.js";
import weeksRoutes from "./routes/weeks.js";
import matchupsRoutes from "./routes/matchups.js";

dotenv.config();

const PORT = process.env.PORT || 5000;
const MONGODB_URI = process.env.MONGODB_URI;
const CLERK_ISSUER = process.env.CLERK_ISSUER;

// ---- Clerk JWT middleware (JWKS) ----
if (!CLERK_ISSUER) {
  console.error("Missing CLERK_ISSUER in .env");
  process.exit(1);
}

const jwks = createRemoteJWKSet(new URL(`${CLERK_ISSUER}/.well-known/jwks.json`));
createRequireClerkAuth(jwks, CLERK_ISSUER);

const app = express();

const origins = [
  "http://localhost:5173",
  "http://localhost",
  "https://use-em-lose-em-client-1b9a368419b2.herokuapp.com",
];

app.use(
  cors({
    origin: origins,
    credentials: true,
  })
);
app.use(express.json());

// ---- Routes ----
app.use("/health", healthRoutes);
app.use("/leagues", leaguesRoutes);
app.use("/contestants", contestantsRoutes);
app.use("/players", playersRoutes);
app.use("/teams", teamsRoutes);
app.use("/lineups", lineupsRoutes);
app.use("/weeks", weeksRoutes);
app.use("/matchups", matchupsRoutes);

// ---- Start ----
async function start() {
  if (!MONGODB_URI) {
    console.error("Missing MONGODB_URI in .env");
    process.exit(1);
  }

  await mongoose.connect(MONGODB_URI, { dbName: "ff_db", uuidRepresentation: "standard" });
  console.log("Connected to MongoDB");

  app.listen(PORT, () => {
    console.log(`API listening on http://localhost:${PORT}`);
  });
}

start().catch((e) => {
  console.error(e);
  process.exit(1);
});
