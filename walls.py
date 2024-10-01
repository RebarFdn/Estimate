# walls 
from pydantic import BaseModel
from elibrary import Library

# DAta sources

openings = [
    {'tag': 'window-1', "width": 1.6, "height": 1.2, "amt": 2, 'unit': 'm'},
    {'tag': 'window-2', "width": .6, "height": .6, "amt": 1, 'unit': 'm'},
    {'tag': 'door-1', "width": 0.96, "height": 2.1, "amt": 1, 'unit': 'm'},
]
data = {'tag': "W1", "thickness":0.150, "length": 6.0, "height": 4.5, 'unit': 'm', "openings": openings}


class BlockWall(BaseModel):
    tag:str
    thickness:float
    length:float
    height:float
    unit:str = "m"

    @property
    def area(self):
        return self.length * self.height 


class Opening(BaseModel):
    tag:str    
    width:float
    height:float
    amt:int
    unit:str = "m"

    @property
    def area(self):
        return ( self.width * self.height ) * self.amt 
    
    @property
    def jamb(self):
        if 'W' in self.tag or 'w' in self.tag or 'window' in self.tag:
            return ( ( self.width * 2 ) + ( self.height * 2 ) ) * self.amt 
        else:
            return ( self.width + ( self.height * 2 ) ) * self.amt 
            
       

class Wall:
    def __init__(self, data:dict=None):
        if data:
            self.data=BlockWall( **data )
            self.openings = [ Opening( **item ) for item in data.get('openings') ]
            self.set_unit_system(self.data.unit)
            if self.units.get('length') == 'm':
                self.cmu = {
                    "length": {"unit": 'm', "value": 0.4},
                    "depth": {"unit": 'm', "value": 0.2}
                }
            else:
                self.cmu = {
                    "length": {"unit": 'ft', "value": 1.33},
                    "depth": {"unit": 'ft', "value": 0.667}
                }
            self.cmu['area'] = round(self.cmu.get('length').get('value') * self.cmu.get('depth').get('value'),3)

    def set_unit_system(self, unit): 
        ''' Establish or convert the system of measurement units'''       
        self.units = Library().set_unit_system(unit)

    @property
    def length(self):
        return {
            "value": self.data.length,
            "unit": self.units.get('length')
        }
    
    @property
    def height(self):
        return {
            "value": self.data.height,
            "unit": self.units.get('length')
        }
        
    
    @property
    def area(self):
        return {
            "value": (self.data.length * self.data.height) - sum([ opening.area for opening in self.openings ]),
            "unit": self.units.get('area')
        }
    

    @property 
    def blocks(self):
        
        return {
            "value": round(self.area.get('value') / self.cmu.get('area')),
            "unit": 'Each'
        }
    
    @property 
    def rough_cast(self):        
        return {
            "value": self.area.get('value') * 2,
            "unit": self.units.get('area')
        }
    

    @property 
    def render(self):        
        return {
            "value": self.area.get('value') * 2,
            "unit": self.units.get('area')
        }
    
    @property
    def cut_out(self):
        return {
            "value": sum([ opening.area for opening in self.openings ]),
            "unit": self.units.get('area')
        }
    
    @property
    def flat_jamb(self):
        return {
            "value": round(sum([ opening.jamb for opening in self.openings ]),2),
            "unit": self.units.get('length')
        }
    




wall = Wall( data=data )
print(wall.blocks)