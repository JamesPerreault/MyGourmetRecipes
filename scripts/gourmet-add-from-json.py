#!/usr/bin/python3

import SqliteDb
import RecipeJson
import argparse
import json

parser = argparse.ArgumentParser(description='Import recipes from web gourmet json into sqlite db')
parser.add_argument('files',  nargs="+",
                    help='Input files(json)')
parser.add_argument('--outfile',  default='recipes.db',
                    help='Output database file.')

args = parser.parse_args()

db = SqliteDb.Db(args.outfile) 
id = db.getMaxRecipe()

for file in args.files:
    with open(file) as fp:
        recipe = json.load(fp)
    id += 1

    recipe['id'] = id
    r_dict,cat,ing = RecipeJson.parseRecipe(recipe)
    if  db.checkRecipe(id) :
        print( "Recipe {} found in db, skipping ...".format(id))
        continue
    print("Importing recipe {} - {}".format(id, RecipeJson.check(recipe,'title') )  )
    db.insertRecipe(r_dict)
    db.insertCategory(id,cat)
    db.insertIngredients(id,ing)

db.close()
 

