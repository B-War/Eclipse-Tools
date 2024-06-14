import os
import json
import atexit
import eclipse_combat

# Directory of the current script (package directory)
PACKAGE_DIR = os.path.dirname(eclipse_combat.__file__)

# File to store ship types data within the package directory
SHIP_TYPES_FILE = os.path.join(PACKAGE_DIR, "ship_types.json")

# Default ship types
DEFAULT_SHIP_TYPES = {
    'Interceptor': {'type': 'interceptor', 'hull': 0, 'computer': 0, 'shield': 0, 'dice': {1: 1}, 'rift_cannon': 0, 'missiles': {},
                    'initiative': 3, 'antimatter_splitter': False},
    'Cruiser': {'type': 'cruiser', 'hull': 1, 'computer': 1, 'shield': 0, 'dice': {1: 1}, 'rift_cannon': 0, 'missiles': {},
                'initiative': 2, 'antimatter_splitter': False},
    'Dreadnought': {'type': 'dreadnought', 'hull': 2, 'computer': 1, 'shield': 0, 'dice': {1: 2}, 'rift_cannon': 0, 'missiles': {},
                    'initiative': 1, 'antimatter_splitter': False},
    'Starbase': {'type': 'starbase', 'hull': 2, 'computer': 1, 'shield': 0, 'dice': {1: 1}, 'rift_cannon': 0, 'missiles': {},
                 'initiative': 4, 'antimatter_splitter': False},
    'Ancient': {'type': 'ancient', 'hull': 1, 'computer': 1, 'shield': 0, 'dice': {1: 2}, 'rift_cannon': 0, 'missiles': {},
                'initiative': 2, 'antimatter_splitter': False},
    'GCDS': {'type': 'neutral', 'hull': 7, 'computer': 2, 'shield': 0, 'dice': {1: 4}, 'rift_cannon': 0, 'missiles': {}, 'initiative': 0,
             'antimatter_splitter': False},
    'Guardian': {'type': 'neutral', 'hull': 2, 'computer': 2, 'shield': 0, 'dice': {1: 3}, 'rift_cannon': 0, 'missiles': {},
                 'initiative': 3, 'antimatter_splitter': False},
}

# Load ship types data from file
try:
    with open(SHIP_TYPES_FILE, "r") as file:
        SHIP_TYPES = json.load(file)
except FileNotFoundError:
    SHIP_TYPES = {}

# Merge default ship types with loaded ship types
for name, attributes in DEFAULT_SHIP_TYPES.items():
    if name not in SHIP_TYPES:
        SHIP_TYPES[name] = attributes


def save_ship_types():
    with open(SHIP_TYPES_FILE, "w") as file:
        json.dump(SHIP_TYPES, file)

def reset_ship_types_to_defaults():
    global SHIP_TYPES
    SHIP_TYPES = DEFAULT_SHIP_TYPES
    save_ship_types()
    print("Ship types reset to defaults successfully!")

def create_ship_type(name, attributes):
    SHIP_TYPES[name] = attributes


def get_ship_type(name):
    return SHIP_TYPES.get(name)

def create_ship():
    print("Let's create a new ship type.")

    name = input("Enter the name of the ship type: ")

    # Check if a ship with the same name already exists
    existing_ship = get_ship_type(name)
    if existing_ship:
        print(f"A ship type with the name '{name}' already exists.")
        choice = input("Do you want to continue and overwrite the existing ship type? (y/n): ").lower()
        if choice != 'y':
            print("Operation canceled.")
            return

    attributes = {}

    # Define valid ship type options
    valid_types = ['interceptor', 'cruiser', 'dreadnought', 'starbase', 'ancient', 'neutral']

    # Prompt user to select a ship type from the list of options
    print("Select the type of ship from the following options:")
    for index, ship_type in enumerate(valid_types, start=1):
        print(f"{index}. {ship_type}")

    type_choice = input("Enter the number corresponding to the ship type: ")

    # Validate user input
    if not type_choice.isdigit() or not (1 <= int(type_choice) <= len(valid_types)):
        print("Invalid choice.")
        return

    attributes['type'] = valid_types[int(type_choice) - 1]

    attributes['hull'] = float(input("Enter the hull points (an integer): "))
    attributes['computer'] = float(input("Enter the computer points (an integer): "))
    attributes['shield'] = float(input("Enter the shield points (an integer): "))

    dice_count = int(input("Enter the number of different damage dice (0 to skip): "))
    if dice_count > 0:
        dice = {}
        for _ in range(dice_count):
            side = int(input("Enter the die damage (enter largest damage die first): "))
            count = int(input("Enter the number dice of this damage: "))
            dice[side] = count
        attributes['dice'] = dice
    else:
        attributes['dice'] = {}

    attributes['rift_cannon'] = int(input("Enter the number of rift cannons (an integer): "))

    missile_count = int(input("Enter the number of different missile damage dice (0 to skip): "))
    if missile_count > 0:
        missile = {}
        for _ in range(missile_count):
            side = int(input("Enter the die damage: "))
            count = int(input("Enter the number dice of this damage: "))
            missile[side] = count
        attributes['missiles'] = missile
    else:
        attributes['missiles'] = {}

    attributes['initiative'] = int(input("Enter the ships initiative (an integer): "))
    attributes['antimatter_splitter'] = bool(input("Does the ship have antimatter splitter (True or False): "))

    create_ship_type(name, attributes)

    print(f"Ship type '{name}' created successfully!")


def update_ship_type():
    print("Select a ship type to update:")
    for index, name in enumerate(SHIP_TYPES, start=1):
        print(f"{index}. {name}")

    choice = input("Enter the number corresponding to the ship type to update (0 to cancel): ")
    if not choice.isdigit() or int(choice) <= 0 or int(choice) > len(SHIP_TYPES):
        print("Invalid choice.")
        return

    choice = int(choice)
    name = list(SHIP_TYPES.keys())[choice - 1]
    ship = get_ship_type(name)

    print(f"Current attributes for '{name}':")
    for attr, value in ship.items():
        print(f"{attr}: {value}")

    print("Enter the new values for the attributes you want to update. Press Enter to skip an attribute.")

    for attr in ship:
        if attr == 'type':
            # Update ship type
            valid_types = ['interceptor', 'cruiser', 'dreadnought', 'starbase', 'ancient', 'neutral']
            print("Select the new type of ship from the following options:")
            for index, ship_type in enumerate(valid_types, start=1):
                print(f"{index}. {ship_type}")

            type_choice = input(f"Enter the number corresponding to the new ship type (current: {ship[attr]}): ")

            if type_choice.isdigit() and (1 <= int(type_choice) <= len(valid_types)):
                selected_type = valid_types[int(type_choice) - 1]
                ship[attr] = selected_type
            else:
                print("Invalid choice. Ship type not updated.")
        if isinstance(ship[attr], dict):
            if attr == 'dice' or attr == 'missiles':
                count = input(f"Enter the number of different {attr} (current: {ship[attr]}) (0 to clear, Enter to skip): ").strip()
                if count.isdigit():
                    count = int(count)
                    if count == 0:
                        ship[attr] = {}
                    else:
                        new_dict = {}
                        for _ in range(count):
                            side = int(input(f"Enter the {attr[:-1]} damage: "))
                            amount = int(input(f"Enter the number of {attr[:-1]} of this damage: "))
                            new_dict[side] = amount
                        ship[attr] = new_dict
        elif isinstance(ship[attr], bool):
            value = input(f"{attr} (current: {ship[attr]}): ").strip()
            if value:
                ship[attr] = value.lower() in ['true', '1', 'yes', 'y']
        else:
            value = input(f"{attr} (current: {ship[attr]}): ").strip()
            if value:
                if attr in ['hull', 'computer', 'shield', 'rift_cannon', 'initiative']:
                    ship[attr] = int(value)
                else:
                    ship[attr] = value

    print(f"Ship type '{name}' updated successfully!")


def list_ship_types():
    print("List of currently saved ship types:")
    for name, attributes in SHIP_TYPES.items():
        print(f"\n{name}:")
        for attr, value in attributes.items():
            if isinstance(value, dict):  # Format nested dictionaries (e.g., dice, missiles)
                print(f"  {attr}:")
                for sub_attr, sub_value in value.items():
                    print(f"    {sub_attr}: {sub_value}")
            else:
                print(f"  {attr}: {value}")


def delete_ship_type():
    print("Select a ship type to delete:")
    for index, name in enumerate(SHIP_TYPES, start=1):
        print(f"{index}. {name}")

    choice = input("Enter the number corresponding to the ship type to delete (0 to cancel): ")
    if choice.isdigit():
        choice = int(choice)
        if 0 < choice <= len(SHIP_TYPES):
            name = list(SHIP_TYPES.keys())[choice - 1]
            del SHIP_TYPES[name]
            print(f"Ship type '{name}' deleted successfully!")
        else:
            print("Invalid choice.")
    else:
        print("Invalid input. Please enter a number.")


# Call save_ship_types() when the program exits to ensure data persistence
atexit.register(save_ship_types)
