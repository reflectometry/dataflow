"""
For TripleAxis, normalize monitor
"""

from ... import config
from ...core import Module

def normalize_monitor_module(id=None, datatype=None, action=None,
                             version='0.0', fields={},
                             description="apply TripleAxis monitor normalization", **kwargs):
    """
    Return a module for normalizing a TripleAxis monitor
    """

    icon = {
        'URI': config.IMAGES + 'TAS/monitor_normalization.png', 
        'image': config.IMAGES + 'TAS/monitor_normalization.png',
        'width': 'auto', 
        'terminals': {
            'input': (-12, 16, -1, 0),
            'output': (48, 16, 1, 0),
        }
    }
    
    
    terminals = [
        dict(id='input',
             datatype=datatype,
             use='in',
             description='TripleAxis object and target monitor input',
             required=False,
             multiple=False,
             ),
        dict(id='output',
             datatype=datatype,
             use='out',
             description='TripleAxis object with normalized monitor',
             ),
    ]
    
    fields['target_monitor'] = {
        "type": "float",
        "label": "Target monitor",
        "name": "target_monitor",
        "value": None,
    }
    
    # Combine everything into a module.
    module = Module(id=id,
                  name='Normalize Monitor',
                  version=version,
                  description=description,
                  icon=icon,
                  terminals=terminals,
                  fields=fields,
                  action=action,
                  **kwargs
                  )

    return module
