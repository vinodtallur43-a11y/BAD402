# ============================================================
# 8-Queens Problem — Genetic Algorithm
# Evolves a population of boards toward a valid solution
# ============================================================
import random
# -------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------
BOARD_SIZE      = 8       # Number of queens / board size
POPULATION_SIZE = 100     # Number of individuals in population
MUTATION_RATE   = 0.1     # 10% chance of mutation per child
MAX_GENERATIONS = 1000    # Stop if no solution found by this
MAX_FITNESS     = 28      # 8C2 = 28 non-attacking pairs = solution

# -------------------------------------------------------
# Function: compute_fitness
# Fitness = 28 - number of attacking pairs
# Higher fitness = better board
# Perfect solution = fitness of 28
# -------------------------------------------------------
def compute_fitness(board):
    attacking = 0
    n = len(board)
    for i in range(n):
        for j in range(i + 1, n):
            if board[i] == board[j]:                    # Same row
                attacking += 1
            if abs(board[i] - board[j]) == abs(i - j): # Diagonal
                attacking += 1
    return MAX_FITNESS - attacking

# -------------------------------------------------------
# Function: random_board
# Creates one random board — one queen per column
# -------------------------------------------------------
def random_board():
    return [random.randint(0, BOARD_SIZE - 1)
            for _ in range(BOARD_SIZE)]

# -------------------------------------------------------
# Function: initial_population
# Creates the starting population of random boards
# -------------------------------------------------------
def initial_population():
    return [random_board() for _ in range(POPULATION_SIZE)]

# -------------------------------------------------------
# Function: select_parent
# Fitness-proportionate selection (Roulette Wheel)
# Boards with higher fitness have higher chance of selection
# -------------------------------------------------------
def select_parent(population, fitnesses):
    total_fitness = sum(fitnesses)
    pick          = random.uniform(0, total_fitness)
    running_sum   = 0

    for individual, fitness in zip(population, fitnesses):
        running_sum += fitness
        if running_sum >= pick:
            return individual

    return population[-1]   # Fallback

# -------------------------------------------------------
# Function: crossover
# Single-point crossover between two parents
# Creates one child board
# -------------------------------------------------------
def crossover(parent1, parent2):
    point = random.randint(1, BOARD_SIZE - 1)   # Crossover point
    child = parent1[:point] + parent2[point:]   # Merge parents
    return child

# -------------------------------------------------------
# Function: mutate
# With MUTATION_RATE probability, change one gene randomly
# -------------------------------------------------------
def mutate(board):
    if random.random() < MUTATION_RATE:
        col        = random.randint(0, BOARD_SIZE - 1)  # Pick random column
        board[col] = random.randint(0, BOARD_SIZE - 1)  # Assign random row
    return board

# -------------------------------------------------------
# Function: print_board
# Prints the chessboard for the current board state
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
    print(f"  Chromosome  : {board}")
    print(f"  Fitness     : {compute_fitness(board)} / 28")
    attacking = MAX_FITNESS - compute_fitness(board)
    print(f"  Conflicts   : {attacking}")

# -------------------------------------------------------
# Function: print_generation_summary
# Prints stats for the current generation
# -------------------------------------------------------
def print_generation_summary(gen, fitnesses, best_board):
    best_f = max(fitnesses)
    avg_f  = sum(fitnesses) / len(fitnesses)
    worst_f= min(fitnesses)
    print(f"  Gen {gen:>4} |"
          f" Best Fitness: {best_f:>2}/28 |"
          f" Avg: {avg_f:>5.2f} |"
          f" Worst: {worst_f:>2} |"
          f" Best Board: {best_board}")

# -------------------------------------------------------
# Function: genetic_algorithm
# Main GA loop — evolves population over generations
# -------------------------------------------------------
def genetic_algorithm():
    print("=" * 60)
    print("   8-Queens Problem — Genetic Algorithm")
    print("=" * 60)
    print(f"  Population Size : {POPULATION_SIZE}")
    print(f"  Mutation Rate   : {MUTATION_RATE * 100}%")
    print(f"  Max Generations : {MAX_GENERATIONS}")
    print(f"  Target Fitness  : {MAX_FITNESS}")
    print("=" * 60)

    # Step 1 — Create initial population
    population  = initial_population()
    generation  = 0

    print("\n  EVOLUTION PROGRESS:")
    print("-" * 60)

    while generation < MAX_GENERATIONS:

        # Step 2 — Calculate fitness for each individual
        fitnesses = [compute_fitness(board) for board in population]

        # Step 3 — Find the best board in current generation
        best_fitness = max(fitnesses)
        best_board   = population[fitnesses.index(best_fitness)]

        # Print summary every 50 generations and first 5
        if generation < 5 or generation % 50 == 0:
            print_generation_summary(generation, fitnesses, best_board)

        # Step 4 — Check if solution found
        if best_fitness == MAX_FITNESS:
            print("-" * 60)
            print(f"\n  Solution found at Generation {generation}!")
            print("=" * 60)
            print_board(best_board, label="FINAL SOLUTION:")
            print(f"\n  Total Generations Evolved : {generation}")
            print(f"  Final Fitness             : {best_fitness} / 28")
            print(f"  Attacking Pairs           : 0")
            return True

        # Step 5 — Create new population through selection,
        #           crossover and mutation
        new_population = []

        while len(new_population) < POPULATION_SIZE:

            # Selection — pick two parents
            parent1 = select_parent(population, fitnesses)
            parent2 = select_parent(population, fitnesses)

            # Crossover — produce a child
            child   = crossover(parent1, parent2)

            # Mutation — randomly alter child
            child   = mutate(child)

            new_population.append(child)

        # Step 6 — Replace old population with new generation
        population = new_population
        generation += 1

    # Max generations reached without solution
    print("-" * 60)
    print("\n  No solution found within maximum generations.")
    print(f"  Best fitness reached : {max(fitnesses)} / 28")
    return False

# -------------------------------------------------------
# MAIN
# -------------------------------------------------------
if __name__ == "__main__":
    random.seed(42)
    genetic_algorithm()