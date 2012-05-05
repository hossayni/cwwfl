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
    
def IA(data):
    """ this function performs the Interval Approach as described in [Liu and Mendel
    2008]
    
    Args:
        data: a VadSurveyTaskResults instance

    Returns: an interval type-2 fuzzy set with a trapeziodal upper and a
        triangular lower
    
    Raises: 
        TBA

    """ 
    print data
    # Bad data processing
    
    # Outlier processing
    
    # Tolerance limit processing

    # Reasonable interval processing

    # Admissible region determination

    # Establish nature of FOU

    # Delete inadmissible T1 FSs

    # Compute the mathematical model for FOU

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
        print "wha"
        continue
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
    data['turkish'][word].vmf = IA([x for x in data['turkish'][word].valence()])
    data['turkish'][word].amf = IA([x for x in data['turkish'][word].activation()])
    data['turkish'][word].dmf = IA([x for x in data['turkish'][word].dominance()])

    #for resp in 
    #    print resp['stimuli'] 


assert type(data['turkish'][u'ÅŸiddetli']) is VadSurveyTaskResults
# then iterate over each word of each task and compute fuzzy set membership
# functions for each dimension (valence, activation, and dominance)

