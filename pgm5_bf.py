# ============================================================
# 8-Queens Problem — Brute Force Approach
# Generates all permutations and checks each for validity
# ============================================================

from itertools import permutations
# -------------------------------------------------------
# Function: is_valid
# Checks whether a given permutation is a valid solution
# -------------------------------------------------------
def is_valid(arrangement):
    n = len(arrangement)
    for i in range(n):
        for j in range(i + 1, n):
            # Check diagonal conflict
            # Row conflict is already avoided by using permutations
            if abs(arrangement[i] - arrangement[j]) == abs(i - j):
                return False
    return True

# -------------------------------------------------------
# Function: print_board
# Prints the chessboard for a given arrangement
# -------------------------------------------------------
def print_board(arrangement):
    n = len(arrangement)
    print("\n+" + "---+" * n)
    for row in range(n):
        line = "|"
        for col in range(n):
            if arrangement[col] == row:
                line += " Q |"
            else:
                line += " . |"
        print(line)
        print("+" + "---+" * n)
    print("Column positions (0-indexed):", list(arrangement))

# -------------------------------------------------------
# Function: brute_force_8queens
# Main function to solve 8-Queens using brute force
# -------------------------------------------------------
def brute_force_8queens(n=8, display_all=1):
    solution_count  = 0
    total_checked   = 0
    first_solution  = None
    solutions_displayed = 0

    print("=" * 50)
    print("   8-Queens Problem — Brute Force Approach")
    print("=" * 50)
    print(f"Generating all {n}! = {__import__('math').factorial(n)} permutations...\n")

    # Generate all permutations of rows [0, 1, ..., n-1]
    for arrangement in permutations(range(n)):
        total_checked += 1

        if is_valid(arrangement):
            solution_count += 1

            # Store the first solution found
            if solution_count == 1:
                first_solution = arrangement

            if display_all == 0 or solutions_displayed < display_all:
                print(f"Solution #{solution_count}:")
                print_board(arrangement)
                solutions_displayed += 1

    # Display summary
    print("\n" + "=" * 50)
    print(f"Total permutations checked : {total_checked}")
    print(f"Total valid solutions found : {solution_count}")
    print("=" * 50)

# -------------------------------------------------------
# MAIN
# -------------------------------------------------------
if __name__ == "__main__":
    # Set display_all=True to print all 92 solutions
    # display_all should allow me to enter number of solutions to display, or all if I enter 0
    display_all = int(input("Enter number of solutions to display (0 for all): "))
    brute_force_8queens(n=8, display_all=display_all)