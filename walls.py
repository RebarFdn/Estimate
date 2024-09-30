# walls 
from pydantic import BaseModel


class BlockWall(BaseModel):
    tag:str
    thickness:float
    length:float
    height:float
    unit:str = "m"

    @property
    def area(self):
        return self.length * self.height


data = {'tag': "W1", "thickness":0.150, "length": 5.0, "height": 4.5, 'unit': 'm'}

wall = BlockWall( **data )
print(wall)