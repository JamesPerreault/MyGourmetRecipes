#!/usr/bin/python3

import json
import base64
from io import BytesIO
from PIL import Image


def loadRecipes(fname='recipes.grmt-web.json'):
    with open(fname) as fp:
        recipes = json.load(fp)
    return recipes['recipes']

def check(record,field):
    if field in record:
        return record[field]
    return ""

def safe_get_and_set(out_dict, in_dict, in_field, out_field=None) :
    if out_field == None:
        out_field = in_field 
    if in_field in in_dict:
        out_dict[out_field] = in_dict[in_field] 

def parseIngredients(ingredients):
    ing_list = [] 
    for ing in ingredients:
        if 'ingredients' in ing:
            subgroup = ing['text']
            subings = parseIngredients(ing['ingredients']) ;
            for i in subings:
                i['inggroup'] = subgroup
            ing_list.extend(subings)
        else:
            amt = ing['amount'] 
            i = { 'item' : ing['text'], 'deleted' : False, 'optional' : False } 
            safe_get_and_set(i,amt,'unit')
            safe_get_and_set(i,amt,'amount')
            safe_get_and_set(i,amt,'rangeamount')
            safe_get_and_set(i,ing,'optional')
            ing_list.append(i)
    return ing_list

def parseSources(out_dict, in_dict):
    if 'sources' in in_dict:
        sources = in_dict['sources']
        if len(sources) > 0:
            safe_get_and_set(out_dict,sources[0],'name','source')
            safe_get_and_set(out_dict,sources[0],'url','link')

def parseCategory(out_dict, in_dict):
    category = None
    if 'categories' in in_dict:
        categories = in_dict['categories']
        for c in categories:
            name = c['name'] 
            if 'type' in c and c['type'] == 'cuisine':
                out_dict['cuisine'] = name.capitalize()
            elif name.startswith('CUISINE'):
                out_dict['cuisine'] = name.replace('CUISINE:','').strip().capitalize()
            else:
                category = c['name']
    return category 

def parseTimes(out_dict, in_dict):
    if 'times' in in_dict:
        times = in_dict['times']
        for t in times:
            name = t['name'].lower()
            if name.find('prep') >= 0 :
                out_dict['preptime'] = t['seconds']
            if name.find('cook') >= 0 :
                out_dict['cooktime'] = t['seconds']

def parseYields(out_dict, in_dict):
    if 'yields' in in_dict:
        yields = in_dict['yields']
        if len(yields) > 0 and 'amount' in yields[0]:
            out_dict['yields'] = yields[0]['amount']
            safe_get_and_set(out_dict,yields[0],'unit','yield_unit')
            if 'yield_unit' in out_dict:
                out_dict['yield_unit'] = out_dict['yield_unit'].lower()

def parseText(out_dict, in_dict):
    if 'text' in in_dict:
        text = in_dict['text']
        for t in text:
            if t['header'].startswith( 'Modifications'):
                out_dict['description'] = t['body']
            elif t['header'].startswith('Instructions'):
                out_dict['instructions'] = t['body']

def decode_image(data):
    b64 = data.split(',',2)[1]
    image = base64.b64decode(b64)
    stream = BytesIO(image)
    img = Image.open(stream)
    with BytesIO() as output:
        img.save(output, format="JPEG")
        img_jpeg = output.getvalue() 
    stream.close()
    return img_jpeg

def generate_thumbnail(image):
    stream = BytesIO(image)
    img = Image.open(stream)
    img.thumbnail((30,30))  # edits image in place

    with BytesIO() as output:
        img.save(output, format="JPEG")
        thumb = output.getvalue() 
    stream.close()
    return thumb

def scale_image(image):
    stream = False
    if type(image) != bytes:
        img = image
    else:
        stream = BytesIO(image)
        img = Image.open(stream)
    lth, width = img.size
    aspect = False
    if lth > 300:
        aspect = lth/300 
        lth,width = lth/aspect, width/aspect
    if width > 176:
        aspect = width/176 
        lth,width = lth/aspect, width/aspect
    if aspect:
        scale = int(lth),int(width)
        with BytesIO() as output:
            img.resize(scale).save(output, format="JPEG")
            image = output.getvalue() 
    if stream:
        stream.close()
    
    return image

def parseImages(out_dict, in_dict) :
    if 'images' in in_dict:
        images = in_dict['images']
        if len(images) > 0 :
            for label,data in images[0].items():
                if label == 'url':
                    image = decode_image(data) 
                    out_dict['image'] = scale_image(data) 
                elif label == 'thumbnailUrl':
                    out_dict['thumb'] = decode_image(data) 
            if 'thumb' not in out_dict:
                out_dict['thumb'] = generate_thumbnail(out_dict['image'])
         

def parseRecipe( in_dict):
    recipe = {'deleted': False}
    recipe['id'] = in_dict['id']
    recipe['title'] = in_dict['title'] 
    safe_get_and_set(recipe,in_dict,'rating')
    parseSources(recipe,in_dict) # source, link
    category = parseCategory(recipe,in_dict) # cateogry, cuisine
    parseTimes(recipe,in_dict) # preptime, cooktime
    parseYields(recipe,in_dict) # yields, yield_unit, servings?
    parseText(recipe,in_dict) # instructions, description
    parseImages(recipe,in_dict) # image, thumb
    ingredients = parseIngredients(in_dict['ingredients'])
    return recipe,category,ingredients 

