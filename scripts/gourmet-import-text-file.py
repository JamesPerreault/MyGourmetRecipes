#!/usr/bin/python3

import gourmet
import gourmet.ingredients
from gourmet.generic_recipe_parser import RecipeParser, parse_group
from gourmet import convert 
import glob
import re
import SqliteDb
import argparse
import traceback

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
        'description',  'rating', 'title','modifications',   None ]

tags_to_reparse = ['yields', 'category', 'cuisine', 'preptime', 'cooktime'] 
tags_number = ['yields',  'preptime', 'cooktime'] 

number_re = re.compile('([^\d]*)\s*:?\s*(\d+.*)',re.IGNORECASE)
tags_re = {'yields' : re.compile('([^\d]*)\s*:?\s*(\d+)\s+(.*)',re.IGNORECASE),
        'category' : [re.compile( '(.*)category\s?:?\s*(.*)(cuisine.*)'), 
                      re.compile( '(.*)category\s?:?\s*(.*)')], 
           'cuisine': [ re.compile( '(.*)cuisine\s?:?\s*(.*)(category.*)'), 
                      re.compile( '(.*)cuisine\s?:?\s*(.*)')], 
           'preptime': number_re, 
           'cooktime': number_re
           }

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
    new_tag = tags[new_tag] 
    if not new_tag in tags_to_reparse:
      parsed[i][1] = new_tag
      return
    # special logic for some tags
    pattern = tags_re[new_tag]
    line = parsed[i][0]
    if type(pattern) != list:  # not cuisine or cateogry, which have 2
        m = pattern.search(line)
        if m:
            if new_tag == 'yields':
                update = parser.parse_yield(m,line,new_tag)
            else:
                update = parse_group(m,line,2,new_tag)
    else:
        m = pattern[0].search(line)
        if not m:
            m = pattern[1].search(line)
        if m:
            update = parse_group(m,line,2,new_tag)
    # common update logic if a match was made
    if m and len(update) > 0:
        parsed[i] = list(update[0] )
        for u in update[1:] :
            parsed.insert(i+1,list(u))
    else:
        print("Reparsing failed\n")

        
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

def convert_times(recipe):
    conv = convert.get_converter()
    for t in ['preptime','cooktime']:
        if t in recipe and type(recipe[t])!=int:
                secs = conv.timestring_to_seconds(recipe[t])
                if secs != None:
                    recipe[t]=secs
                else:
                    del recipe[t]


def parseRecipe(parsed):

    ingr = parse_ingredients(parsed)
    category = None
    recipe = { 'instructions' : "" , 'modifications' : ""}
    for line in parsed:
        tag = line[1]
        if tag == 'category':
            category = line[0]
        elif tag == 'instructions' or tag == 'modifications':
            recipe[tag] += "\n" + line[0]
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
        except ValueError as e:
            print("Invalid number ", e)
            traceback.print_exc()
        except IndexError:
            print("Invalid index")
            traceback.print_exc()
        display(parsed)

    recipe, category, ingr = parseRecipe(parsed)
    recipe['id'] = id
    recipe['deleted'] = False 
    check_and_add(recipe,args.url,'link')
    check_and_add(recipe,args.cuisine,'cuisine')
    category = category if not args.category else args.category
    convert_times(recipe)

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
