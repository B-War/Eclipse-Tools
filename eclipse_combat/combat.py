import random
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import itertools
from .ship_types import SHIP_TYPES
from timeit import default_timer as time

# Define Rift Cannon sides
RIFT_CANNON_SIDES = {
    'Hit and Damage Self': {'damage_target': 3, 'damage_self': 1},
    '2 Damage to Target': {'damage_target': 2},
    '1 Damage to Target': {'damage_target': 1},
    '1 Damage to Self': {'damage_self': 1},
    'Miss': {},
    'Miss': {},
}


# Function to create a fleet based on the number of each ship type
def create_fleet(ship_counts):
    fleet = []
    for ship_type, count in ship_counts.items():
        for _ in range(count):
            ship = SHIP_TYPES[ship_type].copy()
            ship['type'] = ship_type  # Add the 'type' key
            fleet.append(ship)
    return fleet


# Function to calculate the average damage output of a ship
def calculate_average_damage(ship, target_shield):
    total_damage = 0
    for damage, count in ship['dice'].items():
        hit_chance = lambda ship_computer, shield: min(
            max((1 / 6) + (ship_computer * (1 / 6)) - (shield * (1 / 6)), 1 / 6), 5 / 6)
        total_damage += float(damage) * float(count) * hit_chance(ship['computer'], target_shield)  # Call hit_chance with arguments
    rift = ship['rift_cannon']
    total_damage += rift
    return total_damage

# Function to calculate the average damage output of a ship with missiles
def calculate_average_damage_missile(ship, target_shield):
    total_damage = 0
    for damage, count in ship['dice'].items():
        hit_chance = lambda ship_computer, shield: min(
            max((1 / 6) + (ship_computer * (1 / 6)) - (shield * (1 / 6)), 1 / 6), 5 / 6)
        total_damage += float(damage) * float(count) * hit_chance(ship['computer'], target_shield)  # Call hit_chance with arguments
    for damage, count in ship['missiles'].items():
        hit_chance = lambda ship_computer, shield: min(
            max((1 / 6) + (ship_computer * (1 / 6)) - (shield * (1 / 6)), 1 / 6), 5 / 6)
        total_damage += float(damage) * float(count) * hit_chance(ship['computer'], target_shield)  # Call hit_chance with arguments
    rift = ship['rift_cannon']
    total_damage += rift
    return total_damage


def select_target(fleet, dice_roll, attacking_ship, attacking_fleet, damage):
    # Calculate threat levels for each ship
    target_shield = max(ship['shield'] for ship in attacking_fleet)
    threat_levels = [(calculate_average_damage(ship, target_shield), ship) for ship in fleet if ship['hull'] >= 0]

    # Sort by threat level descending
    threat_levels.sort(key=lambda x: -x[0])

    # Sort targets within each threat level group based on the new prioritization rules
    sorted_targets = []
    for threat, group in itertools.groupby(threat_levels, key=lambda x: x[0]):
        group = list(group)
        # Sort group by hull criteria: hull == damage-1 first, then descending to 0, then ascending from damage
        group.sort(key=lambda x: (abs(x[1]['hull'] - (damage - 1)), x[1]['hull'] < damage, x[1]['hull']))
        sorted_targets.extend(group)

    # Return the highest priority target that can be hit
    for threat, ship in sorted_targets:
        if (dice_roll + attacking_ship['computer'] - ship['shield'] >= 6 or dice_roll == 6):
            return ship
    return None


def select_target_missile(fleet, dice_roll, attacking_ship, attacking_fleet, damage):
    # Calculate target shield from the attacking fleet
    target_shield = max(ship['shield'] for ship in attacking_fleet)

    # Separate fleet into two groups based on initiative
    lower_initiative_ships = [ship for ship in fleet if ship['initiative'] < attacking_ship['initiative']]
    higher_initiative_ships = [ship for ship in fleet if ship['initiative'] >= attacking_ship['initiative']]

    # Calculate threat levels for lower initiative ships
    lower_threat_levels = [(calculate_average_damage_missile(ship, target_shield), ship) for ship in
                           lower_initiative_ships if ship['hull'] >= 0]
    # Calculate threat levels for higher initiative ships
    higher_threat_levels = [(calculate_average_damage(ship, target_shield), ship) for ship in
                            higher_initiative_ships if ship['hull'] >= 0]

    # Combine threat levels
    threat_levels = lower_threat_levels + higher_threat_levels

    # Sort by threat level descending
    threat_levels.sort(key=lambda x: -x[0])

    # Sort targets within each threat level group based on the new prioritization rules
    sorted_targets = []
    for threat, group in itertools.groupby(threat_levels, key=lambda x: x[0]):
        group = list(group)
        # Sort group by hull criteria: hull == damage-1 first, then descending to 0, then ascending from damage
        group.sort(key=lambda x: (abs(x[1]['hull'] - (damage - 1)), x[1]['hull'] < damage, x[1]['hull']))
        sorted_targets.extend(group)

    # Return the highest priority target that can be hit
    for threat, ship in sorted_targets:
        if (dice_roll + attacking_ship['computer'] - ship['shield'] >= 6 or dice_roll == 6):
            return ship
    return None


# Function to determine the outcome of a single ship types dice rolls
def rolls(ship):
    results = {}
    for damage, counts in ship['dice'].items():
        results[damage] = []
        for _ in range(counts):
            roll = random.randint(1, 6)
            if roll != 1:
                if damage == 4 and ship['antimatter_splitter']:
                    results[1].extend([roll] * 4)
                else:
                    results[damage].append(roll)
    return results


# Function to assign hits from a ship to the opposing fleet
def assign_hits(ship, fleet, attacking_fleet):
    dice = rolls(ship)
    for die in dice:
        for roll in dice[die]:
            if fleet is None:
                continue
            else:
                target = select_target(fleet, roll, ship, attacking_fleet, int(die))
                if target is not None:
                    target['hull'] -= int(die)


# Function to determine the outcome of a single ship types rift cannon rolls
def rolls_rift_cannon(ship):
    results = {side: 0 for side in RIFT_CANNON_SIDES}
    for _ in range(ship['rift_cannon']):
        side = random.choice(list(RIFT_CANNON_SIDES.keys()))
        results[side] += 1
    return results


# Function to assign rift cannon hits from a ship to the opposing fleet
def assign_rift_cannon(ship, fleet, attacking_fleet):
    dice = rolls_rift_cannon(ship)
    attacking_ships_with_rift_cannons = sorted([s for s in attacking_fleet if s['rift_cannon'] > 0],
                                               key=lambda s: s['hull'], reverse=True)

    for side, count in dice.items():
        for _ in range(count):
            if fleet is None:
                continue

            # Calculate the damage to target
            damage_target = RIFT_CANNON_SIDES[side].get('damage_target', 0)

            # Select the target considering the damage
            target = select_target(fleet, 6, ship, attacking_fleet,
                                   damage_target)  # Assuming a roll of 6 for the rift cannon

            if target is not None:
                # Apply damage to the target
                if 'damage_target' in RIFT_CANNON_SIDES[side]:
                    target['hull'] -= RIFT_CANNON_SIDES[side]['damage_target']

                # Apply damage to the firing ship
                if 'damage_self' in RIFT_CANNON_SIDES[side] and attacking_ships_with_rift_cannons:
                    attacking_ships_with_rift_cannons[0]['hull'] -= RIFT_CANNON_SIDES[side]['damage_self']


# Function to determine the outcome of a single ship types missile rolls
def rolls_missiles(ship):
    results = {}
    for damage, counts in ship['missiles'].items():
        results[damage] = []
        for _ in range(counts):
            roll = random.randint(1, 6)
            if roll != 1:
                results[damage].append(roll)
    return results


# Function to assign missile hits from a ship to the opposing fleet
def assign_missiles(ship, fleet, attacking_fleet):
    dice = rolls_missiles(ship)
    for die in dice:
        for roll in dice[die]:
            if fleet is None:
                continue
            else:
                target = select_target_missile(fleet, roll, ship, attacking_fleet, int(die))
                if target is not None:
                    target['hull'] -= int(die)


def simulate_combat_round(attacker, defender):
    # Add an index to each ship for tie-breaking
    for idx, ship in enumerate(attacker):
        ship['index'] = idx
    for idx, ship in enumerate(defender):
        ship['index'] = idx + len(attacker)  # Ensure unique indices across both lists

    # Sort ships by initiative, defender status, and index
    all_ships = sorted(attacker + defender, key=lambda ship: (ship['initiative'], ship in defender, ship['index']),
                       reverse=True)

    for ship in all_ships:
        # Check if all ships in either attacker or defender have hull <= -1
        if all(ship['hull'] <= -1 for ship in attacker) or all(ship['hull'] <= -1 for ship in defender):
            break

        if ship['hull'] < 0:
            continue

        if ship in attacker:
            targets = [target for target in defender]
            allies = [ally for ally in attacker if ally['hull'] >= 0]
            assign_hits(ship, targets, allies)
            assign_rift_cannon(ship, targets, allies)
        else:
            targets = [target for target in attacker]
            allies = [ally for ally in defender if ally['hull'] >= 0]
            assign_hits(ship, targets, allies)
            assign_rift_cannon(ship, targets, allies)

    attacker = [ship for ship in attacker if ship['hull'] >= 0]
    defender = [ship for ship in defender if ship['hull'] >= 0]

    return attacker, defender


# Function to simulate the missile attacks
def missile_attack(attacker, defender):
    # Add an index to each ship for tie-breaking
    for idx, ship in enumerate(attacker):
        ship['index'] = idx
    for idx, ship in enumerate(defender):
        ship['index'] = idx + len(attacker)  # Ensure unique indices across both lists

    # Sort ships by initiative, defender status, and index
    all_ships = sorted(attacker + defender, key=lambda ship: (ship['initiative'], ship in defender, ship['index']),
                       reverse=True)

    for ship in all_ships:
        # Check if all ships in either attacker or defender have hull <= -1
        if all(ship['hull'] <= -1 for ship in attacker) or all(ship['hull'] <= -1 for ship in defender):
            break

        if ship['hull'] < 0:
            continue

        if ship in attacker:
            targets = [target for target in defender]
            allies = [ally for ally in attacker if ally['hull'] >= 0]
            assign_missiles(ship, targets, allies)
        else:
            targets = [target for target in attacker]
            allies = [ally for ally in defender if ally['hull'] >= 0]
            assign_missiles(ship, targets, allies)

# Mapping of ship categories to their max counts
SHIP_CATEGORY_LIMITS = {
    'interceptor': 8,
    'cruiser': 4,
    'dreadnought': 2,
    'starbase': 4,
    'ancient': 2,
    'neutral': 1
}

def input_fleet(fleet_name):
    fleet_counts = {}
    print(f"Input the {fleet_name} fleet:")
    while True:
        print("Available ship types:")
        for index, ship_name in enumerate(SHIP_TYPES.keys(), start=1):
            ship_type = SHIP_TYPES[ship_name]['type']
            max_count = SHIP_CATEGORY_LIMITS.get(ship_type, 0)
            print(f"{index}. {ship_name} (Category: {ship_type}, Max: {max_count})")
        choice = input("Enter the number of the ship type to add to the fleet (or leave blank to finish): ").strip()
        if not choice:
            break
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(SHIP_TYPES):
            print("Invalid choice. Please enter a valid number.")
            continue
        ship_name = list(SHIP_TYPES.keys())[int(choice) - 1]
        ship_type = SHIP_TYPES[ship_name]['type']
        max_count = SHIP_CATEGORY_LIMITS.get(ship_type, 0)
        count = int(input(f"Enter the number of '{ship_name}' ships (max {max_count}): "))
        if count > max_count:
            print(f"Exceeded maximum allowed count of {ship_name} ({max_count}). Using {max_count}.")
            count = max_count
        fleet_counts[ship_name] = count
    return fleet_counts

def simulate_combat():
    print("Let's simulate a combat!")

    attacker_counts = input_fleet("attacker")
    defender_counts = input_fleet("defender")

    iterations = int(input("Enter the number of combat iterations: "))

    start_time = time()
    attacker_wins = 0
    defender_wins = 0
    attacker_survivors = {ship_type: [] for ship_type in attacker_counts}
    defender_survivors = {ship_type: [] for ship_type in defender_counts}

    for i in tqdm(range(iterations)):
        attacker_fleet = create_fleet(attacker_counts)
        defender_fleet = create_fleet(defender_counts)

        missile_attack(attacker_fleet, defender_fleet)

        while attacker_fleet and defender_fleet:
            attacker_fleet, defender_fleet = simulate_combat_round(attacker_fleet, defender_fleet)

        if attacker_fleet and not defender_fleet:
            attacker_wins += 1
            for ship_type in attacker_counts:
                attacker_survivors[ship_type].append(sum(ship['type'] == ship_type for ship in attacker_fleet))

        if defender_fleet and not attacker_fleet:
            defender_wins += 1
            for ship_type in defender_counts:
                defender_survivors[ship_type].append(sum(ship['type'] == ship_type for ship in defender_fleet))
    end_time = time()
    print(f"Simulated {iterations} combat iterations in {end_time - start_time:.2f} seconds.")

    attacker_survival_avg = {ship_type: sum(counts) / len(counts) if counts else 0 for ship_type, counts in
                             attacker_survivors.items()}
    defender_survival_avg = {ship_type: sum(counts) / len(counts) if counts else 0 for ship_type, counts in
                             defender_survivors.items()}

    results = {
        'attacker_win_prob': attacker_wins / iterations,
        'defender_win_prob': defender_wins / iterations,
        'attacker_survival_avg': attacker_survival_avg,
        'defender_survival_avg': defender_survival_avg
    }

    print(f"\nResults:\n{'-' * 20}")
    print(f"Attacker win probability: {results['attacker_win_prob']}")
    print(f"Defender win probability: {results['defender_win_prob']}")
    print(f"\nAttacker survival average:")
    for ship_type, avg in results['attacker_survival_avg'].items():
        print(f"{ship_type}: {avg}")
    print(f"\nDefender survival average:")
    for ship_type, avg in results['defender_survival_avg'].items():
        print(f"{ship_type}: {avg}")


def simulate_combat_iteration(attacker_counts, defender_counts):
    """ Simulate one combat chain until one side is defeated
    :param attacker_counts: Dictionary of ship types and their counts for the attacker
    :param defender_counts: Dictionary of ship types and their counts for the defender
    :return: Tuple of attacker wins, defender wins, attacker survivors, defender survivors

    """
    attacker_fleet = create_fleet(attacker_counts)
    defender_fleet = create_fleet(defender_counts)

    attacker_wins = 0
    defender_wins = 0
    attacker_survivors = {ship_type: [] for ship_type in attacker_counts}
    defender_survivors = {ship_type: [] for ship_type in defender_counts}

    missile_attack(attacker_fleet, defender_fleet)

    while attacker_fleet and defender_fleet:
        attacker_fleet, defender_fleet = simulate_combat_round(attacker_fleet, defender_fleet)

    if attacker_fleet and not defender_fleet:
        attacker_wins += 1
        for ship_type in attacker_counts:
            attacker_survivors[ship_type].append(sum(ship['type'] == ship_type for ship in attacker_fleet))

    if defender_fleet and not attacker_fleet:
        defender_wins += 1
        for ship_type in defender_counts:
            defender_survivors[ship_type].append(sum(ship['type'] == ship_type for ship in defender_fleet))

    return attacker_wins, defender_wins, attacker_survivors, defender_survivors

def simulate_combat_parallel():
    """ Simulate a battle in parallel.
    :return: None
    """
    print("Let's simulate a combat!")

    attacker_counts = input_fleet("attacker")
    defender_counts = input_fleet("defender")
    start_time = time()
    iterations = int(input("Enter the number of combat iterations: "))

    attacker_survivors = {ship_type: [] for ship_type in attacker_counts}
    defender_survivors = {ship_type: [] for ship_type in defender_counts}

    results = process_map(simulate_combat_iteration, [attacker_counts] * iterations, [defender_counts] * iterations, chunksize=200)
    end_time = time()
    print(f"Simulated {iterations} combat iterations in {end_time - start_time:.2f} seconds.")
    attacker_wins = sum(result[0] for result in results)
    defender_wins = sum(result[1] for result in results)
    for result in results:
        for ship_type in attacker_counts:
            attacker_survivors[ship_type].extend(result[2][ship_type])
        for ship_type in defender_counts:
            defender_survivors[ship_type].extend(result[3][ship_type])

    attacker_survival_avg = {ship_type: sum(counts) / len(counts) if counts else 0 for ship_type, counts in
                                attacker_survivors.items()}
    defender_survival_avg = {ship_type: sum(counts) / len(counts) if counts else 0 for ship_type, counts in
                                defender_survivors.items()}
    final_results = {
        'attacker_win_prob': attacker_wins / iterations,
        'defender_win_prob': defender_wins / iterations,
        'attacker_survival_avg': attacker_survival_avg,
        'defender_survival_avg': defender_survival_avg
    }
    print(f"\nResults:\n{'-' * 20}")
    print(f"Attacker win probability: {final_results['attacker_win_prob']}")
    print(f"Defender win probability: {final_results['defender_win_prob']}")
    print(f"\nAttacker survival average:")
    for ship_type, avg in final_results['attacker_survival_avg'].items():
        print(f"{ship_type}: {avg}")
    print(f"\nDefender survival average:")
    for ship_type, avg in final_results['defender_survival_avg'].items():
        print(f"{ship_type}: {avg}")
