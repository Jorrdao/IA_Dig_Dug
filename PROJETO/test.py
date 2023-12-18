from consts import Direction
import math, random

def agent_possible_moves(state, chave='j'):
    if 'digdug' not in state:
        return ''

    digdug_pos = state['digdug']
    x, y = digdug_pos

    dicio = {
        'w': [x, y - 1] if y > 0 else [x, y],
        's': [x, y + 1] if y < 23 else [x, y],
        'a': [x - 1, y] if x > 0 else [x, y],
        'd': [x + 1, y] if x < 47 else [x, y],
        ' ': [x, y]
    }

    return dicio[chave] if chave in 'wsad ' else dicio

def all_enemies_current_and_possible_next_positions(state):
    zone = []

    def process_enemy(enemy):
        enemy_name = enemy["name"]
        enemy_id = enemy["id"]
        enemy_pos = enemy["pos"]
        enemy_danger_zones = enemy_current_and_possible_next_positions(enemy_pos)

       
        return (enemy_name + enemy_id, enemy_danger_zones)

    dicio = {
        key: value
        for enemy in state.get('enemies', [])
        if math.dist(state['digdug'], enemy['pos']) <= 5
        for key, value in [process_enemy(enemy)]
    }

    dicio.update({
        rock["id"]: [rock["pos"], [rock["pos"][0], rock["pos"][1] + 1]]
        for rock in state.get('rocks', [])
    })

    zone = [pos for values in dicio.values() for pos in values]

    return zone

def enemy_current_and_possible_next_positions(enemy_pos):
    x, y = enemy_pos
    directions = {'0': [x, y], '1': [x - 1, y], '2': [x + 1, y], '3': [x, y - 1], '4': [x, y + 1]}

    zone = list(directions.values())
    return zone



def agent_shooting_conditions(state, digdug_pos, digdug_dir, closest_enemy_pos, closest_enemy_name):
    x, y = digdug_pos
    shooting_ranges = {
        Direction.WEST: [[x - i, y] for i in range(1, 4)],
        Direction.EAST: [[x + i, y] for i in range(1, 4)],
        Direction.NORTH: [[x, y - i] for i in range(1, 4)],
        Direction.SOUTH: [[x, y + i] for i in range(1, 4)],
    }

    close_enemy_pos = [closest_enemy_pos]
    close_enemy_fygar = [closest_enemy_name] if closest_enemy_name == 'Fygar' else []

    if 'enemies' in state:
        for entry in state["enemies"]:
            distance = math.floor(math.dist(digdug_pos, entry["pos"]))
            if distance <= 4:
                close_enemy_pos.append(entry["pos"])
                if entry['name'] == 'Fygar':
                    close_enemy_fygar.append(entry['pos'])

    for potential_target in shooting_ranges.get(digdug_dir, []):
        if potential_target in close_enemy_pos:
            return 'A', digdug_dir

    
    if digdug_pos[0] != closest_enemy_pos[0] or digdug_pos[1] != closest_enemy_pos[1]:
        return agent_random_move(state, digdug_dir)

    return '', digdug_dir

def agent_random_move(state, digdug_dir, preferred_movements=''):
    possible_moves = agent_possible_moves(state)
    
    if not possible_moves:
        return '', digdug_dir
    
    possible_death_positions = all_enemies_current_and_possible_next_positions(state) 
    safe_moves = [key for key, position in possible_moves.items() if position not in possible_death_positions]

    if not safe_moves:
        return '', digdug_dir

    preferred_potential_moves = ''.join(i for i in preferred_movements if i in safe_moves)

    if preferred_potential_moves:
        key = random.choice(preferred_potential_moves)
    else:
        key = random.choice(safe_moves)

    return key, get_direction_from_key(key)

def get_direction_from_key(key):
    directions = {'w': Direction.NORTH, 'a': Direction.WEST, 'd': Direction.EAST, 's': Direction.SOUTH}
    return directions.get(key, None)

def agent_dist_closest_enemy(state):
    if "digdug" in state:
        digdug_pos = state["digdug"]

        distances = {}  # store the positions and distances of each enemy to digdug
        for key, values in state.items():
            if key == "enemies":
                for entry in values:
                    enemy_name_id = entry["name"] + entry["id"]
                    distances[enemy_name_id] = [
                        entry["pos"],
                        math.floor(math.dist(digdug_pos, entry["pos"])),
                        entry["dir"],
                        entry['name']
                    ]

        closest_enemy_dist = 47 # max distance a enemy can be in the current grids
        closest_enemy_pos = [0, 0]
        closest_enemy_name = 'Fygar'

        for key, dists in distances.items():
            if dists[1] < closest_enemy_dist:
                closest_enemy_dist = dists[1]
                closest_enemy_pos = dists[0]
                closest_enemy_name = dists[3]

        return closest_enemy_pos, closest_enemy_dist, closest_enemy_name

    return None, None, None
   
def agent_move(digdug_pos, digdug_dir, closest_enemy_pos, closest_enemy_name, possible_death_keys=''):
    def adjust_position(value, enemy_value):
        return abs(value - enemy_value - 3) if value <= enemy_value else abs(value - enemy_value + 3)

    def update_direction_and_key(direction, key):
        nonlocal digdug_dir
        digdug_dir = direction
        return key, digdug_dir

    horizontal = adjust_position(digdug_pos[0], closest_enemy_pos[0])
    vertical = adjust_position(digdug_pos[1], closest_enemy_pos[1])

    key = ''
    dist = math.floor(math.dist(digdug_pos, closest_enemy_pos))


    if closest_enemy_name == 'Fygar' and dist <= 7:
       
        
        if digdug_pos[1] <= closest_enemy_pos[1]: # em baixo
            digdug_pos[1]+=1
            
        elif digdug_pos[1] > closest_enemy_pos[1] : #em cima
            digdug_pos[1]-=1

    if dist >= 4:
        if horizontal > vertical:
            key = "d" if digdug_pos[0] < closest_enemy_pos[0] else "a"
            return update_direction_and_key(Direction.EAST if key == "d" else Direction.WEST, key)

        key = "s" if digdug_pos[1] < closest_enemy_pos[1] else "w"
        return update_direction_and_key(Direction.SOUTH if key == "s" else Direction.NORTH, key)

    if dist > 2:
        key = "s" if digdug_pos[1] < closest_enemy_pos[1] else "w" if digdug_pos[1] > closest_enemy_pos[1] else "d" if digdug_pos[0] < closest_enemy_pos[0] else "a"
        return update_direction_and_key(Direction.SOUTH if key == "s" else Direction.NORTH if key == "w" else Direction.EAST if key == "d" else Direction.WEST, key)

    if dist <= 2:
        key = "w" if digdug_pos[1] <= closest_enemy_pos[1] else "s" if digdug_pos[1] > closest_enemy_pos[1] else "a" if digdug_pos[0] < closest_enemy_pos[0] else "d"
        return update_direction_and_key(Direction.NORTH if key == "w" else Direction.SOUTH if key == "s" else Direction.WEST if key == "a" else Direction.EAST, key)

    return key, digdug_dir

def agent_stalk_enemy(state, digdug_dir, closest_enemy_pos, closest_enemy_name, possible_death_keys=''):
    if closest_enemy_pos is None:
        return "", digdug_dir

    return agent_move(state["digdug"], digdug_dir, closest_enemy_pos, closest_enemy_name, possible_death_keys)


def agent_flee(state, digdug_dir, possible_death_positions):
    possible_moves = agent_possible_moves(state)
    
    key = ''
    closest_center_dist = 100
    safe_moves = {}

    for move, pos in possible_moves.items():
        if pos not in possible_death_positions:
            dist = math.dist(pos, [23, 12]) # get closer to the middle of the grid
            safe_moves[key] = [move, dist]
            if dist < closest_center_dist:
                key = move
                digdug_dir = key2direction(key, digdug_dir)
                closest_center_dist = dist

    possible_death_keys = ''.join(move for move, pos in possible_moves.items() if pos in possible_death_positions)
    if len(possible_death_keys) > 4:
        print("flee possible death keys:", possible_death_keys)

    return key, digdug_dir

def key2direction(key, digdug_dir):
    if key == "w":
        return Direction.NORTH
    elif key == "a":
        return Direction.WEST
    elif key == "s":
        return Direction.SOUTH
    elif key == "d":
        return Direction.EAST
    return digdug_dir

def agent_AI(state, digdug_dir):
    if 'digdug' not in state:
        return '', digdug_dir

    possible_death_positions = all_enemies_current_and_possible_next_positions(state)

    if 'digdug' in state and state["digdug"] in possible_death_positions:
        return agent_flee(state, digdug_dir, possible_death_positions)

    closest_enemy_pos, dist, closest_enemy_name = agent_dist_closest_enemy(state)
    if dist is None:
        return '', digdug_dir

    if dist <= 3 and state["digdug"]:
        key, digdug_dir = agent_shooting_conditions(state, state["digdug"], digdug_dir, closest_enemy_pos, closest_enemy_name)
        if key == 'A' or len(key) > 1:
            return key, digdug_dir

    if 'step' in state and state['step'] >= state['timeout'] - 300:
        closest_enemy_pos = [47, 23]

    possibles_moves = agent_possible_moves(state)
    possible_death_keys = ''.join(action for action, value in possibles_moves.items() if value in possible_death_positions)

    key, digdug_dir = agent_stalk_enemy(state, digdug_dir, closest_enemy_pos, closest_enemy_name, possible_death_keys)

    return key, digdug_dir
    
    