#!/usr/bin/python3

import gourmet
import gourmet.ingredients
from gourmet.generic_recipe_parser import RecipeParser
import glob
import re
import SqliteDb
import argparse

parser = argparse.ArgumentParser(description='Import recipes from text file into sqlite db')
parser.add_argument('files',  nargs="+",
                    help='Input files')
parser.add_argument('--test',action='store_true' ,
                    help="Don't insert, just display parsed recipe.")
parser.add_argument('--url', default=None,
                    help="Source url of recipe(s)")
parser.add_argument('--category', default=None,
                    help="Set category. Overrides any category in recipe text.")
parser.add_argument('--cuisine', default=None,
                    help="Set cuisine. Overrides any cuisine in recipe text.")
parser.add_argument('--dbfile',  default='recipes.db',
                    help='Output database file.')

args = parser.parse_args()

db = SqliteDb.Db(args.dbfile) 
id = db.getMaxRecipe()

if args.test:
    print("Max id is {}".format(id))

tags = [ 'ingredients', 'inggroup', 'yields', 'category', 'cuisine', 
        'source', 'link', 'preptime', 'cooktime', 'instructions', 
        'description',  'rating', 'title', None ]

def print_tags():
    i = 0 ;
    output = ""
    for tag in tags:
        output += "{} - {:14}".format(i,str(tag)) 
        if len(output) > 70:
            print(output)
            output = ""
        i += 1
    print(output)

def display(data):
    for i,items in enumerate(parsed):
        print(i,items)

def split_item(parsed, i):
    item = parsed[i]
    print(item)
    resp = input("Max splits [Enter for all]? ")
    max_splits = 0 if resp == "" else int(resp)
    items = re.split(r"\n+", item[0], max_splits) 
    if len(items) > 1:
        items = [ [ i, item[1] ] for i in items ]
        for ii in range(len(items)):
            edit_tag(items,ii)
        parsed[i] = items[0]
        for ii in range(1,len(items)):
            parsed.insert(i+ii, items[ii])

def edit_tag(parsed,i):
    if i < 0 :
        print("Invalid line number")
        return
    print_tags()
    print(parsed[i])
    new_tag = input("New tag? ")
    if new_tag == "":
        return
    new_tag = int(new_tag)
    #if new_tag < 0 or new_tag >= len(tags):
    #    print("Invalid tag number")
    #    continue
    parsed[i][1] = tags[new_tag] 
        
def parse_ingredients(parsed):
    retval = []
    i=0
    inggroup = None
    for items in parsed:
        if items[1] == 'inggroup':
            inggroup = items[0].strip()
        if items[1] == 'ingredients' :
            for ing in items[0].split("\n"):
                ing_parsed = gourmet.ingredients.parse_ingredient(ing)
                if inggroup:
                    ing_parsed['inggroup'] = inggroup
                ing_parsed['deleted'] = False
                # print(i,ing_parsed)
                retval.append( ing_parsed)
        i += 1
    return retval

def check_and_add(recipe,argv,label):
    if argv:
        recipe[label] = argv 

def parseRecipe(parsed):

    ingr = parse_ingredients(parsed)
    category = None
    recipe = { 'instructions' : "" }
    for line in parsed:
        tag = line[1]
        if tag == 'category':
            category = line[0]
        elif tag == 'instructions':
            recipe['instructions'] += "\n" + line[0]
        elif tag != None and tag != 'ingredients' and tag != 'inggroup':
            recipe[line[1]] = line[0]
    return recipe, category, ingr

for file in args.files:
    with open(file) as fp:
        lines = fp.readlines()
    id += 1

    recipe_text = "".join(lines)
    
    parser = RecipeParser()
    parsed = parser.parse(recipe_text)

    display(parsed)
    while True:
        resp = input("Enter Line number to change, commit, or quit [cq]? ") 
        try:
            if (resp == 'c' ):
                break
            elif (resp == 'q' ):
                db.close()
                exit()
            else:
                i = int(resp) 
                resp = input('Change tag (C) or split (s)? ')
                if resp == 's' :
                    split_item(parsed,i)
                elif resp == 'c' or resp == '':
                    edit_tag(parsed,i)
        except ValueError:
            print("Invalid number")
        except IndexError:
            print("Invalid index")
        display(parsed)

    recipe, category, ingr = parseRecipe(parsed)
    recipe['id'] = id
    recipe['deleted'] = False 
    check_and_add(recipe,args.url,'link')
    check_and_add(recipe,args.category,'category')
    check_and_add(recipe,args.cuisine,'cuisine')

    if args.test:
        print(category)
        print(recipe)
        print(ingr)
    else:
        db.insertRecipe(recipe)
        db.insertCategory(id,category)
        db.insertIngredients(id,ingr)
        print("Commited recipe {} - {}".format(recipe['id'], recipe['title']))

db.close()

# TODO:  fix units dictionary in ingredients module
