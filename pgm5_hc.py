# ============================================================
# 8-Queens Problem — Pure Hill Climbing (No Random Restart)
# Demonstrates the LOCAL MINIMA problem clearly
# ============================================================

# -------------------------------------------------------
# Function: compute_conflicts
# Counts attacking queen pairs — heuristic h(n)
# Goal is h(n) = 0
# -------------------------------------------------------
def compute_conflicts(board):
    conflicts = 0
    n = len(board)
    for i in range(n):
        for j in range(i + 1, n):
            if board[i] == board[j]:                    # Same row
                conflicts += 1
            if abs(board[i] - board[j]) == abs(i - j): # Diagonal
                conflicts += 1
    return conflicts

# -------------------------------------------------------
# Function: print_board
# Prints the chessboard with conflict count
# -------------------------------------------------------
def print_board(board, label=""):
    n = len(board)
    if label:
        print(f"\n{label}")
    print("+" + "---+" * n)
    for row in range(n):
        line = "|"
        for col in range(n):
            if board[col] == row:
                line += " Q |"
            else:
                line += " . |"
        print(line)
        print("+" + "---+" * n)
    print(f"  Board         : {board}")
    print(f"  Conflicts h(n): {compute_conflicts(board)}")

# -------------------------------------------------------
# Function: get_best_neighbour
# Scans all 56 neighbours (move 1 queen in any column)
# Returns the neighbour with the lowest h(n)
# improved = False means no better neighbour found → stuck
# -------------------------------------------------------
def get_best_neighbour(board):
    n              = len(board)
    best_board     = board[:]
    best_conflicts = compute_conflicts(board)
    improved       = False

    for col in range(n):
        for row in range(n):
            if row != board[col]:
                neighbour      = board[:]
                neighbour[col] = row
                c              = compute_conflicts(neighbour)
                if c < best_conflicts:
                    best_conflicts = c
                    best_board     = neighbour[:]
                    improved       = True

    return best_board, best_conflicts, improved

# -------------------------------------------------------
# Function: print_all_neighbours
# Prints every neighbour and its h(n) to prove the
# algorithm is genuinely stuck at a local minimum
# -------------------------------------------------------
def print_all_neighbours(board):
    n         = len(board)
    current_h = compute_conflicts(board)

    print("\n" + "-" * 60)
    print("  Proof: Analysing ALL 56 neighbours of local minimum")
    print("-" * 60)
    print(f"  {'Col':<5} {'New Row':<8} {'Neighbour Board':<32} {'h(n)':<6} {'Better?'}")
    print("-" * 60)

    any_better = False
    for col in range(n):
        for row in range(n):
            if row != board[col]:
                neighbour      = board[:]
                neighbour[col] = row
                h              = compute_conflicts(neighbour)
                better         = "<-- YES" if h < current_h else ""
                if h < current_h:
                    any_better = True
                print(f"  {col:<5} {row:<8} {str(neighbour):<32} {h:<6} {better}")
        print()

    print("-" * 60)
    if not any_better:
        print(f"  RESULT: NO neighbour has h(n) < {current_h}")
        print("  CONCLUSION: Algorithm is stuck. Cannot move forward.")
    print("-" * 60)

# -------------------------------------------------------
# Function: hill_climbing_no_restart
# Pure hill climbing — stops the moment it gets stuck
# -------------------------------------------------------
def hill_climbing_no_restart(initial_board):
    current_board     = initial_board[:]
    current_conflicts = compute_conflicts(current_board)
    iteration         = 0

    print("=" * 60)
    print("   8-Queens Problem - Pure Hill Climbing (No Restart)")
    print("   Objective : Demonstrate the LOCAL MINIMA problem")
    print("=" * 60)

    print_board(current_board, label="INITIAL BOARD STATE:")

    while True:
        print("\n" + "-" * 60)
        print(f"  ITERATION {iteration}")
        print(f"  Current h(n) = {current_conflicts}")
        print(f"  Scanning all 56 neighbours...")
        print("-" * 60)

        best_board, best_conflicts, improved = get_best_neighbour(current_board)

        # Case 1 — Solution found
        if current_conflicts == 0:
            print("\n" + "=" * 60)
            print("  *** SOLUTION FOUND ***")
            print("=" * 60)
            print_board(current_board, label="FINAL SOLUTION:")
            print(f"\n  Solved in {iteration} iteration(s).")
            return True

        # Case 2 — Stuck at local minimum
        if not improved:
            print(f"  Best neighbour h(n) = {current_conflicts}  (no improvement)")
            print(f"  Every neighbour has h(n) >= {current_conflicts}")
            print("\n" + "=" * 60)
            print("  *** STUCK AT LOCAL MINIMUM — ALGORITHM STOPS ***")
            print("=" * 60)
            print_board(current_board, label="LOCAL MINIMUM STATE:")
            print_all_neighbours(current_board)
            print("\n  SUMMARY")
            print(f"  Initial board    : {initial_board}")
            print(f"  Initial h(n)     : {compute_conflicts(initial_board)}")
            print(f"  Final board      : {current_board}")
            print(f"  Final h(n)       : {current_conflicts}  (NOT zero — not a solution)")
            print(f"  Iterations taken : {iteration}")
            print("\n  The algorithm improved h(n) step by step but")
            print("  got trapped where no single queen move helps.")
            print("  Fix: Use Random Restart or Simulated Annealing.")
            return False

        # Case 3 — Move to better neighbour
        print(f"  Best neighbour h(n) = {best_conflicts}  (improvement found!)")
        print(f"  Moving queen from row {current_board} ")
        print(f"                   to  {best_board}")

        current_board     = best_board
        current_conflicts = best_conflicts
        iteration        += 1

        print_board(current_board, label=f"BOARD AFTER ITERATION {iteration}:")

# -------------------------------------------------------
# MAIN
# -------------------------------------------------------
if __name__ == "__main__":

    # This board is verified to get stuck at h=1 after 3 iterations
    board_stuck = [0, 6, 7, 0, 3, 7, 7, 4]

    hill_climbing_no_restart(board_stuck)