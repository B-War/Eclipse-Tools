from setuptools import setup, find_packages

setup(
    name='eclipse_tools',
    version='1.31',
    packages=find_packages(),
    install_requires=[
        # List your dependencies here
    ],
    entry_points={
        'console_scripts': [
            'create_ship_type = eclipse_combat.ship_types:create_ship',
            'update_ship_type = eclipse_combat.ship_types:update_ship_type',
            'list_ship_types = eclipse_combat.ship_types:list_ship_types',
            'delete_ship_type = eclipse_combat.ship_types:delete_ship_type',
            'simulate_combat = eclipse_combat.combat:simulate_combat',
            'simulate_combat_parallel = eclipse_combat.combat:simulate_combat_parallel',
            'reset_ship_types = eclipse_combat.ship_types:reset_ship_types_to_defaults',
        ],
    },
)
