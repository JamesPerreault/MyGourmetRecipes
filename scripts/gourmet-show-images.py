#!/usr/bin/python3

import SqliteDb
from io import BytesIO
from PIL import Image, UnidentifiedImageError
import argparse

parser = argparse.ArgumentParser(description='Show images from Gourmet Sqlite db')
parser.add_argument('ids', type=int, nargs='+',
                    help='id(s) of recipes to show')
parser.add_argument('--dbfile',  default='recipes.db',
                    help='Database file.')

args = parser.parse_args()

db = SqliteDb.Db(args.dbfile) 

for id in args.ids:
    print("Image {}".format(id))
    data = db.getImage(id)
    try:
        img = Image.open(BytesIO(data))  
        img.show()
    except UnidentifiedImageError:
        print("Skipping")
db.close()
 

