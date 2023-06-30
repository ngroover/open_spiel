#!/usr/bin/python3
import pyspiel
import pickle
import numpy as np
from open_spiel.python.bots.policy import PolicyBot
from open_spiel.python.bots.uniform_random import UniformRandomBot
from open_spiel.python.bots.human import HumanBot

f=open('liars_dice_1d.pickle','rb')
policy=pickle.load(f)

NUM_GAMES=10
p1_wins=0
p2_wins=0
draws=0
bots=[PolicyBot(0,np.random,policy),HumanBot()]
game = pyspiel.load_game('liars_dice(numdice=1)')
for _ in range(NUM_GAMES):
  state = game.new_initial_state()
  for bot in bots:
    bot.restart_at(state)
  while not state.is_terminal():
    if state.is_chance_node():
      outcomes, probs = zip(*state.chance_outcomes())
      action = np.random.choice(outcomes, p=probs)
      state.apply_action(action)
    else:
      current_player = state.current_player()
      if current_player == 1:
          print(state)
      action = bots[current_player].step(state)
      state.apply_action(action)
  if state.returns()[1] > 0:
    p2_wins+=1
    print(f'state {state}')
    print('p2 (human) wins!')
  elif state.returns()[0] > 0:
    p1_wins+=1
    print(f'state {state}')
    print('p1 (policy bot) wins!')
  else:
    draws+=1
    print('draw')
print(f'p1 (policy bot) wins: {p1_wins}')
print(f'p2 (human) wins: {p2_wins}')
print(f'draws: {draws}')


