"""
Applies footprint correction to data set
"""

from ... import config
from ...core import Module

def footprint_module(id=None, datatype=None, action=None,  # Footprint module constructor
                    version='0.0', fields=[], xtype=None, filterModule=None):
    """Module for correcting a dataset"""
    
    icon = {  # how the module will look
        'URI': config.IMAGES + config.ANDR_FOLDER + 'autogrid.png',
        'image': config.IMAGES + config.ANDR_FOLDER + 'autgrid_image.png',
        'terminals': {
            'input': (None, None, -1, 0),
            'output': (None, None, 1, 0)
        }
    }
    
    terminals = [   # the terminals of the module where the wires connect
        dict(id='input',
            datatype=datatype,
            use='in',
            description='original data',
            required=True,
            multiple=False,
            ),
        dict(id='output',
            datatype=datatype,
            use='out',
            description='corrected data',
            direction=[1,0]
            )
    ]
    
    fields = {  # fields that will appear when user right clicks module
        "beginning": {
            "type":"string",
            "label":"Beginning of Interval",
            "name":"beginning",
            "value":""},
        "end": {
            "type":"string",
            "label":"End of Interval",
            "name":"end",
            "value":""},
        "slope": {
            "type":"string",
            "label":"Slope of Line",
            "name":"slope",
            "value":""},
        "intercept": {
            "type":"string",
            "label":"y-Intercept",
            "name":"intercept",
            "value":""}
    }
    
    module = Module(id=id,  # creates customized module 
                    name='Footprint Data',
                    version=version,
                    description=action.__doc__,
                    icon=icon,
                    terminals=terminals,
                    fields=fields,
                    action=action,
                    filterModule=filterModule,
                    xtype=xtype
                    )
    module.LABEL_WIDTH = 150
    return module
