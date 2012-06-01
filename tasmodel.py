# Look for the peak fitter in the same file as the modeller
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from peaks import Peaks, Gaussian, Background
from bumps.names import Parameter, pmath, FitProblem



def read_data():
    tasdata = np.genfromtxt("datatest.txt")
    x = tasdata[0]
    y = tasdata[1]
    data = tasdata[2].x
    err = tasdata[2].variance

    return X, Y, data, err

def build_problem():

    M = Peaks([Gaussian(name="G1-"),
               Gaussian(name="G2-"),
               #Gaussian(name="G3-"),
               #Gaussian(name="G4-"),
               Background()],
               *read_data())
    background = np.min(M.data)
    background += np.sqrt(background)
    signal = np.sum(M.data) - M.data.size*background
    M.parts[-1].C.value = background
    peak1 = M.parts[0]

    if 0:
        # Peak centers are independent
        for peak in M.parts[:-1]:
            peak.xc.range(0.45,0.55)
            peak.yc.range(-0.55,-0.4)
    else:
        # Peak centers lie on a line
        theta=Parameter(45, name="theta")
        theta.range(0,90)
        peak1.xc.range(0.45,0.55)
        peak1.yc.range(-0.55,-0.4)
        for i,peak in enumerate(M.parts[1:-1]):
            delta=Parameter(.0045, name="delta-%d"%(i+1))
            delta.range(0.0,0.015)
            peak.xc = peak1.xc + delta*pmath.cosd(theta)
            peak.yc = peak1.yc + delta*pmath.sind(theta)

        # Initial values
        cx, cy = 0.4996-0.4957, -0.4849+0.4917
        theta.value = np.degrees(np.arctan2(cy,cx))
        delta.value = np.sqrt(cx**2+cy**2)
        peak1.xc.value,peak1.yc.value = 0.4957,-0.4917

    # Initial values
    for peak in M.parts[:-1]:
        peak.A.value = signal/(len(M.parts)-1)  # Equal size peaks
    dx, dy = 0.4997-0.4903, -0.4969+0.4851
    dxm, dym = 0.4951-0.4960, -0.4941+0.4879
    peak1.s1.value = np.sqrt(dx**2+dy**2)/2.35/2
    peak1.s2.value = np.sqrt(dxm**2+dym**2)/2.35/2
    peak1.theta.value = np.degrees(np.arctan2(dy,dx))


    # Peak intensity varies
    for peak in M.parts[:-1]:
        peak.A.range(0.25*signal,1.1*signal)

    # Peak shape is the same across all peaks
    peak1.s1.range(0.002,0.02)
    peak1.s2.range(0.002,0.02)
    peak1.theta.range(-90, -0)
    for peak in M.parts[1:-1]:
        peak.s1 = peak1.s1
        peak.s2 = peak1.s2
        peak.theta = peak1.theta

    if 1:
        print "shape",peak1.s1.value,peak1.s2.value,peak1.theta.value
        print "centers theta,delta",theta.value,delta.value
        print "centers",(peak1.xc.value,peak1.yc.value),\
            (M.parts[1].xc.value,M.parts[1].yc.value)
    return FitProblem(M)

problem = build_problem()
