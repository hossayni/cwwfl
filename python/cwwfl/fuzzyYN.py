#!/usr/bin/python

import fuzzyset as fs
from intervalapproach import IntervalApproachCwwEstimator
from intervalapproach import EnhancedIntervalApproachCwwEstimator
from collections import defaultdict 
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg') # Must be before importing matplotlib.pyplot or pylab!
import matplotlib.pyplot as plt 

class T2FuzzyYnSurveyTaskResults(list):
    """Wrap/inherit from a list to keep track of data from an interval survey
    
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
    def truth(self): 
        """A generator function for truth-value intervals"""
        for row in self:
            yield (row['l'],row['u'])
    def plot(self,r=[0,100]):
        pass

class T1FuzzyYnSurveyTaskResults(list):
    """Wrap/inherit from a list to keep track of data from an interval survey
    
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
    def truth(self): 
        """A generator function for truth-value points"""
        for row in self:
            yield row['p']
    def median(self):
        return np.median([x for x in self.truth()])
    def plot(self,ax=None,r=[0,100]):
        pass


#if __name__ == "__main__":

t2data = defaultdict(T2FuzzyYnSurveyTaskResults) 
t1data = defaultdict(T1FuzzyYnSurveyTaskResults) 
import csv
#t2reader = csv.DictReader(open('fuzzyYnDataAll_20120514.txt', 'rb'), delimiter='\t', quotechar='"', )
t2reader = csv.DictReader(open('fuzzyYnDataAll_20120519.txt', 'rb'), delimiter='\t', quotechar='"', )
#t2reader = csv.DictReader(open('fuzzyYnDataGood_20120514.txt', 'rb'), delimiter='\t', quotechar='"', )
for row in t2reader:
    #print row
    #print row['username'].decode("utf8").encode("iso-8859-9","ignore")
    #print row['username'].decode("utf8").encode("utf8","ignore")

    #convert from strings to floats
    row['l'] = float(row['l'])
    row['u'] = float(row['u'])
    t2data[row['stimuli']] += [row]

t1reader = csv.DictReader(open('t1FuzzyYnDataAll_20120514.txt', 'rb'), delimiter='\t', quotechar='"', )
for row in t1reader:
    #print row
    row['p'] = float(row['p'])
    t1data[row['stimuli']] += [row]

#ia = IntervalApproachCwwEstimator()
ia = EnhancedIntervalApproachCwwEstimator()
for word in t2data: 
    print word
    for i in t2data[word]:
        print i
    t2data[word].fs = ia([x for x in 
                             t2data[word].truth()])
    print t2data[word].fs
    print t2data[word].fs.umf
    print t2data[word].fs.lmf
    print "median", t1data[word].median()
    print 'output for {0:>40}'.format(word), 
    print "\t%f\t%f"% t2data[word].fs(float(t1data[word].median()))
    print word, "centroid ", t2data[word].fs.centroid()
    print word, "centerOfMass", t2data[word].fs.centerOfMass()
    # plt = fs.plotIT2FS(t2data[word].fs, label=word)
    # plt.gca().stem([t1data[word].median()],[1],linefmt='r')
    # plt.show()

sortedwords = sorted(t2data.keys(), key=lambda x: t2data[x].fs.centerOfMass())
#for word in sortedwords: 
    #print word
    #plt = fs.plotIT2FS(t2data[word].fs, label=word)
    #plt.gca().stem([t1data[word].median()],[1],linefmt='r')
    #plt.show()

    #except ValueError as e:
    #print word, e
    
# fig = plt.figure()
# fig.subplots_adjust(hspace=0.35)
# #x = np.linspace(r[0],r[1],100)
# words = ["no","nope", "definitely not", "no, not normally",
#          #"that's a hard one... I guess not really",
#          "maybe", 
#          "not really", 
#          "possibly not", "sort of", 
#          "kind of", "sometimes", "I think so", "perhaps",
#          "probably", "yes usually", "certainly", "yes" 
#          ]

# for i,w in enumerate(words):
#     print w,
#     print i+1
#     x = np.linspace(0,100,201)
#     plotnum = (1 + 4*i)%16 + (1 + 4*i)//16 #modular awesomeness
#     ax1 = fig.add_subplot(4,4,plotnum)
#     ax1.fill_between(x,
#                      map(t2data[w].fs.umf, x),
#                      map(t2data[w].fs.lmf, x))
#     ax1.set_ybound(0,1)
#     ax1.set_xbound(0,100)
#     #ax1.set_title(w, x=2, y=.5)
#     ax1.set_title(w)
#     #ax1.get_xaxis().set_ticks_position('none')
#     #ax1.spines['bottom'].set_visible(False)
#     #plt.gca().axison = False
#     if plotnum not in (1,5,9,13):
#         ax1.set_yticklabels( () )
#     if plotnum not in (13,14,15,16):
#         ax1.set_xticklabels( () )
# #plt.savefig('ynExample.svg', bbox_inches='tight')
# plt.show()
