#!/usr/bin/python
# -*- coding: UTF-8 -*

# first read data and assign it to VadSurveyTask's

# store it like this: data["task X"] = vadSurveyTask
# vadSurveyTask["word"] = [row1, row2, ...]

# with open("fuzzyVad.events_20120502.txt") as fh:
#     for line in fh:
#         print line.split("\t")[4]

from collections import defaultdict 
import sys
from scipy.stats import scoreatpercentile,nanmean,nanstd
import random
from math import sqrt,log

class VadSurveyTaskResults(list):
    """Wrap/inherit from a list to keep track of VAD data from an interval survey
    
    (VAD is valence, activation and dominance)
    
    The list elements are dicts, where the keys correspond to column names
    from a given row in the database
 
    """
    def valence(self): # return a list of intervals observed for valence
        """A generator function for valence intervals"""
        for row in self:
            yield (row['v_l'],row['v_u'])
    def activation(self): # return a list of intervals observed for activation
        """A generator function for activation intervals"""
        for row in self:
            yield (row['a_l'],row['a_u'])
    def dominance(self): # return a list of intervals observed for dominance
        """A generator function for dominance intervals"""
        for row in self:
            yield (row['d_l'],row['d_u'])
    
def IA(data,r=(0,100)):
    """ this function performs the Interval Approach as described in [Liu and Mendel
    2008]
    
    Args:
        data: a VadSurveyTaskResults instance
        r: range, default [0,100]

    Returns: an interval type-2 fuzzy set with a trapeziodal upper and a
        triangular lower
    
    Raises: 
        TBA

    """ 
    print len(data)
    if len(data)==0: raise ValueError("No Remaining intervals")
    
    # Bad data processing: check that data is in range
    try:
        for d in data:
            if d[0] < r[0] or d[1] > r[1] or d[0] > d[1]:
                raise ValueError("Bad Data: %s is out of range %s" % (str(d), str(r)))
    except ValueError as e:
        old = len(data)
        filter(lambda d: d[0] < r[0] or d[1] > r[1] or d[0] > d[1], data)
        print "bad data found, removing %d data points" % old - len(data)

    
    print len(data)
    if len(data)==0: raise ValueError("No Remaining intervals")

    # Outlier processing
    intervalLengths = map(lambda x: x[1]-x[0], data)
    (lower,upper) = zip(*data)
    firstQuartileLower = scoreatpercentile(lower,25)
    thirdQuartileLower = scoreatpercentile(lower,75)
    interQtlRangeLower = thirdQuartileLower - firstQuartileLower
    firstQuartileUpper = scoreatpercentile(upper,25)
    thirdQuartileUpper = scoreatpercentile(upper,75)
    interQtlRangeUpper = thirdQuartileUpper - firstQuartileUpper
    firstQuartileInterval = scoreatpercentile(intervalLengths,25)
    thirdQuartileInterval = scoreatpercentile(intervalLengths,75)
    interQtlRangeInterval = thirdQuartileInterval - firstQuartileInterval
    print "lower", firstQuartileLower,thirdQuartileLower, interQtlRangeLower
    print "upper", firstQuartileUpper,thirdQuartileUpper, interQtlRangeUpper
    print "interval", firstQuartileInterval,thirdQuartileInterval, interQtlRangeInterval
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
            print e
            print "Outlier: removing data point %s" % str(d)
            data.remove(d)

    print len(data)
    if len(data)==0: raise ValueError("No Remaining intervals")

    # Tolerance limit processing
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
            print e
            print "Intolerable: removing data point %s" % str(d)
            data.remove(d)

    print len(data)
    if len(data)==0: raise ValueError("No Remaining intervals")

    # Reasonable interval processing
    # note: need to do resampling again
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
    elif stdLower == 0:
        barrier = meanLower+0.01
    elif stdUpper == 0:
        barrier = meanUpper+0.01
    else:
        barrier1 = ( -(meanLower*stdUpper**2-meanUpper*stdLower**2) + 
                      stdLower*stdUpper*sqrt((meanLower-meanUpper)**2 + 
                                             2*(stdLower**2-stdUpper**2)*log(stdLower/stdUpper)))/(stdLower**2-stdUpper**2)
        barrier2 = ( -(meanLower*stdUpper**2-meanUpper*stdLower**2) - 
                      stdLower*stdUpper*sqrt((meanLower-meanUpper)**2 + 
                                             2*(stdLower**2-stdUpper**2)*log(stdLower/stdUpper)))/(stdLower**2-stdUpper**2)
                      
        if barrier1 >= meanLower and barrier1 <= meanUpper:
            barrier = barrier1
        else:
            barrier = barrier2
    for (l,u) in data[:]:
        try:
            if l > barrier or u < barrier:
                raise ValueError("Unreasonable: interval %s does not cross reasonable barrier  %s" % (str((l,u)), str(barrier)),(l,u))
        except ValueError as (e,d):
            print e
            print "Unreasonable: removing data point %s" % str(d)
            data.remove(d)

    print len(data)
    if len(data)==0: raise ValueError("No Remaining intervals")


    # Admissible region determination
    tTable=[6.314, 2.920, 2.353, 2.132, 2.015, 1.943, 1.895, 1.860, 1.833, 1.812, 
            1.796, 1.782, 1.771, 1.761, 1.753, 1.746, 1.740, 1.734, 1.729, 1.725, 
            1.721, 1.717, 1.714, 1.711, 1.708, 1.706, 1.703, 1.701, 1.699, 1.697, 1.684] 
    tAlpha=tTable[min(len(data),30)]
    (lower,upper) = zip(*data)
    meanLower = nanmean(lower)
    meanUpper = nanmean(upper)
    c = map(lambda d: d[1] - 5.831*d[0], data)
    # as opp to Liu/Mendel, no assumption that FS is in [0,10]
    # BUT WE DO ASSUME THAT r[0] is 0!
    d = map(lambda d: d[1] - 0.171*d[0] - .829*(r[1]-r[0]), data) 
    shift1 = tAlpha * nanstd(c)/sqrt(len(data)) # todo: better name than shift
    shift2 = tAlpha * nanstd(d)/sqrt(len(data)) # todo: better name than shift

    # Establish nature of FOU
    for (l,u) in data[:]:
        try:
            pass
        except ValueError as (e,d):
            print e
            print "faldfsd: removing data point %s" % str(d)
            data.remove(d)
    

    # Delete inadmissible T1 FSs

    # Compute the mathematical model for FOU
    print "done"
    print
    return 1

# create a dictionary of dictionaries where the bottom level refers to VadSurveyTaskResults
# eg: {'turkish': { u'kÄ±smetli': <class '__main__.VadSurveyTaskResults'> ... }
data = defaultdict(lambda: defaultdict(VadSurveyTaskResults)) 
import csv
vadreader = csv.DictReader(open('fuzzyVad.events_20120502.txt', 'rb'), delimiter='\t', quotechar='"', )
for row in vadreader:
    #print row['username'].decode("utf8").encode("iso-8859-9","ignore")
    #print row['username'].decode("utf8").encode("utf8","ignore")
    # get only turkish
    if row['task'].find("Turkish") == 0:
        row['task'] = "turkish"
    else: continue
    # ignore null
    if row['task'] == "NULL":
        continue
    if row['v_l'] == "NULL":
        continue
    if row['v_u'] == "NULL":
        continue
    if row['a_l'] == "NULL":
        continue
    if row['a_u'] == "NULL":
        continue
    if row['d_l'] == "NULL":
        continue
    if row['d_u'] == "NULL":
        continue
    # ignore certain users
    if row['username'].find("testabe")==0:
        continue
    if row['username'].find("test")==0:
        continue
    if row['username'].find("samet")==0:
        continue
    if row['username'].decode("utf8").find(u'Ã–zge ahras')==0:
        continue
    #convert from strings to floats
    row['v_l'] = float(row['v_l'])
    row['v_u'] = float(row['v_u'])
    row['a_l'] = float(row['a_l'])
    row['a_u'] = float(row['a_u'])
    row['d_l'] = float(row['d_l'])
    row['d_u'] = float(row['d_u'])
    data[row['task']][row['stimuli']] += [row]


    

# for word in data['turkish']: 
#     for resp in data['turkish'][word]:
#         print \
#             resp['stimuli'], \
#             resp['v_l'], resp['v_u'], \
#             resp['a_l'], resp['a_u'], \
#             resp['d_l'], resp['d_u']
for word in data['turkish']: 
    print word
    try:
        # data['turkish'][word].vmf = IA([x for x in data['turkish'][word].valence()])
        # data['turkish'][word].amf = IA([x for x in data['turkish'][word].activation()])
        # data['turkish'][word].dmf = IA([x for x in data['turkish'][word].dominance()])
        IA([x for x in data['turkish'][word].valence()])
        IA([x for x in data['turkish'][word].activation()])
        IA([x for x in data['turkish'][word].dominance()])
    except ValueError as e:
        print word, e
    
    #for resp in 
    #    print resp['stimuli'] 


assert type(data['turkish'][u'ÅŸiddetli']) is VadSurveyTaskResults
# then iterate over each word of each task and compute fuzzy set membership
# functions for each dimension (valence, activation, and dominance)

