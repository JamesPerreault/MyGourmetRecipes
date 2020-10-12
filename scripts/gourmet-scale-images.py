#!/usr/bin/python3

import SqliteDb
import RecipeJson
import argparse
from PIL import Image, UnidentifiedImageError
from io import BytesIO

parser = argparse.ArgumentParser(description='Scale images in Gourmet Sqlite db')
parser.add_argument('ids', type=int, nargs='+',
                    help='id(s) of recipes to scale')
parser.add_argument('--display',action='store_true' ,
                    help='Display scaled images')
parser.add_argument('--dbfile',  default='recipes.db',
                    help='Database file.')

args = parser.parse_args()

db = SqliteDb.Db(args.dbfile) 

for id in args.ids:
    print("Scaling image {}".format(id))
    img = db.getImage(id)
    try:
        scaled = RecipeJson.scale_image(img)
        db.updateImage(id,scaled)
        if args.display:
            img2 = Image.open(BytesIO(scaled))
            img2.show()
    except UnidentifiedImageError:
        print("Skipping")

db.close()
 

