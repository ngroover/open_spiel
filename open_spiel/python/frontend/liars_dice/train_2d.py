#!/usr/bin/python3
import tensorflow as tf
import pyspiel
import numpy as np
from open_spiel.python.algorithms import deep_cfr_tf2
from open_spiel.python.algorithms import exploitability
from open_spiel.python import policy

def main():
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
  deep_cfr_solver.solve()
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
