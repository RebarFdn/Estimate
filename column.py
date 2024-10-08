# Column.py
from pydantic import BaseModel

try:
    from elibrary import Library
except:
    from modules.Estimate.elibrary import Library


class Column(BaseModel):
    id:str
    unit:str | None = None
    width:float
    bredth:float
    height:float
    amt:int

    @property
    def volume(self):
        return round(((self.width * self.bredth ) * self.height),3)
    
    @property
    def girth(self):
        return round(( self.width * 2) + (self.bredth * 2),2)
    
    @property
    def surface(self):
        return self.girth * self.height
    

class Mainbar(BaseModel):
    type:str
    unit:str
    length:float = 0
    amt:int = 0
    
    @property
    def data(self):
        return Library().rebarnotes.get(self.type)    
    
    @property
    def cut_length(self):
        if float(self.length) < 9.0:
            return { "value": float(self.length), "unit": self.unit }
        else:
            return { "value": 9.0, "unit": self.unit }


    @property
    def bars(self):
        if self.unit == 'm':
            bar_length = self.data.get('standard_length').get('metric').get('value')
            bar_weight_per_unit = self.data.get('weight').get('metric').get('value')
            weight_per_unit = 'kg'

        else:
            bar_length = self.data.get('standard_length').get('imperial').get('value')
            bar_weight_per_unit = self.data.get('weight').get('imperial').get('value')
            weight_per_unit = 'lb'
        
        return {
            'rebars': { "type": f"{self.type} ( {self.data.get('insize')}inch )", "value": round((self.length * self.amt ) / bar_length), "unit": "length"},
            'weight': { "value": round((self.length * self.amt ) * bar_weight_per_unit, 3), "unit": weight_per_unit }            

        }


class Stirup(BaseModel):
    type:str
    unit:str
    clm_width:float
    clm_bredth:float
    clm_height:float
    span:float | None = None 
    support_spacing:float | None = None 
    spacing:float = 0.2

    @property
    def length(self):
        cover = 0.025
        lap = 0.1
        return ( (self.clm_bredth - (cover * 2) )* 2 ) + ((self.clm_width - (cover * 2)) * 2 ) + lap

    @property
    def over_support(self):
        if self.span:
            return self.clm_height * self.span
        return 0

    @property
    def stirups(self):
        if self.span and self.support_spacing:
            support_length = self.over_support * 2
            support_stirups = support_length / self.support_spacing
            main_stirups = (self.clm_height - support_length) / self.spacing
            return {
                "main": round(main_stirups), 
                "support": round(support_stirups), 
                "total": round(main_stirups + support_stirups),
                "length": self.length
                }
        else:
            main_stirups = round(self.clm_height / self.spacing)
            return {
                "main": main_stirups,                
                "total": main_stirups,
                "length": self.length
                }






    

cdata = dict(   
    id = 'C121',
    height= 3.800,
    width=.402,
    bredth=.450,
    amt=3,
    unit='m'    
    )


def test():    
    column = Column(**cdata)
    
    data = {
        "column": column.model_dump(),
        "volume": column.volume,
        "girth": column.girth,
        "surface": column.surface
        


    }
    print(data)




rebars ={
    "main":{"type":"m16", "unit": "m", "length": 4.5, "amt": 4},
    "stirup": {"type":"m10", "spacing": 0.25 , "clm_width":cdata['width'],
    "clm_bredth":cdata['bredth'], "clm_height":cdata['height'], "span": 0.3, "support_spacing": 0.1, "unit": "m"} 
}

bars = Mainbar(**rebars['main'])  
stirup = Stirup(**rebars['stirup'])

print(bars.bars)
print(stirup.stirups)

if __name__ == '__main__':
    test()