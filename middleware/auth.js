import { jwtVerify } from "jose";

let requireClerkAuthInstance = null;

export function createRequireClerkAuth(jwks, CLERK_ISSUER) {
  const middleware = async function requireClerkAuth(req, res, next) {
    try {
      const authHeader = req.headers.authorization || "";
      if (!authHeader.startsWith("Bearer ")) {
        return res.status(401).json({ error: "Missing Bearer token" });
      }

      const token = authHeader.slice("Bearer ".length).trim();
      const { payload } = await jwtVerify(token, jwks, { issuer: CLERK_ISSUER });

      // Clerk user id is typically in `sub`
      if (!payload.sub) {
        return res.status(401).json({ error: "Token missing sub (userId)" });
      }

      req.auth = {
        userId: payload.sub,
        claims: payload,
      };

      next();
    } catch (err) {
      return res.status(401).json({ error: "Invalid token" });
    }
  };

  requireClerkAuthInstance = middleware;
  return middleware;
}

// Export getter function that routes can use (lazy - returns a wrapper that gets the middleware when called)
export function getRequireClerkAuth() {
  return (req, res, next) => {
    if (!requireClerkAuthInstance) {
      return res.status(500).json({ error: "Authentication middleware not initialized" });
    }
    return requireClerkAuthInstance(req, res, next);
  };
}
