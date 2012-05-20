#!/usr/bin/python
# -*- coding: UTF-8 -*

# first read data and assign it to VadSurveyTask's

# store it like this: data["task X"] = vadSurveyTask
# vadSurveyTask["word"] = [row1, row2, ...]

# with open("fuzzyVad.events_20120502.txt") as fh:
#     for line in fh:
#         print line.split("\t")[4]

from __future__ import division
from collections import defaultdict 
import sys
from scipy.stats import scoreatpercentile,nanmean,nanstd,t
import random
from math import sqrt,log
import fuzzyset as fs
import matplotlib.pyplot as plt
import numpy as np

class IntervalApproachCwwEstimator(object):
    """ this class performs the interval approach

    __call__ is the main function (it allows the object instance to be
    "callable", while the other member functions perform the various
    sub-steps, e.g., bad data processing, outlier processing, tolerance limit
    processing, reasonable interval processing, admissible region
    determination, establishing the nature of the footprint of uncertainty
    (FOU), and computing the mathematical model for the FOU (the output) 

    """

    def __call__(self,data,r=(0,100)):
        """ this function performs the Interval Approach as described in [Liu and Mendel
        2008]
     
        note that 'data', as a python list, is passed as a mutable reference
        
        Args:
            data: a VadSurveyTaskResults instance
            r: range, default [0,100]

        Returns: an interval type-2 fuzzy set with a trapeziodal upper and a
            triangular lower
    
        Raises: 
            TBA

            """ 
        
        self.r = r

        #data part: filters out data
        self.badDataProcessing(data)
        self.outlierProcessing(data)
        #self.defaultValueCorrection(data) #to correct for turkers that leave
                                          #slider at default value
        self.toleranceLimitProcessing(data)
        self.reasonableIntervalProcessing(data)
        #Fuzzy set part: creates the fuzzy set
        #first,check to make sure multiple model types do not match
        fsType = self.determineFsModelType(data)

        print fsType
        if fsType == "lowerShoulder" :
            t1fss = map(self.datumToLowerShoulderT1, data)
            self.deleteInadmissibleT1Fss(t1fss)
            f = self.lowerShoulderT1ListToLowerShoulderIT2(t1fss)
        elif fsType == "upperShoulder" :
            t1fss = map(self.datumToUpperShoulderT1, data)
            self.deleteInadmissibleT1Fss(t1fss)
            f = self.upperShoulderT1ListToUpperShoulderIT2(t1fss)
        elif fsType == "interior" :
            t1fss = map(self.datumToInteriorT1,data)
            self.deleteInadmissibleT1Fss(t1fss)
            f = self.interiorT1ListToInteriorIT2(t1fss)
        else:
            raise Exception()
        print "raw fuzzy set", f
        return fs.intervalType2FS(fs.TrapezoidalMf(*f[0:4]), fs.TrapezoidalMf(*f[4:]))
        # self.admissibleRegionDetermination(data)
        # self.establishNatureOfFou(data)
        # self.deleteInadmissibleT1Fss(data)
        # self.computeMathematicalModelForFou(data)
        

    def badDataProcessing(self,data):
        # Bad data processing: check that data is in range
        print len(data)
        if len(data)==0: raise ValueError("No Remaining intervals")
        
        try:
            for d in data:
                if d[0] < self.r[0] or d[1] > self.r[1] or d[0] > d[1]:
                    raise ValueError("Bad Data: %s is out of range %s" % (str(d), str(r)))
        except ValueError as e:
            old = len(data)
            filter(lambda d: d[0] < self.r[0] or d[1] > self.r[1] or d[0] > d[1], data)
            #print "bad data found, removing %d data points" % old - len(data)
            
            
        print  len(data), "after bad data processing"
        if len(data)==0: raise ValueError("No Remaining intervals")
        return data

    def outlierProcessing(self,data):
        # Outlier processing
        intervalLengths = map(lambda x: x[1]-x[0], data)
        (lower,upper) = zip(*data)
        # firstQuartileLower = scoreatpercentile(lower,25)
        # thirdQuartileLower = scoreatpercentile(lower,75)
        # interQtlRangeLower = thirdQuartileLower - firstQuartileLower
        # firstQuartileUpper = scoreatpercentile(upper,25)
        # thirdQuartileUpper = scoreatpercentile(upper,75)
        # interQtlRangeUpper = thirdQuartileUpper - firstQuartileUpper
        # firstQuartileInterval = scoreatpercentile(intervalLengths,25)
        # thirdQuartileInterval = scoreatpercentile(intervalLengths,75)
        # interQtlRangeInterval = thirdQuartileInterval - firstQuartileInterval

        firstQuartileLower = scoreatpercentile(lower,30)
        thirdQuartileLower = scoreatpercentile(lower,70)
        interQtlRangeLower = thirdQuartileLower - firstQuartileLower
        firstQuartileUpper = scoreatpercentile(upper,30)
        thirdQuartileUpper = scoreatpercentile(upper,70)
        interQtlRangeUpper = thirdQuartileUpper - firstQuartileUpper
        firstQuartileInterval = scoreatpercentile(intervalLengths,30)
        thirdQuartileInterval = scoreatpercentile(intervalLengths,70)
        interQtlRangeInterval = thirdQuartileInterval - firstQuartileInterval
        #print "lower", firstQuartileLower,thirdQuartileLower, interQtlRangeLower
        #print "upper", firstQuartileUpper,thirdQuartileUpper, interQtlRangeUpper
        #print "interval", firstQuartileInterval,thirdQuartileInterval, interQtlRangeInterval
        #bound = .25 #in Liu/Mendel matlab code, not explained in their paper, excluded here
        acceptableLower = (firstQuartileLower-1.5*interQtlRangeLower,thirdQuartileLower+1.5*interQtlRangeLower)
        acceptableUpper = (firstQuartileUpper-1.5*interQtlRangeUpper,thirdQuartileUpper+1.5*interQtlRangeUpper)
        acceptableInterval = (firstQuartileInterval-1.5*interQtlRangeInterval,thirdQuartileInterval+1.5*interQtlRangeInterval)
        for (l,u) in data[:]:
            try:
                if not acceptableLower[0] <= l <= acceptableLower[1]:
                    raise ValueError("Outlier: lower bound %s not in  %s" % (str(l), str(acceptableLower)),(l,u))
                if not acceptableUpper[0] <= u <= acceptableUpper[1]:
                    raise ValueError("Outlier: upper bound %s not in %s" % (str(u), str(acceptableUpper)),(l,u))
                if not acceptableInterval[0] <= u-l <= acceptableInterval[1]:
                    raise ValueError("Outlier: interval length %s not in %s" % (str(u-l), str(acceptableInterval)),(l,u))
            except ValueError as (e,d):
                #print e
                #print "Outlier: removing data point %s" % str(d)
                data.remove(d)

        print   len(data), "after outlier processing"
        if len(data)==0: raise ValueError("No Remaining intervals")

    def defaultValueCorrection(self,data):
        #address default values:
        middle = nanmean([(d[1]+d[0])/2 for d in data])/(self.r[1]-self.r[0])
        print "middle", middle
        if middle < .35:
            print "filtering  u=100"
            for d in data:
                if d[1] == 100 and  random.random() > .3:
                    data.remove(d)
        if middle > .65:
            print "filtering l=0"
            for d in data:
                if d[0] == 0 and random.random() > .3:
                    data.remove(d)
        for d in data:
            if (d[0] == 0 or d[1]==100) and random.random() > .7:
                data.remove(d)
        print len(data), "after correcting for default values"



    def toleranceLimitProcessing(self,data):
        # Tolerance limit processing
        random.seed(1)
        resampledData = [random.choice(data) for x in xrange(2000)]

        #address default values:
        # middle = nanmean([(d[1]+d[0])/2 for d in data])/(self.r[1]-self.r[0])
        # print "middle", middle
        # if(middle < .35):
        #     print "filtering higher range"
        #     f = lambda x: x[1] != 100 or  random.random() > .3
        #     resampledData = filter(f, resampledData)
        # if(middle > .65*(self.r[1]-self.r[0])):
        #     print "filtering higher range"
        #     f = lambda x: x[0] != 0 or random.random() > .3
        #     resampledData = filter(f, resampledData)
        # f = lambda x: (x[0] != 0 and x[1]!=100) or random.random() > .1
        # resampledData = filter(f, resampledData)
        # print "resampled data length", len(resampledData)

        (resampLower,resampUpper) = zip(*resampledData)
        resampInterval = map(lambda x: x[1]-x[0], resampledData)
        meanLower = nanmean(resampLower)
        stdLower = nanstd(resampLower) * sqrt(len(data)) # it appears *sqrt is done to estimage population std from sample 
        meanUpper = nanmean(resampUpper)
        stdUpper = nanstd(resampUpper) * sqrt(len(data)) # ditto
        meanInterval = nanmean(resampInterval)
        stdInterval = nanstd(resampInterval) * sqrt(len(data)) # ditto
        K=[32.019, 32.019, 8.380, 5.369, 4.275, 3.712, 3.369, 3.136, 2.967, 2.839,
           2.737, 2.655, 2.587, 2.529, 2.48, 2.437, 2.4, 2.366, 2.337, 2.31,
           2.31, 2.31, 2.31, 2.31, 2.208] # taken from Liu/Mendel matlab code, in turn from Walpole,Myers,Myers,Ye2008
        k = K[min(len(data),24)]
        acceptableLower = (meanLower-k*stdLower, meanLower+k*stdLower)
        acceptableUpper = (meanUpper-k*stdUpper, meanUpper+k*stdUpper)
        acceptableInterval = (meanInterval-k*stdInterval, meanInterval+k*stdInterval)
        for (l,u) in data[:]:
            try:
                if not acceptableLower[0] <= l <= acceptableLower[1]:
                    raise ValueError("Intolerable: lower bound %s not in  %s" % (str(l), str(acceptableLower)),(l,u))
                if not acceptableUpper[0] <= u <= acceptableUpper[1]:
                    raise ValueError("Intolerable: upper bound %s not in %s" % (str(u), str(acceptableUpper)),(l,u))
                if not acceptableInterval[0] <= u-l <= acceptableInterval[1]:
                    raise ValueError("Intolerable: interval %s greater than %s" % (str(u-l), str(acceptableInterval)),(l,u))
            except ValueError as (e,d):
                #print e
                #print "Intolerable: removing data point %s" % str(d)
                data.remove(d)

        print len(data), "after tolerance limit processing"
        if len(data)==0: raise ValueError("No Remaining intervals")


    def reasonableIntervalProcessing(self,data):
        databackup = data[:]   #keep backup in case all intervals are deleted
        random.seed(1)
        resampledData = [random.choice(data) for x in xrange(2000)]
        (resampLower,resampUpper) = zip(*resampledData)
        resampInterval = map(lambda x: x[1]-x[0], resampledData)
        meanLower = nanmean(resampLower)
        stdLower = nanstd(resampLower) * sqrt(len(data)) # it appears *sqrt is done to estimage population std from sample 
        meanUpper = nanmean(resampUpper)
        stdUpper = nanstd(resampUpper) * sqrt(len(data)) # ditto
        meanInterval = nanmean(resampInterval)
        stdInterval = nanstd(resampInterval) * sqrt(len(data)) # ditto
        if stdLower+stdUpper==0:
            barrier = (meanLower+meanUpper)/2
            print "barrierAvg", barrier
        elif stdLower == 0:
            barrier = meanLower+.5
            print "barrierlower", barrier
        elif stdUpper == 0:
            barrier = meanUpper-.5
            print "barrierupper", barrier

        else:
            barrier1 = ( -(meanLower*stdUpper**2-meanUpper*stdLower**2) + 
                          stdLower*stdUpper*sqrt((meanLower-meanUpper)**2 + 
                                                 2*(stdLower**2-stdUpper**2)*log(stdLower/stdUpper)))/(stdLower**2-stdUpper**2)
            barrier2 = ( -(meanLower*stdUpper**2-meanUpper*stdLower**2) - 
                          stdLower*stdUpper*sqrt((meanLower-meanUpper)**2 + 
                                                 2*(stdLower**2-stdUpper**2)*log(stdLower/stdUpper)))/(stdLower**2-stdUpper**2)
            
            if barrier1 >= meanLower and barrier1 <= meanUpper:
                barrier = barrier1
                print "barrier1", barrier
            else:
                barrier = barrier2
                print "barrier2", barrier
        for (l,u) in data[:]:
            try:

                #if l > barrier+(.1*stdLower) or u < barrier-(.1*stdUpper):
                #if l > barrier+stdLower or u < barrier-stdUpper:
                #if l > barrier and u < barrier:
                if l > barrier+(.001*stdLower) or u < barrier-(.001*stdUpper):                    raise ValueError("Unreasonable: interval %s does not cross reasonable barrier  %s" % (str((l,u)), str(barrier)),(l,u))
            except ValueError as (e,d):
                #print e
                #print "Unreasonable: removing data point %s" % str(d)
                data.remove(d)

        print len(data), "after reasonable interval processing"
        #if len(data)==0: raise ValueError("No Remaining intervals")
        if len(data) == 0:
            print "no remaining intervals: skipping resonable interval processing"            
            for d in databackup:
                data.append(d)


    def determineFsModelType(self,data,plot=False):
        # Admissible region determination
        #TODO: incorporate scipy stats:
        #stats.t.ppf(1-0.05, 1...)
        # tTable=[6.314, 2.920, 2.353, 2.132, 2.015, 1.943, 1.895, 1.860, 1.833, 1.812, 
        #         1.796, 1.782, 1.771, 1.761, 1.753, 1.746, 1.740, 1.734, 1.729, 1.725, 
        #         1.721, 1.717, 1.714, 1.711, 1.708, 1.706, 1.703, 1.701, 1.699, 1.697, 1.684] 
        tTable = map(lambda df: t.ppf(1-0.05,df), range(1,35))
        tAlpha=tTable[min(len(data)-1,30)]
        (lower,upper) = zip(*data)
        meanLower = nanmean(lower)
        meanUpper = nanmean(upper)
        c = map(lambda x: (x[1] - 5.831*x[0])/(self.r[1]-self.r[0]), data)
        # as opp to Liu/Mendel, no assumption that FS is in [0,10]
        d = map(lambda x: x[1] - 0.171*x[0] - .829*(self.r[1]-self.r[0]), data) 
        print "nanstd(c)", nanstd(c)
        print "nanstd(d)", nanstd(d)
        shift1 = tAlpha * nanstd(c)/sqrt(len(data)) 
        shift2 = tAlpha * nanstd(d)/sqrt(len(data)) 

        final = None

        if True is True:
            print "meanLower", meanLower, "meanUpper", meanUpper
            print "shift1", shift1, "shift2", shift2
            print "5.831*meanLower-shift1", 5.831*meanLower-shift1 
            print ".829*(self.r[1]-self.r[0]) +0.171*meanLower-shift2:",.829*(self.r[1]-self.r[0]) +0.171*meanLower-shift2
            print "if meanUpper >= 5.831*meanLower-shift1"
            step = self.r[1]-self.r[0]/200
            x = range(self.r[0],self.r[1]+step,step)
            y1 = map(lambda i: 5.831*i, x)
            y2 = map(lambda i: 0.171*i + .829*(self.r[1]-self.r[0]), x)
            
            plt.plot(x,y1,color='black')
            plt.plot(x,y2,color='black')
            plt.plot(x,x,color='black')
            plt.plot([meanLower],[meanUpper],'ro')
            plt.axis([self.r[0],self.r[1],self.r[0],self.r[1]])
        # Establish nature of FOU 
        if meanUpper >= 5.831*meanLower-shift1: #left/lower shoulder T1FS
            print meanUpper, .829*(self.r[1]-self.r[0]) +0.171*meanLower-shift2
            if meanUpper <= .829*(self.r[1]-self.r[0]) +0.171*meanLower-shift2:
                final = "lowerShoulder"
            else:
                #raise Exception("this matches both lower and upper shapes")
                print "weird interior"
                if (self.r[1]-meanUpper) < (meanLower-self.r[0]):
                    final = "interior"
                elif (self.r[1]-meanUpper) > (meanLower-self.r[0]):
                    final = "lowerShoulder"
                else:
                    final = "interior"
        elif meanUpper > .829*(self.r[1]-self.r[0]) +0.171*meanLower-shift2:
            final = "upperShoulder"
        else:
            if meanUpper >= meanLower:
                final =  "interior"
            else:
                raise Exception("the meanLower is greater than the meanUpper: something is wrong")
        return final

    def datumToLowerShoulderT1(self,datum):
        l,r = datum
        fs_l = 0.5*(l+r) - (r-l)/sqrt(6)
        fs_r = 0.5*(l+r) + sqrt(6)*(r-l)/3
        return (fs_l,fs_r)
    def datumToUpperShoulderT1(self,datum):
        l,r = datum
        fs_l = 0.5*(l+r) - sqrt(6)*(r-l)/3
        fs_r = 0.5*(l+r) + (r-l)/sqrt(6)
        return (fs_l,fs_r)
    def datumToInteriorT1(self,datum):
        l,r = datum
        fs_l = 0.5*(l+r) - sqrt(2)*(r-l)/2
        fs_r = 0.5*(l+r) + sqrt(2)*(r-l)/2
        return (fs_l,fs_r)
        
    def lowerShoulderT1ListToLowerShoulderIT2(self,t1fss):
        assert len(t1fss) > 0
        (lower,upper) = zip(*t1fss)
        return (self.r[0], self.r[0], max(lower), max(upper), 
                self.r[0], self.r[0], min(lower), min(upper), 1 )
    
    def upperShoulderT1ListToUpperShoulderIT2(self,t1fss):
        assert len(t1fss) > 0
        (lower,upper) = zip(*t1fss)
        #print "uppershouldert1listtouppershoulderit2", (min(lower), min(upper), self.r[1], self.r[1]), (max(lower), max(upper), self.r[1], self.r[1], 1)
        return (min(lower), min(upper), self.r[1], self.r[1],
                max(lower), max(upper), self.r[1], self.r[1], 1)

    def interiorT1ListToInteriorIT2(self,t1fss):
        assert len(t1fss) > 0
        (lower,upper) = zip(*t1fss)
        print t1fss
        middle = map(lambda d: (d[0]+d[1])/2,t1fss)
        print "min(lower)=%f"%min(lower)
        print "max(lower)=%f"%max(lower)
        print "min(middle)=%f"%min(middle)
        print "max(middle)=%f"%max(middle)
        print "min(upper)=%f"%min(upper)
        print "max(upper)=%f"%max(upper)
        #tmp = (min(upper)-min(middle))/(max(middle)-max(lower))
        #apex = (min(upper)+tmp*max(lower))/(1+tmp)
        if max(middle)-max(lower) + min(upper)-min(middle) == 0:
            apex = (max(middle) + min(middle))/2
        else:
            apex = ( min(upper)*(max(middle)-max(lower)) + 
                     max(lower)*(min(upper)-min(middle))   ) / \
                     ( (max(middle)-max(lower)) + 
                       (min(upper)-min(middle))   )
                     
                 
        if min(upper)-min(middle) == 0:
            height = 0
        else:
            height = (min(upper)-apex)/(min(upper)-min(middle))
        try:
            assert min(lower) <= min(middle) <= max(middle) <= max(upper) and height >= 0
        except AssertionError:
            print "caught assert error: from skipping reasonable interval processing"
            #this is a hack: when reasonable interval processing fails, there
            #is a possibility that the order of the max/min for upper and
            #lower will overlap, so here we resort them
            out = sorted([min(lower),max(lower), min(middle), max(middle), min(upper),max(upper),apex,apex])
            height = 0
            return (out[0],out[2],out[-3],out[-1],
                    out[1],out[3],out[4],out[-2],height)


        return (min(lower), min(middle), max(middle), max(upper),
                max(lower), apex, apex, min(upper), height)



    def establishNatureOfFou(self,data):
        pass

    def deleteInadmissibleT1Fss(self,data):
        (lower,upper) = zip(*data)
        lastDitchLower = max(max(lower),self.r[0])
        lastDitchUpper = min(min(upper),self.r[1])
        for d in data[:]:
            if d[0] < self.r[0] or d[1] > self.r[1]:
                #print d
                data.remove(d)
            #this is different than the original paper
            # if d[0] < self.r[0] or d[1] > self.r[1]:
            #     replacement0 = d[0]
            #     replacement1 = d[1]
            #     if d[0] < self.r[0] :
            #         replacement0 = self.r[0]
            #     if d[1] > self.r[1]:
            #         replacement1 = self.r[1]
            #     data[data.index(d)] = (replacement0,replacement1)
                                
            if len(data) == 0:
                print "in deleteInadmissibleT1Fss, using (%d,%d)"%(lastDitchLower,lastDitchUpper)
                data.append((lastDitchLower,lastDitchUpper))

    def computeMathematicalModelForFou(self,data):
        # Compute the mathematical model for FOU
        print "done"
        print
        return 1


###########################################
# Main
if __name__ == "__main__":
###########################################
    pass

