"""
Return transmission based on bottom left and top right coordinates
"""

from .. import config
from ..core import Module
from ..SANS.map_pics import map_pics
def generate_transmission_module(id=None, datatype=None, action=None,
                 version='0.0', fields={}, **kwargs):
    """Return transmission based on bottom left and top right coordinates"""

    icon = {
        'URI': config.IMAGES + "SANS/gen_trans.png",
	'image': config.IMAGES + "SANS/gen_trans_image.png",
        'terminals': {
            #inputs
            'sample_in': (-16, 5, -1, 0),
            'empty_cell_in': (-16, 15, -1, 0),
            'empty_in': (-16, 25, -1, 0),
            'Tsam_in': (-16, 35, -1, 0),
            'Temp_in': (-16, 45, -1, 0),
            
            'sample_out': (48, 10, 1, 0),
            'empty_cell_out': (48, 30, 1, 0),
            #'empty_out': (20, 10, 1, 0),
            #'trans': (20, 10, 1, 0),
        }
    }
    
    terminals = [
        dict(id='sample_in',
             datatype=datatype,
             use='in',
             description='data',
             required=False,
             multiple=False,
             ),
        dict(id='empty_cell_in',
             datatype=datatype,
             use='in',
             description='data',
             required=False,
             multiple=False,
             ),
        dict(id='empty_in',
             datatype=datatype,
             use='in',
             description='data',
             required=False,
             multiple=False,
             ),
        dict(id='Tsam_in',
             datatype=datatype,
             use='in',
             description='data',
             required=False,
             multiple=False,
             ),
        dict(id='Temp_in',
             datatype=datatype,
             use='in',
             description='data',
             required=False,
             multiple=False,
             ),
        
        
        dict(id='sample_out',
             datatype=datatype,
             use='out',
             description='correct',
             ),
        dict(id='empty_cell_out',
             datatype=datatype,
             use='out',
             description='correct',
             ),
        #dict(id='empty_out',
             #datatype=datatype,
             #use='out',
             #description='correct',
             #),
        #dict(id='trans',
             #datatype=datatype,
             #use='out',
             #description='correct',
             #),
    ]
    fields['monitorNormalize'] ={
        'type' :'float',
        'label':'Monitor Normalization Count (default=1e8)',
        'name' :'monitorNormalize',
        'value':1e8,
        
        }
    fields['bottomLeftCoord'] = {
        'type' :'object',
        'label':'Bottom Left Coordinate',
        'name' :'bottomLeftCoord',
        'value':{'X': 
                    {'type': 'float', 'value': 0, 'label': 'X'}, 
                 'Y':
                    {'type': 'float', 'value': 0, 'label': 'Y'}}
        }
    fields['topRightCoord'] = {
        'type' :'object',
        'label':'Top Right Coordinate',
        'name' :'topRightCoord',
        'value':{'X': 
                    {'type': 'float', 'value': 0, 'label': 'X'}, 
                 'Y':
                    {'type': 'float', 'value': 0, 'label': 'Y'}}
        }
    # Combine everything into a module.
    module = Module(id=id,
                  name='Generate Transmission',
                  version=version,
                  description=action.__doc__,
                  icon=icon,
                  terminals=terminals,
                  fields=fields,
                  action=action,
                  **kwargs
                  )

    return module
