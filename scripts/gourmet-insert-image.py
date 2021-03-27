#!/usr/bin/python3

import SqliteDb
import RecipeJson
import argparse
from PIL import Image, UnidentifiedImageError
from io import BytesIO

parser = argparse.ArgumentParser(description='Import images in Gourmet Sqlite db')
parser.add_argument('--id', type=int, required=True,
                    help='id of recipe')
parser.add_argument('--image', required=True,
                    help='image to add')
parser.add_argument('--display',action='store_true' ,
                    help='Display scaled images')
parser.add_argument('--dbfile',  default='recipes.db',
                    help='Database file.')
parser.add_argument('--icon_only',  action='store_true' ,
                    help='Only scale the image and insert the recipe icon.')
parser.add_argument('--no_icon',  action='store_true' , 
                    help='Only scale the image and insert the recipe icon.')

args = parser.parse_args()

db = SqliteDb.Db(args.dbfile) 

img = Image.open(args.image) 
scaled = RecipeJson.scale_image(img)
if args.no_icon:
    thumb = None
else:
    thumb = RecipeJson.generate_thumbnail (scaled) 
if args.icon_only:
    db.updateThumb(args.id,thumb)
else:
    db.updateImage(args.id,scaled,thumb)
if args.display:
    for data in [scaled, thumb]:
        if data != None:
            img2 = Image.open(BytesIO(data))  
            img2.show()

db.close()
 

