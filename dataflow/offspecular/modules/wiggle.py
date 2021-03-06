"""
Wiggle correction
"""

from ... import config
from ...core import Module

def wiggle_module(id=None, datatype=None, action=None,
                 version='0.0', fields={}, xtype=None, **kwargs):
    """Module for wiggle correction"""

    icon = {
        'URI': config.IMAGES + config.ANDR_FOLDER + "wiggle.png",
        'image': config.IMAGES + config.ANDR_FOLDER + "wiggle_image.png",
        'terminals': {
            'input': (-12, 16, -1, 0),
            'output': (48, 16, 1, 0),
        }
    }
    
    xtype = 'AutosizeImageContainer'
    terminals = [
        dict(id='input',
             datatype=datatype,
             use='in',
             description='data',
             required=True,
             multiple=False,
             ),
        dict(id='output',
             datatype=datatype,
             use='out',
             description='corrected data',
             ),
    ]

    fields['amplitude'] = {
            "type":"float",
            "label": "amplitude",
            "name": "amplitude",
            "value": 0.14,
        }

    # Combine everything into a module.
    module = Module(id=id,
                  name='Wiggle',
                  version=version,
                  description=action.__doc__,
                  icon=icon,
                  terminals=terminals,
                  fields=fields,
                  action=action,
                  xtype=xtype,
                  **kwargs
                  )

    return module
