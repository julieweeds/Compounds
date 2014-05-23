__author__ = 'juliewe'

import sys,os
from conf import configure
from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet_ic as wn_ic
import numpy as np
import random, time, datetime,math

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
#            print "Warning error with name stripping "+phrase
            return(phrase)
        return np1+':'+np2+':'+np3

    elif len(parts)==1:
        return stripcompop(phrase)
    else:
 #       print "Warning error with name stripping "+phrase
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
    elif metric=='jcn':
        sim=ss1.jcn_similarity(ss2,wn_ic.ic('ic-semcor.dat'))
    return sim

def wnsim(phrase,neighbour,metric='path',pos='N'):

    (wnphrase,ptag)=wnFormat(phrase)
    (wnneighbour,ntag)=wnFormat(neighbour)

    neighsynsets=wn.synsets(wnneighbour,pos=wnmapping[pos])
    phrasesynsets=wn.synsets(wnphrase,pos=wnmapping[pos])

    maxsim=0
    if len(phrasesynsets)==0:
        maxsim=-2
    elif len(neighsynsets)==0:
        maxsim=-1  #no neighbours in wn

    else:
        for psynset in phrasesynsets:
            for nsynset in neighsynsets:
                sim=sensesim(psynset,nsynset,metric)
                if sim>maxsim:
                    maxsim=sim
    return maxsim


class ThesEntry:
    verbose=True

    def __init__(self,phrase,score=1):

        self.phrase=phrase
        self.comp_score=score
        self.neighdict={}
        self.complete=False

    def getHead(self):
        return self.phrase.split(':')[0]

    def getMod(self):
        return self.phrase.split(':')[2]

    def getRel(self):
        return self.phrase.split(':')[1]

    def addhead(self,head):

        self.neighdict[head]=1


    def addneighs(self,fields,k=10):

        if len(self.neighdict.keys())>0:
            print "Warning: neighbours already added for "+self.phrase
            print self.neighdict
            print fields[0:10]

        #print fields
        while len(self.neighdict.keys()) < k and len(fields)>0:
            neigh=fields.pop()
            sc=fields.pop()
            if self.validcheck(neigh):
                #self.neighdict[neigh]=float(sc)
                self.neighdict[neigh]=1
        if ThesEntry.verbose:
            print self.phrase, self.neighdict.keys()

        if len(self.neighdict.keys())==k:
            self.complete=True
            return 1
        else:
            self.complete=False
            return 0

    def validcheck(self,neigh):
        if neigh == self.phrase:
            #print neigh + "is phrase itself"
            return False  #neighbour can't be phrase itself
        parts=neigh.split(':')
        if len(parts)>1: #neighbour can't be any phrase
            #print neigh + " is a phrase"
            return False
        parts=neigh.split('/')
        if len(parts)<2: #neigh is score (random function)
            return False
        neighsynsets=wn.synsets(wnFormat(neigh)[0],wn.NOUN)
        if len(neighsynsets)==0:
            #print neigh + " not in WN" #neighbour must be in WN
            return False
        #if self.neighdict.get(neigh,0)==1: #neighbour already added - don't need this as it is a dict and won't add repeats anyway
        #    print neigh + " already added"
        #    return False


        return True

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
                mymean=-1  #no neighbours found or no neighbours in wn
            else:
                sarray=np.array(sims)
                mymean=np.average(sarray)
        if ThesEntry.verbose:
            print self.phrase,mymean
        return mymean


class Experiments:

    def __init__(self,parameters):

        self.parameters=parameters
        if self.parameters['testing']:
            ThesEntry.verbose=True
            self.parameters['ks']=[2]
        else:
            ThesEntry.verbose=False
        #if self.parameters['baseline']:
         #   self.parameters['ks']=[0]+self.parameters['ks']


    def run(self):

        for compdatadir,vsource in zip(self.parameters['compdatadirs'],self.parameters['vsources']):
            self.parameters['compdatadir']=compdatadir
            self.parameters['vsource']=vsource
            for k in self.parameters['ks']:
                self.parameters['k']=k
                with open(self.parameters['outfile'],'a') as self.parameters['outstream']:
                    myComparer=Comparer(self.parameters)
                    myComparer.go()



class Comparer:


    def __init__(self,parameters):
        self.parameters=parameters
        self.collocdict={}
        self.leftdict={}
        self.rightdict={}
        self.keydict={}  #key (head,mod or phrase --> collocate list)
        self.mwpath=os.path.join(parameters['compdatadir'],parameters['mwfile'])
        self.neighpath=os.path.join(parameters['compdatadir'],parameters['neighfile'])
        self.k=self.parameters['k']
        self.complete=0

    def loadphrases(self):

        with open(self.mwpath,'r') as instream:
            print "Reading "+self.mwpath
            for line in instream:
                fields=line.rstrip().split('\t')
                collocate=fields[0] #helmet/N:nn-DEP:football/N
                parts=collocate.split(':')
                left=parts[0] #helmet/N
                rel=parts[1]  #'nn-DEP'
                right=parts[2] #football/N
                inversematch = self.parameters['inversefeatures'][self.parameters['featurematch']]
                #print "Attempting to match "+rel+" and "+inversematch
                if rel==inversematch:
                    rel=self.parameters['featurematch']
                    collocate=right+':'+rel+':'+left
                    parts=collocate.split(':')
                    left=parts[0]
                    right=parts[2]


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

                    if self.parameters['unigram']: #enable comparison of just the heads or mods
                        parts=collocate.split(':') #[helmet/N,nn-DEP,football/N]
                        if self.parameters['dohead']:
                            collocate=parts[0]  #helmet/N
                        elif self.parameters['domod']:
                            collocate=parts[2]  #football/N
                    if self.parameters['dohead']:
                        self.collocdict[collocate]=ThesEntry(collocate,score=sc)
                        key = left

                    elif self.parameters['domod']:
                        self.collocdict[collocate]=ThesEntry(collocate,score=sc)
                        key=right
                    else:
                        self.collocdict[collocate]=ThesEntry(collocate,score=sc)
                        key = collocate
                    keylist=self.keydict.get(key,None)
                    if keylist==None:
                        self.keydict[key]=[collocate]
                    elif not self.parameters['unigram']:
                        keylist.append(collocate)
                        self.keydict[key]=keylist
                    #print "mod: ",mod,"head: ",head
                    self.leftdict[left]=self.leftdict.get(left,0)+1
                    self.rightdict[right]=self.rightdict.get(right,0)+1
                #if len(self.collocdict.keys())>1 and self.parameters['testing']:
                #    break
        print "Number of collocations is "+str(len(self.collocdict.keys()))
        print "Number of (right) mods is "+str(len(self.rightdict.keys()))
        print "Number of (left) heads is "+str(len(self.leftdict.keys()))
        print "Number of keys is "+str(len(self.keydict.keys()))

        keysum=0
        for key in self.keydict.keys():
            keysum+=len(self.keydict[key])
            if len(self.keydict[key])>1:
                print key, self.keydict[key]
        print "Number of collocations in keydict is "+str(keysum)
        #print self.keydict
        #self.collocorder=sorted(self.collocdict.keys())
        if self.parameters['testing']:
            print self.collocdict.keys()
        return

    def addbaseline(self):

        for phrase in self.collocdict.keys():
            thisEntry=self.collocdict[phrase]
            parts=phrase.split(':')
            thisEntry.addhead(parts[0])


    def loadneighbours(self):
        if self.k>0:
            allentries=list(self.collocdict.keys())  #for random mode
            random.shuffle(allentries)
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
                    #thisEntry= self.collocdict.get(entry,None)
                    keylist = self.keydict.get(entry,None)
                    if keylist!=None:
                        neighs=list(fields[1:])
                        neighs.reverse()
                        for key in keylist:
                            thisEntry=self.collocdict.get(key,None)
                            if thisEntry!=None:
                                if self.parameters['random']:
                                    #added shuffled neighbours to randomly selected target noun
                                    random.shuffle(neighs)
                                    randomentry=allentries.pop()
                                    thisEntry=self.collocdict[randomentry]

                                self.complete+=thisEntry.addneighs(neighs,self.k)
                        #print "Adding entry for "+entry
                                added+=1
            print "Added thesaurus entry for phrases: "+str(added)
            return

    def compareneighbours(self):
        sims=[]
        for myThes in self.collocdict.values():
            if myThes.complete:
                sim=myThes.average_wnsim(metric=self.parameters['wnsim'])
                if sim>-1:
                    sims.append(sim)
                #if self.parameters['testing'] and len(sims)>1:
                #    exit()

        if len(sims)>0:
            sarray=np.array(sims)
            mean=np.average(sarray)
            stdev=np.std(sarray)
            error=stdev/math.pow(len(sims),0.5)
        else:
            mean=0
            error =0
        mylength=len(sims)
        possible=len(self.collocdict.keys())
        #print possible
        recall=float(self.complete)/float(possible)
        print "Recall (proportion with complete neighbour list) size: "+str(self.parameters['k'])+" is "+str(recall)
        print "Mean is "+str(mean)+', error: '+str(error)
        if not self.parameters['testing']:
            self.writeoutput([recall,mean,error])
        return

    def writeoutput(self,values):

        if self.parameters['baseline']:
            bflag='_baseline'
        else:
            bflag='_nb'

        outline=self.parameters['phrasetype']+','+self.parameters['typelist'][0]+','+self.parameters['neighsource']+','+self.parameters['vsource']+','+parameters['rflag']+bflag+','+str(self.parameters['k'])
        for value in values:
            outline +=','+str(value)
        outline+='\n'
        ts=time.time()
        st=datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        outline=st+','+outline
        self.parameters['outstream'].write(outline)
        return

    def check(self):
        for myThes in self.collocdict.values():
            if len(myThes.neighdict.keys())==0:
                print myThes.phrase


    def go(self):
        if self.parameters['testing']:
            print self.parameters
        self.loadphrases()
        if self.parameters['baseline']:
            self.addbaseline()
        self.loadneighbours()
        if self.parameters['testing']:
            self.check()
        self.compareneighbours()

if __name__=='__main__':


    parameters=configure(sys.argv)
    print parameters
    random.seed(parameters['seed'])
    myexperiments=Experiments(parameters)
    myexperiments.run()