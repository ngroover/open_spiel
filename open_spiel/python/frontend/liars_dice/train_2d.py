#!/usr/bin/python3
import tensorflow as tf
import pyspiel
import numpy as np
from open_spiel.python.algorithms import deep_cfr_tf2
from open_spiel.python.algorithms import exploitability
from open_spiel.python import policy
from tqdm import tqdm

from dataclasses import dataclass

@dataclass
class CFRSolver:
    name : str
    policy : tuple
    advantage : tuple
    iterations : int
    traversals : int
    batch_size_advantage : int
    batch_size_strategy : int
    memory_capacity : int


def capture_cfr_info():
    name=input("name: ")
    policy_layers=input("policy layers (ex:8,4): ")
    policy_tuple = tuple(map(int, policy_layers.split(',')))
    advantage_layers=input("advantage layers (ex:4,2): ")
    advantage_tuple = tuple(map(int, advantage_layers.split(',')))
    iterations = int(input("iterations (ex: 10): "))
    traversals = int(input("traversals (ex: 10): "))
    batch_size_advantage = int(input("batch size advantage (ex: 8): "))
    batch_size_strategy = int(input("batch size_strategy (ex: 8): "))
    memory_capacity = int(float(input("memory capacity (ex: 1e7): ")))

    cfr_solver = CFRSolver(name, policy_tuple, advantage_tuple,
                iterations, traversals, batch_size_advantage,
                batch_size_strategy, memory_capacity)
    print(cfr_solver)

  

def main():
    capture_cfr_info()
    return 0
    game = pyspiel.load_game('liars_dice(numdice=2)')
    deep_cfr_solver = deep_cfr_tf2.DeepCFRSolver(
        game,
        policy_network_layers=(8,4),
        advantage_network_layers=(4,2),
        num_iterations=10,
        num_traversals=10,
        learning_rate=1e-3,
        batch_size_advantage=8,
        batch_size_strategy=8,
        memory_capacity=1e7
    )
    pbar = tqdm(desc='training', total = 10*10*2)
    for x in deep_cfr_solver.solve_gen():
        pbar.update()
    print('First state probabilities')
    deep_cfr_solver.save_policy_network('policy_network')
    print('saving policy')
    state = game.new_initial_state()
    while state.is_chance_node():
        outcomes, probs = zip(*state.chance_outcomes())
        action = np.random.choice(outcomes, p=probs)
        state.apply_action(action)
    probs = deep_cfr_solver.action_probabilities(state)
    print(f'state is {state}')
    for x in probs:
        print(f'{state.action_to_string(x)} : {probs[x]}')

if __name__ == '__main__':
    main()
