__author__ = 'juliewe'

import sys,os
from conf import configure
from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet_ic as wn_ic
import numpy as np

wnmapping={'N':wn.NOUN,'V':wn.VERB,'J':wn.ADJ,'R':wn.ADV}

def stripcompop(phrase):
    parts=phrase.split(':')
    if len(parts)==4:
        result=parts[0]+':'+parts[2]+':'+parts[3]
    else:
        result=phrase
    return result

def stripdiffc(constit):
    parts=constit.split('!')
    if len(parts)>1:
        return parts[0]
    else:
        return constit


def stripdiffp(phrase):
    parts=stripcompop(phrase).split('!')
    if len(parts)==5:
        np1=parts[0]
        middleparts=parts[2].split(':')
        if len(middleparts)==6:
            np2=middleparts[4]
            np3=middleparts[5]
        elif len(middleparts)==5:
            np2=middleparts[3]
            np3=middleparts[4]

        else:
            print "Warning error with name stripping "+phrase
            return(phrase)
        return np1+':'+np2+':'+np3

    elif len(parts)==1:
        return stripcompop(phrase)
    else:
        print "Warning error with name stripping "+phrase
        return phrase

def wnFormat(phrase):
    parts=stripdiffp(phrase).split(':')
    wnphrase=''
    tag=''
    if len(parts)==3:
        if parts[1]=='nn-DEP':
            lex1=parts[2].split('/')[0]
            (lex2,tag)=parts[0].split('/')
            wnphrase=lex1+'_'+lex2
    elif len(parts)==1:
        (wnphrase,tag)=parts[0].split('/')
    return (wnphrase,tag)

def sensesim(ss1,ss2,metric):

    if metric=='path':
        sim=ss1.path_similarity(ss2)
    elif metric=='lin':
        sim=ss1.lin_similarity(ss2,wn_ic.ic('ic-semcor.dat'))
    return sim

def wnsim(phrase,neighbour,metric='path'):

    (wnphrase,ptag)=wnFormat(phrase)
    (wnneighbour,ntag)=wnFormat(neighbour)

    neighsynsets=wn.synsets(wnneighbour,pos=wnmapping['N'])
    phrasesynsets=wn.synsets(wnphrase,pos=wnmapping['N'])

    maxsim=0
    if len(phrasesynsets)==0:
        maxsim=-2
    if len(neighsynsets)==0:
        maxsim=-1
    for psynset in phrasesynsets:
        for nsynset in neighsynsets:
            sim=sensesim(psynset,nsynset,metric)
            if sim>maxsim:
                maxsim=sim
    return maxsim


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

    def average_wnsim(self,metric='path'):
        sims=[]
        mymean=0
        for neigh in self.neighdict.keys():
            sim=wnsim(self.phrase,neigh,metric)
            if sim>-1:
                sims.append(sim)
            elif sim==-2:
                mymean=-2
                break
        if mymean>-2:
            if len(sims)==0:
                mymean=-1
            else:
                sarray=np.array(sims)
                mymean=np.average(sarray)
        print self.phrase,mymean
        return mymean


class Comparer:


    def __init__(self,parameters):
        self.parameters=parameters
        self.collocdict={}
        self.leftdict={}
        self.rightdict={}
        self.mwpath=os.path.join(parameters['compdatadir'],parameters['mwfile'])
        self.neighpath=os.path.join(parameters['compdatadir'],parameters['neighfile'])
        self.k=self.parameters['k']

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
                #print "Attempting to match "+rel+" and "+inversematch
                if rel==inversematch:
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
                if linesread%10000==0:
                    print "Processed lines: "+str(linesread)
                fields=line.rstrip().split('\t')
                entry=stripdiffp(fields[0])
                thisEntry= self.collocdict.get(entry,None)
                if thisEntry!=None:
                    thisEntry.addneighs(fields[1:2*self.k+1])
                    #print "Adding entry for "+entry
                    added+=1
        print "Added thesaurus entry for phrases: "+str(added)
        return

    def compareneighbours(self):
        sims=[]
        for myThes in self.collocdict.values():
            sim=myThes.average_wnsim(metric=self.parameters['wnsim'])
            if sim>-1:
                sims.append(sim)

        sarray=np.array(sims)
        mean=np.average(sarray)
        print "Mean is "+str(mean)


        return

    def go(self):
        print self.parameters
        self.loadphrases()
        self.loadneighbours()
        self.compareneighbours()

if __name__=='__main__':

    parameters=configure(sys.argv)
    myComparer=Comparer(parameters)

    myComparer.go()