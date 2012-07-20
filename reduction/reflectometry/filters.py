from numpy import ndarray, zeros
import os
from FilterableMetaArray import FilterableMetaArray as MetaArray
from reduction.formats import load

def LoadICPData(filename, path=None, auto_PolState=False, PolState=''):
    """ 
    loads a data file into a MetaArray and returns that.
    Checks to see if data being loaded is 2D; if not, quits
    
    Need to rebin and regrid if the detector is moving...
    """
    lookup = {"a":"_down_down", "b":"_up_down", "c":"_down_up", "d":"_up_up", "g": ""}
    if path == None:
        path = os.getcwd()
    file_obj = load(os.path.join(path, filename), format='NCNR NG-1')
    if not (len(file_obj.detector.counts.shape) == 2):
        # not a 2D object!
        return
    if auto_PolState:
        key = filename[-2] # na1, ca1 etc. are --, nc1, cc1 are -+...
        PolState = lookup[key]
    # force PolState to a regularized version:
    if not PolState in lookup.values():
        PolState = ''
    datalen, xpixels = file_obj.detector.counts.shape
    creation_story = "LoadICPData('{fn}', path='{p}', auto_PolState={aPS}, PolState='{PS}'".format(fn=filename, p=path, aPS=auto_PolState, PS=PolState)

# doesn't really matter; changing so that each keyword (whether it took the default value
# provided or not) will be defined
#    if not PolState == '':
#        creation_story += ", PolState='{0}'".format(PolState)

        
    creation_story += ")" 
    info = [{"name": "theta", "units": "degrees", "values": file_obj.sample.angle_x, "det_angle":file_obj.detector.angle_x },
            {"name": "xpixel", "units": "pixels", "values": range(xpixels) },
            {"name": "Measurements", "cols": [
                    {"name": "counts"},
                    {"name": "pixels"},
                    {"name": "monitor"},
                    {"name": "count_time"}]},
            {"PolState": PolState, "filename": filename, "start_datetime": file_obj.date,
             "CreationStory":creation_story, "path":path}]
    data_array = zeros((datalen, xpixels, 4))
    mon = file_obj.monitor.counts
    mon.shape += (1,) # broadcast the monitor over the other dimension
    count_time = file_obj.monitor.count_time
    count_time.shape += (1,)
    data_array[:, :, 0] = file_obj.detector.counts
    data_array[:, :, 1] = 1
    data_array[:, :, 2] = mon
    data_array[:, :, 3] = count_time
    # data_array[:,:,4]... I wish!!!  Have to do by hand.
    data = MetaArray(data_array, dtype='float', info=info)
    return data

def FootprintCorrection(DataArray, start, finish, slope, intercept):
    """ 
    Iterates through MetaArray (beginning at "start" and ending at "finish") and adds footprint correction to each value.
    Returns resulting data values as a MetaArray.
    """
    data = MetaArray(DataArray.view(ndarray).copy(), DataArray.dtype, DataArray.infoCopy())
    counts = data[0][start:finish, 0] # interval of data specified by start and finish
    ccounts = (counts * slope) + intercept # applying footprint correction 
    data[0][start:finish, 0] = ccounts # replacing original data in specified interval with corrected data
    return data
    
    
    
    
    
   