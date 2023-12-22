#!/usr/bin/python3

import database

def main():
    game_name=input("game name: ")
    database.dumpStats(game_name)

if __name__ == '__main__':
    main()
