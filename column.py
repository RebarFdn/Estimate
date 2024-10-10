# Column.py
import json
from pydantic import BaseModel, Field
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
    def data(self):
        return Library().rebarnotes.get(self.type)  

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
            'rebars': { "type": f"{self.type} ( {self.data.get('insize')}inch )", "value": round((self.length * self.stirups.get('total') ) / bar_length), "unit": "length"},
            'weight': { "value": round((self.length * self.stirups.get('total') ) * bar_weight_per_unit, 3), "unit": weight_per_unit }            

        }



class RCColumn:
    """ ReinforcedConcreteColumn """
    def __init__(self, data:dict=None):
        
        if data:
            self.data = Column( **data )
            self.mainbars = Mainbar( **data['rebars']['main'])
            self.stirups = Stirup( **data['rebars']['stirup'])              
            self.set_unit_system(self.data.unit)

    def set_unit_system(self, unit): 
        ''' Establish or convert the system of measurement units'''       
        self.units = Library().set_unit_system(unit)
    
    @property
    def amt(self):
        return {'value': self.data.amt, 'unit': 'each'}

    @property
    def bredth(self):
        return {'value': self.data.bredth, 'unit': self.units.get('length')}

    @property
    def width(self):
        return {'value': self.data.width, 'unit': self.units.get('length')}

    @property
    def height(self):
        return {'value': self.data.height, 'unit': self.units.get('length')}

    @property
    def formwork(self):
        return {"value": self.data.surface * self.data.amt, "unit": self.units.get('area')}

    @property
    def concrete(self):
        vol = self.data.volume * self.data.amt
        
        return {'value': vol, 'unit': self.units.get('volume')}
        
    @property
    def rebars(self):
        exclude = { "clm_width": True, "clm_bredth": True, "clm_height": True }
        if not self.stirups.span or not self.stirups.support_spacing:
            exclude["span"] = True
            exclude["support_spacing"] = True
        main_bars = json.loads(json.dumps(self.mainbars.bars))
        stirups = json.loads(json.dumps(self.stirups.bars))
        main_bars['rebars']['value'] = self.mainbars.bars['rebars']['value'] * self.data.amt # calucale the total amount of bars
        main_bars['weight']['value'] = self.mainbars.bars['weight']['value'] * self.data.amt

        stirups['rebars']['value'] = self.stirups.bars['rebars']['value'] * self.data.amt # calucale the total amount of bars
        stirups['weight']['value'] = self.stirups.bars['weight']['value'] * self.data.amt
        main_bars['data'] = self.mainbars.model_dump()
        stirups['data'] = self.stirups.model_dump(exclude=exclude)
        return {
            'main': main_bars,
            'stirups': stirups            
        }

    @property
    def report(self):
        
        return {
        "column": self.data.model_dump(),         
        "rebars": self.rebars,     
        "formwork": self.formwork,
        "concrete": self.concrete
    }


    

cdata = dict(   
    id = 'C121',
    height= 3.800,
    width=.402,
    bredth=.450,
    amt=3,
    unit='m'    
    )


rebars ={
    "main":{"type":"m16", "unit": "m", "length": 4.5, "amt": 4},
    "stirup": {"type":"m10", "spacing": 0.25 , "clm_width":cdata['width'],
    "clm_bredth":cdata['bredth'], "clm_height":cdata['height'], "span": 0.25, "support_spacing": 0.11, "unit": "m"} 
}
cdata['rebars'] = rebars

def test():    
    column = RCColumn( data=cdata )
    
    
    print(column.report)



if __name__ == '__main__':
    test()