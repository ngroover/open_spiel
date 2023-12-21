#!/usr/bin/python3

import sqlite3
import shutil
import os

agent_table_create_query = "CREATE TABLE IF NOT EXISTS agents(name string PRIMARY KEY, game_name string, start_time datetime, finish_time datetime, model blob, policy_layers, advantage_layers, num_iterations, traversals, learning_rate, batch_size_advantage, batch_size_strategy, memory_capacity, total_games_vs_random, total_wins_vs_random)"

insert_agent_query = "INSERT INTO agents (name, game_name, start_time, finish_time, model, policy_layers, advantage_layers, num_iterations, traversals, learning_rate, batch_size_advantage, batch_size_strategy, memory_capacity) VALUES(?, ?, datetime(?, 'unixepoch'), datetime('now'), ?, ?, ?, ?, ?, ?, ?, ?, ?)"

def saveModelToDB(cfrsolver, model_folder, start_time):
    zipname=model_folder+'.zip'
    if os.path.isfile(zipname):
        os.remove(zipname)
    shutil.make_archive(model_folder, 'zip', model_folder)
    shutil.rmtree(model_folder)

    conn = sqlite3.connect('games.db')
    cur = conn.cursor()
    cur.execute(agent_table_create_query)
    model_binary_data = convertToBinaryData(zipname)
    os.remove(zipname)
    insert_agent_tuple = (cfrsolver.name, 
                    cfrsolver.game_name,
                    start_time,
                    model_binary_data,
                    str(cfrsolver.policy),
                    str(cfrsolver.advantage),
                    cfrsolver.iterations,
                    cfrsolver.traversals,
                    cfrsolver.learning_rate,
                    cfrsolver.batch_size_advantage,
                    cfrsolver.batch_size_strategy,
                    cfrsolver.memory_capacity)
    cur.execute(insert_agent_query, insert_agent_tuple)
    conn.commit()

    cur.close()

def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData

