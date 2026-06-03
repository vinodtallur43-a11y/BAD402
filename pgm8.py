"""
First-Order Predicate Logic Resolution Prover
==============================================

A common resolution prover that solves two classic FOPL problems:
  1. The "Humza is a Spy" problem (Chaudhry Aslam's case file)
  2. The "Colonel West is a Criminal" problem (Russell & Norvig)

The prover implements:
  - Term representation (variables, constants, compound terms)
  - Robinson's unification algorithm
  - Resolution rule with most-general-unifier (MGU)
  - Refutation-based proof search (negate goal, derive empty clause)
"""

from itertools import count
from typing import Optional


# ---------------------------------------------------------------------------
# Term representation
# ---------------------------------------------------------------------------
#
# We represent terms uniformly as tuples:
#   ("var",   name)              -> a variable (e.g. x, y, z)
#   ("const", name)              -> a constant (e.g. Humza, West, M1)
# A literal is represented as:
#   (negated_bool, predicate_name, (arg1, arg2, ...))
# A clause is represented as a frozenset of literals (disjunction).
# ---------------------------------------------------------------------------

# For simplicity, we only have variables and constants (no compound terms like f(x)).
def var(name):
    return ("var", name)

# Constants are just atoms with no arguments. We can auto-promote strings to
# either var or const based on capitalization (lowercase = var, else const).
def const(name):
    return ("const", name)

# Helper to check if a term is a variable.
def is_var(t):
    return isinstance(t, tuple) and t[0] == "var"

# Explanation of literals: a literal is a predicate applied to some terms, with an optional negation. For example:
def lit(negated, name, *args):
    """Build a literal. Strings are auto-promoted: lowercase = var, else const."""
    promoted = tuple(
        a if isinstance(a, tuple) else (var(a) if a[0].islower() else const(a))
        for a in args
    )
    return (negated, name, promoted)

# Negation of a literal just flips the negated flag.
def neg(literal):
    """Return the negation of a literal."""
    negated, name, args = literal
    return (not negated, name, args)

# ---------------------------------------------------------------------------
# Pretty printing
# ---------------------------------------------------------------------------
def term_str(t):
    return t[1]

def lit_str(l):
    negated, name, args = l
    prefix = "¬" if negated else ""
    return f"{prefix}{name}({', '.join(term_str(a) for a in args)})"

def clause_str(c):
    if not c:
        return "∅"
    return " ∨ ".join(lit_str(l) for l in c)


# ---------------------------------------------------------------------------
# Unification (Robinson's algorithm)
# ---------------------------------------------------------------------------
#
# Returns a substitution (dict from var-name -> term) that makes two terms
# equal, or None if no unifier exists. Includes the occurs check to prevent
# infinite terms like x = f(x).
# ---------------------------------------------------------------------------

def occurs(var_name, term, subst):
    """Occurs check: does var_name appear in term (after substitution)?"""
    term = walk(term, subst)
    if is_var(term):
        return term[1] == var_name
    return False


def walk(term, subst):
    """Follow substitution chain to the canonical form of a term."""
    while is_var(term) and term[1] in subst:
        term = subst[term[1]]
    return term


def unify(t1, t2, subst=None):
    """Unify two terms. Returns a substitution dict or None."""
    if subst is None:
        subst = {}
    t1 = walk(t1, subst)
    t2 = walk(t2, subst)

    if t1 == t2:
        return subst
    if is_var(t1):
        if occurs(t1[1], t2, subst):
            return None
        return {**subst, t1[1]: t2}
    if is_var(t2):
        if occurs(t2[1], t1, subst):
            return None
        return {**subst, t2[1]: t1}
    # Both are constants (or compound terms — not used here)
    return None


def unify_literals(l1, l2):
    """Unify two literals if they have the same predicate and arity."""
    neg1, name1, args1 = l1
    neg2, name2, args2 = l2
    if name1 != name2 or len(args1) != len(args2):
        return None
    subst = {}
    for a, b in zip(args1, args2):
        subst = unify(a, b, subst)
        if subst is None:
            return None
    return subst


# ---------------------------------------------------------------------------
# Applying substitutions
# ---------------------------------------------------------------------------

def apply_subst_term(t, subst):
    t = walk(t, subst)
    return t


def apply_subst_literal(l, subst):
    negated, name, args = l
    return (negated, name, tuple(apply_subst_term(a, subst) for a in args))


def apply_subst_clause(clause, subst):
    return frozenset(apply_subst_literal(l, subst) for l in clause)


# ---------------------------------------------------------------------------
# Variable renaming (standardize apart)
# ---------------------------------------------------------------------------
#
# Before resolving two clauses, we must rename their variables apart so they
# don't accidentally clash. Each clause gets fresh variable names.
# ---------------------------------------------------------------------------

_rename_counter = count(0)


def rename_clause(clause):
    """Rename all variables in a clause to fresh unique names."""
    mapping = {}
    new_lits = []
    for negated, name, args in clause:
        new_args = []
        for a in args:
            if is_var(a):
                if a[1] not in mapping:
                    mapping[a[1]] = var(f"{a[1]}_{next(_rename_counter)}")
                new_args.append(mapping[a[1]])
            else:
                new_args.append(a)
        new_lits.append((negated, name, tuple(new_args)))
    return frozenset(new_lits)


# ---------------------------------------------------------------------------
# Resolution rule
# ---------------------------------------------------------------------------

def resolve(c1, c2):
    """
    Apply binary resolution to two clauses. Returns a list of resolvent
    clauses (one per pair of complementary literals that unify).
    """
    c1 = rename_clause(c1)
    c2 = rename_clause(c2)
    resolvents = []
    for l1 in c1:
        for l2 in c2:
            # We need l1 and the negation of l2 to unify
            if l1[0] == l2[0]:
                continue  # Same polarity — can't resolve
            if l1[1] != l2[1]:
                continue  # Different predicates
            subst = unify_literals(l1, neg(l2))
            if subst is None:
                continue
            # Build resolvent: union of both clauses minus the resolved pair,
            # with the substitution applied.
            new_clause = (c1 - {l1}) | (c2 - {l2})
            new_clause = apply_subst_clause(new_clause, subst)
            resolvents.append(new_clause)
    return resolvents


# ---------------------------------------------------------------------------
# Resolution prover (refutation-based proof search)
# ---------------------------------------------------------------------------

def prove(kb_clauses, goal_literal, max_iterations=200, verbose=True):
    """
    Try to prove `goal_literal` from `kb_clauses` using resolution refutation.
    Returns True if a proof was found, False otherwise.
    """
    # Step 1: Negate the goal and add to clause set.
    negated_goal = frozenset([neg(goal_literal)])

    clauses = set(frozenset(c) for c in kb_clauses)
    clauses.add(negated_goal)

    if verbose:
        print(f"\n  Negated goal added: {clause_str(negated_goal)}")
        print(f"  Starting with {len(clauses)} clauses.\n")

    # Step 2: Iteratively apply resolution. Track the parents of each new
    # clause so we can print the proof trace.
    parents = {}  # clause -> (parent1, parent2)
    new_clauses_log = []

    for iteration in range(max_iterations):
        clause_list = list(clauses)
        new_resolvents = set()

        for i in range(len(clause_list)):
            for j in range(i + 1, len(clause_list)):
                resolvents = resolve(clause_list[i], clause_list[j])
                for r in resolvents:
                    # Skip tautologies (e.g. P ∨ ¬P)
                    if is_tautology(r):
                        continue
                    if r not in clauses and r not in new_resolvents:
                        new_resolvents.add(r)
                        parents[r] = (clause_list[i], clause_list[j])
                        new_clauses_log.append(r)
                        # Empty clause found -> contradiction!
                        if len(r) == 0:
                            if verbose:
                                print_proof(parents, r, kb_clauses, negated_goal)
                            return True

        if not new_resolvents:
            if verbose:
                print("  No new clauses can be derived. Proof failed.")
            return False
        clauses.update(new_resolvents)

    if verbose:
        print(f"  Reached iteration limit ({max_iterations}). Proof failed.")
    return False


def is_tautology(clause):
    """A clause is a tautology if it contains both P and ¬P."""
    seen = {}
    for negated, name, args in clause:
        key = (name, args)
        if key in seen and seen[key] != negated:
            return True
        seen[key] = negated
    return False


def print_proof(parents, empty_clause, original_kb, negated_goal):
    """Walk back from the empty clause and print every step that led to it."""
    # Collect every clause used in the derivation chain.
    used = []
    stack = [empty_clause]
    visited = set()
    while stack:
        c = stack.pop()
        if c in visited:
            continue
        visited.add(c)
        used.append(c)
        if c in parents:
            p1, p2 = parents[c]
            stack.append(p1)
            stack.append(p2)

    # Build a numbering: KB clauses first, then derived clauses in order of derivation.
    numbering = {}
    counter = 1
    for c in original_kb:
        numbering[frozenset(c)] = f"C{counter}"
        counter += 1
    numbering[negated_goal] = f"C{counter}"
    counter += 1

    # Number the derived clauses in the order they were created.
    derived_in_order = [c for c in used if c not in numbering]
    # Sort derived clauses by their depth from the KB (rough topological order)
    derived_in_order = sorted(
        derived_in_order, key=lambda c: derivation_depth(c, parents)
    )
    for c in derived_in_order:
        numbering[c] = f"C{counter}"
        counter += 1

    print("  Proof (resolution steps that led to the empty clause):")
    print("  " + "-" * 70)
    for c in derived_in_order:
        p1, p2 = parents[c]
        p1_id = numbering.get(p1, "?")
        p2_id = numbering.get(p2, "?")
        c_id = numbering[c]
        print(f"  {c_id} = resolve({p1_id}, {p2_id}) = {clause_str(c)}")
    print("  " + "-" * 70)
    print("  ∅ derived → contradiction reached → goal is PROVED.\n")


def derivation_depth(clause, parents, _cache=None):
    if _cache is None:
        _cache = {}
    if clause in _cache:
        return _cache[clause]
    if clause not in parents:
        _cache[clause] = 0
        return 0
    p1, p2 = parents[clause]
    d = 1 + max(derivation_depth(p1, parents, _cache), derivation_depth(p2, parents, _cache))
    _cache[clause] = d
    return d


# ===========================================================================
# Problem 1: Is Humza a Spy?
# ===========================================================================

def humza_problem():
    print("=" * 72)
    print("  PROBLEM 1: Is Humza a Spy?")
    print("  (Chaudhry Aslam's case file in Lyari Town)")
    print("=" * 72)

    # Predicates use uppercase for the first letter of constants and lowercase
    # for variables, so the auto-promotion in lit() does the right thing.

    # C1: ∀x∀y (Meets(x,y) ∧ Gangster(y) ∧ OperatesIn(x,Lyari) → Infiltrated(x,y))
    #     ≡ ¬Meets(x,y) ∨ ¬Gangster(y) ∨ ¬OperatesIn(x,Lyari) ∨ Infiltrated(x,y)
    c1 = frozenset([
        lit(True,  "Meets",       "x", "y"),
        lit(True,  "Gangster",    "y"),
        lit(True,  "OperatesIn",  "x", "Lyari"),
        lit(False, "Infiltrated", "x", "y"),
    ])

    # C2: ∀x∀y (Infiltrated(x,y) ∧ CommWith(x,RAW) → Spy(x))
    #     ≡ ¬Infiltrated(x,y) ∨ ¬CommWith(x,RAW) ∨ Spy(x)
    c2 = frozenset([
        lit(True,  "Infiltrated", "x", "y"),
        lit(True,  "CommWith",    "x", "RAW"),
        lit(False, "Spy",         "x"),
    ])

    # Facts
    c3 = frozenset([lit(False, "Meets",      "Humza", "Rehman")])
    c4 = frozenset([lit(False, "Gangster",   "Rehman")])
    c5 = frozenset([lit(False, "OperatesIn", "Humza", "Lyari")])
    c6 = frozenset([lit(False, "CommWith",   "Humza", "RAW")])

    kb = [c1, c2, c3, c4, c5, c6]
    print("\n  Knowledge base:")
    for i, c in enumerate(kb, 1):
        print(f"    C{i}: {clause_str(c)}")

    goal = lit(False, "Spy", "Humza")
    print(f"\n  Goal: {lit_str(goal)}")

    result = prove(kb, goal)
    print(f"  RESULT: Spy(Humza) = {result}")


# ===========================================================================
# Problem 2: Is Colonel West a Criminal?
# ===========================================================================

def west_problem():
    print("\n" + "=" * 72)
    print("  PROBLEM 2: Is Colonel West a Criminal?")
    print("  (Russell & Norvig — Artificial Intelligence: A Modern Approach)")
    print("=" * 72)

    # C1: ∀x∀y∀z (American(x) ∧ Weapon(y) ∧ Sells(x,y,z) ∧ Hostile(z) → Criminal(x))
    c1 = frozenset([
        lit(True,  "American", "x"),
        lit(True,  "Weapon",   "y"),
        lit(True,  "Sells",    "x", "y", "z"),
        lit(True,  "Hostile",  "z"),
        lit(False, "Criminal", "x"),
    ])

    # C2, C3: ∃x (Owns(Nono,x) ∧ Missile(x))  -- Skolemized with M1
    c2 = frozenset([lit(False, "Owns",    "Nono", "M1")])
    c3 = frozenset([lit(False, "Missile", "M1")])

    # C4: ∀x (Missile(x) ∧ Owns(Nono,x) → Sells(West,x,Nono))
    c4 = frozenset([
        lit(True,  "Missile", "x"),
        lit(True,  "Owns",    "Nono", "x"),
        lit(False, "Sells",   "West", "x", "Nono"),
    ])

    # C5: ∀x (Missile(x) → Weapon(x))
    c5 = frozenset([
        lit(True,  "Missile", "x"),
        lit(False, "Weapon",  "x"),
    ])

    # C6: ∀x (Enemy(x,America) → Hostile(x))
    c6 = frozenset([
        lit(True,  "Enemy",   "x", "America"),
        lit(False, "Hostile", "x"),
    ])

    # C7, C8: ground facts
    c7 = frozenset([lit(False, "American", "West")])
    c8 = frozenset([lit(False, "Enemy",    "Nono", "America")])

    kb = [c1, c2, c3, c4, c5, c6, c7, c8]
    print("\n  Knowledge base:")
    for i, c in enumerate(kb, 1):
        print(f"    C{i}: {clause_str(c)}")

    goal = lit(False, "Criminal", "West")
    print(f"\n  Goal: {lit_str(goal)}")

    result = prove(kb, goal)
    print(f"  RESULT: Criminal(West) = {result}")


if __name__ == "__main__":
    humza_problem()
    west_problem()
