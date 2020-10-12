#!/usr/bin/python3

import SqliteDb
import RecipeJson
import argparse

parser = argparse.ArgumentParser(description='Import recipes from web gourmet json into sqlite db')
parser.add_argument('ids', type=int, nargs='+',
                    help='id(s) to import')
parser.add_argument('--infile',  default='recipes.grmt-web.json',
                    help='Input file (web json)')
parser.add_argument('--outfile',  default='recipes.db',
                    help='Output database file.')

args = parser.parse_args()

rec = RecipeJson.loadRecipes(args.infile)

db = SqliteDb.Db(args.outfile) 

for r in rec:
    id = RecipeJson.check(r,'id') 
    if id in args.ids : # 151: #83: # 155:
        r_dict,cat,ing = RecipeJson.parseRecipe(r)
        if  db.checkRecipe(id) :
            print( "Recipe {} found in db, skipping ...".format(id))
            continue
        print("Importing recipe {} - {}".format(id, RecipeJson.check(r,'title') )  )
        db.insertRecipe(r_dict)
        db.insertCategory(id,cat)
        db.insertIngredients(id,ing)
db.close()
 

"""
 dict_keys(['_id', 'ingredients', 'images', 'yields', 'categories', 'sources', 'times', 'text', 'alternatives', 'last_modified', 'deleted', 'categoryNames', 'sourceNames', 'id', 'owner', 'savedRemote', 'rating', 'title', 'merged', 'ingTexts', 'previousServerSaveTime', 'previousLocalServerSaveTime', 'last_remote_save'])

In [26]: i = r['ingredients']                                                   

# This is a subgroup
In [27]: i[0].keys()                                                              
Out[27]: dict_keys(['text', 'ingredients'])

# no subgroup
In [28]: i[1].keys()                                                            
Out[28]: dict_keys(['amount', 'text', 'originalText'])

# Contents of sub-group
In [31]: i[0]['ingredients'][0]                                                 
Out[31]: 
{'amount': {'amount': 0.3333333333333333,
  'textAmount': '1/3',
  'unit': 'lb',
  'standardUnit': 'lb'},
 'text': 'Italian sausage',
 'originalText': '1/3 lb Italian sausage'}

 
"""





