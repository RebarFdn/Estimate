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
    spacing:float | None = None
    
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
    spacing:float = 0    

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


class Links(BaseModel):    
    type:str
    unit:str
    ftn_width:float 
    ftn_length:float    
    spacing:float = 0.2    

    @property
    def data(self):
        return Library().rebarnotes.get(self.type)  

    @property
    def length(self):
        cover = 0.025
        lap = 0.15
        return  (self.ftn_width - (cover * 2) ) + lap

    
    @property
    def link(self):        
        return {                               
                "total": round(self.ftn_length / self.spacing),
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
            'rebars': { "type": f"{self.type} ( {self.data.get('insize')}inch )", "value": round((self.length * self.link.get('total') ) / bar_length), "unit": "length"},
            'weight': { "value": round((self.length * self.link.get('total') ) * bar_weight_per_unit, 3), "unit": weight_per_unit }            

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


class StripFooting(BaseModel):
    id:str    
    unit:str | None = None
    width:float
    depth:float
    length:float
    excavation_depth:float    
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
            self.data = StripFooting( **data )           
            self.mainbars = Mainbar( **data['rebars']['main'])           
            self.links = Links( **data['rebars']['links']) 
            self.set_unit_system(self.data.unit)

    def set_unit_system(self, unit): 
        ''' Establish or convert the system of measurement units'''       
        self.units = Library().set_unit_system(unit)
    
    @property
    def concrete_type(self):
        return self.data.ctype
    
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
    def volume(self):
        return {'value': self.data.volume, 'unit': self.units.get('volume')}
    
    @property
    def excavation(self):
        return {'value': self.data.excavation, 'unit': self.units.get('volume')}
    
    @property
    def back_fill(self):
        return {'value': self.data.excavation - self.data.volume, 'unit': self.units.get('volume')}
    

    @property
    def concrete(self):
        dry_vol = self.data.volume 
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
        exclude = { "ftn_width": True, "ftn_length": True }        
        main_bars = json.loads(json.dumps(self.mainbars.bars))
        links = json.loads(json.dumps(self.links.bars))        
        main_bars['rebars']['value'] = self.mainbars.bars['rebars']['value'] # calucale the total amount of bars
        main_bars['weight']['value'] = self.mainbars.bars['weight']['value'] 
        links['rebars']['value'] = self.links.bars['rebars']['value']  # calucale the total amount of bars
        links['weight']['value'] = self.links.bars['weight']['value'] 
        main_bars['data'] = self.mainbars.model_dump()
        links['data'] = self.links.model_dump(exclude=exclude)
        links['data']['cut_length'] = round(self.links.length,2)
        links['data']['amount'] = self.links.link.get('total')
        
        
        return {
            'main': main_bars,           
            'links': links            
        }

    @property
    def report(self):  
        foundation = self.data.model_dump()
        foundation['excavation'] = self.excavation
        foundation['backfill'] = self.back_fill
        return {
        "foundation": foundation,         
        "rebars": self.rebars,        
        "concrete": self.concrete
        }
    


class SuspendedSlab(BaseModel):
    id:str   
    unit:str | None = None
    width:float
    depth:float
    length:float
    span:float
    ctype:str
    notes:str | None = None

    @property
    def volume(self):
        return round(((self.width * self.length ) * self.depth), 3)   
    
    
    @property
    def surface(self):
        return round( self.width * self.length, 2)
    

   
class Slab:
    """ Reinforced Concrete Slab """
    def __init__(self, data:dict=None):
        
        if data:
            self.data = SuspendedSlab( **data )           
            self.mainbars = Mainbar( **data['rebars']['main'])           
            self.distribution = Mainbar( **data['rebars']['dist']) 
            self.set_unit_system(self.data.unit)
            # calculate oversupport bars lengths
            omain_1 = self.mainbars.length * self.data.span 
            omain_2 = self.distribution.length * self.data.span 
            odist_1 = self.distribution.length - ( omain_2 *2 )
            odist_2 = self.mainbars.length - ( omain_1 * 2 )
            # calculate amount
            omain_1_amt = odist_1 / float(data['rebars']['omain']['spacing'])
            omain_2_amt = odist_2 / float(data['rebars']['omain']['spacing'])
            odist_1_amt = omain_1 / float(data['rebars']['odist']['spacing'])
            odist_2_amt = omain_2 / float(data['rebars']['odist']['spacing'])
            om1 = json.loads(json.dumps(data['rebars']['omain']))
            om2 = json.loads(json.dumps(data['rebars']['omain']))
            od1 = json.loads(json.dumps(data['rebars']['odist']))
            od2 = json.loads(json.dumps(data['rebars']['odist']))
            om1['length'] = omain_1
            om1['amt'] = int(omain_1_amt * 2)
            om2['length'] = omain_2
            om2['amt'] = int(omain_2_amt * 2)
            od1['length'] = odist_1
            od1['amt'] = int(odist_1_amt * 2 )
            od2['length'] = odist_2
            od2['amt'] = int(odist_2_amt * 2 )
            self.temperature_bar_1 = Mainbar( **om1 )
            self.temperature_bar_2 = Mainbar( **om2 )
            self.anticrack_bar_1 = Mainbar( **od1 )
            self.anticrack_bar_2 = Mainbar( **od2 )

            
    def set_unit_system(self, unit): 
        ''' Establish or convert the system of measurement units'''       
        self.units = Library().set_unit_system(unit)
    
    @property
    def concrete_type(self):
        return self.data.ctype
    
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
    def volume(self):
        return {'value': self.data.volume, 'unit': self.units.get('volume')}

    @property
    def formwork(self):
        return {'value': self.data.surface, 'unit': self.units.get('area')}
    
    

    @property
    def concrete(self):
        dry_vol = self.data.volume 
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
               
        main_bars = json.loads(json.dumps(self.mainbars.bars))
        dist_bars = json.loads(json.dumps(self.distribution.bars))  
        temp_bars1 = json.loads(json.dumps(self.temperature_bar_1.bars))  
        temp_bars2 = json.loads(json.dumps(self.temperature_bar_2.bars)) 
        ac_bars1 = json.loads(json.dumps(self.anticrack_bar_1.bars))  
        ac_bars2 = json.loads(json.dumps(self.anticrack_bar_2.bars)) 


        main_bars['rebars']['value'] = self.mainbars.bars['rebars']['value'] # calucale the total amount of bars
        main_bars['weight']['value'] = self.mainbars.bars['weight']['value'] 
        dist_bars['rebars']['value'] = self.distribution.bars['rebars']['value']  # calucale the total amount of bars
        dist_bars['weight']['value'] = self.distribution.bars['weight']['value'] 
        temp_bars1['rebars']['value'] = self.temperature_bar_1.bars['rebars']['value'] # calucale the total amount of bars
        temp_bars1['weight']['value'] = self.temperature_bar_1.bars['weight']['value'] 
        temp_bars2['rebars']['value'] = self.temperature_bar_2.bars['rebars']['value'] # calucale the total amount of bars
        temp_bars2['weight']['value'] = self.temperature_bar_2.bars['weight']['value'] 
        ac_bars1['rebars']['value'] = self.anticrack_bar_1.bars['rebars']['value'] # calucale the total amount of bars
        ac_bars1['weight']['value'] = self.anticrack_bar_1.bars['weight']['value'] 
        ac_bars2['rebars']['value'] = self.anticrack_bar_2.bars['rebars']['value'] # calucale the total amount of bars
        ac_bars2['weight']['value'] = self.anticrack_bar_2.bars['weight']['value'] 
       
       
        main_bars['data'] = self.mainbars.model_dump()
        dist_bars['data'] = self.distribution.model_dump()
        temp_bars1['data'] = self.temperature_bar_1.model_dump()
        temp_bars2['data'] = self.temperature_bar_2.model_dump()
        ac_bars1['data'] = self.anticrack_bar_1.model_dump()
        ac_bars2['data'] = self.anticrack_bar_2.model_dump()
        
        
        
        
        return {
            'main': main_bars,           
            'distribution': dist_bars,
            'temp_bars1': temp_bars1,
            'temp_bars2': temp_bars2,
            'ac_bars1': ac_bars1,
            'ac_bars2': ac_bars2


        }

    @property
    def report(self):  
        slab = self.data.model_dump()        
        return {
        "slab": slab,  
        "formwork": self.formwork,       
        "rebars": self.rebars,        
        "concrete": self.concrete
        }


class Floor(BaseModel):
    id:str   
    unit:str | None = None
    width:float
    depth:float
    length:float
    mesh:str | None = None
    ctype:str
    notes:str | None = None

    @property
    def volume(self):
        return round(((self.width * self.length ) * self.depth), 3)   
    
    @property
    def surface(self):
        return round( self.width * self.length, 2)
    

class ConcreteFloor:
    """ Concrete Floor """
    def __init__(self, data:dict=None):
        self.data = Floor( **data ) 
        self.set_unit_system(self.data.unit)
    
    def set_unit_system(self, unit): 
        ''' Establish or convert the system of measurement units'''       
        self.units = Library().set_unit_system(unit)
    
    @property
    def concrete_type(self):
        return self.data.ctype
    
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
    def area(self):
        return {'value': self.data.surface, 'unit': self.units.get('area')}
    
    @property
    def volume(self):
        return {'value': self.data.volume, 'unit': self.units.get('volume')}
    
    @property
    def concrete(self):
        dry_vol = self.data.volume 
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
    def reinforcement(self):
        return {
            'type': self.data.mesh,
            'area': self.area
        }    

    @property
    def report(self):  
        floor = self.data.model_dump()        
        return {
        "floor": self.data.model_dump(),               
        "reinforcement": self.reinforcement,        
        "concrete": self.concrete
        }

        

     
## _______________________________  tests ____________________

def test_rccColumn():  
    
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
    column = RCColumn( data=cdata )    
    print(column.report)



def test_foundation():  
    
    cdata = dict(   
        id = 'STF450',
        length= 6.800,
        width=.450,
        depth=.350,
        excavation_depth=1.2,
        unit='m',
        ctype='m15'   
        )
    rebars ={
        "main":{"type":"m12", "unit": cdata['unit'], "length": cdata['length'], "amt": 3},
        "links": {"type":"m10", "spacing": 0.25 , "ftn_width":cdata['width'],
        "ftn_length":cdata['length'], "unit": cdata['unit']} 
    }
    cdata['rebars'] = rebars  
    fdn = Foundation( data=cdata )    
    print('FOUNDATION REPORT', fdn.report)

if __name__ == '__main__':
    #test_rccColumn()
    test_foundation()