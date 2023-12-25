#!/usr/bin/python3
import torch
import pyspiel
from open_spiel.python.algorithms import deep_cfr_tf2
import numpy as np
import tensorflow as tf

import tensorflow as tf
import pyspiel
import numpy as np
from open_spiel.python.algorithms import deep_cfr_tf2
from open_spiel.python.algorithms import exploitability
from open_spiel.python import policy
from open_spiel.python.bots.uniform_random import UniformRandomBot
import database
from tqdm import tqdm

class PolicyNetworkBot(pyspiel.Bot):
    """Samples an action from action probabilities based on a policy network.
    """

    def __init__(self, player_id, rng, policy):
        """Initializes a policy bot.

        Args:
          player_id: The integer id of the player for this bot, e.g. `0` if acting
            as the first player.
          rng: A random number generator supporting a `choice` method, e.g.
            `np.random`
          policy: A policy to get action distributions
        """
        pyspiel.Bot.__init__(self)
        self._player_id = player_id
        self._rng = rng
        self._policy = policy

    def player_id(self):
        return self._player_id

    def restart_at(self, state):
        pass

    def step_with_policy(self, state):
        cur_player = state.current_player()
        legal_actions = state.legal_actions(cur_player)
        legal_action_mask = tf.constant(state.legal_actions_mask(cur_player), dtype=tf.float32)
        info_state_vector = tf.constant(state.information_state_tensor(), dtype=tf.float32)
        if len(info_state_vector.shape) == 1:
            info_state_vector = tf.expand_dims(info_state_vector,axis=0)
        if len(legal_action_mask.shape) == 1:
            legal_action_mask = tf.expand_dims(legal_action_mask,axis=0)

        inp = (info_state_vector, legal_action_mask)
        probs = self._policy.call(inp).numpy()
        action_probs = [probs[0][action] for action in legal_actions]
        #print(legal_actions)
        #print(action_probs)
        action_probs=np.array(action_probs)
        #print(action_probs)
        #print(info_state_vector)
        #print(legal_action_mask)
        chosen_action = self._rng.choice(legal_actions, p=action_probs)
        action_tuples = list(zip(action_probs, legal_actions))
        #print(action_tuples)
        #print(legal_actions)
        #print(action_probs)
        action_tuples.sort(reverse=True)
        for prob,act in action_tuples:
            print(f'{state.action_to_string(act)} : {prob}')
        #print(f'choosing {chosen_action}')
        #print('----')
        return chosen_action

    def step(self, state):
        return self.step_with_policy(state)

def printState(state):
    state_str=str(state)
    state_split=state_str.split(' ')
    print(f'bot dice: {state_split[0]}')
    print(f'random dice: {state_split[1]}')
    bids_str = ' '.join(state_split[2:])
    print(f'bids : {bids_str}')

def main():
    game_name = input("game_name: ")
    print('Agents:')
    database.listAgentModels(game_name)
    agent_name = input("name: ")
    model_folder='player1_model_spectate'
    database.dumpAgentModel(agent_name, model_folder)
    policy_network = tf.keras.models.load_model(model_folder,compile=False)
    NUM_GAMES=0
    p1_wins=0
    p2_wins=0
    draws=0
    done=False
    bots=[PolicyNetworkBot(0,np.random,policy_network),UniformRandomBot(1,np.random)]
    game = pyspiel.load_game(game_name)

    while not done:
        state = game.new_initial_state()
        for bot in bots:
            bot.restart_at(state)
        while not state.is_terminal():
            if state.is_chance_node():
                outcomes, probs = zip(*state.chance_outcomes())
                action = np.random.choice(outcomes, p=probs)
                state.apply_action(action)
            else:
                printState(state)
                current_player = state.current_player()
                action = bots[current_player].step(state)
                state.apply_action(action)
                pause=input("press any key")
        if state.returns()[1] > 0:
            p2_wins+=1
            printState(state)
            print(f'p2 (random) wins!')
        elif state.returns()[0] > 0:
            p1_wins+=1
            printState(state)
            print(f'p1 (bot) wins!')
        else:
            draws+=1
        NUM_GAMES += 1
        prompt_quit = input("quit?")
        if prompt_quit == 'q' or prompt_quit == 'Q':
            done = True
            
    print(f'p1 (policy) wins: {p1_wins} {p1_wins/NUM_GAMES*100} %')
    print(f'p2 (random) wins: {p2_wins} {p2_wins/NUM_GAMES*100} %')
    print(f'draws: {draws}')

if __name__ == '__main__':
    main()

