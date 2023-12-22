#!/usr/bin/python3

import sqlite3
import shutil
import os

agent_table_create_query = "CREATE TABLE IF NOT EXISTS agents(name TEXT PRIMARY KEY, game_name TEXT, start_time datetime, finish_time datetime, model BLOB, policy_layers TEXT, advantage_layers TEXT, num_iterations INTEGER, traversals INTEGER, learning_rate REAL, batch_size_advantage INTEGER, batch_size_strategy INTEGER, memory_capacity REAL, total_games_vs_random INTEGER, total_wins_vs_random INTEGER)"

insert_agent_query = "INSERT INTO agents (name, game_name, start_time, finish_time, model, policy_layers, advantage_layers, num_iterations, traversals, learning_rate, batch_size_advantage, batch_size_strategy, memory_capacity, total_games_vs_random, total_wins_vs_random) VALUES(?, ?, datetime(?, 'unixepoch'), datetime('now'), ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0)"

select_agents_by_game_query = "SELECT name FROM agents WHERE game_name = ?;"

select_agent_by_name= "SELECT model FROM agents WHERE name = ?;"
select_agent_stats_by_game = "SELECT name, policy_layers, advantage_layers, num_iterations, traversals, learning_rate, batch_size_advantage, batch_size_strategy, memory_capacity, total_games_vs_random, CAST(total_wins_vs_random AS REAL)/CAST(total_games_vs_random AS REAL)*100 AS win_rate FROM agents WHERE game_name = ? AND total_games_vs_random > 0"

get_agent_winrate = "SELECT total_wins_vs_random, total_games_vs_random FROM agents WHERE name = ?;"

update_agent_winrate = "UPDATE agents SET total_wins_vs_random = ?, total_games_vs_random = ? WHERE name = ?;"

create_matchups_table = "CREATE TABLE IF NOT EXISTS matchups(p1_name TEXT NOT NULL, p2_name TEXT NOT NULL, p1_wins INTEGER, p2_wins INTEGER, PRIMARY KEY (p1_name, p2_name), FOREIGN KEY(p1_name) REFERENCES agents(name), FOREIGN KEY(p2_name) REFERENCES agents(name));"

get_matchups_query = "SELECT p1_wins, p2_wins FROM matchups WHERE p1_name = ? AND p2_name = ?"

insert_matchup= "INSERT OR IGNORE INTO matchups (p1_name, p2_name) VALUES (?, ?);"
update_matchup = "UPDATE matchups SET p1_wins = ?, p2_wins = ? WHERE p1_name = ? AND p2_name = ?;"

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
    cur.close()

def dumpStats(game_name):
    conn = sqlite3.connect('games.db')
    cur = conn.cursor()
    results = cur.execute(select_agent_stats_by_game, (game_name,))
    print(list(map(lambda x: x[0], results.description)))
    for row in results:
        print(row)
    cur.close()

def addRandomGames(name, wins, games):
    conn = sqlite3.connect('games.db')
    cur = conn.cursor()
    results = cur.execute(get_agent_winrate, (name,))
    first_result = results.fetchone()
    total_wins = first_result[0] + wins
    total_games = first_result[1] + games
    cur.execute(update_agent_winrate, (total_wins, total_games, name))
    conn.commit()
    cur.close()
    
def updateMatchupData(p1_name, p2_name, p1_wins, p2_wins):
    conn = sqlite3.connect('games.db')
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")    # we need to enable foreign keys every time
    cur.execute(create_matchups_table)
    cur.execute(insert_matchup, (p1_name, p2_name))
    cur.execute(update_matchup, (p1_name,p2_name,p1_wins,p2_wins))
    conn.commit()
    cur.close()
