# Create your views here.

from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect, QueryDict
from django.utils import simplejson
from apps.tracks.forms import languageSelectForm, titleOnlyForm, experimentForm1, experimentForm2, titleOnlyFormExperiment
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger #paging for lists
from django.core.exceptions import ObjectDoesNotExist

import hashlib

## models
from django.contrib.auth.models import User 
from models import * #add models by name

## adds test objects to DB
from ... import fillDB


from ...apps.fileview import testftp

#from ...dataflow import wireit
from ...dataflow.calc import run_template
from ...dataflow.calc import calc_single, fingerprint_template, get_plottable
from ...dataflow.offspecular.instruments import ANDR
print "ANDR imported: ", ANDR.id
from ...dataflow.SANS.novelinstruments import SANS_INS
print "SANS imported: ", SANS_INS.id
from ...dataflow.tas.instruments import BT7 as TAS_INS
print "TAS imported: ", TAS_INS.id


from ...dataflow import wireit

import random

def xhr_test(request):
    if request.is_ajax():
        if request.method == 'GET':
                message = "This is an XHR GET request"
        elif request.method == 'POST':
            message = "This is an XHR POST request"
            # Here we can access the POST data
            print request.POST
        else:
            message = "No XHR"
    else:
	message = "What is this, WSGI?"
    return HttpResponse(message)

def showInteractors(request):
	return render_to_response('interactors.html')

def mytest(request):
   return render_to_response('tracer_testingforWireit/xhr_temp.html')

def home(request):
    context = RequestContext(request)
    site_list = ['/editor/', '/login/', '/interactors/']
    return render_to_response('tracer_testingforWireit/home.html', locals(), context_instance=context)
    
##################
#### file loading testing

store = [{
        "id": 0,
        "text": "A leaf Node",
        "leaf": True
    }, {
        "id": 1,
        "text": "A folder Node",
        "children": [{
            "id": 2,
            "text": "A child Node",
            "leaf": True
            #"children":[{}],
        }]
   }]
def getNCNRdirectories(request):
	return HttpResponse(simplejson.dumps(testftp.runMe()))  #testftp.runMe()
    
def displayFileLoad(request):
	return render_to_response('FileUpload/FileTreeTest.html', locals())
    
###################
#### TRACKS testing

#### template list

a = [{"name":"test tas", "wires": [{"src": {"terminal": "output", "moduleId": 0}, "tgt": {"terminal": "input", "moduleId": 1}}, {"src": {"terminal": "output", "moduleId": 1}, "tgt": {"terminal": "input", "moduleId": 2}}, {"src": {"terminal": "output", "moduleId": 2}, "tgt": {"terminal": "input", "moduleId": 3}}], "modules": [{"terminals": "", "config": {"position": [5, 20], "xtype": "WireIt.Container"}, "name": "Load", "value": {}}, {"terminals": {"input": [-15, 1, -1, 0], "output": [15, 1, 1, 0]}, "config": {"position": [160, 20], "xtype": "WireIt.ImageContainer"}, "name": "Join", "value": {}}, {"terminals": {"input": [0, 10, -1, 0], "output": [20, 10, 1, 0]}, "config": {"position": [280, 40], "xtype": "WireIt.ImageContainer"}, "name": "Scale", "value": {}}, {"terminals": "", "config": {"position": [340, 40], "xtype": "WireIt.Container"}, "name": "Save", "value": {}}], "properties": {"name": "test tas", "description": "example TAS diagram"}}]    
offspec = [{"name":"andr test", "wires": [{"src": {"terminal": "output", "moduleId": 0}, "tgt": {"terminal": "input_data", "moduleId": 2}}, {"src": {"terminal": "output", "moduleId": 2}, "tgt": {"terminal": "input", "moduleId": 3}}, {"src": {"terminal": "output", "moduleId": 3}, "tgt": {"terminal": "input", "moduleId": 4}}, {"src": {"terminal": "output", "moduleId": 4}, "tgt": {"terminal": "input", "moduleId": 5}}, {"src": {"terminal": "output", "moduleId": 5}, "tgt": {"terminal": "input", "moduleId": 6}}, {"src": {"terminal": "output", "moduleId": 6}, "tgt": {"terminal": "input", "moduleId": 1}}], "modules": [{"terminals": "", "config": {"files": ["/home/brendan/sampledata/ANDR/sabc/Isabc2002.cg1", "/home/brendan/sampledata/ANDR/sabc/Isabc2003.cg1", "/home/brendan/sampledata/ANDR/sabc/Isabc2004.cg1", "/home/brendan/sampledata/ANDR/sabc/Isabc2005.cg1", "/home/brendan/sampledata/ANDR/sabc/Isabc2006.cg1", "/home/brendan/sampledata/ANDR/sabc/Isabc2007.cg1", "/home/brendan/sampledata/ANDR/sabc/Isabc2008.cg1", "/home/brendan/sampledata/ANDR/sabc/Isabc2009.cg1", "/home/brendan/sampledata/ANDR/sabc/Isabc2010.cg1", "/home/brendan/sampledata/ANDR/sabc/Isabc2011.cg1", "/home/brendan/sampledata/ANDR/sabc/Isabc2012.cg1"], "position": [50, 50], "intent": "signal", "xtype": "WireIt.Container"}, "name": "Load", "value": {}}, {"terminals": "", "config": {"position": [650, 350], "ext": "dat", "xtype": "WireIt.Container"}, "name": "Save", "value": {}}, {"terminals": {"input_data": [-16, 1, -1, 0], "input_grid":[-16, 16, -1, 0], "output": [15, 1, 1, 0]}, "config": {"position": [150, 100], "xtype": "WireIt.ImageContainer"}, "name": "Combine", "value": {}}, {"terminals": {"input": [0, 10, -1, 0], "output": [20, 10, 1, 0]}, "config": {"position": [250, 150], "xtype": "WireIt.ImageContainer", "offsets": {"theta": 0.10000000000000001}}, "name": "Offset", "value": {}}, {"terminals": {"input": [0, 10, -1, 0], "output": [20, 10, 1, 0]}, "config": {"position": [350, 200], "xtype": "WireIt.ImageContainer"}, "name": "Wiggle", "value": {}}, {"terminals": {"input": [0, 10, -1, 0], "output": [20, 10, 1, 0]}, "config": {"position": [450, 250], "xtype": "WireIt.ImageContainer"}, "name": "Pixels to two theta", "value": {}}, {"terminals": {"input": [0, 10, -1, 0], "output": [20, 10, 1, 0]}, "config": {"position": [550, 300], "xtype": "WireIt.ImageContainer"}, "name": "Two theta to qxqz", "value": {}}], "properties": {"name": "test ospec", "description": "example ospec diagram"}},
{"name":"test ospec", "modules":[{"name":"Load", "value":{}, "config":{"position":[50, 50], "xtype":"WireIt.Container"}}, {"name":"Save", "value":{}, "config":{"position":[650, 350], "xtype":"WireIt.Container"}}, {"name":"Offset", "value":{}, "config":{"position":[204, 92], "xtype":"WireIt.ImageContainer"}}, {"name":"Wiggle", "value":{}, "config":{"position":[321, 171], "xtype":"WireIt.ImageContainer"}}, {"name":"Pixels to two theta", "value":{}, "config":{"position":[450, 250], "xtype":"WireIt.ImageContainer"}}, {"name":"Two theta to qxqz", "value":{}, "config":{"position":[560, 392], "xtype":"WireIt.ImageContainer"}}, {"name":"Combine", "value":{}, "config":{"position":[452, 390], "xtype":"WireIt.ImageContainer"}}], "properties":{"name":"test ospec", "description":"example ospec diagram"}, "wires":[{"xtype":"WireIt.BezierWire", "src":{"moduleId":2, "terminal":"output"}, "tgt":{"moduleId":3, "terminal":"input"}}, {"xtype":"WireIt.BezierWire", "src":{"moduleId":3, "terminal":"output"}, "tgt":{"moduleId":4, "terminal":"input"}}, {"xtype":"WireIt.BezierWire", "src":{"moduleId":5, "terminal":"output"}, "tgt":{"moduleId":1, "terminal":"input"}}, {"xtype":"WireIt.BezierWire", "src":{"moduleId":0, "terminal":"output"}, "tgt":{"moduleId":2, "terminal":"input"}}, {"xtype":"WireIt.BezierWire", "src":{"moduleId":4, "terminal":"output"}, "tgt":{"moduleId":6, "terminal":"input_data"}}, {"xtype":"WireIt.BezierWire", "src":{"moduleId":6, "terminal":"output"}, "tgt":{"moduleId":5, "terminal":"input"}}], "language":"NCNR ANDR"},
{"name":"new andr", 'wires': [{'src': {'terminal': 'output', 'moduleId': 0}, 'tgt': {'terminal': 'input', 'moduleId': 4}}, {'src': {'terminal': 'output', 'moduleId': 4}, 'tgt': {'terminal': 'input', 'moduleId': 3}}, {'src': {'terminal': 'output', 'moduleId': 3}, 'tgt': {'terminal': 'input', 'moduleId': 5}}, {'src': {'terminal': 'output', 'moduleId': 5}, 'tgt': {'terminal': 'input_data', 'moduleId': 2}}, {'src': {'terminal': 'output', 'moduleId': 5}, 'tgt': {'terminal': 'input', 'moduleId': 7}}, {'src': {'terminal': 'output', 'moduleId': 7}, 'tgt': {'terminal': 'input_grid', 'moduleId': 2}}, {'src': {'terminal': 'output', 'moduleId': 2}, 'tgt': {'terminal': 'input', 'moduleId': 6}}, {'src': {'terminal': 'output', 'moduleId': 8}, 'tgt': {'terminal': 'output_grid', 'moduleId': 6}}, {'src': {'terminal': 'output', 'moduleId': 6}, 'tgt': {'terminal': 'input', 'moduleId': 1}}], 'modules': [{'terminals': '', 'config': {'files': ['/home/brendan/dataflow/sampledata/ANDR/sabc/Isabc2002.cg1', '/home/brendan/dataflow/sampledata/ANDR/sabc/Isabc2003.cg1', '/home/brendan/dataflow/sampledata/ANDR/sabc/Isabc2004.cg1', '/home/brendan/dataflow/sampledata/ANDR/sabc/Isabc2005.cg1', '/home/brendan/dataflow/sampledata/ANDR/sabc/Isabc2006.cg1', '/home/brendan/dataflow/sampledata/ANDR/sabc/Isabc2007.cg1', '/home/brendan/dataflow/sampledata/ANDR/sabc/Isabc2008.cg1', '/home/brendan/dataflow/sampledata/ANDR/sabc/Isabc2009.cg1', '/home/brendan/dataflow/sampledata/ANDR/sabc/Isabc2010.cg1', '/home/brendan/dataflow/sampledata/ANDR/sabc/Isabc2011.cg1', '/home/brendan/dataflow/sampledata/ANDR/sabc/Isabc2012.cg1'], 'position': (50, 50), 'intent': 'signal', 'xtype': 'WireIt.Container'}, 'name': 'Load', 'value': {}}, {'terminals': '', 'config': {'position': (650, 350), 'ext': 'dat', 'xtype': 'WireIt.Container'}, 'name': 'Save', 'value': {}}, {'terminals': {'input_data': (-12, 4, -1, 0), 'input_grid': (-12, 40, -1, 0), 'output': (48, 16, 1, 0)}, 'config': {'position': (452, 390), 'xtype': 'WireIt.ImageContainer'}, 'name': 'Combine', 'value': {}}, {'terminals': {'input': (-12, 16, -1, 0), 'output': (48, 16, 1, 0)}, 'config': {'position': (321, 171), 'xtype': 'WireIt.ImageContainer', 'offsets': {'theta': 0}}, 'name': 'Offset', 'value': {}}, {'terminals': {'input': (-12, 16, -1, 0), 'output': (48, 16, 1, 0)}, 'config': {'position': (204, 92), 'xtype': 'WireIt.ImageContainer'}, 'name': 'Wiggle', 'value': {}}, {'terminals': {'input': (-12, 16, -1, 0), 'output': (48, 16, 1, 0)}, 'config': {'position': (450, 250), 'xtype': 'WireIt.ImageContainer'}, 'name': 'Pixels to two theta', 'value': {}}, {'terminals': {'input': (-12, 4, -1, 0), 'output': (48, 16, 1, 0), 'output_grid': (-12, 40, -1, 0)}, 'config': {'position': (560, 392), 'xtype': 'WireIt.ImageContainer'}, 'name': 'Two theta to qxqz', 'value': {}}, {'terminals': {'input': (-12, 16, -1, 0), 'output': (48, 16, 1, 0)}, 'config': {'position': (350, 390), 'xtype': 'WireIt.ImageContainer'}, 'name': 'Autogrid', 'value': {}}, {'terminals': '', 'config': {'position': (350, 470), 'xtype': 'WireIt.Container'}, 'name': 'Empty QxQz grid', 'value': {}}], 'properties': {'name': 'test ospec', 'description': 'example ospec diagram'}},
{"name":"andr polarized", 'wires': [{'src': {'terminal': 'output', 'moduleId': 0}, 'tgt': {'terminal': 'input', 'moduleId': 1}}, {'src': {'terminal': 'output', 'moduleId': 8}, 'tgt': {'terminal': 'stamps', 'moduleId': 1}}, {'src': {'terminal': 'output', 'moduleId': 1}, 'tgt': {'terminal': 'input', 'moduleId': 5}}, {'src': {'terminal': 'output', 'moduleId': 2}, 'tgt': {'terminal': 'he3cell', 'moduleId': 5}}, {'src': {'terminal': 'output', 'moduleId': 5}, 'tgt': {'terminal': 'input', 'moduleId': 4}}, {'src': {'terminal': 'output', 'moduleId': 5}, 'tgt': {'terminal': 'input', 'moduleId': 7}}, {'src': {'terminal': 'output', 'moduleId': 7}, 'tgt': {'terminal': 'grid', 'moduleId': 4}}, {'src': {'terminal': 'output', 'moduleId': 4}, 'tgt': {'terminal': 'input', 'moduleId': 6}}, {'src': {'terminal': 'output', 'moduleId': 6}, 'tgt': {'terminal': 'input', 'moduleId': 3}}], 'modules': [{'terminals': '', 'config': {'files': ['/home/brendan/dataflow/sampledata/ANDR/cshape_121609/Iremun001.ca1', '/home/brendan/dataflow/sampledata/ANDR/cshape_121609/Iremun001.cb1', '/home/brendan/dataflow/sampledata/ANDR/cshape_121609/Iremun002.ca1', '/home/brendan/dataflow/sampledata/ANDR/cshape_121609/Iremun002.cb1', '/home/brendan/dataflow/sampledata/ANDR/cshape_121609/Iremun004.ca1', '/home/brendan/dataflow/sampledata/ANDR/cshape_121609/Iremun004.cb1', '/home/brendan/dataflow/sampledata/ANDR/cshape_121609/Iremun005.ca1', '/home/brendan/dataflow/sampledata/ANDR/cshape_121609/Iremun005.cb1', '/home/brendan/dataflow/sampledata/ANDR/cshape_121609/Iremun006.ca1', '/home/brendan/dataflow/sampledata/ANDR/cshape_121609/Iremun006.cb1', '/home/brendan/dataflow/sampledata/ANDR/cshape_121609/Iremun007.ca1', '/home/brendan/dataflow/sampledata/ANDR/cshape_121609/Iremun007.cb1', '/home/brendan/dataflow/sampledata/ANDR/cshape_121609/Iremun008.ca1', '/home/brendan/dataflow/sampledata/ANDR/cshape_121609/Iremun008.cb1', '/home/brendan/dataflow/sampledata/ANDR/cshape_121609/Iremun009.ca1', '/home/brendan/dataflow/sampledata/ANDR/cshape_121609/Iremun009.cb1'], 'position': (50, 25), 'intent': 'signal', 'xtype': 'WireIt.Container', 'PolStates': {'Iremun004.cb1': '--', 'Iremun009.ca1': '++', 'Iremun004.ca1': '+-', 'Iremun002.ca1': '++', 'Iremun009.cb1': '-+', 'Iremun001.ca1': '++', 'Iremun006.ca1': '+-', 'Iremun002.cb1': '-+', 'Iremun005.ca1': '+-', 'Iremun007.cb1': '--', 'Iremun006.cb1': '--', 'Iremun001.cb1': '-+', 'Iremun008.cb1': '-+', 'Iremun007.ca1': '+-', 'Iremun005.cb1': '--', 'Iremun008.ca1': '++'}}, 'name': 'Load', 'value': {}}, {'terminals': {'input': (-12, 4, -1, 0), 'stamps': (-12, 40, -1, 0), 'output': (48, 16, 1, 0)}, 'config': {'position': (100, 125), 'xtype': 'WireIt.ImageContainer'}, 'name': 'Timestamp', 'value': {}}, {'terminals': '', 'config': {'files': ['/home/brendan/dataflow/sampledata/ANDR/cshape_121609/He3Cells.json'], 'position': (50, 375), 'xtype': 'WireIt.Container'}, 'name': 'Load he3', 'value': {}}, {'terminals': '', 'config': {'position': (700, 175), 'ext': 'dat', 'xtype': 'WireIt.Container'}, 'name': 'Save', 'value': {}}, {'terminals': {'input': (-12, 4, -1, 0), 'grid': (-12, 40, -1, 0), 'output': (48, 16, 1, 0)}, 'config': {'position': (450, 180), 'xtype': 'WireIt.ImageContainer'}, 'name': 'Combine polarized', 'value': {}}, {'terminals': {'input': (-12, 4, -1, 0), 'output': (48, 16, 1, 0), 'he3cell': (-12, 40, -1, 0)}, 'config': {'position': (300, 225), 'xtype': 'WireIt.ImageContainer'}, 'name': 'Append polarization matrix', 'value': {}}, {'terminals': {'input': (-12, 16, -1, 0), 'output': (48, 16, 1, 0)}, 'config': {'position': (570, 125), 'xtype': 'WireIt.ImageContainer'}, 'name': 'Polarization correction', 'value': {}}, {'terminals': {'input': (-12, 16, -1, 0), 'output': (48, 16, 1, 0)}, 'config': {'position': (350, 375), 'xtype': 'WireIt.ImageContainer'}, 'name': 'Autogrid', 'value': {}}, {'terminals': '', 'config': {'files': ['/home/brendan/dataflow/sampledata/ANDR/cshape_121609/end_times.json'], 'position': (50, 250), 'xtype': 'WireIt.Container'}, 'name': 'Load stamps', 'value': {}}], 'properties': {'name': 'test ospec', 'description': 'example ospec diagram'}}]
SANS = [{"name":"sans test", "wires": [{"src": {"terminal": "output", "moduleId": 0}, "tgt": {"terminal": "input", "moduleId": 2}}, {"src": {"terminal": "output", "moduleId": 2}, "tgt": {"terminal": "input", "moduleId": 3}}, {"src": {"terminal": "output", "moduleId": 3}, "tgt": {"terminal": "input", "moduleId": 4}}, {"src": {"terminal": "output", "moduleId": 4}, "tgt": {"terminal": "input", "moduleId": 5}}, {"src": {"terminal": "output", "moduleId": 5}, "tgt": {"terminal": "input", "moduleId": 1}}], "modules": [{"terminals": "", "config": {"files": ["/var/www/DATAFLOW/dataflow/reduction/sans/ncnr_sample_data/SILIC010.SA3_SRK_S110", "/var/www/DATAFLOW/dataflow/reduction/sans/ncnr_sample_data/SILIC008.SA3_SRK_S108", "/var/www/DATAFLOW/dataflow/reduction/sans/ncnr_sample_data/SILIC002.SA3_SRK_S102", "/var/www/DATAFLOW/dataflow/reduction/sans/ncnr_sample_data/SILIC006.SA3_SRK_S106", "/var/www/DATAFLOW/dataflow/reduction/sans/ncnr_sample_data/SILIC005.SA3_SRK_S105", "/var/www/DATAFLOW/dataflow/reduction/sans/ncnr_sample_data/SILIC007.SA3_SRK_S107", "/var/www/DATAFLOW/dataflow/reduction/sans/ncnr_sample_data/PLEX_2NOV2007_NG3.DIV"], "position": [5, 20], "intent": "signal", "xtype": "WireIt.Container"}, "name": "Load", "value": {}}, {"terminals": "", "config": {"position": [500, 500], "ext": "dat", "xtype": "WireIt.Container"}, "name": "Save", "value": {}}, {"terminals": {"input": [0, 10, -1, 0], "output": [20, 10, 1, 0]}, "config": {"position": [360, 100], "xtype": "WireIt.ImageContainer"}, "name": "initial_correction", "value": {}}, {"terminals": {"input": [0, 10, -1, 0], "output": [20, 10, 1, 0]}, "config": {"position": [360, 200], "xtype": "WireIt.ImageContainer"}, "name": "correct_detector_efficiency", "value": {}}, {"terminals": {"input": [0, 10, -1, 0], "output": [20, 10, 1, 0]}, "config": {"position": [360, 300], "xtype": "WireIt.ImageContainer"}, "name": "absolute_scaling", "value": {}}, {"terminals": {"input": [0, 10, -1, 0], "output": [20, 10, 1, 0]}, "config": {"position": [360, 400], "xtype": "WireIt.ImageContainer"}, "name": "annular_av", "value": {}}], "properties": {"name": "test sans", "description": "example sans data"}}]


TAS_2 = [{"name": "TAS_NEW", "wires": [{"src": {"terminal": "output", "moduleId": 0}, "tgt": {"terminal": "input", "moduleId": 1}}, {"src": {"terminal": "output", "moduleId": 1}, "tgt": {"terminal": "input", "moduleId": 5}}, {"src": {"terminal": "output", "moduleId": 0}, "tgt": {"terminal": "input", "moduleId": 2}}, {"src": {"terminal": "output", "moduleId": 2}, "tgt": {"terminal": "input", "moduleId": 5}}, {"src": {"terminal": "output", "moduleId": 0}, "tgt": {"terminal": "input", "moduleId": 3}}, {"src": {"terminal": "output", "moduleId": 3}, "tgt": {"terminal": "input", "moduleId": 5}}, {"src": {"terminal": "output", "moduleId": 0}, "tgt": {"terminal": "input", "moduleId": 4}}, {"src": {"terminal": "output", "moduleId": 4}, "tgt": {"terminal": "input", "moduleId": 5}}], "modules": [{"terminals": "", "config": {"files": ["/home/brendan/dataflowreduction/tripleaxis/EscanQQ7HorNSF91831.bt7"], "position": [10, 150], "xtype": "WireIt.Container"}, "name": "Load", "value": {}}, {"terminals": {"input": [-12, 16, -1, 0], "output": [48, 16, 1, 0]}, "config": {"position": [270, 20], "target_monitor": 165000, "xtype": "WireIt.ImageContainer"}, "name": "Normalize Monitor", "value": {}}, {"terminals": {"input": [-12, 16, -1, 0], "output": [48, 16, 1, 0]}, "config": {"position": [270, 120], "xtype": "WireIt.ImageContainer"}, "name": "Detailed Balance", "value": {}}, {"terminals": {"input": [-12, 16, -1, 0], "output": [48, 16, 1, 0]}, "config": {"position": [270, 220], "instrument_name": "BT7", "xtype": "WireIt.ImageContainer"}, "name": "Monitor Correction", "value": {}}, {"terminals": {"input": [-12, 16, -1, 0], "output": [48, 16, 1, 0]}, "config": {"position": [270, 320], "xtype": "WireIt.ImageContainer"}, "name": "Volume Correction", "value": {}}, {"terminals": "", "config": {"position": [500, 150], "xtype": "WireIt.Container"}, "name": "Save", "value": {}}], "properties": {"name": "test reduction presentation", "description": "example reduction diagram"}}]

SANS_4 = [{"name":"SANS_FINAL", "wires": [{"src": {"terminal": "output", "moduleId": 0}, "tgt": {"terminal": "sample_in", "moduleId": 4}}, {"src": {"terminal": "output", "moduleId": 1}, "tgt": {"terminal": "empty_cell_in", "moduleId": 4}}, {"src": {"terminal": "output", "moduleId": 2}, "tgt": {"terminal": "empty_in", "moduleId": 4}}, {"src": {"terminal": "output", "moduleId": 3}, "tgt": {"terminal": "blocked_in", "moduleId": 4}}, {"src": {"terminal": "sample_out", "moduleId": 4}, "tgt": {"terminal": "sample_in", "moduleId": 7}}, {"src": {"terminal": "empty_cell_out", "moduleId": 4}, "tgt": {"terminal": "empty_cell_in", "moduleId": 7}}, {"src": {"terminal": "empty_out", "moduleId": 4}, "tgt": {"terminal": "empty_in", "moduleId": 7}}, {"src": {"terminal": "output", "moduleId": 5}, "tgt": {"terminal": "Tsam_in", "moduleId": 7}}, {"src": {"terminal": "output", "moduleId": 6}, "tgt": {"terminal": "Temp_in", "moduleId": 7}}, {"src": {"terminal": "sample_out", "moduleId": 7}, "tgt": {"terminal": "sample", "moduleId": 9}}, {"src": {"terminal": "empty_cell_out", "moduleId": 7}, "tgt": {"terminal": "empty_cell", "moduleId": 9}}, {"src": {"terminal": "blocked_out", "moduleId": 4}, "tgt": {"terminal": "blocked", "moduleId": 9}}, {"src": {"terminal": "COR", "moduleId": 9}, "tgt": {"terminal": "COR", "moduleId": 11}}, {"src": {"terminal": "output", "moduleId": 10}, "tgt": {"terminal": "DIV_in", "moduleId": 11}}, {"src": {"terminal": "DIV_out", "moduleId": 11}, "tgt": {"terminal": "DIV", "moduleId": 12}}, {"src": {"terminal": "output", "moduleId": 2}, "tgt": {"terminal": "empty", "moduleId": 12}}, {"src": {"terminal": "output", "moduleId": 10}, "tgt": {"terminal": "sensitivity", "moduleId": 12}}, {"src": {"terminal": "ABS", "moduleId": 12}, "tgt": {"terminal": "ABS", "moduleId": 13}}, {"src": {"terminal": "OneD", "moduleId": 13}, "tgt": {"terminal": "input", "moduleId": 8}}], "modules": [{"terminals": "", "config": {"files": ["/home/elakian/dataflow/reduction/sans/ncnr_sample_data/SILIC010.SA3_SRK_S110"], "position": [5, 20], "intent": "signal", "xtype": "WireIt.Container"}, "name": "Load", "value": {}}, {"terminals": "", "config": {"files": ["/home/elakian/dataflow/reduction/sans/ncnr_sample_data/SILIC008.SA3_SRK_S108"], "position": [5, 50], "intent": "signal", "xtype": "WireIt.Container"}, "name": "Load", "value": {}}, {"terminals": "", "config": {"files": ["/home/elakian/dataflow/reduction/sans/ncnr_sample_data/SILIC002.SA3_SRK_S102"], "position": [5, 80], "intent": "signal", "xtype": "WireIt.Container"}, "name": "Load", "value": {}}, {"terminals": "", "config": {"files": ["/home/elakian/dataflow/reduction/sans/ncnr_sample_data/SILIC007.SA3_SRK_S107"], "position": [5, 110], "intent": "signal", "xtype": "WireIt.Container"}, "name": "Load", "value": {}}, {"terminals": {"blocked_in": [-16, 40, -1, 0], "empty_cell_in": [-16, 20, -1, 0], "empty_out": [48, 30, 1, 0], "empty_cell_out": [48, 20, 1, 0], "sample_out": [48, 10, 1, 0], "sample_in": [-16, 10, -1, 0], "blocked_out": [48, 40, 1, 0], "empty_in": [-16, 30, -1, 0]}, "config": {"position": [250, 10], "xtype": "WireIt.ImageContainer", "deadtimeConstant": 3.4e-06}, "name": "Dead time Correction", "value": {}}, {"terminals": "", "config": {"files": ["/home/elakian/dataflow/reduction/sans/ncnr_sample_data/SILIC006.SA3_SRK_S106"], "position": [5, 200], "intent": "signal", "xtype": "WireIt.Container"}, "name": "Load", "value": {}}, {"terminals": "", "config": {"files": ["/home/elakian/dataflow/reduction/sans/ncnr_sample_data/SILIC005.SA3_SRK_S105"], "position": [5, 230], "intent": "signal", "xtype": "WireIt.Container"}, "name": "Load", "value": {}}, {"terminals": {"empty_cell_in": [-16, 15, -1, 0], "Tsam_in": [-16, 35, -1, 0], "sample_out": [48, 10, 1, 0], "Temp_in": [-16, 45, -1, 0], "empty_cell_out": [48, 30, 1, 0], "empty_in": [-16, 25, -1, 0], "sample_in": [-16, 5, -1, 0]}, "config": {"position": [400, 10], "bottomLeftCoord": {"Y": 53, "X": 55}, "monitorNormalize": 100000000.0, "xtype": "WireIt.ImageContainer", "topRightCoord": {"Y": 72, "X": 74}}, "name": "Generate Transmission", "value": {}}, {"terminals": "", "config": {"position": [660, 660], "ext": "dat", "xtype": "WireIt.Container"}, "name": "Save", "value": {}}, {"terminals": {"sample": [-16, 8, -1, 0], "COR": [48, 10, 1, 0], "empty_cell": [-16, 28, -1, 0], "blocked": [-16, 48, -1, 0]}, "config": {"position": [480, 100], "xtype": "WireIt.ImageContainer"}, "name": "Initial Correction", "value": {}}, {"terminals": "", "config": {"files": ["/home/elakian/dataflow/reduction/sans/ncnr_sample_data/PLEX_2NOV2007_NG3.DIV"], "position": [5, 300], "intent": "signal", "xtype": "WireIt.Container"}, "name": "Load", "value": {}}, {"terminals": {"DIV_out": [48, 10, 1, 0], "COR": [-16, 10, -1, 0], "DIV_in": [-16, 30, -1, 0]}, "config": {"position": [540, 200], "xtype": "WireIt.ImageContainer"}, "name": "Correct Detector Sensitivity", "value": {}}, {"terminals": {"DIV": [-16, 5, -1, 0], "ABS": [48, 10, 1, 0], "sensitivity": [-16, 40, -1, 0], "empty": [-16, 25, -1, 0]}, "config": {"position": [580, 300], "bottomLeftCoord": {"Y": 53, "X": 55}, "xtype": "WireIt.ImageContainer", "ins_name": "NG3", "topRightCoord": {"Y": 72, "X": 74}}, "name": "Absolute Scaling", "value": {}}, {"terminals": {"ABS": [-16, 10, -1, 0], "OneD": [48, 10, 1, 0]}, "config": {"position": [610, 400], "xtype": "WireIt.ImageContainer"}, "name": "Annular Average", "value": {}}], "properties": {"name": "test sans", "description": "example sans data"}}]



sample_data = {
    'type': '2d',
    'z':  [ [1, 2], [3, 4] ],
    'title': 'This is the title',
    'dims': {
      'xmax': 1.0,
      'xmin': 0.0,
      'ymin': 0.0,
      'ymax': 12.0,
      'xdim': 2,
      'ydim': 2,
    },
    'xlabel': 'This is my x-axis label',
    'ylabel': 'This is my y-axis label',
    'zlabel': 'This is my z-axis label',
}

b = {'save':'successful'}

SANS_NEW_TEMPLATE_FROM_WIREIT = {"modules":[{"config":{"files":"SILIC010.SA3_SRK_S110", "position":[5, 20], "xtype":"WireIt.Container"}, "name":"Load", "value":{}}, {"config":{"files":"SILIC008.SA3_SRK_S108", "position":[5, 30], "xtype":"WireIt.Container"}, "name":"Load", "value":{}}, {"config":{"position":[5, 40], "xtype":"WireIt.Container"}, "name":"Load", "value":{}}, {"config":{"position":[5, 50], "xtype":"WireIt.Container"}, "name":"Load", "value":{}}, {"config":{"position":[360, 50], "xtype":"WireIt.ImageContainer"}, "name":"Dead time Correction", "value":{}}, {"config":{"files":"SILIC005.SA3_SRK_S105", "position":[9, 128], "xtype":"WireIt.Container"}, "name":"Load", "value":{}}, {"config":{"files":"SILIC006.SA3_SRK_S106", "position":[42, 326], "xtype":"WireIt.Container"}, "name":"Load", "value":{}}, {"config":{"position":[120, 80], "xtype":"WireIt.ImageContainer"}, "name":"generate_transmission", "value":{}}, {"config":{"position":[696, 555], "xtype":"WireIt.Container"}, "name":"Save", "value":{}}, {"config":{"position":[360, 100], "xtype":"WireIt.ImageContainer"}, "name":"initial_correction", "value":{}}, {"config":{"files":"PLEX_2NOV2007_NG3.DIV", "position":[32, 394], "xtype":"WireIt.Container"}, "name":"Load", "value":{}}, {"config":{"position":[360, 200], "xtype":"WireIt.ImageContainer"}, "name":"Correct Detector Sensitivity", "value":{}}, {"config":{"files":"SILIC002.SA3_SRK_S102", "position":[72, 474], "xtype":"WireIt.Container"}, "name":"Load", "value":{}}, {"config":{"position":[360, 300], "xtype":"WireIt.ImageContainer"}, "name":"absolute_scaling", "value":{}}, {"config":{"position":[360, 400], "xtype":"WireIt.ImageContainer"}, "name":"annular_av", "value":{}}], "name":"test sans", "properties":{"description":"example sans data", "name":"test sans"}, "wires":[{"src":{"moduleId":0, "terminal":"output"}, "tgt":{"moduleId":4, "terminal":"sample"}, "xtype":"WireIt.BezierWire"}, {"src":{"moduleId":1, "terminal":"output"}, "tgt":{"moduleId":4, "terminal":"empty_cell"}, "xtype":"WireIt.BezierWire"}, {"src":{"moduleId":3, "terminal":"output"}, "tgt":{"moduleId":4, "terminal":"blocked"}, "xtype":"WireIt.BezierWire"}, {"src":{"moduleId":4, "terminal":"sample"}, "tgt":{"moduleId":7, "terminal":"sample"}, "xtype":"WireIt.BezierWire"}, {"src":{"moduleId":4, "terminal":"empty_cell"}, "tgt":{"moduleId":7, "terminal":"empty_cell"}, "xtype":"WireIt.BezierWire"}, {"src":{"moduleId":5, "terminal":"output"}, "tgt":{"moduleId":7, "terminal":"Tsam"}, "xtype":"WireIt.BezierWire"}, {"src":{"moduleId":6, "terminal":"output"}, "tgt":{"moduleId":7, "terminal":"Temp"}, "xtype":"WireIt.BezierWire"}, {"src":{"moduleId":7, "terminal":"sample"}, "tgt":{"moduleId":9, "terminal":"sample"}, "xtype":"WireIt.BezierWire"}, {"src":{"moduleId":7, "terminal":"empty_cell"}, "tgt":{"moduleId":9, "terminal":"empty_cell"}, "xtype":"WireIt.BezierWire"}, {"src":{"moduleId":4, "terminal":"blocked"}, "tgt":{"moduleId":9, "terminal":"blocked"}, "xtype":"WireIt.BezierWire"}, {"src":{"moduleId":9, "terminal":"COR"}, "tgt":{"moduleId":11, "terminal":"COR"}, "xtype":"WireIt.BezierWire"}, {"src":{"moduleId":10, "terminal":"output"}, "tgt":{"moduleId":11, "terminal":"DIV"}, "xtype":"WireIt.BezierWire"}, {"src":{"moduleId":11, "terminal":"DIV"}, "tgt":{"moduleId":8, "terminal":"input"}, "xtype":"WireIt.BezierWire"}, {"src":{"moduleId":11, "terminal":"DIV"}, "tgt":{"moduleId":13, "terminal":"DIV"}, "xtype":"WireIt.BezierWire"}, {"src":{"moduleId":12, "terminal":"output"}, "tgt":{"moduleId":13, "terminal":"empty"}, "xtype":"WireIt.BezierWire"}, {"src":{"moduleId":10, "terminal":"output"}, "tgt":{"moduleId":13, "terminal":"sensitivity"}, "xtype":"WireIt.BezierWire"}, {"src":{"moduleId":13, "terminal":"ABS"}, "tgt":{"moduleId":14, "terminal":"ABS"}, "xtype":"WireIt.BezierWire"}, {"src":{"moduleId":14, "terminal":"OneD"}, "tgt":{"moduleId":8, "terminal":"input"}, "xtype":"WireIt.BezierWire"}]}

TAS_TEMPLATE_FROM_WIREIT = {"modules":[{"config":{"position":[50, 50], "xtype":"WireIt.Container"}, "name":"Load", "value":{}}, {"config":{"position":[250, 400], "xtype":"WireIt.ImageContainer"}, "name":"Normalize Monitor", "value":{}}], "name":"test reduction", "properties":{"description":"example reduction diagram", "name":"test reduction"}, "wires":[{"src":{"moduleId":0, "terminal":"output"}, "tgt":{"moduleId":1, "terminal":"input"}, "xtype":"WireIt.BezierWire"}]}


# apps.tracks.models, convert file hash to file path
	# File.objects.get(id=hash).location ("/tmp/FILES/{filename}")
	# wireit.py, convert wireit_diagram to template
# 





# this is a temporary option until wirings are stored in the database:
# they can be stored in a local list:
wirings_list = offspec + a + SANS + TAS_2 + SANS_4

@csrf_exempt 
def listWirings(request):
    context = RequestContext(request)
    print 'I am loading'
    data = simplejson.loads(request.POST['data'])
    if data['experiment_id'] == -1:
    	return HttpResponse(simplejson.dumps(wirings_list)) #, context_instance=context
    else:
    	wires = []
    	experiments = Experiment.objects.get(id=data['experiment_id']).templates.all()
    	for i in experiments:
    		wires += [simplejson.loads(i.Representation)]
    	if len(wires) == 0:
    		return HttpResponse(simplejson.dumps(wirings_list))
    	else:
    		return HttpResponse(simplejson.dumps(wires)) 

#    return HttpResponse(simplejson.dumps(a)) #andr vs bt7 testing

@csrf_exempt 
def saveWiring(request):
    #context = RequestContext(request)
    print 'I am saving'
    print request.POST
    new_wiring = simplejson.loads(request.POST['data'])
    # this stores the wires in a simple list, in memory on the django server.
    # replace this with a call to storing the wiring in a real database.
    #print 'TEMPLATE NAME: ', new_wiring['name']
    #print 'TEMPLATE REPR: ', new_wiring
    #print 'USER: ',request.user
    print new_wiring
    Template.objects.create(Title=new_wiring['name'], Representation=simplejson.dumps(new_wiring), user=request.user)
    #wirings_list.append(new_wiring)
    return HttpResponse(simplejson.dumps(b)) #, context_instance=context

def get_filepath_by_hash(fh):
    return File.objects.get(name=str(fh)).location + str(fh)

@csrf_exempt 
def runReduction(request):
    data = simplejson.loads(request.POST['data'])
    print 'IN RUN REDUCTION'
    config = {}
    bad_headers = ["files", "position", "xtype", "width", "terminals", "height", "title", "image", "icon"]
    for i, m in enumerate(data['modules']):
        conf = {}
        for key, value in m.get('config', {}).items():
            if key == 'files':
                file_hashes = m['config']['files']
                file_paths = [get_filepath_by_hash(fh) for fh in file_hashes]
                conf.update({'files': file_paths})
            elif key not in bad_headers:
                conf.update({key: value})
        config.update({i:conf})
    print config
    context = RequestContext(request)
    terminal_id = data['clickedOn']['source']['terminal']
    nodenum = int(data['clickedOn']['source']['moduleId'])
    print "calculating: terminal=%s, nodenum=%d" % (terminal_id, nodenum)
    language = data['language']
    instrument_by_language = {'andr2': ANDR, 'andr':ANDR, 'sans':SANS_INS, 'tas':TAS_INS}
    instrument = instrument_by_language.get(language, None)
    result = ['{}']
    if instrument is not None:
        template = wireit.wireit_diagram_to_template(data, instrument)
        # configuration for template is embedded
        print "getting result"
        result = get_plottable(template, config, nodenum, terminal_id)
    # result is a list of plottable items (JSON strings) - need to concatenate them
    JSON_result = '[' + ','.join(result) + ']' 
    return HttpResponse(JSON_result) #, context_instance=context
    
    #print FILES
###### BT7 TESTING
#    register_instrument(BT7)
#    instruments.init_data()
#    template = wireit.wireit_diagram_to_template(simplejson.loads(str(request.POST['data'])), BT7)
 #   a = run_template(template, [{'files': ['f1.bt7', 'f2.bt7']}, {'align': ['A3']}, {'scale': 2.5}, {'ext': 'dat'}])
 #   print a    
 #   data = [[random.random(), random.random()] for i in range(10)]
 #   c = {'reduction':'successful', 'data': data}
 #   return HttpResponse(simplejson.dumps(a))

###### ANDR TESTING
#    register_instrument(ANDR)
#    print "DONE REGISTERING"
#    template = wireit.wireit_diagram_to_template(simplejson.loads(str(request.POST['data'])), ANDR)
#    template = wireit.wireit_diagram_to_template(offspec[0], ANDR)
#    print template
#    print "RUNNING"
#    a = run_template(template, [d['config'] for d in template.modules])
#    print "DONE RUNNING"
#    print a
#    return HttpResponse(simplejson.dumps(a))


######## 
## Views for displaying a language selection form and for calling the file association table with the selected language.
## scheme is the same as for the editor



########
## Views for displaying a language selection form and for calling the editor template with the selected language.
## The intermediate template 'editorRedirect.html' is used so that we can redirect to /editor/ while preserving 
## the language selection.

## HAVING TROUBLE SENDING LIST OF STRINGS AS CONTEXT TO THE EDITOR
@csrf_exempt 
def displayEditor(request):
    context = RequestContext(request)
    file_context = {}
    print request.POST.has_key('language')
    if request.POST.has_key('language'):
    	if request.POST.has_key('experiment_id'):
    		experiment = Experiment.objects.get(id=request.POST['experiment_id'])
    		file_list = experiment.Files.all()
    		experiment_id = request.POST['experiment_id']
    	else:
    		experiment = []
    		file_list = []
    		experiment_id = -1
    	for i in range(len(file_list)):
    		file_context[file_list[i].name + ',,,z,z,z,z,,,' + file_list[i].friendly_name] = ''
    	file_context['file_keys'] = file_context.keys()
	file_context['lang'] = request.POST['language']
	file_context['experiment_id'] = experiment_id
        return render_to_response('tracer_testingforWireit/editor.html', file_context, context_instance=context)
    else:
        return HttpResponseRedirect('/editor/langSelect/')

@csrf_exempt 
def languageSelect(request):
    context = RequestContext(request)
    if request.POST.has_key('instruments'):
        return render_to_response('tracer_testingforWireit/editorRedirect.html',
                            {'lang':request.POST['instruments']}, context_instance=context)
    form = languageSelectForm()
    return render_to_response('tracer_testingforWireit/languageSelect.html', {'form':form}, context_instance=context)
    
    
###########
## Views for users, redirects to MyProjects page from login. Then continues logically from there.
@login_required
def myProjects(request):
	context = RequestContext(request)
	if request.POST.has_key('new_project'):
		Project.objects.create(Title=request.POST['new_project'], user=request.user)
	project_list = Project.objects.filter(user=request.user)
	paginator = Paginator(project_list, 10) #10 projects per pages
	page = request.GET.get('page')
	if page == None:
		page = 1
	try:
		projects = paginator.page(page)
	except PageNotAnInteger:
		projects = paginator.page(1)
	except EmptyPage:
		projects = paginator.page(paginator.num_pages)
	form = titleOnlyForm()
	return render_to_response('userProjects/displayProjects.html', {'projects':projects, 'form':form}, context_instance=context)

@login_required
def editProject(request, project_id):
	if request.POST.has_key('new_experiment'):
		new_exp = Experiment.objects.create(ProposalNum=request.POST['new_experiment'], users=request.user)
		new_exp.save()
		Project.objects.get(id=project_id).experiments.add(new_exp) 
	context = RequestContext(request)
	project = Project.objects.get(id=project_id)
	experiment_list = project.experiments.all()
	paginator = Paginator(experiment_list, 10)
	page = request.GET.get('page')
	if page == None:
		page = 1
	try:
		experiments = paginator.page(page)
	except PageNotAnInteger:
		experiments = paginator.page(1)
	except EmptyPage:
		experiments = paginator.page(paginator.num_pages)
	form = titleOnlyFormExperiment()
	return render_to_response('userProjects/editProject.html', {'project':project, 'form':form, 'experiments':experiments}, context_instance=context) 

@login_required 
def editExperiment(request, experiment_id):
    print request
    experiment = Experiment.objects.get(id=experiment_id)
    if request.FILES.has_key('files'):
        file_data = request.FILES['files']
        file_sha1 = hashlib.sha1()
        for line in file_data.read():
            file_sha1.update(line)
        write_here = '/tmp/FILES/' + file_sha1.hexdigest()
        write_here = open(write_here, 'w')
        for line in file_data:
            write_here.write(line)
        write_here.close()
        new_files = File.objects.filter(name=file_sha1.hexdigest())
        if len(new_files) > 0:
            new_file = new_files[0]
        else:
		    new_file = File.objects.create(name=file_sha1.hexdigest(), friendly_name=file_data.name, location='/tmp/FILES/')
        experiment.Files.add(new_file)
    if request.POST.has_key('instrument_name'):
        if request.POST['instrument_name']:
            instrument = Instrument.objects.get(id=request.POST['instrument_name'])
            instrument_class = instrument.instrument_class
            experiment.instrument = instrument
            experiment.save()
    if request.POST.has_key('facility'):
        if request.POST['facility']:
            facility = Facility.objects.get(id=request.POST['facility'])
            experiment.facility = facility
            experiment.save()
    if request.POST.has_key('templates'):
        if request.POST['templates']:
            template = Template.objects.get(id=request.POST['templates'])
            experiment.templates.add(template)
        #print file_sha1.hexdigest()
        #print hashlib.sha1(request.FILES['files'].read()).hexdigest()	
    context = RequestContext(request)
    facility = experiment.facility
    instrument = experiment.instrument
    if instrument:
        instrument_class = experiment.instrument.instrument_class
    else:
        instrument_class = None
    form1 = experimentForm1(initial={'facility':facility, 'instrument_class':instrument_class, 'instrument_name':instrument})
    form2 = experimentForm2(USER=request.user)
    return render_to_response('userProjects/editExperiment.html', {'form1':form1, 'form2':form2, 'experiment':experiment, }, context_instance=context)
