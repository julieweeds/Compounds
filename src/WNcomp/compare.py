__author__ = 'juliewe'

import sys,os
from conf import configure
from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet_ic as wn_ic

class ThesEntry:

    def __init__(self,phrase,score=1):

        self.phrase=phrase
        self.comp_score=score
        self.neighdict={}

    def getHead(self):
        return self.phrase.split(':')[0]

    def getMod(self):
        return self.phrase.split(':')[2]

    def getRel(self):
        return self.phrase.split(':')[1]

    def addneighs(self,fields):

        while len(fields) > 0:
            sc=fields.pop()
            neigh=fields.pop()
            self.neighdict[neigh]=float(sc)


class Comparer:


    def __init__(self,parameters):
        self.parameters=parameters
        self.collocdict={}
        self.leftdict={}
        self.rightdict={}
        self.mwpath=os.path.join(parameters['compdatadir'],parameters['mwfile'])
        self.neighpath=os.path.join(parameters['compdatadir'],parameters['neighfile'])

    def loadphrases(self):

        with open(self.mwpath,'r') as instream:
            print "Reading "+self.mwpath
            for line in instream:
                fields=line.rstrip().split('\t')
                collocate=fields[0]
                parts=collocate.split(':')
                left=parts[0] #black/J
                rel=parts[1]  #'amod-DEP'
                right=parts[2] #swan/N
                inversematch = self.parameters['inversefeatures'][self.parameters['featurematch']]
                print "Attempting to match "+rel+" and "+inversematch
                if rel==inversematch
                    rel=self.parameters['featurematch']
                    collocate=right+':'+rel+':'+left


                if rel == self.parameters['featurematch']:

                    if len(fields)>1:
                        if self.parameters['literalityscore']=='compound':
                            sc=float(fields[1]) #compound literality score
                        elif self.parameters['literalityscore']=='right':
                            sc=float(fields[3]) #right word literality score
                        elif self.parameters['literalityscore']=='left':
                            sc=float(fields[2])

                    else:
                        sc=float(hash(collocate))

                    self.collocdict[collocate]=ThesEntry(collocate,score=sc)

                    #print "mod: ",mod,"head: ",head
                    self.leftdict[left]=self.leftdict.get(left,0)+1
                    self.rightdict[right]=self.rightdict.get(right,0)+1


        print "Number of collocations is "+str(len(self.collocdict.keys()))
        print "Number of right heads is "+str(len(self.rightdict.keys()))
        print "Number of left modifiers is "+str(len(self.leftdict.keys()))
        self.collocorder=sorted(self.collocdict.keys())

        return

    def loadneighbours(self):
        with open(self.neighpath,'r') as instream:
            print "Reading "+self.neighpath
            linesread=0
            added=0
            for line in instream:
                linesread+=1
                if linesread%1000==0:
                    print "Processed lines: "+str(linesread)
                fields=line.rstrip().split('\t')
                entry=fields[0]
                thisEntry= self.collocdict.get(entry,None)
                if thisEntry!=None:
                    thisEntry.addneighs(fields[1:2*self.k+1])
                    print "Adding entry for "+entry
                    added+=1
        print "Added thesaurus entry for phrases: "+str(added)
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