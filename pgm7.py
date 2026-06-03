"""
Wumpus World - Full Agent
=========================
The agent enters at (1,1), explores the cave, uses forward/backward
chaining to identify safe cells, grabs the gold, and climbs out.

Percept = (Stench, Breeze, Glitter, Bump, Scream)
Actions = Forward | TurnLeft | TurnRight | Grab | Shoot | Climb
Score   = +1000 (gold + climb out)
          -1000 (death by pit/wumpus)
          -1    (each action)
          -10   (using the arrow)
"""

import random
from collections import defaultdict, deque, namedtuple

Percept = namedtuple("Percept", ["stench", "breeze", "glitter", "bump", "scream"])

GRID_SIZE = 4
DIRECTIONS = ["E", "N", "W", "S"]   # rotation order: TurnLeft moves forward in this list
DELTAS = {"E": (1, 0), "N": (0, 1), "W": (-1, 0), "S": (0, -1)}


# ============================================================
# Knowledge Base + Inference
# ============================================================

class Clause:
    def __init__(self, premises, conclusion):
        self.premises = set(premises)
        self.conclusion = conclusion


class KnowledgeBase:
    def __init__(self):
        self.clauses = []
        self.facts = set()

    def tell_fact(self, s):
        if s not in self.facts:
            self.facts.add(s)
            self.clauses.append(Clause([], s))

    def tell_rule(self, premises, conclusion):
        self.clauses.append(Clause(premises, conclusion))


def forward_chaining(kb, query):
    """Returns True iff `query` is entailed."""
    count = {i: len(c.premises) for i, c in enumerate(kb.clauses)}
    inferred = defaultdict(bool)
    agenda = [c.conclusion for c in kb.clauses if not c.premises]
    while agenda:
        p = agenda.pop(0)
        if inferred[p]:
            continue
        inferred[p] = True
        if p == query:
            return True
        for i, c in enumerate(kb.clauses):
            if p in c.premises:
                count[i] -= 1
                if count[i] == 0 and not inferred[c.conclusion]:
                    agenda.append(c.conclusion)
    return False


def backward_chaining(kb, query, visited=None):
    """Returns True iff `query` is entailed (goal-driven)."""
    if visited is None:
        visited = set()
    if query in kb.facts:
        return True
    if query in visited:
        return False
    visited = visited | {query}
    for c in kb.clauses:
        if c.conclusion == query and c.premises:
            if all(backward_chaining(kb, p, visited) for p in c.premises):
                return True
    return False


# ============================================================
# Grid helpers
# ============================================================

def in_bounds(x, y):
    return 1 <= x <= GRID_SIZE and 1 <= y <= GRID_SIZE


def adjacent(x, y):
    return [(x + dx, y + dy) for dx, dy in DELTAS.values() if in_bounds(x + dx, y + dy)]


# ============================================================
# Percept -> KB translation
# ============================================================

def add_percept(kb, x, y, p):
    kb.tell_fact(f"Visited_{x}_{y}")
    kb.tell_fact(f"NoPit_{x}_{y}")
    kb.tell_fact(f"NoWumpus_{x}_{y}")

    if p.stench:
        kb.tell_fact(f"Stench_{x}_{y}")
    else:
        kb.tell_fact(f"NoStench_{x}_{y}")
        for (nx, ny) in adjacent(x, y):
            kb.tell_rule([f"NoStench_{x}_{y}"], f"NoWumpus_{nx}_{ny}")

    if p.breeze:
        kb.tell_fact(f"Breeze_{x}_{y}")
    else:
        kb.tell_fact(f"NoBreeze_{x}_{y}")
        for (nx, ny) in adjacent(x, y):
            kb.tell_rule([f"NoBreeze_{x}_{y}"], f"NoPit_{nx}_{ny}")

    if p.glitter:
        kb.tell_fact(f"Glitter_{x}_{y}")
        kb.tell_fact(f"Gold_{x}_{y}")

    if p.scream:
        kb.tell_fact("WumpusDead")
        for i in range(1, GRID_SIZE + 1):
            for j in range(1, GRID_SIZE + 1):
                kb.tell_rule(["WumpusDead"], f"NoWumpus_{i}_{j}")


def add_safety_rules(kb):
    for x in range(1, GRID_SIZE + 1):
        for y in range(1, GRID_SIZE + 1):
            kb.tell_rule([f"NoPit_{x}_{y}", f"NoWumpus_{x}_{y}"], f"Safe_{x}_{y}")


# ============================================================
# The cave (the "real" world the agent doesn't see)
# ============================================================

class Cave:
    def __init__(self, pits, wumpus, gold, size=GRID_SIZE):
        self.size = size
        self.pits = set(pits)
        self.wumpus = wumpus
        self.wumpus_alive = True
        self.gold = gold
        self.gold_taken = False
        self.scream_pending = False

    def percept_at(self, x, y):
        stench = (self.wumpus_alive and
                  (x, y) != self.wumpus and
                  self.wumpus in adjacent(x, y))
        breeze = any(p in adjacent(x, y) for p in self.pits)
        glitter = (not self.gold_taken) and (x, y) == self.gold
        scream = self.scream_pending
        self.scream_pending = False
        return Percept(stench, breeze, glitter, False, scream)

    def is_deadly(self, x, y):
        if (x, y) in self.pits:
            return "pit"
        if self.wumpus_alive and (x, y) == self.wumpus:
            return "wumpus"
        return None


# ============================================================
# The Agent
# ============================================================

class Agent:
    def __init__(self, cave):
        self.cave = cave
        self.x, self.y = 1, 1
        self.facing = "E"
        self.has_gold = False
        self.has_arrow = True
        self.alive = True
        self.escaped = False
        self.score = 0
        self.kb = KnowledgeBase()
        add_safety_rules(self.kb)
        self.action_log = []
        self.visited = set()

    # --- helpers ---
    def turn_left(self):
        self.facing = DIRECTIONS[(DIRECTIONS.index(self.facing) + 1) % 4]
        self._cost(1)
        self.action_log.append(f"TurnLeft  -> facing {self.facing}")

    def turn_right(self):
        self.facing = DIRECTIONS[(DIRECTIONS.index(self.facing) - 1) % 4]
        self._cost(1)
        self.action_log.append(f"TurnRight -> facing {self.facing}")

    def _cost(self, n):
        self.score -= n

    def front_cell(self):
        dx, dy = DELTAS[self.facing]
        return (self.x + dx, self.y + dy)

    def perceive(self):
        return self.cave.percept_at(self.x, self.y)

    def update_kb(self, p):
        add_percept(self.kb, self.x, self.y, p)

    def is_proven_safe(self, x, y):
        return forward_chaining(self.kb, f"Safe_{x}_{y}")

    # --- actions ---
    def move_forward(self):
        nx, ny = self.front_cell()
        if not in_bounds(nx, ny):
            self.action_log.append(f"Forward -> BUMP at wall")
            self._cost(1)
            return  # bump (we don't add it to percept here for brevity)
        self.x, self.y = nx, ny
        self._cost(1)
        self.action_log.append(f"Forward  -> ({self.x},{self.y})")
        cause = self.cave.is_deadly(self.x, self.y)
        if cause:
            self.alive = False
            self._cost(1000)
            self.action_log.append(f"*** Killed by {cause} at ({self.x},{self.y}) ***")

    def grab(self):
        self._cost(1)
        if (self.x, self.y) == self.cave.gold and not self.cave.gold_taken:
            self.cave.gold_taken = True
            self.has_gold = True
            self.action_log.append(f"Grab     -> got the GOLD at ({self.x},{self.y})")
        else:
            self.action_log.append(f"Grab     -> nothing here")

    def shoot(self):
        if not self.has_arrow:
            return
        self.has_arrow = False
        self._cost(10)
        # Arrow flies in the facing direction; check if wumpus in that line
        dx, dy = DELTAS[self.facing]
        cx, cy = self.x, self.y
        hit = False
        while True:
            cx, cy = cx + dx, cy + dy
            if not in_bounds(cx, cy):
                break
            if self.cave.wumpus_alive and (cx, cy) == self.cave.wumpus:
                hit = True
                self.cave.wumpus_alive = False
                self.cave.scream_pending = True
                break
        self.action_log.append(f"Shoot    -> {'HIT (Scream)' if hit else 'miss'}")

    def climb(self):
        self._cost(1)
        if (self.x, self.y) == (1, 1):
            self.escaped = True
            if self.has_gold:
                self._cost(-1000)  # bonus for escaping with gold
            self.action_log.append(f"Climb    -> ESCAPED with{'out' if not self.has_gold else ''} gold")

    # --- planning ---
    def turn_to_face(self, target_dir):
        """Turn the cheapest way to face `target_dir`."""
        while self.facing != target_dir:
            cur = DIRECTIONS.index(self.facing)
            tgt = DIRECTIONS.index(target_dir)
            # rotate the short way (left or right)
            if (tgt - cur) % 4 == 1:
                self.turn_left()
            else:
                self.turn_right()

    def plan_path(self, goal):
        """BFS through proven-safe cells from (x,y) to goal. Returns list of cells."""
        start = (self.x, self.y)
        if start == goal:
            return [start]
        q = deque([(start, [start])])
        seen = {start}
        while q:
            (cx, cy), path = q.popleft()
            for (nx, ny) in adjacent(cx, cy):
                if (nx, ny) in seen:
                    continue
                # allow moving to goal even if not proven safe (we already chose it)
                if (nx, ny) == goal or self.is_proven_safe(nx, ny):
                    new_path = path + [(nx, ny)]
                    if (nx, ny) == goal:
                        return new_path
                    seen.add((nx, ny))
                    q.append(((nx, ny), new_path))
        return None

    def follow_path(self, path):
        """Walk the agent through the given list of cells."""
        for (nx, ny) in path[1:]:
            if not self.alive:
                return
            dx, dy = nx - self.x, ny - self.y
            for d, (ddx, ddy) in DELTAS.items():
                if (ddx, ddy) == (dx, dy):
                    self.turn_to_face(d)
                    break
            self.move_forward()
            if self.alive:
                p = self.perceive()
                self.update_kb(p)
                self.visited.add((self.x, self.y))
                if p.glitter and not self.has_gold:
                    self.grab()

    def choose_next_target(self):
        """Pick the closest proven-safe, unvisited cell."""
        candidates = []
        for x in range(1, GRID_SIZE + 1):
            for y in range(1, GRID_SIZE + 1):
                if (x, y) in self.visited:
                    continue
                if self.is_proven_safe(x, y):
                    # must be reachable through proven-safe cells
                    path = self.plan_path((x, y))
                    if path:
                        candidates.append((len(path), (x, y)))
        if not candidates:
            return None
        candidates.sort()
        return candidates[0][1]

    # --- main loop ---
    def run(self):
        # Initial percept at (1,1)
        p = self.perceive()
        self.update_kb(p)
        self.visited.add((1, 1))
        self.action_log.append(f"Start at (1,1), percept={p}")
        if p.glitter:
            self.grab()

        while self.alive and not self.escaped:
            # If we have the gold, head home and climb out
            if self.has_gold:
                if (self.x, self.y) == (1, 1):
                    self.climb()
                    break
                path = self.plan_path((1, 1))
                if path is None:
                    self.action_log.append("No safe path home — giving up.")
                    break
                self.follow_path(path)
                continue

            target = self.choose_next_target()
            if target is None:
                self.action_log.append("No more safe unvisited cells; heading home.")
                if (self.x, self.y) != (1, 1):
                    path = self.plan_path((1, 1))
                    if path:
                        self.follow_path(path)
                self.climb()
                break

            path = self.plan_path(target)
            if path is None:
                self.action_log.append(f"Can't reach {target} safely.")
                break
            self.follow_path(path)


# ============================================================
# Demo
# ============================================================

def render_cave(cave, agent=None):
    print("True cave layout (top row = y=4):")
    for y in range(GRID_SIZE, 0, -1):
        row = []
        for x in range(1, GRID_SIZE + 1):
            cell = []
            if (x, y) in cave.pits:
                cell.append("P")
            if (x, y) == cave.wumpus:
                cell.append("W" if cave.wumpus_alive else "w")
            if (x, y) == cave.gold and not cave.gold_taken:
                cell.append("G")
            if agent and (x, y) == (agent.x, agent.y):
                cell.append("A")
            row.append(f"{''.join(cell) or '.':^4}")
        print(" | ".join(row))
    print()


def main():
    random.seed(42)

    # A solvable layout
    cave = Cave(
        pits={(3, 1), (3, 3), (4, 4)},
        wumpus=(1, 3),
        gold=(2, 3),
    )

    print("=" * 60)
    print("WUMPUS WORLD - FULL AGENT JOURNEY")
    print("=" * 60)
    render_cave(cave)
    print("Legend: P=Pit, W=Wumpus, G=Gold, A=Agent, .=empty\n")

    agent = Agent(cave)
    agent.run()

    print("Action log:")
    print("-" * 60)
    for i, line in enumerate(agent.action_log, 1):
        print(f"{i:3d}. {line}")

    print("-" * 60)
    print(f"Final position: ({agent.x},{agent.y})")
    print(f"Has gold:       {agent.has_gold}")
    print(f"Escaped:        {agent.escaped}")
    print(f"Alive:          {agent.alive}")
    print(f"Final score:    {agent.score}")
    print(f"Cells visited:  {sorted(agent.visited)}")


if __name__ == "__main__":
    main()
