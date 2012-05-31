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
import fuzzyset as fs
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
pp = PdfPages('multipage.pdf')

import numpy as np


from intervalapproach import IntervalApproachCwwEstimator

class VadSurveyTaskResults(list):
    """Wrap/inherit from a list to keep track of VAD data from an interval survey
    
    (VAD is valence, activation and dominance)
    
    The list elements are dicts, where the keys correspond to column names
    from a given row in the database
 
    """
    
    def append(self,item):
        """Override the append operator to check that there is a stimuli field
        and add the stimuli field to the object as a member variable"""

        if not item['stimuli']:
            raise ValueError('this row does not have a stimuli field: %s' %
                             str(item))
        self.stimulus = item['stimuli']
        super(VadSurveyTaskResults, self).append(item)
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
    def plot(self,r=[0,100]):
        """plots interval type-2 fuzzy set membership functions (footprints of
        uncertainty) for valence, activation, and dominance scales"""
        fig = plt.figure()
        #fig.suptitle(unicode(self.stimulus,"utf8","replace"))
        fig.suptitle(self.stimulus)
        x = np.linspace(r[0],r[1],100)
        ax1 = fig.add_subplot(441)
        ax2 = fig.add_subplot(442,sharex=ax1)
        ax3 = fig.add_subplot(443,sharex=ax1)
        #valence
        ax1.fill_between(x,
                         map(self.val.umf, x),
                         map(self.val.lmf, x))
        ax1.set_xlabel('valence')
        #activation
        ax2.fill_between(x,
                         map(self.act.umf, x),
                         map(self.act.lmf, x))
        ax2.set_xlabel('activation')
        #dominance
        ax3.fill_between(x,
                         map(self.dom.umf, x),
                         map(self.dom.lmf, x))
        ax3.set_xlabel('dominance')
        
        #plt.show()
        pp.savefig()



###########################################
# Main
if __name__ == "__main__":
###########################################

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

        #damn it all to hell, mysql+unicode
        #print row['stimuli']
        #print type(row['stimuli'])
        #print row['stimuli'].decode("utf8").encode("raw_unicode_escape").decode("utf8","replace")
        #print type(row['stimuli'].decode("utf8").encode("raw_unicode_escape").decode("utf8","replace"))
        
        #this fixes most of the problems with mysql+unicode:
        row['stimuli'] = row['stimuli'].decode("utf8").encode("raw_unicode_escape").decode("utf8","replace")
        
        #data[row['task']][row['stimuli']] += [row]
        data[row['task']][row['stimuli']].append(row)


# for word in data['turkish']: 
#     for resp in data['turkish'][word]:
#         print \
#             resp['stimuli'], \
#             resp['v_l'], resp['v_u'], \
#             resp['a_l'], resp['a_u'], \
#             resp['d_l'], resp['d_u']

    ia = IntervalApproachCwwEstimator()
    for word in data['turkish']: 

        #print word.decode("utf8").encode("raw_unicode_escape")
        print word
        try:
            data['turkish'][word].val = ia([x for x in 
                                            data['turkish'][word].valence()])
            data['turkish'][word].act = ia([x for x in 
                                            data['turkish'][word].activation()])
            data['turkish'][word].dom = ia([x for x in 
                                            data['turkish'][word].dominance()])
            
            data['turkish'][word].plot()
        
        except ValueError as e:
            print word, e
    
    #for resp in 
    #    print resp['stimuli'] 


pp.close() #for pdf plotting
# then iterate over each word of each task and compute fuzzy set membership
# functions for each dimension (valence, activation, and dominance)

