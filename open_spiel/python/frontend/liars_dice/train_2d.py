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
    learning_rate : float
    batch_size_advantage : int
    batch_size_strategy : int
    memory_capacity : float


def capture_cfr_info():
    name=input("name: ")
    policy_layers=input("policy layers (ex:8,4): ")
    policy_tuple = tuple(map(int, policy_layers.split(',')))
    advantage_layers=input("advantage layers (ex:4,2): ")
    advantage_tuple = tuple(map(int, advantage_layers.split(',')))
    iterations = int(input("iterations (ex: 10): "))
    traversals = int(input("traversals (ex: 10): "))
    learning_rate = float(input("learning rate (ex: 1e-3): "))
    batch_size_advantage = int(input("batch size advantage (ex: 8): "))
    batch_size_strategy = int(input("batch size_strategy (ex: 8): "))
    memory_capacity = float(input("memory capacity (ex: 1e7): "))

    return  CFRSolver(name, policy_tuple, advantage_tuple,
                iterations, traversals, learning_rate,
                batch_size_advantage, batch_size_strategy,
                memory_capacity)

def main():
    cfr_solver = capture_cfr_info()
    game = pyspiel.load_game('liars_dice(numdice=2)')
    deep_cfr_solver = deep_cfr_tf2.DeepCFRSolver(
        game,
        policy_network_layers=cfr_solver.policy,
        advantage_network_layers=cfr_solver.advantage,
        num_iterations=cfr_solver.iterations,
        num_traversals=cfr_solver.traversals,
        learning_rate=cfr_solver.learning_rate,
        batch_size_advantage=cfr_solver.batch_size_advantage,
        batch_size_strategy=cfr_solver.batch_size_strategy,
        memory_capacity=cfr_solver.memory_capacity
    )
    # TODO: fetch from game
    num_players=2
    total_steps = num_players*cfr_solver.iterations*cfr_solver.traversals
    pbar = tqdm(desc='training', total = total_steps)
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
    action_tuples = list(map(lambda x: (probs[x], x),probs))
    action_tuples.sort(reverse=True)
    for prob,act in action_tuples:
        print(f'{state.action_to_string(act)} : {prob}')

if __name__ == '__main__':
    main()
