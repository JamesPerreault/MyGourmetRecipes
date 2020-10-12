#!/usr/bin/python3

import sqlite3
import argparse

parser = argparse.ArgumentParser(description='Print recipe titles')
parser.add_argument('--dbfile',  default='recipes.db',
                    help='Output database file.')

args = parser.parse_args()


conn = sqlite3.connect(args.dbfile)
c = conn.cursor() 
c.execute("""select id,title from recipe where deleted = False""") 
for row in c:
    print(row)

c.close()

