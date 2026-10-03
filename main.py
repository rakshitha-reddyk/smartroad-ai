"""SmartRoad AI - FastAPI backend: JWT auth, Kruskal MST engine, saved projects.
Run:  uvicorn main:app --reload      Docs: http://localhost:8000/docs
Env:  SECRET_KEY (required in production), MONGO_URI (optional; in-memory if unset), CORS_ORIGINS
"""
from fastapi.responses import FileResponse
import os
from collections import deque
from datetime import datetime, timedelta, timezone
from time import perf_counter
from uuid import uuid4

import bcrypt
import jwt
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field

SECRET = os.getenv("SECRET_KEY", "change-me-in-production")
ALGO, TOKEN_MINUTES = "HS256", 60
app =FastAPI(title="SmartRoad AI API", version="1.0.0")

app = FastAPI(title="SmartRoad AI API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
                   allow_methods=["*"], allow_headers=["*"])
@app.get("/", include_in_schema=False)
def home():
    return FileResponse("smartroad.html")


# ---------------------------------------------------------------- auth
def _hash(pw: str) -> bytes:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt())

# Demo users (passwords hashed at startup). In production load these from MongoDB.
USERS = {"officer": _hash("smartroad123"), "admin": _hash("admin@123")}
_DUMMY = _hash("dummy")  # compared when the user is unknown, so timing doesn't reveal valid IDs
oauth2 = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

@app.post("/api/auth/login", tags=["auth"])
def login(form: OAuth2PasswordRequestForm = Depends()):
    ok = bcrypt.checkpw(form.password.encode(), USERS.get(form.username, _DUMMY))
    if not ok or form.username not in USERS:
        raise HTTPException(401, "Invalid Officer ID or password")
    exp = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_MINUTES)
    return {"access_token": jwt.encode({"sub": form.username, "exp": exp}, SECRET, ALGO), "token_type": "bearer"}

def current_user(token: str = Depends(oauth2)) -> str:
    try:
        return jwt.decode(token, SECRET, algorithms=[ALGO])["sub"]
    except jwt.PyJWTError:
        raise HTTPException(401, "Invalid or expired token", headers={"WWW-Authenticate": "Bearer"})

@app.get("/api/auth/me", tags=["auth"])
def me(user: str = Depends(current_user)):
    return {"user": user}

# ---------------------------------------------------------------- models
class Village(BaseModel):
    id: int
    name: str
    population: int = Field(0, ge=0)
    hospital: bool = False
    school: bool = False
    industrial: bool = False
    emergency: bool = False

class Road(BaseModel):
    a: int
    b: int
    cost: float = Field(gt=0)               # Rs lakh
    quality: float = Field(6, ge=1, le=10)
    flood: float = Field(0, ge=0, le=100)   # percent
    maintenance: float = Field(3, ge=0)
    length: float = Field(15, gt=0)         # km

class Scenario(BaseModel):
    villages: list[Village]
    roads: list[Road]
    budget: float = Field(90, ge=0)
    cost_multiplier: float = Field(1, gt=0)
    weather: float = Field(0, ge=0, le=100)  # weather severity %
    min_quality: float = Field(1, ge=1, le=10)

# ---------------------------------------------------------------- Kruskal engine
class DSU:
    """Union-Find with path compression and union by rank."""
    def __init__(self, ids):
        self.p = {i: i for i in ids}
        self.r = {i: 0 for i in ids}
    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x
    def union(self, x, y) -> bool:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.r[rx] < self.r[ry]:
            rx, ry = ry, rx
        self.p[ry] = rx
        self.r[rx] += self.r[ry] == self.r[rx]
        return True

def _score(v: Village) -> float:
    return v.population / 1000 + 5 * v.hospital + 3 * v.school + 3 * v.industrial + 6 * v.emergency

def _path(adj, s, t):
    prev, q = {s: None}, deque([s])
    while q:
        u = q.popleft()
        if u == t:
            break
        for w in adj[u]:
            if w not in prev:
                prev[w] = u
                q.append(w)
    out, c = [], t
    while c is not None:
        out.append(c)
        c = prev.get(c)
    return out[::-1]

def solve(s: Scenario) -> dict:
    t0 = perf_counter()
    V = {v.id: v for v in s.villages}
    for r in s.roads:
        if r.a not in V or r.b not in V or r.a == r.b:
            raise HTTPException(422, f"Road {r.a}-{r.b} references an unknown village or loops on itself")
    # effective cost grows with flood risk when weather is severe
    eff = lambda r: r.cost * s.cost_multiplier * (1 + r.flood / 100 * s.weather / 100 * 0.5)
    ranked = sorted(range(len(s.roads)), key=lambda i: eff(s.roads[i]))
    dsu, adj = DSU(V), {i: [] for i in V}
    selected, rejected = [], []
    for i in ranked:
        r = s.roads[i]
        base = {"index": i, "from": V[r.a].name, "to": V[r.b].name, "cost": r.cost, "effective_cost": round(eff(r), 2)}
        if r.quality < s.min_quality:
            rejected.append({**base, "reason": f"Poor road quality ({r.quality}/10, minimum is {s.min_quality})."})
        elif dsu.union(r.a, r.b):
            adj[r.a].append(r.b); adj[r.b].append(r.a)
            small = min((V[r.a], V[r.b]), key=lambda v: v.population)
            reasons = ["Cheapest remaining road that joins two separate regions", f"Connects {small.name} (pop. {small.population})"]
            if _score(V[r.a]) + _score(V[r.b]) > 12: reasons.append("Serves a high-priority village")
            if r.quality >= 7: reasons.append("Good road quality")
            if r.maintenance <= 2: reasons.append("Low maintenance cost")
            if r.flood > 60: reasons.append("WARNING: high flood risk, consider an alternative")
            selected.append({**base, "reasons": reasons})
        else:
            cyc = " -> ".join(V[x].name for x in _path(adj, r.a, r.b))
            rejected.append({**base, "reason": f"Creates a cycle: {cyc} are already connected."
                             + (" High flood risk." if r.flood > 50 else "")})
    chosen = [s.roads[x["index"]] for x in selected]
    total = sum(x["effective_cost"] for x in selected)
    km = sum(r.length for r in chosen)
    trees = km * 120
    return {
        "selected": selected, "rejected": rejected,
        "connected": len(selected) == len(V) - 1,
        "total_cost": round(total, 2),
        "money_saved": round(sum(r.cost for r in s.roads) - total, 2),
        "budget": {"required": round(total, 2), "remaining": round(max(0, s.budget - total), 2),
                   "shortage": round(max(0, total - s.budget), 2)},
        "risk_score": round(sum(r.flood for r in chosen) / len(chosen), 1) if chosen else 0,
        "environment": {"length_km": km, "trees_removed": round(trees), "co2_tonnes": round(km * 85),
                        "saplings_to_plant": round(trees * 3),
                        "green_score": max(0, round(100 - km / 3 - sum(r.flood > 60 for r in chosen) * 2))},
        "runtime_ms": round((perf_counter() - t0) * 1000, 3),
    }

@app.post("/api/mst", tags=["planning"])
def mst(s: Scenario, user: str = Depends(current_user)):
    """Run Kruskal's algorithm on a scenario and return the plan with explanations."""
    return solve(s)

# ---------------------------------------------------------------- saved projects
_mem: dict = {}
_col = None
if os.getenv("MONGO_URI"):
    from motor.motor_asyncio import AsyncIOMotorClient
    _col = AsyncIOMotorClient(os.environ["MONGO_URI"])[os.getenv("MONGO_DB", "smartroad")].projects

class ProjectIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    scenario: Scenario

@app.post("/api/projects", status_code=201, tags=["projects"])
async def save_project(p: ProjectIn, user: str = Depends(current_user)):
    doc = {"_id": uuid4().hex, "owner": user, "name": p.name, "scenario": p.scenario.model_dump(),
           "saved_at": datetime.now(timezone.utc).isoformat()}
    if _col is not None: await _col.insert_one(doc)
    else: _mem[doc["_id"]] = doc
    return {"id": doc["_id"]}

@app.get("/api/projects", tags=["projects"])
async def list_projects(user: str = Depends(current_user)):
    docs = [d async for d in _col.find({"owner": user}, {"scenario": 0})] if _col is not None \
        else [{k: v for k, v in d.items() if k != "scenario"} for d in _mem.values() if d["owner"] == user]
    return [{"id": d["_id"], "name": d["name"], "saved_at": d["saved_at"]} for d in docs]

async def _get(pid: str, user: str) -> dict:
    d = await _col.find_one({"_id": pid, "owner": user}) if _col is not None else _mem.get(pid)
    if not d or d["owner"] != user:
        raise HTTPException(404, "Project not found")
    return d

@app.get("/api/projects/{pid}", tags=["projects"])
async def load_project(pid: str, user: str = Depends(current_user)):
    d = await _get(pid, user)
    return {"id": pid, "name": d["name"], "scenario": d["scenario"]}

@app.delete("/api/projects/{pid}", status_code=204, tags=["projects"])
async def delete_project(pid: str, user: str = Depends(current_user)):
    await _get(pid, user)
    if _col is not None: await _col.delete_one({"_id": pid})
    else: _mem.pop(pid, None)

@app.get("/api/health", tags=["meta"])
def health():
    return {"status": "ok"}
