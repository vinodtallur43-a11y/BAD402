from collections import deque

# Initial and goal states
initial_state = (3, 3, 'L')   # (Missionaries_left, Cannibals_left, Boat_position)
goal_state = (0, 0, 'R')

# Possible moves (Missionaries, Cannibals)
moves = [
    (1, 0),
    (2, 0),
    (0, 1),
    (0, 2),
    (1, 1)
]

# Check if a state is valid
def is_valid(m, c):
    if m < 0 or c < 0 or m > 3 or c > 3:
        return False
    mr = 3 - m
    cr = 3 - c

    if m > 0 and c > m:
        return False
    if mr > 0 and cr > mr:
        return False
    return True


def get_action(move_m, move_c, boat):
    action = ""
    if move_m > 0:
        action += f"{move_m} Missionary "
    if move_c > 0:
        action += f"{move_c} Cannibal "

    direction = "Left to Right" if boat == 'L' else "Right to Left"
    return action + "moves from " + direction

def bfs():
    queue = deque()
    queue.append((initial_state, []))
    visited = set()

    while queue:
        (m, c, boat), path = queue.popleft()

        if (m, c, boat) == goal_state:
            return path + [(m, c, boat, "Goal Reached")]

        if (m, c, boat) in visited:
            continue

        visited.add((m, c, boat))

        for move_m, move_c in moves:
            if boat == 'L':
                new_m = m - move_m
                new_c = c - move_c
                new_boat = 'R'
            else:
                new_m = m + move_m
                new_c = c + move_c
                new_boat = 'L'

            if is_valid(new_m, new_c):

                action = get_action(move_m, move_c, boat)

                queue.append(((new_m, new_c, new_boat),
                              path + [(m, c, boat, action)]))
    return None

solution = bfs()

print("\nMissionaries and Cannibals Solution using BFS\n")
step = 1
for state in solution:
    m, c, boat, action = state
    print(f"Step {step}:")
    print(f"Action: {action}")
    print(f"Left Bank -> Missionaries: {m}, Cannibals: {c}, Boat: {boat}")
    print("-----------------------------------")
    step += 1