"""
Module to convert two theta to QxQz
"""

from ... import config
from ...core import Module

def two_theta_lambda_qxqz_module(id=None, datatype=None, action=None,
                 version='0.0', fields=[]):
    """Creates a module for converting two theta and lambda to qx and qz"""

    icon = {
        'URI': config.IMAGES + config.ANDR_FOLDER + "qxqz.png",
        'image': config.IMAGES + config.ANDR_FOLDER + "qxqz_image.png",
        'terminals': {
            'input': (-12, 4, -1, 0),
            'output_grid': (-12, 40, -1, 0),
            'output': (48, 16, 1, 0),
        }
    }
    
    terminals = [
        dict(id='input',
             datatype=datatype,
             use='in',
             description='data',
             required=True,
             multiple=False,
             ),
        dict(id='output_grid',
             datatype=datatype,
             use='in',
             description='output grid',
             required=False,
             multiple=False,
             ),
        dict(id='output',
             datatype=datatype,
             use='out',
             description='data with qxqz',
             ),
    ]
    
    theta_field = {
        "type":"string",
        "label": "Sample angle (theta)",
        "name": "theta",
        "value": "",
    }
    qxmin_field = {
        "type":"float",
        "label": "Qx min",
        "name": "qxmin",
        "value":-0.003,
    }
    qxmax_field = {
        "type":"float",
        "label": "Qx max",
        "name": "qxmax",
        "value": 0.003,
    }
    qxbins_field = {
        "type":"int",
        "label": "Qx bins",
        "name": "qxbins",
        "value": 201,
    }
    qzmin_field = {
        "type":"float",
        "label": "Qz min",
        "name": "qzmin",
        "value": 0.0,
    }
    qzmax_field = {
        "type":"float",
        "label": "Qz max",
        "name": "qzmax",
        "value": 0.1,
    }
    qzbins_field = {
        "type":"int",
        "label": "Qz bins",
        "name": "qzbins",
        "value": 201,
    }

    # Combine everything into a module.
    module = Module(id=id,
                  name='Two theta lambda to qxqz',
                  version=version,
                  description=action.__doc__,
                  icon=icon,
                  terminals=terminals,
                  fields=[theta_field, qxmin_field, qxmax_field, qxbins_field, qzmin_field, qzmax_field, qzbins_field] + fields,
                  action=action,
                  )

    return module
