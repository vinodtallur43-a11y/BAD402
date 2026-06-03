# ============================================================
# 8-Queens Problem — Backtracking Approach
# Places queens column by column and backtracks on conflict
# ============================================================

# -------------------------------------------------------
# Global Variables
# -------------------------------------------------------
board          = [-1] * 8   # board[col] = row where queen is placed
solution_count = 0           # counts total valid solutions
nodes_explored = 0           # counts total states explored

# -------------------------------------------------------
# Function: is_safe
# Checks if placing a queen at (row, col) is safe
# by examining all previously placed queens
# -------------------------------------------------------
def is_safe(board, row, col):
    for prev_col in range(col):
        prev_row = board[prev_col]

        # Check same row
        if prev_row == row:
            return False

        # Check diagonal conflict
        if abs(prev_row - row) == abs(prev_col - col):
            return False

    return True

# -------------------------------------------------------
# Function: print_board
# Prints the chessboard for the current board state
# -------------------------------------------------------
def print_board(board, solution_number):
    n = len(board)
    print(f"\nSolution #{solution_number}:")
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
    print("Column positions (0-indexed):", board)

# -------------------------------------------------------
# Function: place_queen
# Recursive backtracking function
# Places one queen per column and recurses to the next
# -------------------------------------------------------
def place_queen(board, col, display_count):
    global solution_count, nodes_explored

    # Base case: all 8 queens placed successfully
    if col == len(board):
        solution_count += 1
        if display_count == 0 or solution_count <= display_count:
            print_board(board, solution_count)
        return

    # Try placing a queen in each row of the current column
    for row in range(len(board)):
        nodes_explored += 1

        if is_safe(board, row, col):
            board[col] = row                        # Place queen

            place_queen(board, col + 1, display_count) # Recurse

            board[col] = -1                         # Backtrack

# -------------------------------------------------------
# Function: solve_8queens_backtracking
# Initializes the board and starts the solving process
# -------------------------------------------------------
def solve_8queens_backtracking(n=8, display_count=1):
    global solution_count, nodes_explored

    # Reset globals
    solution_count = 0
    nodes_explored = 0
    board          = [-1] * n

    print("=" * 50)
    print("  8-Queens Problem — Backtracking Approach")
    print("=" * 50)

    place_queen(board, col=0, display_count=display_count)

    # Summary
    print("\n" + "=" * 50)
    print(f"Total nodes explored        : {nodes_explored}")
    print(f"Total valid solutions found : {solution_count}")
    print("=" * 50)

# -------------------------------------------------------
# MAIN
# -------------------------------------------------------
if __name__ == "__main__":
    # Set display_all = True to print all 92 solutions
    display_count = int(input("Enter number of solutions to display (0 for all): "))
    solve_8queens_backtracking(n=8, display_count=display_count)