# Eclipse Tools

Eclipse Tools is a Python package designed to assist with simulating combat scenarios in the context of the Eclipse board game. It provides functionalities to create fleets, define ship types, simulate combat rounds, and analyze combat outcomes.

## Features:

### Ship Type Management:
- Create new ship types with customizable attributes such as hull points, computer points, shield points, damage dice, rift cannons, missiles, initiative, and antimatter splitter capability.
- Update existing ship types with new attribute values.
- List all currently saved ship types.
- Delete unwanted ship types.

### Fleet Creation:
- Generate fleets based on user-specified counts of different ship types.

### Combat Simulation:
- Simulate combat rounds between two fleets, determining hits and damage based on ship attributes and dice rolls.
- Compute win probabilities for both attacker and defender fleets.
- Analyze average survival rates of ships in each fleet.

## Usage:

### Ship Type Management:
- Use the provided functions `create_ship_type()`, `update_ship_type()`, `list_ship_types()`, and `delete_ship_type()` to manage ship types.

### Fleet Creation:
- Utilize the `create_fleet()` function to generate fleets based on specified ship type counts.

### Combat Simulation:
- Execute combat simulations using the `simulate_combat()` function, which returns probabilities of win for both attacker and defender fleets, along with average survival rates of ships.

## Installation:

1. First, download the repository, then move to the directory containing `setup.py`.
2. Next, install Eclipse Tools using pip:

```bash
pip install .
```

## Contributing:

Contributions to Eclipse Tools are welcome! Feel free to submit bug reports, feature requests, or pull requests on the project's GitHub repository.

## Acknowledgments:

The Eclipse Tools package was inspired by the Eclipse board game by Touko Tahkokallio.

## Authors:

Ben Warwick

## Note:

This README serves as a general guide to the Eclipse Tools package. For detailed documentation on individual functions and classes, please refer to the inline comments within the source code files.

(Yes I used AI to make this Readme, sue me jk.)
