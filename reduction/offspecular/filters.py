# -*- coding: latin-1 -*-
from numpy import cos, pi, cumsum, arange, ndarray, ones, zeros, array, newaxis, linspace, empty, resize, sin, allclose, zeros_like, linalg, dot, arctan2, float64, histogram2d, sum, sqrt, loadtxt, searchsorted, NaN, logical_not, fliplr, flipud
import numpy
from numpy.ma import MaskedArray
import os, simplejson, datetime, sys, types, xml.dom.minidom
from copy import deepcopy
from scipy import signal

from FilterableMetaArray import FilterableMetaArray as MetaArray
from he3analyzer import wxHe3AnalyzerCollection as He3AnalyzerCollection
from reflred.reflred.formats import load
from reflred.reflred import rebin as reb
import h5py
import dateutil.parser
import tempfile
import subprocess

DEBUG=False

class Supervisor():
    """ class to hold rebinned_data objects and increment their reference count """
    def __init__(self):
        self.rb_count = 0
        self.rebinned_data_objects = []
        self.plottable_count = 0
        self.plottable_2d_data_objects = []
        self.plots2d_count = 0
        self.plots2d_data_objects = []
        self.plots2d_names = []

    def AddRebinnedData(self, new_object, name='', base_data_obj=None):  
        self.rebinned_data_objects.append(new_object)
        new_object.number = self.rb_count
        self.rb_count += 1
    
    def AddPlottable2dData(self, new_object, parent=None, name='', base_data_obj=None):
        self.plottable_2d_data_objects.append(new_object)
        self.plottable_count += 1
  
    def AddPlot2d(self, new_object, parent=None, name=''):
        self.plots2d_data_objects.append(new_object)
        self.plots2d_names.append(name)
        self.plots2d_count += 1
        
    def __iadd__(self, new_object):
        if isinstance(new_object, rebinned_data):
            self.AddRebinnedData(new_object)
        elif isinstance(new_object, plottable_2d_data):
            self.AddPlottable2dData(new_object)
        return self

def th_2th_single_dataobj():
    info = [{"name": "Theta", "units": "degrees", "values": th_list },
            {"name": "TwoTheta", "units": "degrees", "values": twoth_list},
            {"name": "Measurements", "cols": [
                    {"name": "counts"},
                    {"name": "pixels"},
                    {"name": "monitor"},
                    {"name": "count_time"}]},
            {"PolState": '++'}]
    data = MetaArray((th_len, twoth_len, 5), info=info)
    return data
    
def th_2th_polarized_dataobj():
    info = [{"name": "Theta", "units": "degrees", "values": th_list },
            {"name": "TwoTheta", "units": "degrees", "values": twoth_list},
            {"name": "PolState", "values": "++"},
            {"name": "Measurements", "cols": [
                    {"name": "counts"},
                    {"name": "pixels"},
                    {"name": "monitor"},
                    {"name": "count_time"}]},
            {"PolState": '++'}]
    data = MetaArray((th_len, twoth_len, 1, 5), info=info)
    return data

def qx_qz_single_dataobj(qxmin, qxmax, qxbins, qzmin, qzmax, qzbins):
    info = [{"name": "qz", "units": "inv. Angstroms", "values": linspace(qzmin, qzmax, qzbins) },
            {"name": "qx", "units": "inv. Angstroms", "values": linspace(qxmin, qxmax, qxbins) },
            {"name": "Measurements", "cols": [
                    {"name": "counts"},
                    {"name": "pixels"},
                    {"name": "monitor"},
                    {"name": "count_time"}]},
            {"PolState": '++'}]
    data = MetaArray((qzbins, qxbins, 4), info=info)
    return data

def default_qx_qz_grid():
    return EmptyQxQzGrid(-0.003, 0.003, 201, 0, 0.14, 201)

class EmptyQxQzGrid(MetaArray):
    def __new__(subtype, qxmin, qxmax, qxbins, qzmin, qzmax, qzbins):
        creation_story = subtype.__name__
        creation_story += "({0}, {1}, {2}, {3}, {4}, {5})".format(qxmin, qxmax, qxbins, qzmin, qzmax, qzbins)
        info = [
            {"name": "qx", "units": "inv. Angstroms", "values": linspace(qxmin, qxmax, qxbins) },
            {"name": "qz", "units": "inv. Angstroms", "values": linspace(qzmin, qzmax, qzbins) },
            {"name": "Measurements", "cols": [
                    {"name": "counts"},
                    {"name": "pixels"},
                    {"name": "monitor"},
                    {"name": "count_time"}]},
            {'CreationStory': creation_story}]
        data = MetaArray(zeros((qxbins, qzbins, 4)), info=info)
        return data
        
class EmptyQxQzGridPolarized(MetaArray):
    def __new__(subtype, qxmin, qxmax, qxbins, qzmin, qzmax, qzbins):
        creation_story = subtype.__name__
        creation_story += "({0}, {1}, {2}, {3}, {4}, {5})".format(qxmin, qxmax, qxbins, qzmin, qzmax, qzbins)
        info = [
            {"name": "qx", "units": "inv. frakking Angstroms", "values": linspace(qxmin, qxmax, qxbins) },
            {"name": "qz", "units": "inv. Angstroms", "values": linspace(qzmin, qzmax, qzbins) },
            {"name": "Measurements", "cols": [
                    {"name": "counts_down_down"},
                    {"name": "counts_down_up"},
                    {"name": "counts_up_down"},
                    {"name": "counts_up_up"},
                    {"name": "monitor_down_down"},
                    {"name": "monitor_down_up"},
                    {"name": "monitor_up_down"},
                    {"name": "monitor_up_up"},
                    {"name": "pixels"},
                    {"name": "count_time"}]},
            {'CreationStory': creation_story}]
        data = MetaArray(zeros((qxbins, qzbins, 10)), info=info)
        return data
    
def th_2th_combined_dataobj():
    info = [{"name": "Theta", "units": "degrees", "values": th_list },
            {"name": "TwoTheta", "units": "degrees", "values": twoth_list},
            {"name": "PolState", "values": ['++', '+-', '-+', '--']},
            {"name": "Measurements", "cols": [
                    {"name": "counts"},
                    {"name": "pixels"},
                    {"name": "monitor"},
                    {"name": "count_time"}]}]
    data = MetaArray((th_len, twoth_len, 4, 5), dtype='float', info=info)
    return data

def reflbinned_pixel_single_dataobj(datalen, xpixels):
    info = [{"name": "datapoints", "units": None, "values": range(datalen) },
            {"name": "xpixel", "units": "pixels", "values": range(xpixels) },
            {"name": "Measurements", "cols": [
                    {"name": "counts"},
                    {"name": "pixels"},
                    {"name": "monitor"},
                    {"name": "count_time"}]},
            {"PolState": '++'}]
    data = MetaArray(ones((datalen, xpixels, 5)), dtype='float', info=info)
    return data

def reflbinned_pixel_combined_dataobj(datalen, xpixels):
    info = [{"name": "datapoints", "units": None, "values": range(datalen) },
            {"name": "xpixel", "units": "pixels", "values": range(xpixels) },
            {"name": "PolState", "values": ['++', '+-', '-+', '--']},
            {"name": "Measurements", "cols": [
                    {"name": "counts"},
                    {"name": "pixels"},
                    {"name": "monitor"},
                    {"name": "count_time"}]}]
    data = MetaArray((datalen, xpixels, 4, 5), info=info)
    return data

class Filter2D:
    """ takes MetaArray with 2 dims (2 cols) as input
    and outputs the same thing """ 
    default_path = None
    polarizations = ["down_down", "down_up", "up_down", "up_up"]
    
    def __init__(self, *args, **kwargs):
        self.valid_column_labels = [['', '']]

# ******duplicate decorator, so I commented it out********

#    def updateCreationStory(apply):
#        """ 
#        decorator for 'apply' method - it updates the Creation Story
#        for each filter application.
#        """
#        
#        def newfunc(self, data, *args, **kwargs):
#            result = apply(self, *args, **kwargs)
#            name = self.__class__.__name__
#            new_info = result.infoCopy()
#            new_type = result.dtype
#            new_data = result.view(ndarray)
#            new_args = "".join([', {arg}'.format(arg=arg) for arg in args])
#            new_kwargs = "".join([', {key}={value}'.format(key=key, value=kwargs[key]) for key in kwargs])
#            new_creation_story = "{old_cs}.filter('{fname}', {args}, {kwargs})".format(old_cs=old_cs, fname=name, args=new_args, kwargs=new_kwargs)
#            #print new_creation_story
#            #new_info[-1]["CreationStory"]
#            return result
#        return newfunc

    
    def check_labels(self, data):
        validated = True
        labelsets = self.valid_column_labels
        info = data.infoCopy()
        for labelset in labelsets:
            for col, label in zip(info, labelset):
                if not col["name"] == label:
                    validated = False
        return validated
    
    def validate(self, data):
        validated = True
        if not type(data) == MetaArray:
            print "not MetaArray"
            return False #short-circuit
        if not len(data.shape) == 3:
            print "# coordinate dims not equal 2"
            return False 
        return self.check_labels(data)
    
    def apply(self, data):
        if not self.validate(data):
            print "error in data type"
            return
        return data
 
from functools import wraps
def updateCreationStory(apply):
    """ 
    decorator for 'apply' method - it updates the Creation Story
    for each filter application.
    """
    @wraps(apply)
    def newfunc(self, data, *args, **kwargs):
        name = self.__class__.__name__
        new_args = "".join([', {arg}'.format(arg=arg) for arg in args])
        new_kwargs = "".join([', {key}={value}'.format(key=key, value=kwargs[key]) for key in kwargs])
        new_creation_story = ".filter('{fname}'{args}{kwargs})".format(fname=name, args=new_args, kwargs=new_kwargs)
        result = apply(self, data, *args, **kwargs)
        
        # Try update in place data._info instead! 
        result._info[-1]["CreationStory"] += new_creation_story
        # if the above didn't work, uncomment this below:
        #new_info = result.infoCopy()
        #new_dtype = result.dtype
        #new_data_array = result.view(ndarray)
        #new_info[-1]["CreationStory"] += new_creation_story
        #new_data = MetaArray(new_data_array, dtype=new_dtype, info=new_info)
        #return new_data
        return result
    return newfunc

 
def autoApplyToList(apply):
    """ 
    decorator for 'apply' method - if a list of data objects is given
    as the first argument, applies the filter to each item one at a time.
    """
    
    @wraps(apply)
    def newfunc(self, data, *args, **kwargs):
        if type(data) is types.ListType:
            result = []
            for datum in data:
                result.append(apply(self, datum, *args, **kwargs))
            return result
        else:
            return apply(self, data, *args, **kwargs)
    return newfunc

class CoordinateOffset(Filter2D):
    """ apply an offset to one or both of the coordinate axes """
    
    @autoApplyToList
    @updateCreationStory
    def apply(self, data, offsets={}):
        """ to apply an offset to an axis, add it to the dict of offsets.
        e.g. if data is theta, twotheta, then
        to apply 0.01 offset to twotheta only make offsets = {'twotheta': 0.01}
        """
        new_info = data.infoCopy()
        for key in offsets:
            try:
                axisnum = data._getAxis(key)
                new_info[axisnum]['values'] += offsets[key]
            except:
                pass
        new_data = MetaArray(data.view(ndarray).copy(), info=new_info)
        return new_data

class MaskData(Filter2D):
    """ set all data, normalization to zero within mask """
    
    @autoApplyToList
    @updateCreationStory
    def apply(self, data, xmin=None, xmax=None, ymin=None, ymax=None, invert_mask=False):
        def sanitize (item):
            return int(item) if item != "" else None
        mask = zeros(data.shape, dtype=bool) # array of False
        # convert to data coordinates
        x_array = data._info[0]['values']
        y_array = data._info[1]['values']
        
        def get_index(t, x):
            if (x == "" or x == None): 
                return None
            if float(x) > t.max(): 
                return None
            if float(x) < t.min(): 
                return None
            return searchsorted(t, float(x))
            
        dataslice = (slice(get_index(x_array, xmin), get_index(x_array, xmax)), slice(get_index(y_array, ymin), get_index(y_array, ymax)))
        #print "indexing:", get_index(x_array, xmin), get_index(x_array, xmax, get_index(y_array, ymin), get_index(y_array, ymax)
        print dataslice
        mask[dataslice] = True # set the masked portions to False
        if invert_mask:
            mask = logical_not(mask)            
        new_data = MetaArray(data.view(ndarray).copy(), info=data.infoCopy())
        new_data[mask] = 0
        return new_data

#class MaskData(Filter2D):
#    """ set all data, normalization to zero within mask """
#    
#    @autoApplyToList
#    @updateCreationStory
#    def apply(self, data, xmin=None, xmax=None, ymin=None, ymax=None):
#        def sanitize (item):
#            return int(item) if item != "" else None
#        dataslice = (slice(sanitize(xmin), sanitize(xmax)), slice(sanitize(ymin), sanitize(ymax)))
#        new_data = MetaArray(data.view(ndarray).copy(), info=data.infoCopy())
#        new_data[dataslice] = 0
#        return new_data

class SliceNormData(Filter2D):
    """ Sum 2d data along both axes and return 1d datasets,
    normalized to col named in normalization param """
    
    @autoApplyToList
    def apply(self, data, normalization='monitor'):
        new_info = data.infoCopy()
        x_axis = new_info[0]
        y_axis = new_info[1]
        
        counts_array = data['Measurements':'counts'].view(ndarray)
        norm_array = data['Measurements':normalization].view(ndarray)
        y_out = zeros((data.shape[1], 2))
        x_out = zeros((data.shape[0], 2))
        
        norm_y = sum(norm_array, axis=0)
        sum_y = sum(counts_array, axis=0)
        mask_y = (norm_y != 0)
        y_out[:,0][mask_y] += sum_y[mask_y] / norm_y[mask_y]
        y_out[:,1][mask_y] += sqrt(sum_y)[mask_y] / norm_y[mask_y]
        
        norm_x = sum(norm_array, axis=1)
        sum_x = sum(counts_array, axis=1)
        mask_x = (norm_x != 0)
        x_out[:,0][mask_x] += sum_x[mask_x] / norm_x[mask_x]
        x_out[:,1][mask_x] += sqrt(sum_x)[mask_x] / norm_x[mask_x]
        
        col_info = {"name": "Measurements", "cols": [
                    {"name": "counts"},
                    {"name": "error"} ]}
        
        x_data_obj = MetaArray( x_out, info=[x_axis, col_info, new_info[-1]] )
        y_data_obj = MetaArray( y_out, info=[y_axis, col_info, new_info[-1]] )
        
        return [x_data_obj, y_data_obj]

class CollapseData(Filter2D):
    """ Sum 2d data along both axes and return 1d datasets """
    
    @autoApplyToList
    def apply(self, data):
        new_info = data.infoCopy()
        x_axis = new_info[0]
        y_axis = new_info[1]
        col_info = new_info[2]
        extra_info = new_info[3]
        
        x_out = sum(data.view(ndarray), axis=1)
        y_out = sum(data.view(ndarray), axis=0)
        
        x_data_obj = MetaArray( x_out, info=[x_axis, col_info, extra_info] )
        y_data_obj = MetaArray( y_out, info=[y_axis, col_info, extra_info] )
        
        return [x_data_obj, y_data_obj]

class SliceData(Filter2D):
    """ Sum 2d data along both axes and return 1d datasets """
    
    @autoApplyToList
    def apply(self, data, xmin=None, xmax=None, ymin=None, ymax=None):
        new_info = data.infoCopy()
        x_axis = new_info[0]
        y_axis = new_info[1]
        col_info = new_info[2]
        extra_info = new_info[3]
        
        x_array = data._info[0]['values']
        y_array = data._info[1]['values']
        
        print xmin, xmax, ymin, ymax
        
        def get_index(t, x):
            if (x == "" or x == None): 
                return None
            if float(x) > t.max(): 
                return None
            if float(x) < t.min(): 
                return None
            return searchsorted(t, float(x))
            
        xslice = slice(get_index(x_array, xmin), get_index(x_array, xmax))
        yslice = slice(get_index(y_array, ymin), get_index(y_array, ymax))
        dataslice = (xslice, yslice)
        
        x_out = sum(data.view(ndarray)[dataslice], axis=1)
        y_out = sum(data.view(ndarray)[dataslice], axis=0)
        x_axis['values'] = x_axis['values'][xslice]
        y_axis['values'] = y_axis['values'][yslice]
        
        x_data_obj = MetaArray( x_out, info=[x_axis, col_info, extra_info] )
        y_data_obj = MetaArray( y_out, info=[y_axis, col_info, extra_info] )
        
        return [x_data_obj, y_data_obj]


class WiggleCorrection(Filter2D):
    """ 
    Remove the oscillatory artifact from the Brookhaven 2D detector data
    This filter properly works on data in pixel coordinates, so it belongs
    right at the beginning of most filter chains, before data is converted to
    angle (and then Q...) 
    
    The artifact is defined as being a sinusoidal variation in the effective width
    of the pixel --- this results in two effects: 
    1. an apparent oscillation in sensitivity
    2. an oscillatory shift in the effective location of the pixel with
        respect to an ordered grid of pixels.
    """
    
    def __init__(self, amp=0.140, **kwargs):
        Filter2D.__init__(self, **kwargs)
        self.wiggleAmplitude = amp
        self.valid_column_labels = [["theta", "xpixel"]]
        
        
    def correctionFromPixel(self, xpixel, wiggleAmplitude):
        xpixel = xpixel.astype('float')
        #wiggleAmplitude = self.wiggleAmplitude
        #pixelCorrection = ( (32.0 / (2.0 * pi) ) * wiggleAmplitude * sin( 2.0 * pi * xpixel / 32.0 ) )
        widthCorrection = (wiggleAmplitude * cos(2.0 * pi * xpixel / 32.0))
        pixelCorrection = cumsum(widthCorrection) - widthCorrection[0]
        return [widthCorrection, pixelCorrection]
    
    @autoApplyToList
    @updateCreationStory      
    def apply(self, data, amp=0.14):
        """ Data is MetaArray (for now) with axis values + labels
        Output is the same """
        if not self.validate(data):
            print "error in data type"
            return
        
        num_xpixels = len(data.axisValues('xpixel'))
        if not (num_xpixels == 608):
            print "this correction is only defined for Brookhaven detector!"
        xpixel = data.axisValues('xpixel')
        #arange(num_xpixels + 1, 'float')
        widthCorrection, pixelCorrection = self.correctionFromPixel(xpixel, amp)
        corrected_pixel = xpixel + pixelCorrection
        intens = data['Measurements': 'counts']
        corrected_I = intens / (1.0 + widthCorrection)
        new_info = data.infoCopy()
        new_info[1]["values"] = corrected_pixel
        new_data = MetaArray(data.view(ndarray).copy(), info=new_info)
        new_data['Measurements': 'counts'] = corrected_I

        return new_data
        
class SmoothData(Filter2D):
    """ takes the input and smooths it according to
    the specified window type and width, along the given axis """
    
    
    @autoApplyToList
    @updateCreationStory
    def apply(self, data, window="flat", width=5, axis=0):
        """smooth the data using a window with requested size.
        
        ***************************************************************
        *** Adapted from http://www.scipy.org/Cookbook/SignalSmooth ***
        ***************************************************************
        
        This method is based on the convolution of a scaled window with the signal.
        The signal is prepared by introducing reflected copies of the signal 
        (with the window size) in both ends so that transient parts are minimized
        in the begining and end part of the output signal.
        
        input:
            data: the input signal 
            width: the dimension of the smoothing window; should be an odd integer
            window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
                flat window will produce a moving average smoothing.
            axis: the axis to which the smoothing is applied

        output:
            the smoothed signal
            
        example:

        t=linspace(-2,2,0.1)
        x=sin(t)+randn(len(t))*0.1
        y=smooth(x)
        
        see also: 
        
        numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
        scipy.signal.lfilter
     
        TODO: the window parameter could be the window itself if an array instead of a string   
        """

        axis = int(axis)
        width = int(width)
        src_data = data.view(ndarray)
        
        if src_data.shape[axis] < width:
            raise ValueError, "Input vector " + str(src_data.shape) + " needs to be bigger than window size: " + str(width)

        if width<3:
            return data

        if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
            raise ValueError, "Window is not one of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"

        if window == 'flat': #moving average
            kernel=ones(width,'d')
        else:
            #w=eval('numpy.'+window+'(window_len)')
            kernel = getattr(numpy, window)(width)
            
        ia_size = list(src_data.shape) # intermediate array initialization
        ia_size[axis] += 2*(width-1)
        ia = empty(ia_size)
        
        #start with empty slices over first two axes
        output_slice = [slice(None, None)] * len(ia.shape)
        input_slice = [slice(None, None)] * len(src_data.shape)
        first_element_slice = [slice(None, None)] * len(src_data.shape)
        first_element_slice[axis] = slice(0, 1)
        last_element_slice = [slice(None, None)] * len(src_data.shape)
        last_element_slice[axis] = slice(-1, None)
        
        # mirror data around left edge (element zero):
        input_slice[axis] = slice(width, 1, -1)
        output_slice[axis] = slice(None, width-1, 1)
        ia[output_slice] = 2*src_data[first_element_slice] - src_data[input_slice]
        # mirror data around right edge (last element, -1):
        input_slice[axis] = slice(-1, -width, -1)
        output_slice[axis] = slice(-(width-1), None)
        ia[output_slice] = 2*src_data[last_element_slice] - src_data[input_slice]        
        # fill the center of the expanded array with the original array
        output_slice[axis] = slice(width-1, -(width-1), 1)
        ia[output_slice] = src_data[:]
        
        kernel_shape = [1,] * len(src_data.shape)
        kernel_shape[axis] = width
        kernel.shape = tuple(kernel_shape)
        
        # modes include same, valid, full
        sm_ia = signal.convolve(ia, kernel, mode='same')
        output_slice[axis] = slice(width-1, -(width-1), 1)
        
        new_info = data.infoCopy()
        smoothed_data = sm_ia[output_slice]
        output_data = src_data.copy()
        
        # now go through and replace counts cols
        for colnum, col in enumerate(new_info[-2]['cols']):
            if col['name'].startswith('counts'):
                output_data[...,colnum] = smoothed_data[...,colnum]       

        new_data = MetaArray(output_data, info=new_info)
        
        return new_data

        #y=numpy.convolve(w/w.sum(),s,mode='same')
        #return y[window_len-1:-window_len+1]

class AsterixPixelsToTwotheta(Filter2D):
    """ input array has pixels axis, convert to 
    two-theta based on distance from sample to detector and
    center pixel when two-theta motor is set to zero """
    
    @autoApplyToList
    @updateCreationStory
    def apply(self, data, qzero_pixel = 145., twotheta_offset=0.0, pw_over_d=0.0003411385649):
        """ pw_over_d is pixel width divided by distance (sample to detector) """
        new_info = data.infoCopy()
        # find pixels axis, and replace with two-theta
        # assuming there are only 2 dimensions of data, looking only at indices 0, 1
        xpixel_axis = next((i for i in xrange(len(new_info)) if new_info[i]['name'] == 'xpixel'), None) 
        if xpixel_axis < 0:
            print "error: no xpixel axis in this dataset"
            return
        
        new_info[xpixel_axis]['name'] = 'twotheta'
        twotheta_motor = 0.0
        if data._info[-1].has_key('state'):
            twotheta_motor = float(data._info[-1]['state']['A[0]'])
        pixels = data.axisValues('xpixel')
        twotheta = arctan2((pixels - qzero_pixel) * pw_over_d, 1.0) * 180./pi + twotheta_offset + twotheta_motor
        new_info[xpixel_axis]['values'] = twotheta
        new_data = MetaArray(data.view(ndarray).copy(), info=new_info)
        
        return new_data
        
class AsterixTOFToWavelength(Filter2D):
    """ input array has TOF axis, convert to wavelength
    based on calibration (depends on distance from source to detector) """
    
    @autoApplyToList
    @updateCreationStory
    def apply(self, data, wl_over_tof=1.9050372144288577e-5):
        """ wl_over_tof is wavelength divided by time-of-flight """
        new_info = data.infoCopy()
        # find pixels axis, and replace with two-theta
        # assuming there are only 2 dimensions of data, looking only at indices 0, 1
        tof_axis = next((i for i in xrange(len(new_info)) if new_info[i]['name'] == 'tof'), None) 
        if tof_axis < 0:
            print "error: no tof axis in this dataset"
            return
        
        new_info[tof_axis]['name'] = 'wavelength'
        tof = data.axisValues('tof')
        wavelength = (tof * wl_over_tof)
        # shift by half-bin width to align to center of tof bins!
        wavelength += (tof[1] - tof[0])/2.0 * wl_over_tof
        # (bins appear to be centered)
        new_info[tof_axis]['values'] = wavelength
        new_data = MetaArray(data.view(ndarray).copy(), info=new_info)
        
        return new_data

class AsterixShiftData(Filter2D):

    @autoApplyToList
    @updateCreationStory
    def apply(self, data, edge_bin = 180, axis=0):
        """ Shift 2D dataset along axis 0, also shifting the axisValues
        along that edge (assuming linear behaviour) 
        This is useful for time-of-flight data where the low-t data is empty due
        to spectrum shape, and can be interpreted as the high-t data from the
        previous pulse.""" 
        #axis = 0
        axis = int(axis)
        if axis > 1:  
            axis = 1
        if axis < 0: 
            axis = 0
        new_info = data.infoCopy()
        old_axis_values = new_info[axis]['values']
        src_data = data.view(ndarray).copy()
        
        shifted_data = empty(src_data.shape)
        
        #start with empty slices over first two axes
        output_slice = [slice(None, None)] * len(src_data.shape)
        input_slice = [slice(None, None)] * len(src_data.shape)
        
        # move data from edge_bin to end to beginning:
        input_slice[axis] = slice(edge_bin, None)
        output_slice[axis] = slice(None, -edge_bin)
        shifted_data[output_slice] = src_data[input_slice]
        # move data from beginning to edge bin to the end of the new dataset
        input_slice[axis] = slice(None, edge_bin)
        output_slice[axis] = slice(-edge_bin, None)
        shifted_data[output_slice] = src_data[input_slice]

        shifted_axis = zeros(src_data.shape[axis])
        dx = old_axis_values[1] - old_axis_values[0]
        shifted_axis[:-edge_bin] = old_axis_values[edge_bin:]
        shifted_axis[-edge_bin:] = old_axis_values[:edge_bin] + (old_axis_values[-1] - old_axis_values[0]) + dx
        
        new_info[axis]['values'] = shifted_axis
        new_data = MetaArray(shifted_data, info=new_info)
        return new_data

class AsterixCorrectSpectrum(Filter2D):
    
    def apply(self, data, spectrum):
        ##polarizations = ["down_down", "down_up", "up_down", "up_up"]
        # inherit polarizations list from Filter2D:
        passthrough_cols = ["counts_%s" % (pol,) for pol in self.polarizations]
        passthrough_cols.extend(["pixels", "count_time"])
        #expressions = [{"name":col, "expression":"data1_%s" % (col,)} for col in passthrough_cols]
        expressions = []
        spectrum_cols = [col['name'] for col in spectrum._info[-2]['cols']]
        for pol in self.polarizations:
            if ("spectrum_%s" % (pol,) in spectrum_cols):
                spec_id = "data2_spectrum_%s" % (pol,)
            else:
                spec_id = "data2_spectrum"
            expressions.append({"name":"monitor_%s" % (pol,), "expression":"data1_monitor_%s * %s[:,newaxis]" % (pol,spec_id)})
        result = Algebra().apply(data, spectrum, expressions, passthrough_cols)
        return result

class NormalizeToMonitor(Filter2D):
    """ divide all the counts columns by monitor and output as normcounts, with stat. error """
    
    @autoApplyToList
    def apply(self, data):
        cols = [col['name'] for col in data._info[-2]['cols']]
        passthrough_cols = [col for col in cols if (not col.startswith('counts') and not col.startswith('monitor'))]
        counts_cols = [col for col in cols if col.startswith('counts')]
        monitor_cols = [col for col in cols if col.startswith('monitor')]
        info = data.infoCopy()
        info[-2]['cols'] = []
        output_array = zeros( data.shape[:-1] + (len(counts_cols) + len(passthrough_cols),), dtype=float)
        expressions = []
        for i, col in enumerate(passthrough_cols):
            info[-2]['cols'].append({"name":col})
            output_array[..., i] = data["Measurements":col]
            
        for i, col in enumerate(counts_cols):
            j = i + len(passthrough_cols)
            col_suffix = col[len('counts'):]
            monitor_id = 'monitor'
            if ('monitor'+col_suffix) in monitor_cols:
                monitor_id += col_suffix
            info[-2]['cols'].append({"name":"counts_norm%s" % (col_suffix,)})
            mask = data["Measurements":monitor_id].nonzero()
            #print mask
            output_array[..., j][mask] = data["Measurements":col][mask] / data["Measurements":monitor_id][mask]
            #expression = "data1_counts%s / data1_%s" % (col_suffix, monitor_id)
            #error_expression = "sqrt(data1_counts%s) / data1_%s" % (col_suffix, monitor_id)
            #expressions.append({"name": "counts_norm%s" % (col_suffix,), "expression":expression})
            #expressions.append({"name": "error_counts_norm%s" % (col_suffix,), "expression":error_expression})
        #result = Algebra().apply(data, None, expressions, passthrough_cols)
        result = MetaArray(output_array, info=info)
        return result

class PixelsToTwotheta(Filter2D):
    """ input array has axes theta and pixels:
    output array has axes theta and twotheta.
    
    Pixel-to-angle conversion is arithmetic (pixels-per-degree=constant)
    output is rebinned to fit in a rectangular array if detector angle 
    is not fixed. """
    
    @autoApplyToList
    @updateCreationStory 
    def apply(self, data, pixels_per_degree=80.0, qzero_pixel=309, instr_resolution=1e-6, ax_name='xpixel'):
        """\
            input array has axes theta and pixels:
            output array has axes theta and twotheta.
            
            Pixel-to-angle conversion is arithmetic (pixels-per-degree=constant)
            output is rebinned to fit in a rectangular array if detector angle 
            is not fixed. """
        print " inside PixelsToTwoTheta "
        pixels_per_degree = float(pixels_per_degree) # coerce, in case it was an integer
        qzero_pixel = float(qzero_pixel) 
        instr_resolution = float(instr_resolution)
        
        new_info = data.infoCopy()
        det_angle = new_info[-1].get('det_angle', None)
        # det_angle should be a vector of the same length as the other axis (usually theta)
        # or else just a float, in which case the detector is not moving!
        ndim = len(new_info) - 2 # last two entries in info are for metadata
        pixel_axis = next((i for i in xrange(len(new_info)-2) if new_info[i]['name'] == ax_name), None)
        if pixel_axis < 0:
            raise ValueError("error: no %s axis in this dataset" % (ax_name,))
            
        if hasattr(det_angle, 'max'):
            det_angle_max = det_angle.max()
            det_angle_min = det_angle.min()
        else: # we have a number
            det_angle_max = det_angle_min = det_angle
            
        if ((det_angle_max - det_angle_min) < instr_resolution) or ndim == 1 or ax_name != 'xpixel':
            #then the detector is fixed and we just change the values in 'xpixel' axis vector to twotheta
            # or the axis to be converted is y, which doesn't move in angle.
            print "doing the simple switch of axis values..."
            
            #data_slices = [slice(None, None, 1), slice(None, None, 1)]
            #data_slices[pixel_axis] = slice(None, None, -1)
            
            if ax_name == 'xpixel':
                twotheta_motor = det_angle_min
                new_info[pixel_axis]['name'] = 'twotheta'
            else:
                twotheta_motor = 0.0 # we don't have a y-motor!
                new_info[pixel_axis]['name'] = 'twotheta_y'
                
            pixels = new_info[pixel_axis]['values']
            twoth = (pixels - qzero_pixel) / pixels_per_degree + twotheta_motor
            #new_info[pixel_axis]['values'] = twoth[::-1] # reverse: twotheta increases as pixels decrease
            new_info[pixel_axis]['values'] = twoth
            new_info[pixel_axis]['units'] = 'degrees'
            #new_array = (data.view(ndarray).copy())[data_slices]
            new_array = (data.view(ndarray).copy())
            new_data = MetaArray(new_array, info=new_info)
        
        else:
            # the detector is moving - have to rebin the dataset to contain all values of twoth
            # this is silly but have to set other axis!
            other_axis = (1 if pixel_axis == 0 else 0)
            other_vector = new_info[other_axis]['values']
            other_spacing = other_vector[1] - other_vector[0]
            pixels = new_info[pixel_axis]['values']
            twoth = (pixels - qzero_pixel) / pixels_per_degree
            #twoth = twoth[::-1] # reverse
            twoth_min = det_angle_min + twoth.min()
            twoth_max = det_angle_max + twoth.max()
            twoth_max_edge = twoth_max + 1.0 / pixels_per_degree
            dpp = 1.0 / pixels_per_degree
            #output_twoth_bin_edges = arange(twoth_max + dpp, twoth_min - dpp, -dpp)
            output_twoth_bin_edges = arange(twoth_min - dpp, twoth_max + dpp, dpp)
            output_twoth = output_twoth_bin_edges[:-1]
            other_bin_edges = linspace(other_vector[0], other_vector[-1] + other_spacing, len(other_vector) + 1)
            new_info[pixel_axis]['name'] = 'twotheta' # getting rid of pixel units: substitute twoth
            new_info[pixel_axis]['values'] = output_twoth
            new_info[pixel_axis]['units'] = 'degrees'
            output_shape = [0,0,0]
            output_shape[pixel_axis] = len(output_twoth)
            output_shape[other_axis] = len(other_vector)
            output_shape[2] = data.shape[2] # number of columns is unchanged!
            new_data = MetaArray(tuple(output_shape), info=new_info) # create the output data object!
            
            tth_min = twoth.min()
            tth_max = twoth.max()
            data_in = data.view(ndarray).copy()
            for i, da in enumerate(det_angle):
                twoth_min = da + tth_min
                twoth_max = da + tth_max
                input_twoth_bin_edges = empty(len(pixels) + 1)
                input_twoth_bin_edges[-1] = twoth_max + 1.0 / pixels_per_degree
                input_twoth_bin_edges[:-1] = twoth + da         
                #data_cols = ['counts', 'pixels', 'monitor', 'count_time']
                cols = new_info[-2]['cols']
                
                for col in range(len(cols)):
                    input_slice = [slice(None, None), slice(None, None), col]
                    #input_slice[pixel_axis] = slice(i, i+1)
                    input_slice[other_axis] = i
                    array_to_rebin = data_in[input_slice]
                    new_array = reb.rebin(input_twoth_bin_edges, array_to_rebin, output_twoth_bin_edges)
                    new_data.view(ndarray)[input_slice] = new_array
            
#        th_vector = data.axisValues('theta')
#        th_spacing = th_vector[1] - th_vector[0]
#        pixels = data.axisValues('xpixel')
#        twoth = -1.0 * (pixels - qzero_pixel) / pixels_per_degree
#        twoth_min = det_angle.min() + twoth.min()
#        twoth_max = det_angle.max() + twoth.max()
#        twoth_max_edge = twoth_max + 1.0 / pixels_per_degree
#        dpp = 1.0 / pixels_per_degree
#        output_twoth_bin_edges = arange(twoth_max + dpp, twoth_min - dpp, -dpp)
#        output_twoth = output_twoth_bin_edges[:-1]
#        
#        #input_twoth_bin_edges = output_twoth_bin_edges.copy()
#        #input_twoth_bin_edges[:-1] = twoth
#        th_bin_edges = linspace(th_vector[0], th_vector[-1] + th_spacing, len(th_vector) + 1)
#        new_info[1]['name'] = 'twotheta' # getting rid of pixel units: substitute twoth
#        new_info[1]['values'] = output_twoth
#        new_info[1]['units'] = 'degrees'
#        new_data = MetaArray((len(th_vector), len(output_twoth), data.shape[2]), info=new_info) # create the output data object!
#        # (still has to be filled with correct values)
#                       
#        if ((det_angle.max() - det_angle.min()) < instr_resolution):
#            #then the detector is fixed and we can pass a single 2theta vector to rebin2d
#            input_twoth_bin_edges = empty(len(pixels) + 1)
#            input_twoth_bin_edges[0] = twoth_max + 1.0 / pixels_per_degree
#            input_twoth_bin_edges[1:] = twoth + det_angle.min()
#            data_cols = ['counts', 'pixels', 'monitor', 'count_time']
#            for col in data_cols:
#                array_to_rebin = data[:, :, col].view(ndarray).copy() 
#                new_array = reb.rebin2d(th_bin_edges, input_twoth_bin_edges, array_to_rebin, th_bin_edges, output_twoth_bin_edges)
#                new_data[:, :, col] = new_array
#        else:
#            #then the detector is not fixed, and we have to pass in each A4 value at a time to rebin
#            tth_min = twoth.min()
#            tth_max = twoth.max()
#            for i, da in enumerate(det_angle):
#                twoth_min = da + tth_min
#                twoth_max = da + tth_max
#                input_twoth_bin_edges = empty(len(pixels) + 1)
#                input_twoth_bin_edges[0] = twoth_max + 1.0 / pixels_per_degree
#                input_twoth_bin_edges[1:] = twoth + da         
#                data_cols = ['counts', 'pixels', 'monitor', 'count_time']
#                for col in data_cols:
#                    array_to_rebin = data[i, :, col].view(ndarray).copy()
#                    new_array = reb.rebin(input_twoth_bin_edges, array_to_rebin, output_twoth_bin_edges)
#                    new_data[i, :, col] = new_array
                
        return new_data

class Autogrid(Filter2D):
    """ take multiple datasets and create a grid which covers all of them
    - stepsize is smallest stepsize found in datasets
    returns an empty grid with units and labels
    
    if extra_grid_point is True, adds one point to the end of each axis
    so each dimension is incremented by one (makes edges for rebinning) """
    
    def apply(self, list_of_datasets, extra_grid_point=True, min_step=1e-10):
        num_datasets = len(list_of_datasets)
        dims = 2
        dim_min = zeros((dims, num_datasets))
        dim_max = zeros((dims, num_datasets))
        dim_len = zeros((dims, num_datasets))
        dim_step = zeros((dims, num_datasets))
    
        for i, data in enumerate(list_of_datasets):
            info = data.infoCopy()
            for dim in range(dims):
                av = data.axisValues(dim)
                dim_min[dim, i] = av.min()
                dim_max[dim, i] = av.max()
                dim_len[dim, i] = len(av)
                if dim_len[dim, i] > 1:
                    dim_step[dim, i] = float(dim_max[dim, i] - dim_min[dim, i]) / (dim_len[dim, i] - 1)
                    # dim0_max[i] += th_step[i] # add back on the last step
                else:
                    dim_step[dim, i] = min_step

        final_stepsizes = []
        absolute_max = []
        absolute_min = []
        for dim in range(dims):
            dim_stepsize = dim_step[dim].min()
            if dim_stepsize < min_step:
                dim_stepsize = min_step
            final_stepsizes.append(dim_stepsize)
            
            absolute_max.append(dim_max[dim].max())
            absolute_min.append(dim_min[dim].min())
            
        # now calculate number of steps:
        output_dims = []
        for dim in range(dims):
            if (dim_len[dim].max() == 1) or (absolute_max[dim] == absolute_min[dim]):
                steps = 1
            else:
                steps = int(round(float(absolute_max[dim] - absolute_min[dim]) / final_stepsizes[dim]))
            if extra_grid_point == True:
                steps += 1
            output_dims.append(steps)
        
        new_info = list_of_datasets[0].infoCopy() # take units etc from first dataset
         # then tack on the number of columns already there:
        output_dims.append(len(new_info[2]['cols']))
        for dim in range(dims):
            new_info[dim]["values"] = (arange(output_dims[dim], dtype='float') * final_stepsizes[dim]) + absolute_min[dim]
        output_grid = MetaArray(zeros(tuple(output_dims)), info=new_info)
        return output_grid
        
    
# *******duplicate?********
    
#class ICPDataFromFile(MetaArray):
#    default_path = None
#       
#    def __new__(subtype, filename, path=None, auto_PolState=False, PolState=''):
#        """ 
#        loads a data file into a MetaArray and returns that.
#        Checks to see if data being loaded is 2D; if not, quits
#        
#        Need to rebin and regrid if the detector is moving...
#        """
#        lookup = {"a":"--", "b":"+-", "c":"-+", "d":"++", "g": ""}
#        if path == None:
#            path = subtype.default_path
#        if path == None:
#            path = os.getcwd()
#        subtype.default_path = path
#        Filter2D.default_path = path
#        
#        def new_single(filename, path, auto_PolState, PolState):
#            file_obj = load(os.path.join(path, filename))
#            if not (len(file_obj.detector.counts.shape) == 2):
#                # not a 2D object!
#                return
#            if auto_PolState:
#                key = filename[-2] # na1, ca1 etc. are --, nc1, cc1 are -+...
#                PolState = lookup[key]
#            # force PolState to a regularized version:
#            if not PolState in lookup.values():
#                PolState = ''
#            datalen, xpixels = file_obj.detector.counts.shape
#            creation_story = "ICPDataFromFile('{fn}'".format(fn=filename)
#            if not PolState == '':
#                creation_story += ", PolState='{0}'".format(PolState)
#            creation_story += ")" 
#            info = [{"name": "theta", "units": "degrees", "values": file_obj.sample.angle_x, "det_angle":file_obj.detector.angle_x },
#                    {"name": "xpixel", "units": "pixels", "values": range(xpixels) },
#                    {"name": "Measurements", "cols": [
#                            {"name": "counts"},
#                            {"name": "pixels"},
#                            {"name": "monitor"},
#                            {"name": "count_time"}]},
#                    {"PolState": PolState, "filename": filename, "start_datetime": file_obj.date,
#                     "CreationStory":creation_story, "path":path}]
#            data_array = zeros((datalen, xpixels, 4))
#            mon = file_obj.monitor.counts
#            mon.shape += (1,) # broadcast the monitor over the other dimension
#            count_time = file_obj.monitor.count_time
#            count_time.shape += (1,)
#            data_array[:, :, 0] = file_obj.detector.counts
#            data_array[:, :, 1] = 1
#            data_array[:, :, 2] = mon
#            data_array[:, :, 3] = count_time
#            # data_array[:,:,4]... I wish!!!  Have to do by hand.
#            data = MetaArray(data_array, dtype='float', info=info)
#            return data
#        
#        if type(filename) is types.ListType:
#            result = [new_single(fn, path, auto_PolState, PolState) for fn in filename]
#            return result
#        else:
#            return new_single(filename, path, auto_PolState, PolState)

def hdf_to_dict(hdf_obj, convert_i1_tostr=True):
    out_dict = {}
    for key in hdf_obj:
        val = hdf_obj[key]
        if type(val) == h5py.highlevel.Dataset:
            if (val.value.dtype == 'int8') and (convert_i1_tostr == True):
                value = val.value.tostring()
            else:
                value = val.value 
            out_dict[key] = value
        else:
            out_dict[key] = hdf_to_dict(val)
    return out_dict

def LoadAsterixMany(filedescriptors):
    result = [LoadAsterixRawHDF(fd['filename'], friendly_name=fd['friendly_name']) for fd in filedescriptors]
    return result

def LoadAsterixRawHDF(filename, path=None, friendly_name="", format="HDF5", **kwargs):
    if path == None:
        path = os.getcwd()
    print "format:", format
    if friendly_name.endswith('hdf'):
        format = "HDF4"
    else: #h5
        format = "HDF5"
        
    if format == "HDF4":
        print "converting hdf4 to hdf5"
        (tmp_fd, tmp_path) = tempfile.mkstemp() #temporary file for converting to HDF5
        print tmp_path
        print 'h4toh5 %s %s' % (os.path.join(path, filename), tmp_path)
        subprocess.call(['h4toh5',  os.path.join(path, filename), tmp_path])
        hdf_obj = h5py.File(tmp_path, mode='r')
    else:
        hdf_obj = h5py.File(os.path.join(path, filename), mode='r')
    run_title = hdf_obj.keys()[0]
    run_obj = hdf_obj[run_title]
    state = hdf_to_dict(run_obj['ASTERIX'])
    monitor = hdf_to_dict(run_obj['scalars'])
    tof = run_obj['ordela_tof_pz']['tof'].value.astype(float64)
    twotheta_pixel = run_obj['ordela_tof_pz']['X'].value.astype(float64)
    data = run_obj['ordela_tof_pz']['data'].value.astype(float64)
    creation_story = "LoadAsterixRawHDF('{fn}')".format(fn=filename)
    output_objs = []
    #for col in range(4):
    info = [{"name": "tof", "units": "nanoseconds", "values": tof[:-1] },
        {"name": "xpixel", "units": "pixels", "values": twotheta_pixel[:-1] },
        {"name": "Measurements", "cols": [
                {"name": "counts_down_down"},
                {"name": "counts_down_up"},
                {"name": "counts_up_down"},
                {"name": "counts_up_up"},
                {"name": "monitor_down_down"},
                {"name": "monitor_down_up"},
                {"name": "monitor_up_down"},
                {"name": "monitor_up_up"},
                {"name": "pixels"},
                {"name": "count_time"}]},
        {"PolState": '', "filename": filename, "start_datetime": None, 
         "state": state, "CreationStory":creation_story, "path":path}]
    data_array = zeros((500, 256, 10))
    data_array[:,:,-2] = 1.0 # pixels

    data_array[:,:,-1] = 1.0 # count time
    for i in range(4):
        data_array[:,:,i] = data[i,:,:]
        data_array[:,:,i+4] = monitor['microamphours_p%d' % (i,)]
        #data_array[:,:,0] = data[col,:,:]
        #output_objs.append(MetaArray(data_array[:], dtype='float', info=info[:]))

    hdf_obj.close()
    if format == "HDF4":
        print "removing temporary file"
        os.remove(tmp_path)
        print "temp file removed"
        
    #return output_objs
    new_data = MetaArray(data_array[:], dtype='float', info=info[:])
    new_data.friendly_name = friendly_name # goes away on dumps/loads... just for initial object.
    return new_data


def SuperLoadAsterixHDF(filename, friendly_name="", path=None, center_pixel = 145.0, wl_over_tof=1.9050372144288577e-5, pixel_width_over_dist = 0.0195458*pi/180., format="HDF5"):
    """ loads an Asterix file and does the most common reduction steps, 
    giving back a length-4 list of data objects in twotheta-wavelength space,
    with the low-tof region shifted to the high-tof region """
    data_objs = LoadAsterixRawHDF(filename, path, format)
    tth_converted = AsterixPixelsToTwotheta().apply(data_objs, qzero_pixel=center_pixel, pw_over_d=pixel_width_over_dist)
    wl_converted = AsterixTOFToWavelength().apply(tth_converted, wl_over_tof=wl_over_tof)
    shifted = AsterixShiftData().apply(wl_converted, edge_bin=180)
    return shifted   

def LoadAsterixHDF(filename, friendly_name="", path=None, center_pixel = 145.0, wl_over_tof=1.9050372144288577e-5):
    if path == None:
        path = os.getcwd()
    hdf_obj = h5py.File(os.path.join(path, filename))
    run_title = hdf_obj.keys()[0]
    run_obj = hdf_obj[run_title]
    state = hdf_to_dict(run_obj['ASTERIX'])
    print state
    monitor = hdf_to_dict(run_obj['scalars'])
    tof = run_obj['ordela_tof_pz']['tof'].value.astype(float64)
    twotheta_pixel = run_obj['ordela_tof_pz']['X'].value.astype(float64)
    data = run_obj['ordela_tof_pz']['data'].value.astype(float64)
    tof_to_wavelength_conversion = (0.019050372144288577 / 1000.)
    wavelength = (tof * wl_over_tof)[:-1]
    # shift by half-bin width to align to center of tof bins!
    wavelength += (tof[1] - tof[0])/2.0 * wl_over_tof 
    # (bins appear to be centered)
    shifted_data = empty(data.shape)
    shifted_data[:,:320,:] = data[:,-320:,:]
    shifted_data[:,320:,:] = data[:,:-320,:]
    shifted_wavelength = zeros(wavelength.shape)
    shifted_wavelength[:320] = wavelength[-320:]
    shifted_wavelength[320:] = wavelength[:-320] + (wavelength[-1] + wavelength[0])
    pixel_width_over_dist = 0.0195458*pi/180.
    twotheta_offset = float(state['A[0]'])
    twotheta = arctan2((twotheta_pixel - center_pixel) * pixel_width_over_dist, 1.0) * 180./pi + twotheta_offset
    print 'tth:', float(state['A[0]'])
    pol_states = {0:'--', 1:'-+', 2:'+-', 3:'++'}
    creation_story = "LoadAsterixHDF('{fn}')".format(fn=filename)
    #wavelength_axis = data_in[:,0,0]
    #twotheta_axis = data_in[0,:,1]
    output_objs = []
    for col in range(4):
        info = [{"name": "wavelength", "units": "Angstroms", "values": shifted_wavelength },
            {"name": "twotheta", "units": "degrees", "values": twotheta },
            {"name": "Measurements", "cols": [
                    {"name": "counts"},
                    {"name": "pixels"},
                    {"name": "monitor"},
                    {"name": "count_time"}]},
            {"PolState": pol_states[col], "filename": filename, "start_datetime": None, 
             "theta": float(state['A[1]']), "det_angle": float(state['A[0]']),
             "CreationStory":creation_story, "path":path}]
        data_array = zeros((500, 256, 4))
        data_array[:,:,1] = 1.0 # pixels
        data_array[:,:,2] = 1.0 # monitor
        data_array[:,:,3] = 1.0 # count time
        data_array[:,:,0] = shifted_data[col,:,:]
        output_objs.append(MetaArray(data_array[:], dtype='float', info=info[:]))
    return output_objs 

def LoadAsterixData(filename, friendly_name="", path = None):
    if path == None:
        path = os.getcwd()
    pol_states = {2:'--', 3:'-+', 4:'+-', 5:'++'}  
    creation_story = "LoadAsterixData('{fn}')".format(fn=filename)
    data_in = loadtxt(os.path.join(path, filename)).reshape(500,256,6)
    wavelength_axis = data_in[:,0,0]
    twotheta_axis = data_in[0,:,1]
    output_objs = []
    for col in range(2,6):
        info = [{"name": "wavelength", "units": "Angstroms", "values": wavelength_axis },
            {"name": "twotheta", "units": "degrees", "values": twotheta_axis },
            {"name": "Measurements", "cols": [
                    {"name": "counts"},
                    {"name": "pixels"},
                    {"name": "monitor"},
                    {"name": "count_time"}]},
            {"PolState": pol_states[col], "filename": filename, "start_datetime": None, 
             "CreationStory":creation_story, "path":path}]
        data_array = zeros((500, 256, 4))
        data_array[:,:,1] = 1.0 # pixels
        data_array[:,:,2] = 1.0 # monitor
        data_array[:,:,3] = 1.0 # count time
        data_array[:,:,0] = data_in[:,:,col]
        output_objs.append(MetaArray(data_array[:], dtype='float', info=info[:]))
    return output_objs    

def LoadText(filename, friendly_name="", path=None, first_as_x=True):
    if path == None:
        path = os.getcwd()
    creation_story = "LoadText('{fn}')".format(fn=filename)
    data_in = loadtxt(os.path.join(path, filename))
    info = []
    first_y_col = 0
    if first_as_x:
        info.append({"name":"xaxis", "units":"unknown", "values": data_in[:,0]})
        first_y_col = 1
    else:
        info.append({"name":"rownumber", "units":"index", "values": range(data_in.shape[1])})
    
    info.append({"name":"Measurements", "cols":[]})
    for col in range(first_y_col, data_in.shape[1]):
        info[1]["cols"].append({"name": "column%d" % (col,)})
        
    info.append({"filename": filename, "start_datetime": None, 
             "CreationStory":creation_story, "path":path}) 
    output_obj = MetaArray(data_in[:,first_y_col:], dtype='float', info=info[:])
    return output_obj 

def LoadAsterixSpectrum(filename, friendly_name="", path=None):
    spec = LoadText(filename, path, first_as_x = True)
    spec._info[0]["name"] = "tof"
    spec._info[0]["units"] = "microseconds"
    if spec.shape[1] == 1:
        spec._info[1]['cols'][0]['name'] = 'spectrum'
    elif spec.shape[1] == 4:
        for i, pol in enumerate(Filter2D.polarizations):
            spec._info[1]['cols'][i]['name'] = 'spectrum_%' % (pol,)            
    return spec

def LoadICPMany(filedescriptors):
    result = []
    for fd in filedescriptors:
        new_data = LoadICPData(fd.pop('filename'), **fd)
        if type(new_data) is types.ListType:
            result.extend(new_data)
        else:
            result.append(new_data)
    return result        

DETECTOR_ACTIVE = (320, 340)

def LoadMAGIKPSD(filename, path="", friendly_name="", collapse_y=True, auto_PolState=False, PolState='', flip=True, transpose=True, **kw):
    """ 
    loads a data file into a MetaArray and returns that.
    Checks to see if data being loaded is 2D; if not, quits
    
    Need to rebin and regrid if the detector is moving...
    """
    lookup = {"DOWN_DOWN":"_down_down", "UP_DOWN":"_up_down", "DOWN_UP":"_down_up", "UP_UP":"_up_up", "entry": ""}
    file_obj = h5py.File(filename)
    file_obj = h5py.File(os.path.join(path, filename))
    
    #if not (len(file_obj.detector.counts.shape) == 2):
        # not a 2D object!
    #    return
    for entryname in file_obj:
        entry = file_obj[entryname]
        active_slice = slice(None, DETECTOR_ACTIVE[0], DETECTOR_ACTIVE[1])
        counts_value = entry['DAS_logs']['areaDetector']['counts'].value[:, :DETECTOR_ACTIVE[0], :DETECTOR_ACTIVE[1]]
        dims = counts_value.shape
        print dims
        ndims = len(dims)
        if auto_PolState:
            PolState = lookup.get(entryname, "")
        # force PolState to a regularized version:
        if not PolState in lookup.values():
            PolState = ''
        #datalen = file_obj.detector.counts.shape[0]
        if ndims == 2:
            if DEBUG: print "2d"
            ypixels = dims[0]
            xpixels = dims[1]
        elif ndims >= 3:
            if DEBUG: print "3d"
            frames = dims[0]
            xpixels = dims[1]
            ypixels = dims[2]
        
        creation_story = "LoadMAGIKPSD('{fn}', path='{p}')".format(fn=filename, p=path, aPS=auto_PolState, PS=PolState)

        # doesn't really matter; changing so that each keyword (whether it took the default value
        # provided or not) will be defined
        #    if not PolState == '':
        #        creation_story += ", PolState='{0}'".format(PolState)
        # creation_story += ")" 
    
    
        if ndims == 2: # one of the dimensions has been collapsed.
            info = []     
            info.append({"name": "xpixel", "units": "pixels", "values": arange(xpixels) }) # reverse order
            info.append({"name": "theta", "units": "degrees", "values": entry['DAS_logs']['sampleAngle']['softPosition'].value })
            info.extend([
                    {"name": "Measurements", "cols": [
                            {"name": "counts"},
                            {"name": "pixels"},
                            {"name": "monitor"},
                            {"name": "count_time"}]},
                    {"PolState": PolState, "filename": filename, "start_datetime": dateutil.parser.parse(file_obj.attrs.get('file_time')), "friendly_name": friendly_name,
                     "CreationStory":creation_story, "path":path, "det_angle":entry['DAS_logs']['detectorAngle']['softPosition'].value}]
                )
            data_array = zeros((xpixels, ypixels, 4))
            mon =  entry['DAS_logs']['counter']['liveMonitor'].value
            count_time = entry['DAS_logs']['counter']['liveTime'].value
            if ndims == 2:
                mon.shape = (1,) + mon.shape # broadcast the monitor over the other dimension
                count_time.shape = (1,) + count_time.shape
            counts = counts_value
            if transpose == True: counts = counts.swapaxes(0,1)
            if flip == True: counts = flipud(counts)
            data_array[..., 0] = counts
            #data_array[..., 0] = file_obj.detector.counts
            data_array[..., 1] = 1
            data_array[..., 2] = mon
            data_array[..., 3] = count_time
            # data_array[:,:,4]... I wish!!!  Have to do by hand.
            data = MetaArray(data_array, dtype='float', info=info)
            data.friendly_name = friendly_name # goes away on dumps/loads... just for initial object.
        
        elif ndims == 3: # then it's an unsummed collection of detector shots.  Should be one sample and detector angle per frame
            if collapse_y == True:
                info = []     
                info.append({"name": "xpixel", "units": "pixels", "values": arange(xpixels) }) # reverse order
                info.append({"name": "theta", "units": "degrees", "values": entry['DAS_logs']['sampleAngle']['softPosition'].value })
                info.extend([
                        {"name": "Measurements", "cols": [
                                {"name": "counts"},
                                {"name": "pixels"},
                                {"name": "monitor"},
                                {"name": "count_time"}]},
                        {"PolState": PolState, "filename": filename, "start_datetime": dateutil.parser.parse(file_obj.attrs.get('file_time')), "friendly_name": friendly_name,
                         "CreationStory":creation_story, "path":path, "det_angle":entry['DAS_logs']['detectorAngle']['softPosition'].value}]
                    )
                data_array = zeros((xpixels, frames, 4))
                mon =  entry['DAS_logs']['counter']['liveMonitor'].value
                count_time = entry['DAS_logs']['counter']['liveTime'].value
                if ndims == 3:
                    mon.shape = (1,) + mon.shape # broadcast the monitor over the other dimension
                    count_time.shape = (1,) + count_time.shape
                counts = numpy.sum(counts_value, axis=2)
                if transpose == True: counts = counts.swapaxes(0,1)
                if flip == True: counts = flipud(counts)
                data_array[..., 0] = counts
                #data_array[..., 0] = file_obj.detector.counts
                data_array[..., 1] = 1
                data_array[..., 2] = mon
                data_array[..., 3] = count_time
                # data_array[:,:,4]... I wish!!!  Have to do by hand.
                data = MetaArray(data_array, dtype='float', info=info)
                data.friendly_name = friendly_name # goes away on dumps/loads... just for initial object.
            else: # make separate frames           
                infos = []
                data = []
                for i in range(frames):
                    samp_angle = file_obj.sample.angle_x[i]
                    det_angle = file_obj.detector.angle_x[i]
                    info = []
                    info.append({"name": "xpixel", "units": "pixels", "values": range(xpixels) })
                    info.append({"name": "ypixel", "units": "pixels", "values": range(ypixels) })
                    info.extend([
                        {"name": "Measurements", "cols": [
                                {"name": "counts"},
                                {"name": "pixels"},
                                {"name": "monitor"},
                                {"name": "count_time"}]},
                        {"PolState": PolState, "filename": filename, "start_datetime": file_obj.date, "friendly_name": friendly_name,
                         "CreationStory":creation_story, "path":path, "samp_angle": samp_angle, "det_angle": det_angle}]
                    )
                    data_array = zeros((xpixels, ypixels, 4))
                    mon = file_obj.monitor.counts[i]
                    count_time = file_obj.monitor.count_time[i]
                    counts = file_obj.detector.counts[i]
                    if flip == True: counts = flipud(counts) 
                    data_array[..., 0] = counts
                    data_array[..., 1] = 1
                    data_array[..., 2] = mon
                    data_array[..., 3] = count_time
                    # data_array[:,:,4]... I wish!!!  Have to do by hand.
                    subdata = MetaArray(data_array, dtype='float', info=info)
                    subdata.friendly_name = friendly_name + ("_%d" % i) # goes away on dumps/loads... just for initial object.
                    data.append(subdata)
    return data 

def LoadICPData(filename, path="", friendly_name="", auto_PolState=False, PolState='', flip=True, transpose=True, **kw):
    """ 
    loads a data file into a MetaArray and returns that.
    Checks to see if data being loaded is 2D; if not, quits
    
    Need to rebin and regrid if the detector is moving...
    """
    lookup = {"a":"_down_down", "b":"_up_down", "c":"_down_up", "d":"_up_up", "g": ""}
    file_obj = load(os.path.join(path, filename), format='NCNR NG-1')
    dims = file_obj.detector.counts.shape
    ndims = len(dims)
    #if not (len(file_obj.detector.counts.shape) == 2):
        # not a 2D object!
    #    return
    if auto_PolState:
        key = friendly_name[-2:-1] # na1, ca1 etc. are --, nc1, cc1 are -+...
        PolState = lookup.get(key, "")
    # force PolState to a regularized version:
    if not PolState in lookup.values():
        PolState = ''
    #datalen = file_obj.detector.counts.shape[0]
    if ndims == 2:
        if DEBUG: print "2d"
        ypixels = file_obj.detector.counts.shape[0]
        xpixels = file_obj.detector.counts.shape[1]
    elif ndims >= 3:
        if DEBUG: print "3d"
        frames = file_obj.detector.counts.shape[0]
        ypixels = file_obj.detector.counts.shape[1]
        xpixels = file_obj.detector.counts.shape[2]
        
    creation_story = "LoadICPData('{fn}', path='{p}', auto_PolState={aPS}, PolState='{PS}')".format(fn=filename, p=path, aPS=auto_PolState, PS=PolState)

    # doesn't really matter; changing so that each keyword (whether it took the default value
    # provided or not) will be defined
    #    if not PolState == '':
    #        creation_story += ", PolState='{0}'".format(PolState)
    # creation_story += ")" 
    
    
    if ndims == 2: # one of the dimensions has been collapsed.
        info = []     
        info.append({"name": "xpixel", "units": "pixels", "values": arange(xpixels) }) # reverse order
        info.append({"name": "theta", "units": "degrees", "values": file_obj.sample.angle_x })
        info.extend([
                {"name": "Measurements", "cols": [
                        {"name": "counts"},
                        {"name": "pixels"},
                        {"name": "monitor"},
                        {"name": "count_time"}]},
                {"PolState": PolState, "filename": filename, "start_datetime": file_obj.date, "friendly_name": friendly_name,
                 "CreationStory":creation_story, "path":path, "det_angle":file_obj.detector.angle_x}]
            )
        data_array = zeros((xpixels, ypixels, 4))
        mon = file_obj.monitor.counts
        count_time = file_obj.monitor.count_time
        if ndims == 2:
            mon.shape = (1,) + mon.shape # broadcast the monitor over the other dimension
            count_time.shape = (1,) + count_time.shape
        counts = file_obj.detector.counts
        if transpose == True: counts = counts.swapaxes(0,1)
        if flip == True: counts = flipud(counts)
        data_array[..., 0] = counts
        #data_array[..., 0] = file_obj.detector.counts
        data_array[..., 1] = 1
        data_array[..., 2] = mon
        data_array[..., 3] = count_time
        # data_array[:,:,4]... I wish!!!  Have to do by hand.
        data = MetaArray(data_array, dtype='float', info=info)
        data.friendly_name = friendly_name # goes away on dumps/loads... just for initial object.
        
    elif ndims == 3: # then it's an unsummed collection of detector shots.  Should be one sample and detector angle per frame
        infos = []
        data = []
        for i in range(frames):
            samp_angle = file_obj.sample.angle_x[i]
            det_angle = file_obj.detector.angle_x[i]
            info = []
            info.append({"name": "xpixel", "units": "pixels", "values": range(xpixels) })
            info.append({"name": "ypixel", "units": "pixels", "values": range(ypixels) })
            info.extend([
                {"name": "Measurements", "cols": [
                        {"name": "counts"},
                        {"name": "pixels"},
                        {"name": "monitor"},
                        {"name": "count_time"}]},
                {"PolState": PolState, "filename": filename, "start_datetime": file_obj.date, "friendly_name": friendly_name,
                 "CreationStory":creation_story, "path":path, "samp_angle": samp_angle, "det_angle": det_angle}]
            )
            data_array = zeros((xpixels, ypixels, 4))
            mon = file_obj.monitor.counts[i]
            count_time = file_obj.monitor.count_time[i]
            counts = file_obj.detector.counts[i]
            if flip == True: counts = flipud(counts) 
            data_array[..., 0] = counts
            data_array[..., 1] = 1
            data_array[..., 2] = mon
            data_array[..., 3] = count_time
            # data_array[:,:,4]... I wish!!!  Have to do by hand.
            subdata = MetaArray(data_array, dtype='float', info=info)
            subdata.friendly_name = friendly_name + ("_%d" % i) # goes away on dumps/loads... just for initial object.
            data.append(subdata)
    return data                   

def LoadUXDData(filename, path="", friendly_name=""):
    """ Load two-dimensional mesh scans from Bruker x-ray files """
    ###################
    # By André Guzmán #
    ###################

    #This program assumes that the step sizes of all Rocking Curves are the same
    #I do not know what will happen if they are not (I've never tried) - but the result will probably not be pretty
    
    ############# Variables #################################
    #Read from file header (applies to all ranges)
    wavelength = 0

    #Arrays
    data_array = [] #main array to return
    two_theta_array = [] #Isn't it good that I ended all these variables with _array - there's already a two_theta variable that it could've been mixed up with
    theta_array = [] #All of the tube angles for the various scans (Theta)
    counts_array = [] #Counts go here
    pixels_array = [] #This is all 1s
    monitor_array = [] #Does the *100 multiplication for detectorslit.in
    count_time_array = [] #Count times go here

    #Range variables
    #Range Constants (values that don't change within a range, but do change between ranges)
    curr_range = 0 #determines which range is being read
    prev_step_time = 0
    step_time = 0
    step_size = 0
    theta_start = 0
    two_theta = 0
    detector_slit = False
    #Range Counters (these change in the range - and most of them only count up)
    theta = 0
    range_counts_array = []
    range_theta_array = []
    ############# END Variables #################################

    file_obj = open(os.path.join(path, filename), 'r')
    np = numpy
    
    for lines in file_obj:
        line = lines.strip()

        if line != "" and line[0].isdigit():
            #add counts to the count array and other stuff
            range_theta_array.append(theta)
            theta += step_size
            range_counts_array.append(float(line))
            
        elif line.count("_WL1") != 0:
            nums = line.split(" = ")
            wavelength = float(nums[1].strip())
        elif line.count("; Data ") != 0:
            nums = line.split(" ")
            curr_range = int(nums[4].strip())
            #step_time = 0
            step_size = 0
            theta_start = 0
            two_theta = 0
            theta = 0

            if curr_range != 1:
                counts_array.append(range_counts_array)
                theta_array.append(range_theta_array)
                
                range_counts_array = []
                range_theta_array = []
        elif line.count("_STEPTIME") != 0:
            nums = line.split(" = ")
            step_time = float(nums[1].strip()) - prev_step_time #Step time increments for some reason, this fixes that
            prev_step_time = float(nums[1].strip())
            count_time_array.append(step_time)
        elif line.count("_STEPSIZE") != 0:
            nums = line.split(" = ")
            step_size = float(nums[1].strip())
        elif line.count("_START") != 0:
            nums = line.split(" = ")
            theta_start = float(nums[1].strip())
            theta = theta_start
        elif line.count("_2THETA") != 0:
            nums = line.split(" = ")
            two_theta = float(nums[1].strip())
            two_theta_array.append(two_theta)
        elif line.count("_DETECTORSLIT") != 0:
            nums = line.split(" = ")
            slit = nums[1].strip()

            if slit == "in":
                detector_slit = True
                monitor_array.append(1)
            else:
                detector_slit = False
                monitor_array.append(0.01)
        else:
            two = 1 + 1
            #This really doesn't need to be here (at all), but I like IF statements that end in ELSEs

    #For Loop skips over the last range (which might be important), so its added here
    if curr_range != 1:
        # Adding arrays to other arrays and resetting them
        counts_array.append(range_counts_array)
        theta_array.append(range_theta_array)

        range_counts_array = []
        range_theta_array = []
        
    #Now that we're done with reading the file, its time to set up the MetaArray
    file_obj.close() # We're done with the file now

    for i in range(curr_range):
        pixels_array.append(1)

    theta_range = theta_array[-1][-1] - theta_array[0][0]
    theta_elements = int(theta_range / step_size + 0.5) + 1 # Assumes the step sizes of all the ranges are the same

    data_array = np.zeros((theta_elements, curr_range, 4))
    data_theta_array = [] #Rhyming was totally intentional

    theta_incr = theta_array[0][0] # This is a bad name for this variable
    for i in range(theta_elements):
        data_theta_array.append(theta_incr)
        theta_incr += step_size

    for i in range(len(counts_array)):
        start = int((theta_array[i][0] - data_theta_array[0])/step_size + 0.5) #Add 0.5 for rounding - the int() function does strange things to floats
        stop = int(int(start + ((theta_array[i][-1] - theta_array[i][0])/step_size) + .5) + 1) #Add 1 because arrays that go from 0 to N have N+1 elements

        data_array[start:stop, i, 0] = counts_array[i]
        data_array[start:stop, i, 1] = pixels_array[i]
        data_array[start:stop, i, 2] = monitor_array[i]
        data_array[start:stop, i, 3] = count_time_array[i]

    info = [
        {"name": "theta", "units": "degrees", "values": data_theta_array}, 
        {"name": "twotheta", "units": "degrees", "values": two_theta_array}]
    info.append({"name": "Measurements", "cols": [
                        {"name": "counts"},
                        {"name": "pixels"},
                        {"name": "monitor"},
                        {"name": "count_time"}]})
    info.append({"filename": filename, "friendly_name": friendly_name, "path":path, "CreationStory": ""})

    data = MetaArray(data_array, dtype='float', info=info)    
    return data

def LoadUXDMany(filedescriptors):
    result = []
    for fd in filedescriptors:
        new_data = LoadUXDData(fd['filename'], friendly_name=fd['friendly_name'])
        if type(new_data) is types.ListType:
            result.extend(new_data)
        else:
            result.append(new_data)
    return result        

class InsertTimestamps(Filter2D):
    """ This is a hack.  
    Get the timestamps from the source file directory listing
    and interpolate between the start time and the end time.
    """
    
    @autoApplyToList
    @updateCreationStory
    def apply(self, data, timestamps, override_existing=False, filename=None):
        # first of all, if there is already a timestamp, skip!
        #extra info changed
        if data._info[-1].has_key('end_datetime') and not override_existing:
            return data
        # now figure out which file was the source:
        new_info = data.infoCopy()
        source_filename = filename[1:] or new_info[-1]['filename'][1:] # strip off leading 'I'
        try:
            end_timestamp = timestamps[source_filename]
        except KeyError:
            print "source file 'last modified time' (mtime) not found"
            return
        end_datetime = datetime.datetime.fromtimestamp(end_timestamp)
        new_info[-1]['end_datetime'] = end_datetime
        new_data_array = data.view(ndarray).copy()
        new_data = MetaArray(new_data_array, info=new_info)
        return new_data       
    

class AppendPolarizationMatrix(Filter2D):
    """
    Takes a dataset with a defined polarization state (not None) and
    calculates the row of the NT matrix that corresponds to each datapoint
    (This is more straightforward for raw pixel data where the 
    timestamp is the same for all pixels in a single measurement 'point')
    """
        
    @autoApplyToList
    @updateCreationStory
    def apply(self, data, he3cell=None):
        """ can use He3AnalyzerCollection in place of He3Analyzer...
        then calls to getNTRow(t) get automatically routed to the correct cell object
        """
        #cell = self.supervisor.He3_cells[str(inData.cell_id)] # link to the cell object
        if he3cell == None:
            print "where is the He cell?"
            # extra info changed
            he3cell = He3AnalyzerCollection(path=data._info[-1]['path'])
        new_info = data.infoCopy()
        if not new_info[-1]['PolState'] in  ["_down_down", "_up_down", "_down_up", "_up_up"]:
            print "polarization state not defined: can't get correction matrix"
            return
        start_datetime = new_info[-1]['start_datetime']
        #start_time_offset = start_datetime - he3cell.start_datetime
        #offset_seconds = start_time_offset.days * 86400. + start_time_offset.seconds 
        # weird implementation of datetime difference measures in days, seconds, microseconds
        end_datetime = new_info[-1]['end_datetime']
        elapsed = end_datetime - start_datetime
        datalen = data.shape[0]
        delta_t = elapsed / datalen 
        #el_seconds = el.days * 86400. + el.seconds # datetime timedelta is an odd duck

        
        time_list = [start_datetime + delta_t * i for i in range(datalen)]
        #time_array += offset_seconds # get total time from cell T0
        #time_array.shape += (1,)
        
        data_array = data.view(ndarray).copy()
        new_data_array = zeros(data_array.shape[:-1] + (data_array.shape[-1] + 4,))
        new_data_array[:, :, 0:-4] = data_array[:]
        PolState = new_info[-1]['PolState']
        #flipper_on = (PolState[0] == '-') # check for flipper on in incoming polarization state
        flipper_on = PolState.startswith("_down") # check for flipper on in incoming polarization state
        #He3_up = (PolState[1] == '+')
        He3_up = PolState.endswith("up")
        for i in range(datalen):
            t = start_datetime + delta_t * i
            #print 't: ', t
            pol_corr = he3cell.getNTRow(t, flipper_on=flipper_on, He3_up=He3_up)
            monitor_row = data['Measurements':'monitor'][i].view(ndarray).copy()
            # NT is multiplied by I_0, or monitor in this case:
            new_data_array[i, :, -4:] = pol_corr[newaxis, :] * monitor_row[:, newaxis]
            
            
        #pol_corr_list = [he3cell.getNTRow(t, flipper_on = flipper_on, He3_up = He3_up) for t in time_list]
        #pol_corr_array = array(pol_corr_list)

        #fill the first four columns with existing data:
        
        #1new_data_array[:,:,0:4] = data_array[:,:,0:4]
        
        # now append the polarization matrix elements!
        # from He3Analyzer: 
        # """creates matrix elements for the polarization-correction 
        #    this assumes the order of elements is Rup-up, Rup-down, Rdown-down, Rdown-up
        #    and for I: Iup-up, Iup-down, Idown-up, Idown-down   """
        
        #1new_data_array[:,:,4:8] = pol_corr_array[newaxis, newaxis, :]
        
        # the order of columns here is determined by the order coming out of He3Analyer NTRow:
        # (++, +-, --, -+)
        pol_columns = [{"name": 'NT_up_up'}, {"name": 'NT_up_down'}, {"name": 'NT_down_down'}, {"name": 'NT_down_up'}]
        new_info[2]["cols"] = new_info[2]["cols"][:4] + pol_columns
        new_data = MetaArray(new_data_array, info=new_info)
        
        return new_data



class Combine(Filter2D):
    """ combine multiple datasets with or without overlap, adding 
    all the values in the time, monitor and data columns, and populating
    the pixels column (number of pixels in each new bin)
    
    If no grid is provided, use Autogrid filter to generate one.
    """
    #@updateCreationStory
    def apply(self, list_of_datasets, grid=None):
        if grid == None:
            grid = Autogrid().apply(list_of_datasets)
        for dataset in list_of_datasets:
            grid = self.add_to_grid(dataset, grid)
        
        # extra info changed
        old_creation_stories = "[" + "".join([data._info[-1]['CreationStory'] + ", " for data in list_of_datasets]) + "]"
        name = self.__class__.__name__
        new_creation_story = "{fname}().apply({oldcs})".format(fname=name, oldcs=old_creation_stories)
        grid._info[-1]['CreationStory'] = new_creation_story
        # strip info that is meaningless in combined dataset: (filename, start_time, end_time)
        for key in ['filename', 'start_datetime', 'end_datetime']:
            if grid._info[-1].has_key(key): grid._info[-1].pop(key)
        return grid
        
    def add_to_grid(self, dataset, grid):
        dims = 2
        grid_slice = [slice(None, None, 1),] * dims
        bin_edges = []
        for dim in range(dims):
            av = grid.axisValues(dim).copy()
            dspacing = (av[-1] - av[0]) / (len(av) - 1)
            edges = resize(av, len(av) + 1)
            edges[-1] = av[-1] + dspacing
            if dspacing < 0:
                edges = edges[::-1] # reverse
                grid_slice[dim] = slice(None, None, -1)
            bin_edges.append(edges)
        
        data_edges = []
        data_slice = [slice(None, None, 1),] * dims
        for dim in range(dims):
            av = dataset.axisValues(dim).copy()
            dspacing = (av[-1] - av[0]) / (len(av) - 1)
            edges = resize(av, len(av) + 1)
            edges[-1] = av[-1] + dspacing
            if dspacing < 0:
                edges = edges[::-1] # reverse
                data_slice[dim] = slice(None, None, -1)
            data_edges.append(edges)
        
        #cols_to_add = ['counts', 'pixels', 'monitor', 'count_time'] # standard data columns
        #cols_to_add += ['NT++', 'NT+-', 'NT-+', 'NT--'] # add in all the polarization correction matrices too!
        
        new_info = dataset.infoCopy()        
        for i, col in enumerate(new_info[2]['cols']):
            #if col['name'] in cols_to_add:
            array_to_rebin = dataset[:, :, col['name']].view(ndarray) 
            #print data_edges, bin_edges
            new_array = reb.rebin2d(data_edges[0], data_edges[1], array_to_rebin[data_slice], bin_edges[0], bin_edges[1])
            grid[:, :, col['name']] += new_array[grid_slice]
            
        return grid

class CombinePolarized(Filter2D):
    """ 
    Combines on a per-polarization state basis.
    Master output grid is calculated that will cover ALL the inputs,
    without regard for polarization state, but then separate
    copies of this grid are filled with data from each
    PolState separately.
    """

    def sortByPolarization(self, list_of_datasets):
        """ takes an unsorted list of datasets, peeks at the PolState inside,
        and groups them into a labeled list of lists (dictionary!)"""
        pol_datasets = {}
        for dataset in list_of_datasets:
            # extra info changed
            PolState = dataset._info[-1].get('PolState', '')
            if not PolState in pol_datasets.keys():
                pol_datasets[PolState] = []
            pol_datasets[PolState].append(dataset)
        return pol_datasets
        
    def getListOfDatasets(self, pol_datasets):
        """ inverse of sortByPolarization: take a dictionary of PolState-grouped
        data and return a flat list of every dataset inside """
        list_of_datasets = []
        for PolState in pol_datasets:
            list_of_datasets += pol_datasets[PolState]
        return list_of_datasets
                
    
    def apply(self, pol_datasets, grid=None):
        if type(pol_datasets) is types.ListType:
            # then we got an unordered list of polarized datasets.
            # that's ok - we can label and group them together!
            list_of_datasets = pol_datasets
            pol_datasets = self.sortByPolarization(pol_datasets)
        else:
            list_of_datasets = self.getListOfDatasets(pol_datasets)
                
        if grid == None:
            grid = Autogrid().apply(list_of_datasets)
        # grid covering all polstates is now made:  now create
        # sublists for each polarization state
        
        combined_datasets = []
        for PolState in pol_datasets:
            # combined single polarization:
            csingle = Combine().apply(pol_datasets[PolState], deepcopy(grid))
            #print type(pol_datasets[PolState])
            #extra info changed
            csingle._info[-1]['PolState'] = PolState
            combined_datasets.append(csingle)
        # we end up with a dictionary set of datasets (e.g. {"++": data1, "--": data2} )
        
        return   d_datasets

class TwothetaLambdaToQxQz(Filter2D):
    """ Figures out the Qx, Qz values of each datapoint
    and throws them in the correct bin.  If no grid is specified,
    one is created that covers the whole range of Q in the dataset
    
    If autofill_gaps is True, does reverse lookup to plug holes
    in the output (but pixel count is still zero for these bins)
    """
    
    default_qxqz_gridvals = (-0.003, 0.003, 201, 0, 0.1, 201)
    
    def getQxQz (self, theta, twotheta, wavelength = 5.0): 
        qLength = 2.0 * pi / wavelength
        tilt = theta - ( twotheta / 2.0 )
        dq = 2.0 * qLength * sin( ( pi / 180.0 ) * ( twotheta / 2.0 ) )
        qxOut = dq * sin( pi * tilt / 180.0 )
        qzOut = dq * cos( pi * tilt / 180.0 )
        return [qxOut, qzOut]
    
    @autoApplyToList
    #@updateCreationStory
    def apply(self, data, theta=None, qxmin=None, qxmax=None, qxbins=None, qzmin=None, qzmax=None, qzbins=None):
        info = [{"name": "qx", "units": "inv. Angstroms", "values": linspace(qxmin, qxmax, qxbins) },
                {"name": "qz", "units": "inv. Angstroms", "values": linspace(qzmin, qzmax, qzbins) },]
        old_info = data.infoCopy()
        info.append(old_info[2]) # column information!
        info.append(old_info[3]) # creation story!
        output_grid = MetaArray(zeros((qxbins, qzbins, data.shape[-1])), info=info)
        
        
        #if output_grid == None:
        #    output_grid = EmptyQxQzGrid(*self.default_qxqz_gridvals)
        #else:
        #    output_grid = deepcopy(output_grid)
            
        if (theta == "") or (theta == None):
            if 'state' in data._info[-1]:
                theta = float(data._info[-1]['state']['A[1]'])
                print 'theta:', theta
            else:
                print "can't run without theta!"
                return
       
        wl_array = data.axisValues('wavelength').copy()
        wl_array.shape = wl_array.shape + (1,)
        twotheta_array = data.axisValues('twotheta').copy()
        twotheta_array.shape = (1,) + twotheta_array.shape
        qxOut, qzOut = self.getQxQz(theta, twotheta_array, wl_array)
        
        # getting values from output grid:
        outgrid_info = output_grid.infoCopy()
        numcols = len(outgrid_info[2]['cols'])
        qx_array = output_grid.axisValues('qx')
        dqx = qx_array[1] - qx_array[0]
        qz_array = output_grid.axisValues('qz')
        dqz = qz_array[1] - qz_array[0]
        framed_array = zeros((qz_array.shape[0]+2, qx_array.shape[0]+2, numcols))
        target_qx = ((qxOut - qx_array[0])/dqx + 1).astype(int)
        #return target_qx, qxOut
        target_qz = ((qzOut - qz_array[0])/dqz + 1).astype(int)
        target_mask = (target_qx >= 0) * (target_qx < qx_array.shape[0])
        target_mask *= (target_qz >= 0) * (target_qz < qz_array.shape[0])
        target_qx_list = target_qx[target_mask]
        target_qz_list = target_qz[target_mask]
        #target_qx = target_qx.clip(0, qx_array.shape[0]+1)
        #target_qz = target_qz.clip(0, qz_array.shape[0]+1)
        
        for i, col in enumerate(outgrid_info[2]['cols']):
            values_to_bin = data[:,:,col['name']][target_mask]
            outshape = (output_grid.shape[0], output_grid.shape[1])
            hist2d, xedges, yedges = histogram2d(target_qx_list,target_qz_list, bins = (outshape[0],outshape[1]), range=((0,outshape[0]),(0,outshape[1])), weights=values_to_bin)
            output_grid[:,:,col['name']] += hist2d
            #framed_array[target_qz_list, target_qx_list, i] = data[:,:,col['name']][target_mask]
            
        #trimmed_array = framed_array[1:-1, 1:-1]
        #output_grid[:,:] = trimmed_array
        
        creation_story = data._info[-1]['CreationStory']
        new_creation_story = creation_story + ".filter('{0}', {1})".format(self.__class__.__name__, output_grid._info[-1]['CreationStory'])
        #print new_creation_story
        output_grid._info[-1] = data._info[-1].copy()
        output_grid._info[-1]['CreationStory'] = new_creation_story
        return output_grid

class TwothetaToQ(Filter2D):
    """ Figures out the Q values of an axis.
    """
    
    @autoApplyToList
    @updateCreationStory 
    def apply(self, data, wavelength=5.0, ax_name='twotheta'):
        print " inside TwoThetaToQ "
        wavelength = float(wavelength)
        
        new_info = data.infoCopy()
        ndim = len(new_info) - 2 # last two entries in info are for metadata
        twotheta_axis = next((i for i in xrange(len(new_info)-2) if new_info[i]['name'] == ax_name), None)
        if twotheta_axis < 0:
            raise ValueError("error: no %s axis in this dataset" % (ax_name,))
  
        print "doing the simple switch of axis values..."
        
        if ax_name == 'twotheta':
            new_info[twotheta_axis]['name'] = 'qx'
        else:
            new_info[twotheta_axis]['name'] = 'qy'
            
        twotheta = new_info[twotheta_axis]['values']
        q = 4.0*pi/wavelength * sin((twotheta/2.0) * pi/180.0) 
        #new_info[pixel_axis]['values'] = twoth[::-1] # reverse: twotheta increases as pixels decrease
        new_info[twotheta_axis]['values'] = q
        new_info[twotheta_axis]['units'] = 'inv. Angstroms'
        #new_array = (data.view(ndarray).copy())[data_slices]
        new_array = (data.view(ndarray).copy())
        new_data = MetaArray(new_array, info=new_info)
        
        return new_data
   
              
class ThetaTwothetaToQxQz(Filter2D):
    """ Figures out the Qx, Qz values of each datapoint
    and throws them in the correct bin.  If no grid is specified,
    one is created that covers the whole range of Q in the dataset
    
    If autofill_gaps is True, does reverse lookup to plug holes
    in the output (but pixel count is still zero for these bins)
    """
    
    default_qxqz_gridvals = (-0.003, 0.003, 201, 0, 0.1, 201)
    
    @autoApplyToList
    #@updateCreationStory
    def apply(self, data, output_grid=None, wavelength=5.0, qxmin=None, qxmax=None, qxbins=None, qzmin=None, qzmax=None, qzbins=None):
    #def apply(self, data, output_grid=None, wavelength=5.0):
        if output_grid == None:
            info = [{"name": "qx", "units": "inv. Angstroms", "values": linspace(qxmin, qxmax, qxbins) },
                {"name": "qz", "units": "inv. Angstroms", "values": linspace(qzmin, qzmax, qzbins) },]
            old_info = data.infoCopy()
            info.append(old_info[2]) # column information!
            info.append(old_info[3]) # creation story!
            output_grid = MetaArray(zeros((qxbins, qzbins, data.shape[-1])), info=info)
            #output_grid = EmptyQxQzGrid(*self.default_qxqz_gridvals)
        else:
            #outgrid_info = data._info.copy()
            #outgrid_info[0] = {"name": "qx", "units": "inv. frakking Angstroms", "values": linspace(qxmin, qxmax, qxbins) }
            #outgrid_info[1] = {"name": "qz", "units": "inv. Angstroms", "values": linspace(qzmin, qzmax, qzbins) }
            outgrid_info = deepcopy(output_grid._info) # take axes and creation story from emptyqxqz...
            outgrid_info[2] = deepcopy(data._info[2]) # take column number and names from dataset
            output_grid = MetaArray(zeros((output_grid.shape[0], output_grid.shape[1], data.shape[2])), info=outgrid_info)
        
        theta_axis = data._getAxis('theta')
        twotheta_axis = data._getAxis('twotheta')
        
        #theta_axis = next((i for i in xrange(len(old_info)-2) if old_info[i]['name'] == 'theta'), None)
        #twotheta_axis = next((i for i in xrange(len(old_info)-2) if old_info[i]['name'] == 'twotheta'), None)
        
        qLength = 2.0 * pi / wavelength
        th_array = data.axisValues('theta').copy()
        twotheta_array = data.axisValues('twotheta').copy()
        
        if theta_axis < twotheta_axis: # then theta is first: add a dimension at the end
            th_array.shape = th_array.shape + (1,)
            twotheta_array.shape = (1,) + twotheta_array.shape
        else:
            twotheta_array.shape = twotheta_array.shape + (1,)
            th_array.shape = (1,) + th_array.shape
            
        tilt_array = th_array - (twotheta_array / 2.0)
        qxOut = 2.0 * qLength * sin((pi / 180.0) * (twotheta_array / 2.0)) * sin(pi * tilt_array / 180.0)
        qzOut = 2.0 * qLength * sin((pi / 180.0) * (twotheta_array / 2.0)) * cos(pi * tilt_array / 180.0)
        
        # getting values from output grid:
        outgrid_info = output_grid.infoCopy()
        numcols = len(outgrid_info[2]['cols'])
        qx_array = output_grid.axisValues('qx')
        dqx = qx_array[1] - qx_array[0]
        qz_array = output_grid.axisValues('qz')
        dqz = qz_array[1] - qz_array[0]
        framed_array = zeros((qz_array.shape[0] + 2, qx_array.shape[0] + 2, numcols))
        target_qx = ((qxOut - qx_array[0]) / dqx + 1).astype(int)
        #return target_qx, qxOut
        target_qz = ((qzOut - qz_array[0]) / dqz + 1).astype(int)
        
        target_mask = (target_qx >= 0) * (target_qx < qx_array.shape[0])
        target_mask *= (target_qz >= 0) * (target_qz < qz_array.shape[0])
        target_qx_list = target_qx[target_mask]
        target_qz_list = target_qz[target_mask]
        #target_qx = target_qx.clip(0, qx_array.shape[0]+1)
        #target_qz = target_qz.clip(0, qz_array.shape[0]+1)
        
        for i, col in enumerate(outgrid_info[2]['cols']):
            values_to_bin = data[:,:,col['name']][target_mask]
            outshape = (output_grid.shape[0], output_grid.shape[1])
            hist2d, xedges, yedges = histogram2d(target_qx_list,target_qz_list, bins = (outshape[0],outshape[1]), range=((0,outshape[0]),(0,outshape[1])), weights=values_to_bin)
            output_grid[:,:,col['name']] += hist2d
            #framed_array[target_qz_list, target_qx_list, i] = data[:,:,col['name']][target_mask]
     
        cols = outgrid_info[2]['cols']
        data_cols = [col['name'] for col in cols if col['name'].startswith('counts')]
        monitor_cols = [col['name'] for col in cols if col['name'].startswith('monitor')]
        # just take the first one...
        if len(monitor_cols) > 0:
            monitor_col = monitor_cols[0]
            data_missing_mask = (output_grid[:,:,monitor_col] == 0)
            for dc in data_cols:
                output_grid[:,:,dc][data_missing_mask] = NaN;
            
        
        #extra info changed
        creation_story = data._info[-1]['CreationStory']
        new_creation_story = creation_story + ".filter('{0}', {1})".format(self.__class__.__name__, output_grid._info[-1]['CreationStory'])
        #print new_creation_story
        output_grid._info[-1] = data._info[-1].copy()
        output_grid._info[-1]['CreationStory'] = new_creation_story
        return output_grid

class PolarizationCorrect(Filter2D):
    """ 
    Takes 2 to 4 input datasets with appended Polarization Matrix, 
    inverts the polarization matrix and applies to the data.
    Outputs fully polarization-corrected intensities.
    
    # 0: "no assumptions (use all I++, I+-, I-+, I--)",
    # 1: "R+- assumed equal to R-+ (use I++, I-+ and I--)",
    # 2: "R-+ assumed equal to R+- (use I++, I+- and I--)",
    # 3: "R-+ and R+- equal zero (use I++, I--)"
    
    Requires that Polarization state is defined for each dataset ("PolState")
    and that at least "++" and "--" PolStates are present.
    """
    
    polstate_order = {'_up_up':0, '_up_down':1, '_down_up':2, '_down_down':3}
    
    def progress_update(self, percent_done):
        print '{0}% done'.format(percent_done)
        
    def check_grids(self, datasets):
        """ Combined data will be dictionary of labeled datasets: 
        e.g. {"++": datapp, "+-": datapm} etc."""
        compatible = True
        firstdata = datasets[0]
        for dataset in datasets[1:]:
            # allclose is the next best thing to "==" for a floating point array
            compatible &= allclose(dataset.axisValues(0), firstdata.axisValues(0))
            compatible &= allclose(dataset.axisValues(1), firstdata.axisValues(1))
        return compatible
    
    def guess_assumptions(self, datasets):
        assumptions = None
        polstates = [datum._info[-1]['PolState'] for datum in datasets]
        if set(polstates) == set(['_up_up', '_up_down', '_down_up', '_down_down']):
            assumptions = 0
        elif set(polstates) == set(['_up_up', '_down_up', '_down_down']):
            assumptions = 1
        elif set(polstates) == set(['_up_up', '_up_down', '_down_down']):
            assumptions = 2
        elif set(polstates) == set(['_up_up', '_down_down']):
            assumptions = 3
        return assumptions
        
    def apply(self, combined_data, assumptions=0, auto_assumptions=True):
        # do I apply assumptions here, or in separate subclasses?
        if auto_assumptions:
            assumptions = self.guess_assumptions(combined_data)
            print "assumptions: ", assumptions
            
        if not self.check_grids(combined_data):
            # binning on datasets in combined data is not the same!  quit.
            return
            
        data_shape = combined_data[0].shape
        polstates = [datum._info[-1]['PolState'] for datum in combined_data]
            
        NT = empty(data_shape[:2] + (4, 4))
        alldata = empty(data_shape[:2] + (len(polstates), 4))
        # recall order of I, R is different for the way we've set up NT matrix (not diagonal)
        # [Iuu, Iud, Idu, Idd] but [Ruu, Rud, Rdd, Rdu]
        #['NT++','NT+-','NT--','NT-+']
        for dataset in combined_data:
            PolState = dataset._info[-1]['PolState']
            NT[:, :, self.polstate_order[PolState]] = dataset[:, :, ['NT_up_up', 'NT_up_down', 'NT_down_up', 'NT_down_down']]
            alldata[:, :, self.polstate_order[PolState]] = dataset[:, :, ['counts', 'pixels', 'monitor', 'count_time']]
            #alldata[:,:,self.polstate_order[PolState]] = combined_data[PolState][:,:,['counts','pixels','monitor','count_time']]
        # should result in: 
        #NT[:,:,0] = combined_data['++'][:,:,['NT++','NT+-','NT-+','NT--']]
        #NT[:,:,1] = combined_data['+-'][:,:,['NT++','NT+-','NT-+','NT--']]
        #NT[:,:,2] = combined_data['-+'][:,:,['NT++','NT+-','NT-+','NT--']]
        #NT[:,:,3] = combined_data['--'][:,:,['NT++','NT+-','NT-+','NT--']]
        #alldata[:,:,0] = combined_data['++'][:,:,['counts','pixels','monitor','count_time']]
        #alldata[:,:,1] = combined_data['+-'][:,:,['counts','pixels','monitor','count_time']]
        #alldata[:,:,2] = combined_data['-+'][:,:,['counts','pixels','monitor','count_time']]
        #alldata[:,:,3] = combined_data['--'][:,:,['counts','pixels','monitor','count_time']]
        # by arranging this new NT matrix as above, I'm undoing the weird arrangement in
        # the He3Analyzer module.  now the order is: 
        # [Iuu, Iud, Idu, Idd] AND [Ruu, Rud, Rdu, Rdd] !!!
        output_columns = self.polstate_order #{'++':0, '+-':1, '-+':2, '_down_down':3}        
        
        if assumptions == 1:
            NT = NT[:, :, [0, 2, 3], :] #remove +- (second) row
            NT[:, :, :, 1] += NT[:, :, :, 2] # add -+(column 3) to +- (column 2), (cols. 1 and 2 in zero-indexed)
            NT = NT[:, :, :, [0, 1, 4]] # drop column 3 (2 in zero-indexing)
            # should now be (th_len, 2th_len, 3, 3) matrix
            output_columns = {'_up_up':0, '_down_up':1, '_down_down':2} 
        
        elif assumptions == 2:
            NT = NT[:, :, [0, 1, 3], :] #remove -+ (third) row
            NT[:, :, :, 1] += NT[:, :, :, 2] # add -+ column 3 to +- column 2 (zero-indexed)
            NT = NT[:, :, :, [0, 1, 4]] # drop column 3 (2 in zero-indexing)
            # should now be (th_len, 2th_len, 3, 3) matrix
            output_columns = {'_up_up':0, '_up_down':1, '_down_down':2} 
            
        elif assumptions == 3:
            NT = NT[:, :, [0, 3], :] #remove both middle rows
            NT = NT[:, :, :, [0, 3]] # remove both middle columns (1,2 in zero-indexing)
            # should now be (th_len, 2th_len, 2, 2) matrix
            output_columns = {'_up_up':0, '_down_down':1} 
 
        R = deepcopy(alldata)
        # output will have the same shape as input... just with different values!
        
        invNT = zeros_like(NT)
        normNT = zeros(data_shape[:2])
        
        n = 0
        percent_done = -1
        nmax = NT.shape[0] * NT.shape[1]
        #return NT
        
        for i in range(NT.shape[0]):
            for j in range(NT.shape[1]):
                try:
                    invNT[i, j] = linalg.inv(NT[i, j])
                    normNT[i, j] = linalg.norm(invNT[i, j])
                    R[i, j, :, 0] = dot(invNT[i, j], alldata[i, j, :, 0]) # counts
                    R[i, j, :, 1] = dot(invNT[i, j], alldata[i, j, :, 1]) / normNT[i, j] # pixels (need unitary transform)
                    R[i, j, :, 2] = 1.0 # monitor is set to one.  Not sure about this one
                    R[i, j, :, 3] = 1.0 # count time is set to one also.
                except:
                    print sys.exc_info()
                    sys.exit()
                    R[i, j, :, 0] = 0.0 # counts
                    R[i, j, :, 1] = 0.0 # pixels (need unitary transform)
                    R[i, j, :, 2] = 1.0 # monitor is set to one.  Not sure about this one
                    R[i, j, :, 3] = 1.0 # count time is set to one also.
                    # this leaves zeros where the inversion fails
                    # not sure what else to do!
                n += 1
                new_percent_done = (100 * n) / nmax
                if new_percent_done > percent_done:
                    self.progress_update(new_percent_done)
                    percent_done = new_percent_done
                    
        combined_R = []
        for index, PolState in enumerate(polstates):
            combined_R.append(MetaArray(R[:, :, output_columns[PolState]], info=combined_data[index].infoCopy()))
        return combined_R
            
    def add_to_grid(self, dataset, grid):
        dims = 2
        bin_edges = []
        for dim in range(dims):
            av = grid.axisValues(dim).copy()
            dspacing = (av.max() - av.min()) / (len(av) - 1)
            edges = resize(av, len(av) + 1)
            edges[-1] = av[-1] + dspacing
            bin_edges.append(edges)
        
        data_edges = []
        for dim in range(dims):
            av = dataset.axisValues(dim).copy()
            dspacing = (av.max() - av.min()) / (len(av) - 1)
            edges = resize(av, len(av) + 1)
            edges[-1] = av[-1] + dspacing
            data_edges.append(edges)
        
        cols_to_add = ['counts', 'pixels', 'monitor', 'count_time'] # standard data columns
        cols_to_add += ['NT_up_up', 'NT_up_down', 'NT_down_up', 'NT_down_down'] # add in all the polarization correction matrices too!
        
        new_info = dataset.infoCopy()        
        for i, col in enumerate(new_info[2]['cols']):
            if col['name'] in cols_to_add:
                array_to_rebin = dataset[:, :, col['name']].view(ndarray) 
                new_array = reb.rebin2d(data_edges[0], data_edges[1], array_to_rebin, bin_edges[0], bin_edges[1])
                grid[:, :, col['name']] += new_array
                
        return grid

class wxPolarizationCorrect(PolarizationCorrect):
    
    def apply(self, *args, **kwargs):
        self.progress_meter = wx.ProgressDialog("Progress", "% done", parent=None, style=wx.PD_AUTO_HIDE | wx.PD_APP_MODAL) 
        return PolarizationCorrect.apply(self, *args, **kwargs)
        
    def progress_update(self, percent_done): 
        self.progress_meter.Update(int(percent_done), "Polarization Correction Progress:\n{0}% done".format(percent_done))

class Subtract(Filter2D):
    """ takes two data objects and subtracts them.   
    If no grid is provided, use Autogrid filter to generate one.
    """
    #@updateCreationStory
    #@autoApplyToList
    def apply(self, minuend, subtrahend):
        #subtrahend = subtrahend[0] # can only subtract one thing... but from many.
        print len(minuend), len(subtrahend)
        if len(minuend) == len(subtrahend): pass # go with it.
        elif len(subtrahend) == 1: subtrahend = [subtrahend[0] for m in minuend] # broadcast
        else: raise Exception("I don't know what to do with unmatched argument lengths")
        results = []
        for m, s in zip(minuend, subtrahend):    
            dim_m = len(m.shape) - 1
            dim_s = len(s.shape) - 1
            if dim_m == 2 and dim_s == 1:
                print "subtract vector from matrix (broadcast subtrahend)"
                s_units = s._info[0]['units']
                m1_units = m._info[0]['units']
                m2_units = m._info[1]['units']
                if s_units == m1_units: active_axis = 0
                elif s_units == m2_units: active_axis = 1
                else: raise Exception("no matching units to subtract from") # bail out!
                
                new_axisvals = [m._info[0]['values'].copy(), m._info[1]['values'].copy()]
                update_axisvals = new_axisvals[active_axis]
                s_axisvals = s._info[0]['values']
                overlap = slice(get_index(update_axisvals, s_axisvals[0]), get_index(update_axisvals, s_axisvals[-1]))
                print overlap
                new_axisvals[active_axis] = update_axisvals[overlap]
                full_overlap = [slice(None, None), slice(None, None)]
                full_overlap[active_axis] = overlap
                full_overlap = tuple(full_overlap)                
                
                output_array = []
                
                dims = 2
                data_edges = []
                for dim in range(dims):
                    av = new_axisvals[dim].copy()
                    dspacing = (av.max() - av.min()) / (len(av) - 1)
                    edges = resize(av, len(av) + 1)
                    edges[-1] = av[-1] + dspacing
                    data_edges.append(edges)
                
                
                    
                #bin_edges = [[data_edges[0][0], data_edges[0][-1]],[data_edges[1][0], data_edges[1][-1]]]
                av = s_axisvals #give the same treatment to the subtrahend asixvals
                dspacing = (av.max() - av.min()) / (len(av) - 1)
                edges = resize(av, len(av) + 1)
                edges[-1] = av[-1] + dspacing
                #bin_edges[active_axis] = edges
                
                #new_s = reb.rebin(edges, s['Measurements':col], data_edges[active_axis])
                
                #new_sshape = [1,1]
                #new_sshape[active_axis] = len(new_saxisvals)
                #new_saxisvals.shape = tuple(new_sshape)
                
                #new_array = reb.rebin2d(data_edges[0], data_edges[1], array_to_rebin, bin_edges[0], bin_edges[1])
                             
                print m._info[0]['units'], m._info[1]['units'], s._info[0]['units']
                data_array = m.view(ndarray).copy()[full_overlap]
                new_info = m.infoCopy()
                new_info[0]['values'] = new_axisvals[0]
                new_info[1]['values'] = new_axisvals[1]
                print data_array.shape, new_axisvals[0].shape, new_axisvals[1].shape
                new_data = MetaArray(data_array, info=new_info)
                subtractable_columns = [c['name'] for c in s._info[1]['cols'] if c['name'].startswith('counts')]
                #subtractable_columns = dict(subtractable_columns)
                print "subtractable columns:", subtractable_columns 
                for i, col in enumerate(new_info[2]['cols']):
                    if col['name'].startswith('counts') and col['name'] in subtractable_columns:
                        new_s = reb.rebin(edges, s['Measurements':col['name']], data_edges[active_axis])
                        new_sshape = [1,1]
                        new_sshape[active_axis] = len(new_s)
                        new_s.shape = tuple(new_sshape)
                        new_data['Measurements':col['name']] -= new_s
                results.append(new_data)
            elif dim_m == 2 and dim_s == 2:
                print "subtract matrix from matrix (in overlap)"
                print m._info[0]['units'], m._info[1]['units'], s._info[0]['units'], s._info[1]['units']
                results.append(m)
            elif dim_m == 1 and dim_s == 2:
                print "can't do this."
                print m._info[0]['units'], s._info[0]['units'], s._info[1]['units']
                results.append(m)
            elif dim_m == 1 and dim_s == 1:
                print "subtract vector from vector (in overlap)"
                print m._info[0]['units'], s._info[0]['units']
                results.append(m)
                
        return results
        # extra info changed
#        old_creation_stories = "[" + "".join([data._info[-1]['CreationStory'] + ", " for data in list_of_datasets]) + "]"
#        name = self.__class__.__name__
#        new_creation_story = "{fname}().apply({oldcs})".format(fname=name, oldcs=old_creation_stories)
#        grid._info[-1]['CreationStory'] = new_creation_story
#        # strip info that is meaningless in combined dataset: (filename, start_time, end_time)
#        for key in ['filename', 'start_datetime', 'end_datetime']:
#            if grid._info[-1].has_key(key): grid._info[-1].pop(key)
#        return grid
        
    def add_to_grid(self, dataset, grid):
        dims = 2
        bin_edges = []
        for dim in range(dims):
            av = grid.axisValues(dim).copy()
            dspacing = (av.max() - av.min()) / (len(av) - 1)
            edges = resize(av, len(av) + 1)
            edges[-1] = av[-1] + dspacing
            bin_edges.append(edges)
        
        data_edges = []
        for dim in range(dims):
            av = dataset.axisValues(dim).copy()
            dspacing = (av.max() - av.min()) / (len(av) - 1)
            edges = resize(av, len(av) + 1)
            edges[-1] = av[-1] + dspacing
            data_edges.append(edges)
        
        cols_to_add = ['counts', 'pixels', 'monitor', 'count_time'] # standard data columns
        cols_to_add += ['NT++', 'NT+-', 'NT-+', 'NT--'] # add in all the polarization correction matrices too!
        
        new_info = dataset.infoCopy()        
        for i, col in enumerate(new_info[2]['cols']):
            #if col['name'] in cols_to_add:
            array_to_rebin = dataset[:, :, col['name']].view(ndarray) 
            new_array = reb.rebin2d(data_edges[0], data_edges[1], array_to_rebin, bin_edges[0], bin_edges[1])
            grid[:, :, col['name']] += new_array
                
        return grid

class Algebra(Filter2D):
    """ generic algebraic manipulations """
    def get_safe_operations_namespace(self):
        #make a list of safe functions 
        safe_list = ['math', 'acos', 'asin', 'atan', 'atan2', 'ceil', 'cos', 'cosh', 'degrees', 'e', 'exp', 'fabs', 'floor', 'fmod', 'frexp', 'hypot', 'ldexp', 'log', 'log10', 'modf', 'pi', 'pow', 'radians', 'sin', 'sinh', 'sqrt', 'tan', 'tanh','newaxis'] 
        #use the list to filter the local namespace 
        safe_dict = dict([ (k, numpy.__dict__.get(k, None)) for k in safe_list ])
        return safe_dict
        
    def add_to_namespace(self, data, prefix, namespace, automask=True):
        cols = data._info[-2]['cols']
        #if automask and ("pixels" in cols):
        #    mask = ( data["Measurements":"pixels"] > 0 )
        #else:
        #    mask = ones(data.shape[:2], dtype=bool)
        for col in cols:
            new_name = str(prefix) + col['name']
            data_view = data['Measurements':col['name']].view(ndarray)
            if automask and ("pixels" in cols):
                data_view = MaskedArray(data_view)
                data_view.mask = ( data["Measurements":"pixels"] > 0 )
            #namespace[new_name] = data['Measurements':col['name']].view(ndarray)[mask]
            namespace[new_name] = data_view
    
    @autoApplyToList         
    def apply(self, data1=None, data2=None, output_cols=[], passthrough_cols=[], automask=True):
        """ can operate on columns within data1 if needed 
        output_cols is in form 
        [{"name":"output_col_name", "expression":"data1_counts + data2_counts"},...]
        
        automask=True means operations are only applied to places where pixels column is > 0.
        """
        local_namespace = self.get_safe_operations_namespace()
        safe_globals = {"__builtins__":None}
        data_shape = data1.shape
        output_info = data1.infoCopy()
        output_colinfo = []
        self.add_to_namespace(data1, "data1_", local_namespace, automask)
        if data2 is not None:
#            if len(data2.shape) > len(data_shape):
#                data_shape = data2.shape
            self.add_to_namespace(data2, "data2_", local_namespace, automask)
        output_array = zeros( data_shape[:-1] + (len(output_cols) + len(passthrough_cols),), dtype=float)
        for i, o in enumerate(output_cols):
            print o['expression'], data1.shape, output_array[..., i].shape
            output_array[..., i] = eval(o['expression'], safe_globals, local_namespace)
            output_colinfo.append({'name':o['name']})
        
        for i, p in enumerate(passthrough_cols):
            output_array[..., i+len(output_cols)] = data1["Measurements":p]
            output_colinfo.append({'name':p})
            
        output_info[-2]['cols'] = output_colinfo
        output_obj = MetaArray(output_array, info=output_info)
        return output_obj     
        
          
class CombinePolcorrect(Filter2D):
    """ combine and polarization-correct """
    def apply(self, list_of_datasets, grid=None):
        pass
        
def get_index(t, x):
    if (x == "" or x == None): 
        return None
    if float(x) > t.max(): 
        return None
    if float(x) < t.min(): 
        return None
    return searchsorted(t, float(x))

# rowan tests
if __name__ == '__main__':
    data1 = LoadICPData('Isabc2003.cg1', '/home/brendan/dataflow/sampledata/ANDR/sabc/')
    data2 = LoadICPData('Isabc2004.cg1', '/home/brendan/dataflow/sampledata/ANDR/sabc/')
    data = [data1, data2]
    data = Combine().apply(data)
    data = data.filter('CoordinateOffset', offsets={'theta': 0.1})
    data = data.filter('WiggleCorrection')
    print data
    #print data._info[-1]["CreationStory"]
    #print eval(data._info[-1]["CreationStory"])
    #print data
    assert data.all() == eval(data._info[-1]["CreationStory"]).all()

