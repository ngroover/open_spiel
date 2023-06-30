#!/usr/bin/python3
import pyspiel
import pickle
from open_spiel.python.algorithms import cfr
from open_spiel.python.algorithms.exploitability import nash_conv

game = pyspiel.load_game('liars_dice(numdice=1)')

cfr_solver = cfr.CFRSolver(game)
for x in range(50):
  cfr_solver.evaluate_and_update_policy()
  average_policy = cfr_solver.average_policy()
  nash = nash_conv(game,average_policy,False)
  print('nash convergence {}'.format(nash))
with open('liars_dice_1d.pickle', 'wb') as f:
  pickle.dump(average_policy,f,pickle.HIGHEST_PROTOCOL)
print("Done")
