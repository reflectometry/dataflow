"""
Load data sets.
"""

import tarfile
import os

from .. import config
from ...apps.tracks.models import File
from ..core import Module
from ..core import lookup_datatype

def load_action(files=[], **kwargs):
    print "loading saved results"
    result = []
    for fn in files:
        print 'fn: ', fn
        Fileobj = File.objects.get(name=os.path.basename(fn))
        #fn = Fileobj.name
        cls = lookup_datatype(Fileobj.datatype).cls

        fn = Fileobj.name
        fp = Fileobj.location
        tf = tarfile.open(os.path.join(fp, fn), 'r:gz')
        result_objs = [tf.extractfile(member) for member in tf.getmembers()]
        result.extend([cls.loads(robj.read()) for robj in result_objs])        
        #result = [cls.loads(str) for str in server.lrange(terminal_fp, 0, -1)]
        #fp = Fileobj.location
        #read_here = os.path.join(fp, fn)
        #result_str = gzip.open(read_here, 'rb').read()
        #result.append(cls.loads(result_str))
    #result = [FilterableMetaArray.loads(robj.read()) for robj in result_objs]
    return dict(output=result)

def load_module(id=None, datatype=None, action=load_action,
                version='0.0', fields={}, xtype='WireIt.Container', **kwargs):
    """Module for loading data from a raw datafile"""

    icon = {
        'URI': config.IMAGES + "load.png",
        'terminals': {
            'output': (20, 10, 1, 0),
        }
    }
   
    terminals = [
        #dict(id='input',
        #     datatype=datatype,
        #     use='in',
        #     description='data',
        #     required=False,
        #     multiple=True,
        #     ),
        dict(id='output',
             datatype=datatype,
             use='out',
             description='data',
             ),
    ]

    files_field = {
        "type":"files",
        "label": "Files",
        "name": "files",
        "value": [],
    }
    intent_field = {
        "type":"string",
        "label":"Intent",
        "name": "intent",
        "value": '',
    }
    
    fields.update({'files': files_field, 'intent': intent_field})
    
    # Combine everything into a module.
    module = Module(id=id,
                  name='Load Raw',
                  version=version,
                  description=action.__doc__,
                  #icon=icon,
                  terminals=terminals,
                  fields=fields,
                  action=action,
                  xtype=xtype,
                  **kwargs
                  )

    return module
