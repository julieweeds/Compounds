__author__ = 'juliewe'

import sys,os
from conf import configure
from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet_ic as wn_ic

class Comparer:


    def __init__(self,parameters):
        self.parameters=parameters
        self.collocdict={}
        self.leftdict={}
        self.rightdict={}
        self.neighdict={}

    def loadphrases(self):
        self.mwpath=os.path.join(parameters['compdatadir'],parameters['mwfile'])
        with open(self.parameters['mwpath'],'r') as instream:
            print "Reading "+self.parameters['mwpath']
            for line in instream:
                fields=line.rstrip().split('\t')
                collocate=fields[0]
                parts=collocate.split(':')
                left=parts[0] #black/J
                rel=parts[1]  #'amod-DEP'
                right=parts[2] #swan/N
                if rel == self.parameters['inversefeatures']['featurematch']:
                    rel=self.parameters['featurematch']
                    collocate=right+':'+rel+':'+left

                if rel == self.parameters['featurematch']:

                    if len(fields)>1:
                        if self.parameters['literalityscore']=='compound':
                            self.collocdict[collocate]=float(fields[1]) #compound literality score
                        elif self.parameters['literalityscore']=='right':
                            self.collocdict[collocate]=float(fields[3]) #right word literality score
                        elif self.parameters['literalityscore']=='left':
                            self.collocdict[collocate]=float(fields[2])

                    else:
                        self.collocdict[collocate]=float(hash(collocate))

                    #print "mod: ",mod,"head: ",head
                    self.leftdict[left]=self.leftdict.get(left,0)+1
                    self.rightdict[right]=self.rightdict.get(right,0)+1


        print "Number of collocations is "+str(len(self.collocdict.keys()))
        print "Number of right heads is "+str(len(self.rightdict.keys()))
        print "Number of left modifiers is "+str(len(self.leftdict.keys()))
        self.collocorder=sorted(self.collocdict.keys())

        return

    def loadneighbours(self):
        return

    def compareneighbours(self):
        return

    def go(self):

        self.loadphrases()
        self.loadneighbours()
        self.compareneighbours()

if __name__=='__main__':

    parameters=configure(sys.argv)
    myComparer=Comparer(parameters)

    myComparer.go()