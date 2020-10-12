
import sqlite3

class Db:
    def __init__(self, dbfile='recipes.db'):
        self.dbfile = dbfile
        self.conn = sqlite3.connect(dbfile)
        self.cursor = self.conn.cursor()
        self.max_category = self.getMaxCategory()
    def getMaxCategory(self):
        self.cursor.execute("""select max(id) from categories""") 
        row = self.cursor.fetchone()
        retval = row[0]
        return retval
    def getMaxRecipe(self):
        self.cursor.execute("""select max(id) from recipe""") 
        row = self.cursor.fetchone()
        retval = row[0]
        return retval
    def getImage(self,id):
        self.cursor.execute("select image from recipe where id = ?", [id])
        row = self.cursor.fetchone()
        retval = row[0]
        return retval
    def query(self,cmd,*arg):
        self.cursor.execute(cmd,arg)
        return  self.cursor
    def insert(self,cmd,*arg):
        self.cursor.execute(cmd,arg)
        self.conn.commit()
    def updateImage(self,id,image,thumb=None):
        if thumb == None:
            cmd = "update recipe set image = ? where id = ? "
            self.cursor.execute(cmd,[image,id])
        else:
            cmd = "update recipe set image = ?, thumb = ? where id = ? "
            self.cursor.execute(cmd,[image,thumb,id])
        self.conn.commit()
    def checkRecipe(self,id):
        self.cursor.execute("select id from recipe where id = ?", [id] ) 
        res = self.cursor.fetchone()
        return res != None 
    def insertRecipe(self, recipe):
        cmd = "insert into recipe ({}) values ( {})" .format( 
                ",".join(recipe.keys()) ,
                ",".join( [ '?' for k in recipe.keys() ] )
                )
        self.cursor.execute( cmd, list(recipe.values()) )
        self.conn.commit()
    def insertCategory(self, recipe_id, category):
        self.max_category += 1 
        cmd = "insert into categories values ( ?,?,?) "
        self.cursor.execute(cmd, [ self.max_category, recipe_id, category ] )
        self.conn.commit()
    def insertIngredients(self,recipe_id,ingredients):
        for i in ingredients:
            i['recipe_id'] = recipe_id 
            cmd = "insert into ingredients ({}) values ( {})" .format( 
                ",".join(i.keys()) ,
                ",".join( [ '?' for k in i.keys() ] )
                )
            self.cursor.execute( cmd, list(i.values()) )
            self.conn.commit()
    def close(self):
        self.cursor.close()

