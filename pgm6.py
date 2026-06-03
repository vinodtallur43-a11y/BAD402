import random
import math

# -----------------------------
# Distance between two cities
# -----------------------------
def distance(city1, city2):
    return math.sqrt((city1[0] - city2[0])**2 +
                     (city1[1] - city2[1])**2)


# -----------------------------
# Total tour distance
# -----------------------------
def total_distance(route, cities):
    dist = 0

    for i in range(len(route)):
        city1 = cities[route[i]]
        city2 = cities[route[(i + 1) % len(route)]]  # return to start
        dist += distance(city1, city2)

    return dist


# -----------------------------
# Create neighboring solution
# -----------------------------
def generate_neighbor(route):
    new_route = route[:]

    # swap two random cities
    i = random.randint(0, len(route) - 1)
    j = random.randint(0, len(route) - 1)

    new_route[i], new_route[j] = new_route[j], new_route[i]

    return new_route


# -----------------------------
# Simulated Annealing Algorithm
# -----------------------------
def simulated_annealing(cities,
                        initial_temp=10000,
                        cooling_rate=0.995,
                        min_temp=1):

    n = len(cities)

    # random initial route
    current_route = list(range(n))
    random.shuffle(current_route)

    current_cost = total_distance(current_route, cities)

    best_route = current_route[:]
    best_cost = current_cost

    temperature = initial_temp

    iteration = 0

    while temperature > min_temp:

        # generate nearby solution
        new_route = generate_neighbor(current_route)
        new_cost = total_distance(new_route, cities)

        diff = new_cost - current_cost

        accepted = False

        # accept better solution
        if diff < 0:
            current_route = new_route
            current_cost = new_cost
            accepted = True

        # accept worse solution with probability
        else:
            probability = math.exp(-diff / temperature)

            if random.random() < probability:
                current_route = new_route
                current_cost = new_cost
                accepted = True
            else:
                accepted = False

        # update best solution
        if current_cost < best_cost:
            best_route = current_route[:]
            best_cost = current_cost


        # PRINT ITERATION DETAILS
        print("Iteration:", iteration)
        print("Temperature:", round(temperature, 2))
        print("Route:", current_route)
        print("Cost:", round(current_cost, 2))
        print("Accepted:", accepted)
        print("Best Cost:", round(best_cost, 2))
        print("-" * 50)

        # cool down
        temperature *= cooling_rate
        iteration += 1

    return best_route, best_cost


# -----------------------------
# Main Program
# -----------------------------
if __name__ == "__main__":

    # Example cities (x, y)
    '''
    cities = [
        (0, 0),
        (1, 5),
        (5, 2),
        (6, 6),
        (8, 3),
        (2, 7)
    ]
    '''
    cities = [
    (1, 1),   # 0
    (3, 4),   # 1
    (6, 1),   # 2
    (7, 5),   # 3
    (9, 2),   # 4
    (5, 8),   # 5
    (2, 7)    # 6
]
    best_route, best_cost = simulated_annealing(cities)

    print("Best Route:", best_route)
    print("Minimum Distance:", round(best_cost, 2))