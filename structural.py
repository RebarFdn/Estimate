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
    ctype:str

    @property
    def volume(self):
        return round(((self.width * self.bredth ) * self.height),3)
    
    @property
    def girth(self):
        return round(( self.width * 2) + (self.bredth * 2),2)
    
    @property
    def surface(self):
        return self.girth * self.height

   

class Beam(BaseModel):
    id:str
    beam_type:str
    unit:str | None = None
    width:float
    depth:float
    length:float
    amt:int
    ctype:str

    @property
    def volume(self):
        return round(((self.width * self.depth ) * self.length), 3)
    
    @property
    def girth(self):
        if self.beam_type == 'suspended':
            return round( self.width + (self.depth * 2), 2)
        else:
            return round( self.depth * 2,2)

    
    @property
    def surface(self):
        return round( self.girth * self.length, 2)
    
  

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
    """ Reinforced Concrete Column """
    def __init__(self, data:dict=None):
        
        if data:
            self.data = Column( **data )
            data['rebars']['main']["length"] = self.data.height
            self.mainbars = Mainbar( **data['rebars']['main'])
            self.stirups = Stirup( **data['rebars']['stirup'])              
            self.set_unit_system(self.data.unit)

    def set_unit_system(self, unit): 
        ''' Establish or convert the system of measurement units'''       
        self.units = Library().set_unit_system(unit)
    
    @property
    def concrete_type(self):
        return self.data.ctype
    
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
        return {"value": round(self.data.surface * self.data.amt,2), "unit": self.units.get('area')}

    @property
    def concrete(self):
        dry_vol = self.data.volume * self.data.amt
        data = Library().concrete_types.get(self.concrete_type)
        legend = Library().concrete_types.get('legend')
        wet_volume_factor = legend.get("wet_volume_factor")
        bag_weight = legend.get("bag_weight")
        
        report = {
           'dry_volume': {'value': dry_vol, 'unit': self.units.get('volume')},
           "wet_volume":  {'value': dry_vol * wet_volume_factor,  'unit': self.units.get('volume')},
           "cement": {'value': round(data.get('material').get('cement')[0] * dry_vol,3), 'unit': 'kg',
                      "bag": {'value': 0, 'unit': 'bag'}
                      },
           "fine_agg": {'value': round(data.get('material').get('fine_agg')[0] * dry_vol,3), 'unit': 'kg'},
           "course_agg": {'value': round(data.get('material').get('course_agg')[0] * dry_vol,3), 'unit': 'kg'},
           "water": {'value': round(data.get('material').get('water',(190, 'liter'))[0] * dry_vol,3), 'unit': 'liters'}
        }
        report['cement']['bag']['value'] = round((report['cement']['value'] / bag_weight[0]) + 0.5)
        return report
        
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
        stirups['data']['cut_length'] = round(self.stirups.length,2)
        stirups['data']['amount'] = self.stirups.stirups.get('total')
        
        
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



class RCBeam:
    """ Reinforced Concrete Beam """
    def __init__(self, data:dict=None):
        
        if data:
            self.data = Beam( **data )           
            self.mainbars = Mainbar( **data['rebars']['main'])           
            self.stirups = Stirup( **data['rebars']['stirup']) 
            if len(data['rebars'].get('extra'))  > 0:
                self.extrabars = Mainbar( **data['rebars']['extra'])      
            else: 
                self.extrabars = None       
            self.set_unit_system(self.data.unit)

    def set_unit_system(self, unit): 
        ''' Establish or convert the system of measurement units'''       
        self.units = Library().set_unit_system(unit)
    
    @property
    def concrete_type(self):
        return self.data.ctype
    
    @property
    def amt(self):
        return {'value': self.data.amt, 'unit': 'each'}

    @property
    def depth(self):
        return {'value': self.data.depth, 'unit': self.units.get('length')}

    @property
    def width(self):
        return {'value': self.data.width, 'unit': self.units.get('length')}

    @property
    def length(self):
        return {'value': self.data.length, 'unit': self.units.get('length')}

    @property
    def formwork(self):
        return {"value": round(self.data.surface * self.data.amt,2), "unit": self.units.get('area')}

    @property
    def concrete(self):
        dry_vol = self.data.volume * self.data.amt
        data = Library().concrete_types.get(self.concrete_type)
        legend = Library().concrete_types.get('legend')
        wet_volume_factor = legend.get("wet_volume_factor")
        bag_weight = legend.get("bag_weight")        
        report = {
           'dry_volume': {'value': dry_vol, 'unit': self.units.get('volume')},
           "wet_volume":  {'value': dry_vol * wet_volume_factor,  'unit': self.units.get('volume')},
           "cement": {'value': round(data.get('material').get('cement')[0] * dry_vol,3), 'unit': 'kg',
                      "bag": {'value': 0, 'unit': 'bag'}
                      },
           "fine_agg": {'value': round(data.get('material').get('fine_agg')[0] * dry_vol,3), 'unit': 'kg'},
           "course_agg": {'value': round(data.get('material').get('course_agg')[0] * dry_vol,3), 'unit': 'kg'},
           "water": {'value': round(data.get('material').get('water',(190, 'liter'))[0] * dry_vol,3), 'unit': 'liters'}
        }
        report['cement']['bag']['value'] = round((report['cement']['value'] / bag_weight[0]) + 0.5)
        return report
        
    @property
    def rebars(self):
        exclude = { "clm_width": True, "clm_bredth": True, "clm_height": True }
        if not self.stirups.span or not self.stirups.support_spacing:
            exclude["span"] = True
            exclude["support_spacing"] = True
        main_bars = json.loads(json.dumps(self.mainbars.bars))
        stirups = json.loads(json.dumps(self.stirups.bars))
        if self.extrabars:
            extra_bars = json.loads(json.dumps(self.extrabars.bars))
            extra_bars['rebars']['value'] = self.extrabars.bars['rebars']['value'] * self.data.amt # calucale the total amount of bars
            extra_bars['weight']['value'] = self.extrabars.bars['weight']['value'] * self.data.amt
            extra_bars['data'] = self.extrabars.model_dump()
        else:
            extra_bars = None
        main_bars['rebars']['value'] = self.mainbars.bars['rebars']['value'] * self.data.amt # calucale the total amount of bars
        main_bars['weight']['value'] = self.mainbars.bars['weight']['value'] * self.data.amt
        stirups['rebars']['value'] = self.stirups.bars['rebars']['value'] * self.data.amt # calucale the total amount of bars
        stirups['weight']['value'] = self.stirups.bars['weight']['value'] * self.data.amt
        main_bars['data'] = self.mainbars.model_dump()
        stirups['data'] = self.stirups.model_dump(exclude=exclude)
        stirups['data']['cut_length'] = round(self.stirups.length,2)
        stirups['data']['amount'] = self.stirups.stirups.get('total')
        
        
        return {
            'main': main_bars,
            'extra': extra_bars,
            'stirups': stirups            
        }

    @property
    def report(self):
        
        return {
        "beam": self.data.model_dump(),         
        "rebars": self.rebars,     
        "formwork": self.formwork,
        "concrete": self.concrete
        }


class Footing(BaseModel):
    id:str
    footing_type:str
    unit:str | None = None
    width:float
    depth:float
    length:float
    excavation_depth:float
    amt:int
    ctype:str

    @property
    def volume(self):
        return round(((self.width * self.depth ) * self.length), 3)
    
    @property
    def excavation(self):
        return round(((self.width * self.excavation_depth ) * self.length), 3)

    
class Foundation:
    """ Reinforced Concrete Foundation """
    def __init__(self, data:dict=None):
        
        if data:
            self.data = Footing( **data )           
            self.mainbars = Mainbar( **data['rebars']['main'])           
            self.stirups = Stirup( **data['rebars']['stirup']) 
            if len(data['rebars'].get('extra'))  > 0:
                self.extrabars = Mainbar( **data['rebars']['extra'])      
            else: 
                self.extrabars = None       
            self.set_unit_system(self.data.unit)

    def set_unit_system(self, unit): 
        ''' Establish or convert the system of measurement units'''       
        self.units = Library().set_unit_system(unit)
    
    @property
    def concrete_type(self):
        return self.data.ctype
    
    @property
    def amt(self):
        return {'value': self.data.amt, 'unit': 'each'}

    @property
    def depth(self):
        return {'value': self.data.depth, 'unit': self.units.get('length')}
    
    @property
    def excavation_depth(self):
        return {'value': self.data.excavation_depth, 'unit': self.units.get('length')}

    @property
    def width(self):
        return {'value': self.data.width, 'unit': self.units.get('length')}

    @property
    def length(self):
        return {'value': self.data.length, 'unit': self.units.get('length')}

    @property
    def concrete(self):
        dry_vol = self.data.volume * self.data.amt
        data = Library().concrete_types.get(self.concrete_type)
        legend = Library().concrete_types.get('legend')
        wet_volume_factor = legend.get("wet_volume_factor")
        bag_weight = legend.get("bag_weight")        
        report = {
           'dry_volume': {'value': dry_vol, 'unit': self.units.get('volume')},
           "wet_volume":  {'value': dry_vol * wet_volume_factor,  'unit': self.units.get('volume')},
           "cement": {'value': round(data.get('material').get('cement')[0] * dry_vol,3), 'unit': 'kg',
                      "bag": {'value': 0, 'unit': 'bag'}
                      },
           "fine_agg": {'value': round(data.get('material').get('fine_agg')[0] * dry_vol,3), 'unit': 'kg'},
           "course_agg": {'value': round(data.get('material').get('course_agg')[0] * dry_vol,3), 'unit': 'kg'},
           "water": {'value': round(data.get('material').get('water',(190, 'liter'))[0] * dry_vol,3), 'unit': 'liters'}
        }
        report['cement']['bag']['value'] = round((report['cement']['value'] / bag_weight[0]) + 0.5)
        return report
        
    @property
    def rebars(self):
        exclude = { "clm_width": True, "clm_bredth": True, "clm_height": True }
        if not self.stirups.span or not self.stirups.support_spacing:
            exclude["span"] = True
            exclude["support_spacing"] = True
        main_bars = json.loads(json.dumps(self.mainbars.bars))
        stirups = json.loads(json.dumps(self.stirups.bars))
        if self.extrabars:
            extra_bars = json.loads(json.dumps(self.extrabars.bars))
            extra_bars['rebars']['value'] = self.extrabars.bars['rebars']['value'] * self.data.amt # calucale the total amount of bars
            extra_bars['weight']['value'] = self.extrabars.bars['weight']['value'] * self.data.amt
            extra_bars['data'] = self.extrabars.model_dump()
        else:
            extra_bars = None
        main_bars['rebars']['value'] = self.mainbars.bars['rebars']['value'] * self.data.amt # calucale the total amount of bars
        main_bars['weight']['value'] = self.mainbars.bars['weight']['value'] * self.data.amt
        stirups['rebars']['value'] = self.stirups.bars['rebars']['value'] * self.data.amt # calucale the total amount of bars
        stirups['weight']['value'] = self.stirups.bars['weight']['value'] * self.data.amt
        main_bars['data'] = self.mainbars.model_dump()
        stirups['data'] = self.stirups.model_dump(exclude=exclude)
        stirups['data']['cut_length'] = round(self.stirups.length,2)
        stirups['data']['amount'] = self.stirups.stirups.get('total')
        
        
        return {
            'main': main_bars,
            'extra': extra_bars,
            'stirups': stirups            
        }

    @property
    def report(self):
        
        return {
        "beam": self.data.model_dump(),         
        "rebars": self.rebars,     
        "formwork": self.formwork,
        "concrete": self.concrete
        }


    
    

cdata = dict(   
    id = 'C121',
    height= 6.800,
    width=.402,
    bredth=.450,
    amt=5,
    unit='m',
    ctype='m15'   
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