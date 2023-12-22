#!/usr/bin/python3

import sqlite3
import shutil
import os

agent_table_create_query = "CREATE TABLE IF NOT EXISTS agents(name string PRIMARY KEY, game_name string, start_time datetime, finish_time datetime, model blob, policy_layers, advantage_layers, num_iterations, traversals, learning_rate, batch_size_advantage, batch_size_strategy, memory_capacity, total_games_vs_random, total_wins_vs_random)"

insert_agent_query = "INSERT INTO agents (name, game_name, start_time, finish_time, model, policy_layers, advantage_layers, num_iterations, traversals, learning_rate, batch_size_advantage, batch_size_strategy, memory_capacity) VALUES(?, ?, datetime(?, 'unixepoch'), datetime('now'), ?, ?, ?, ?, ?, ?, ?, ?, ?)"

select_agents_by_game_query = "SELECT name FROM agents WHERE game_name = ?;"

select_agent_by_name= "SELECT model FROM agents WHERE name = ?;"

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

def writeBytesToFile(filename, data):
    with open(filename, 'wb') as file:
        file.write(data)

def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData

def listAgentModels(game):
    conn = sqlite3.connect('games.db')
    cur = conn.cursor()
    results = cur.execute(select_agents_by_game_query, (game,))
    for row in results:
        print("" +row[0])
    cur.close()

def dumpAgentModel(name, folder):
    temp_zip = "temp.zip"
    conn = sqlite3.connect('games.db')
    cur = conn.cursor()
    results = cur.execute(select_agent_by_name, (name,))
    first_result=results.fetchone()
    if os.path.isdir(folder):
        shutil.rmtree(folder)
    os.mkdir(folder)
    full_temp_path=os.path.join(folder, temp_zip)
    writeBytesToFile(full_temp_path, first_result[0])
    shutil.unpack_archive(full_temp_path, folder, 'zip',)
    
    
