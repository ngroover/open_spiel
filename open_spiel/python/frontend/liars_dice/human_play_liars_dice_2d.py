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
from open_spiel.python.bots.human import HumanBot
import database

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
        #for i,x in enumerate(legal_actions):
            #print(f'{x} : {state.action_to_string(x)} : {action_probs[i]}')
        #print(f'choosing {chosen_action}')
        #print('----')
        return chosen_action

    def step(self, state):
        return self.step_with_policy(state)

def main():
    game_name = input("game_name: ")
    print('Agents:')
    database.listAgentModels(game_name)
    agent_name = input("name: ")
    model_folder='human_play_policy_model'
    database.dumpAgentModel(agent_name, model_folder)
    policy_network = tf.keras.models.load_model(model_folder,compile=False)
    #NUM_GAMES=10000
    NUM_GAMES=15
    p1_wins=0
    p2_wins=0
    draws=0
    bots=[PolicyNetworkBot(0,np.random,policy_network),HumanBot()]
    game = pyspiel.load_game(game_name)

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
                #print(f'state {state}')
                current_player = state.current_player()
                if current_player == 1:
                    print(f'state {str(state)[3:]}')
                action = bots[current_player].step(state)
                state.apply_action(action)
        if state.returns()[1] > 0:
            p2_wins+=1
            print(f'state {state}')
            print(f'p2 (human) wins!')
        elif state.returns()[0] > 0:
            p1_wins+=1
            print(f'p1 (policy) wins!')
            print(f'state {state}')
        else:
            draws+=1
    print(f'p1 (policy) wins: {p1_wins} {p1_wins/NUM_GAMES*100} %')
    print(f'p2 (human) wins: {p2_wins} {p2_wins/NUM_GAMES*100} %')
    print(f'draws: {draws}')


if __name__ == '__main__':
    main()

