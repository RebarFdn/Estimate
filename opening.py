# coding=utf-8
# opening.py | 10-05-2004 | Ian Moncrieffe
# Dependents

import datetime
from tinydb import TinyDB, Query
from pydantic import BaseModel
from pathlib import Path
from config import DATA_PATH 



class Opening:    
    wall_tag:str
    tag:str    
    width:float
    height:float
    amt:int
    unit:str = "m"
    def __init__(self, data:dict=None):         
        self.db = TinyDB(Path.joinpath(DATA_PATH, "wall_openings.json"))
        if data:
            self.data = data
    
    @property    
    def save(self):   
        if self.data:    
            self.db.insert(self.data)
            Wall = Query()
            return self.db.search(Wall.wall_tag == self.data.get('wall_tag'))             
        return []
    
    
    def get(self, wall_tag:str=None): 
        Wall = Query()
        try:
            return self.db.search(Wall.wall_tag == wall_tag)  
        except:
            return []
        finally:
            del(Wall)

    
    def delete(self, wall_tag:str=None): 
        Wall = Query()
        ids = [ item.doc_id for item in  self.db.search(Wall.wall_tag == wall_tag) ]
        try:              
            self.db.remove(doc_ids=ids)
            return []
        except:
            return []
        finally:
            del(Wall)
            del(ids)         
          
       

    @property
    def all(self):
        return self.db.all()
    
    