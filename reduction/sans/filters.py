
#!/usr/bin/env python

import struct
import sys,os
import vaxutils
import data
from copy import deepcopy,copy
import numpy as np
import math
from matplotlib import pyplot as plt
from uncertainty import Measurement


#I will have a general philosophy that filters do not have side effects.  That is,
#they do not change the state of their inputs.  So, we will always work on copies 
#internally

#TODO:
#  Add copy statements and deepcopy statement (for dictionaries) where appropriate.  The deepcopy on the dictionary is 
# becaue if the value is a list, a simple copy will still reference the original list.  Thus, we are not as decoupled as we would like to be.

#  Create __div__, __truediv__, etc. methods so we only have to do the above in one place
#   Make a constants.py in sans from where we import constants related to the sans instrument
# for example, pixel_size_x_cm, pixel_size_y_cm
#Capital letters will denote constants
#put into wire-it framework
#write tests
#
#Ask Steve Kline where they use attenuation outside of absolute scaling
#implement two absolute scaling methods
#implement annular average
#implement conversion to q
#implement line cut
#ask andrew about reading mask files


PIXEL_SIZE_X_CM=.508
PIXEL_SIZE_Y_CM=.508

class SansData(object):
    def __init__(self,data=None,metadata=None,q=None,qx=None,qy=None,theta=None):
        self.data=Measurement(data,data)
        self.metadata=metadata
        self.q=q
        self.qx=qx
        self.qy=qy
        self.theta=theta
    # Note that I have not defined an inplace subtraction    
    def __sub__(self,other):
        if isinstance(other,SansData):
            SansData(self.data-other.data,deepcopy(self.metadata),qx=copy(self.qx),qy=copy(self.qy),theta=copy(self.theta))
        else:
            return SansData(data=self.data-other,metadata=deepcopy(self.metadata),qx=copy(self.qx),qy=copy(self.qy),theta=copy(self.theta))
        
    def __rsub__(self, other):
        return SansData(data=other-self.data, metadata=deepcopy(self.metadata),qx=copy(self.qx),qy=copy(self.qy),theta=copy(self.theta))

def read_sample(myfilestr="MAY06001.SA3_CM_D545"):
    """Reads in a raw SANS datafile and returns a SansData
    """
    detdata,metadata=data.readNCNRData(myfilestr) #note that it should be None for the default
    return SansData(detdata, metadata)

def read_div(myfilestr="test.div"):
    sensitivity = data.readNCNRSensitivity(myfilestr)
    return sensitivity

def monitor_normalize(sansdata,mon0=1e8):
    """"
    Given a SansData object, normalize the data to the provided monitor
    """
    monitor=sansdata.metadata['run.moncnt']
    result=sansdata.data*mon0/monitor
    res=SansData()
    res.data=result
    res.metadata=deepcopy(sansdata.metadata)
    res.qx=copy(sansdata.qx)
    res.qy=copy(sansdata.qy)
    res.theta=copy(sansdata.theta)
    return res

def correct_detector_efficiency(sansdata,sensitivity):
    """"
    Given a SansData object and an sensitivity map generated from a div,
    correct for the efficiency of the detector.  Recall that sensitivities are
    generated by taking a measurement of plexiglass and dividing by the mean value
    """
    result=sansdata.data/sensitivity  #Could be done more elegantly by defining a division method on SansData
    res=SansData()
    res.data=result
    res.metadata=deepcopy(sansdata.metadata)
    res.qx=copy(sansdata.qx)
    res.qy=copy(sansdata.qy)
    res.theta=copy(sansdata.theta)
    return res

def correct_blocked_beam(sample,blocked_beam,transmission):
    """"
    Given a SansData object, the transmissions and blocked beam, correct for the
    blocked beam.  
    """
    #it would probably be more pleasant to have keyword arguments and to check
    #for their presence so that a user of the class doesn't have to know the 
    #function signature.  The advantage of the current method is that an error is
    #automatically raised if the user doesn't pass a required parameter and there should
    #be no question of whether a parameter is actually required or not.  Here, I am letting
    #the clarity trump convenience.
    result=(sample.data-blocked_beam.data)/transmission
    res=SansData()
    res.data=result
    res.metadata=deepcopy(sample.metadata)
    res.qx=copy(sample.qx)
    res.qy=copy(sample.qy)
    res.theta=copy(sample.theta)
    return res
    
def correct_background(sample,empty_cell):
    """"
    Given a SansData of sample and empty cell that have been corrected, subtract them 
    """
    result=sample-empty_cell
    return result
    
def generate_transmission(in_beam,empty_beam,coords_bottom_left,coords_upper_right):
    """
    To calculate the transmission, we integrate the intensity in a box for a measurement
    with the substance in the beam and with the substance out of the beam and take their ratio.
    The box is definied by its bottom left and upper right corner.  These are registered to pixel coordinates
    the coords are assumed to be tuple or a list in the order of (x,y).  I start counting at (0,0).
    """
    I_in_beam=0
    I_empty_beam=0
    #Vectorize this loop, it's quick, but could be quicker
    #test against this simple minded implementation
    for x in range(coords_bottom_left[0],coords_upper_right[0]):
        for y in range(coords_bottom_left[0],coords_upper_right[0]):
            I_in_beam=I_in_beam+in_beam.data[x,y]
            I_empty_beam=I_empty_beam+empty_beam.data[x,y]
    result=I_in_beam/I_empty_beam
    return result

def correct_solid_angle(sansdata):
    """
    given a SansData with q,qx,qy,and theta images defined,
    correct for the fact that the detector is flat and the eswald sphere is curved.
    """
    result=sansdata.data*(np.cos(sansdata.theta)**3)
    res=SansData()
    res.data=result
    res.metadata=deepcopy(sansdata.metadata)
    res.qx=copy(sansdata.qx)
    res.qy=copy(sansdata.qy)
    res.theta=copy(sansdata.theta)
    return res
    

def convert_q(sansdata):
    """
    generate a q_map for sansdata.  Each pixel will have 4 values: (qx,qy,q,theta)
    
    """
    L2=sansdata.metadata['det.dis']
    x0=sansdata.metadata['det.beamx']  #should be close to 64
    y0=sansdata.metadata['det.beamy']  #should be close to 64
    wavelength=sansdata.metadata['resolution.lmda']
    shape=(128,128)#sansdata.data.shape
    theta=np.empty(shape,'Float64')
    q=np.empty(shape,'Float64')
    qx=np.empty(shape,'Float64')
    qy=np.empty(shape,'Float64')
    #vectorize this loop, it will be slow at 128x128
    #test against this simpleminded implentation
    for x in range(0,shape[0]):
        for y in range(0,shape[1]):
            X=PIXEL_SIZE_X_CM*(x-x0)
            Y=PIXEL_SIZE_Y_CM*(y-y0)
            r=np.sqrt(X**2+Y**2)
            theta[x,y]=np.arctan2(r,L2)/2
            q[x,y]=(4*np.pi/wavelength)*np.sin(theta[x,y])
            alpha=np.arctan2(Y,X)
            qx[x,y]=q[x,y]*np.cos(alpha)
            qy[x,y]=q[x,y]*np.sin(alpha)
    res=SansData()
    res.data=copy(sansdata.data)
    res.metadata=deepcopy(sansdata.metadata)
    res.qx=qx
    res.qy=qy
    res.theta=theta
    return res         
    
def chain_corrections():
    """a sampe chain of corrections"""
    
    #read the files 
    sample_4m=read_sample(map_files('sample_4m'))
    empty_cell_4m=read_sample(map_files('empty_cell_4m'))
    empty_4m=read_sample(map_files('empty_4m'))
    transmission_sample_cell_4m=read_sample(map_files('trans_sample_4m'))
    transmission_empty_cell_4m=read_sample(map_files('trans_empty_cell_4m'))
    blocked_beam_4m=read_sample(map_files('blocked_4m'))
    sensitivity=read_div(map_files('div'))
    #mask=read_sample(map_files('mask'))
    
    #normalize the monitors
    
    sample_4m_norm=monitor_normalize(sample_4m)
    empty_cell_4m_norm=monitor_normalize(empty_cell_4m)
    transmission_sample_cell_4m_norm=monitor_normalize(transmission_sample_cell_4m)
    transmission_empty_cell_4m_norm=monitor_normalize(transmission_empty_cell_4m)
    empty_4m_norm=monitor_normalize(empty_4m) 
    blocked_beam_4m_norm=monitor_normalize(blocked_beam_4m)
        
    #calculate q
    sample_4m_norm_q=convert_q(sample_4m_norm)
    empty_cell_4m_norm_q=convert_q(empty_cell_4m)
    blocked_beam_4m_norm_q=convert_q(blocked_beam_4m_norm)
    transmission_sample_cell_4m_norm_q=convert_q(transmission_sample_cell_4m_norm)
    transmission_empty_cell_4m_norm_q=convert_q(transmission_empty_cell_4m_norm)
    empty_4m_norm_q=convert_q(empty_4m_norm)
    
    
    print 'converted'
    #convert flatness
    sample_4m_solid=correct_solid_angle(sample_4m_norm_q)
    empty_cell_4m_solid=correct_solid_angle(empty_cell_4m_norm_q)
    blocked_beam_4m_solid=correct_solid_angle(blocked_beam_4m_norm_q)
    transmission_sample_cell_4m_solid=correct_solid_angle(transmission_sample_cell_4m_norm_q)
    transmission_empty_cell_4m_solid=correct_solid_angle(transmission_empty_cell_4m_norm_q)
    empty_4m_solid=correct_solid_angle(empty_4m_norm_q)
    
    
    #calculate transmission
    coord_left=(80,80)
    coord_right=(110,110)
    transmission_sample_cell_4m_rat=generate_transmission(transmission_sample_cell_4m_solid,empty_4m_solid,
                                                      coord_left,coord_right)
    transmission_empty_cell_4m_rat=generate_transmission(transmission_empty_cell_4m_solid,empty_4m_solid,
                                                      coord_left,coord_right)
    print 'transmission=',transmission_sample_cell_4m_rat
    print 'transmission=',transmission_empty_cell_4m_rat
    print 'hi'
    
   
    
    
def map_files(key):
    """
    Generate the mapping between files and their roles
    """
    
    datadir=os.path.join(os.path.dirname(__file__),'ncnr_sample_data')
    filedict={'empty_1m':os.path.join(datadir,'SILIC001.SA3_SRK_S101'),
              'empty_4m':os.path.join(datadir,'SILIC002.SA3_SRK_S102'),
              'empty_cell_1m':os.path.join(datadir,'SILIC003.SA3_SRK_S103'),
              'blocked_1m':os.path.join(datadir,'SILIC004.SA3_SRK_S104'),
              'trans_empty_cell_4m':os.path.join(datadir,'SILIC005.SA3_SRK_S105'),
              'trans_sample_4m':os.path.join(datadir,'SILIC006.SA3_SRK_S106'),
              'blocked_4m':os.path.join(datadir,'SILIC007.SA3_SRK_S107'),
              'empty_cell_4m':os.path.join(datadir,'SILIC008.SA3_SRK_S108'), 
              'sample_1m':os.path.join(datadir,'SILIC009.SA3_SRK_S109'),
              'sample_4m':os.path.join(datadir,'SILIC010.SA3_SRK_S110'),
              'mask':os.path.join(datadir,'DEFAULT.MASK'),
              'div':os.path.join(datadir,'PLEX_2NOV2007_NG3.DIV'),
              }
    return filedict[key]
              
    
    


if __name__ == '__main__':
    chain_corrections()
    if 0:
        for key, value in metadata.iteritems():
            print key,value
        print metadata
        
      
        attenuation=metadata['run.atten 7.0']
    
    
    
    
    