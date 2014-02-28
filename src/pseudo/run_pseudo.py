__author__ = 'juliewe'
#run the pseudo disambiguation task setup by setup_pseudo.py using either vectors or neighbours

from conf import configure
import sys,os

def stripcompop(phrase):
    parts=phrase.split(':')
    if len(parts)==4:
        result=parts[0]+':'+parts[2]+':'+parts[3]
    else:
        result=phrase
    return result

class PseudoPair:

    def __init__(self,fields):

        self.phrase=fields[0]
        self.choice1=fields[1]
        self.choice2=fields[2]
        self.votes={}

    def getPhrase(self):
        return self.phrase

    def getHead(self):
        return self.phrase.split(':')[0]

    def get(self,atype):

        if atype=='phrase':
            return self.phrase
        elif atype=='head':
            return self.phrase.split(':')[0]
        elif atype=='choice1':
            return self.choice1
        elif atype=='choice2':
            return self.choice2

    def display(self):
        print self.phrase,self.choice1,self.choice2
        print self.votes

class ThesEntry:

    def __init__(self,name):
        self.name=name
        self.pseudopairs=[]
        self.neighbours=[]

    def addneighs(self,scoredlist):

        for i in range(0,len(scoredlist),2):
            self.neighbours.append(stripcompop(scoredlist[i]))
        return self.neighbours

    def display(self):
        print self.name
        print self.pseudopairs
        print self.neighbours

    def makeselfneigh(self,atype):
        if atype=='phrase':
            self.neighbours.append(self.name)
        elif atype=='head':
            self.neighbours.append(self.name.split(':')[0])
        return self.neighbours

class VectorEntry:

    def __init__(self,name):

        self.name=name
        self.neighbourof=[]
        self.relfeatdict={}

    def addneighbourof(self,neigh):
        self.neighbourof.append(neigh)

class PseudoDisambiguator:

    def __init__(self,parameters):
        self.parameters=parameters
        self.pseudopath=os.path.join(parameters['compdatadir'],parameters['pseudofile'])
        self.neighpath=os.path.join(parameters['compdatadir'],parameters['neighfile'])
        self.phrasepath=os.path.join(parameters['compdatadir'],parameters['phrasefile'])
        self.constitpath=os.path.join(parameters['compdatadir'],parameters['constitfile'])
        self.k=parameters['k']
        self.pseudodict={}  #dict from phrase/head to thesentry
        for type in self.parameters['typelist']:
            self.pseudodict[type]={}
        self.pseudopairs=[]   #list of pseudopairs
        self.vectordict={}  #dict from noun to vector including rel features
        if 'phrase' in self.pseudodict.keys():
            self.dophrase=True
        else:
            self.dophrase=False
        if 'head' in self.pseudodict.keys():
            self.dohead=True
        else:
            self.dohead=False


        self.loadpairs()

    def loadpairs(self):
        pairindex=len(self.pseudopairs)
        with open(self.pseudopath,'r') as instream:
            print "Reading "+self.pseudopath
            for line in instream:
                fields=line.rstrip().split('\t')
                apair = PseudoPair(fields)
                self.pseudopairs.append(apair)
                for atype in self.pseudodict.keys():
                    if self.pseudodict[atype].get(apair.get(atype),None)==None:
                        self.pseudodict[atype][apair.get(atype)]=ThesEntry(apair.getPhrase())

                    self.pseudodict[atype][apair.get(atype)].pseudopairs.append(pairindex)
                # if self.pseudodict['head'].get(apair.get('head'),None)==None:
                #     self.pseudodict['head'][apair.get('head')]=ThesEntry(apair.getHead())
                #
                # self.pseudodict['head'][apair.get('head')].pseudopairs.append(pairindex)


                pairindex+=1
        print "Stored "+str(pairindex)+" pairs"
        #print len(self.pseudophrasedict.keys()), self.pseudophrasedict
        #print len(self.pseudoheaddict.keys()),self.pseudoheaddict

    def processneighbours(self):

        linesread=0
        with open(self.neighpath,'r') as instream:
            print "Reading "+self.neighpath

            for line in instream:
                fields=line.rstrip().split('\t')
                if self.parameters['neighsource']=='observed':
                    name=fields[0]
                else:
                    name=stripcompop(fields[0])
                if self.dophrase:
                    mythes=self.pseudodict['phrase'].get(name,None)

                    if mythes==None and self.dohead:
                        mythes=self.pseudodict['head'].get(name,None)


                elif self.dohead:
                    mythes=self.pseudodict['head'].get(name,None)


                if mythes!=None:
                    kneighbourlist=fields[1:2*self.k+1]
                    #print fields[0],kneighbourlist
                    neighs=mythes.addneighs(kneighbourlist)
                    for neigh in neighs:
                        if self.vectordict.get(neigh,None)==None:
                            self.vectordict[neigh]=VectorEntry(neigh)
                        self.vectordict[neigh].addneighbourof(name)
                        for index in mythes.pseudopairs:
                            self.vectordict[neigh].relfeatdict[self.pseudopairs[index].choice1]=0
                            self.vectordict[neigh].relfeatdict[self.pseudopairs[index].choice2]=0

                else:
                    #ignore this line
                    pass



                linesread+=1
                if linesread%1000==0:
                    print "Processed "+str(linesread)+" lines"
                    #for key in self.pseudophrasedict.keys():
                    #    self.pseudophrasedict[key].display()
                    if self.parameters['testing']:
                        break

    def makeselfneigh(self):

        for atype in self.pseudodict.keys():
            for athesentry in self.pseudodict[atype].values():
                neighs=athesentry.makeselfneigh(atype)
                #print athesentry.name,neighs
                for neigh in neighs:
                    if self.vectordict.get(neigh,None)==None:
                        self.vectordict[neigh]=VectorEntry(neigh)
                    self.vectordict[neigh].addneighbourof(neigh)
                    for index in athesentry.pseudopairs:
                        self.vectordict[neigh].relfeatdict[self.pseudopairs[index].choice1]=0
                        self.vectordict[neigh].relfeatdict[self.pseudopairs[index].choice2]=0
            #print self.pseudodict[atype].keys()


    def processconstituents(self):

        vectorpaths=[self.constitpath,self.phrasepath]
        #vectorpaths=[self.constitpath]
        for vectorpath in vectorpaths:
            with open(vectorpath,'r') as instream:
                print "Reading "+vectorpath
                linesread=0
                for line in instream:
                    fields=line.rstrip().split('\t')
                    name=stripcompop(fields[0])
                    thisvector=self.vectordict.get(name,None)
                    if thisvector!=None:
                        #print "Processing vector for "+name
                        #print fields[1:]

                        while len(fields)>1:
                            score=float(fields.pop())
                            feature=fields.pop()
                            #print feature,score
                            if thisvector.relfeatdict.get(feature,-1)>-1:
                                thisvector.relfeatdict[feature]=score

                    else:
                        #ignore line
                        pass
                    linesread+=1
                    if linesread%1000==0:
                        print "Processed "+str(linesread)+" lines"
                        if self.parameters['testing']:
                            break

    def evaltask(self):

        processed=0
        totals={}
        for atype in self.pseudodict.keys():
            totals[atype]=0

        for pseudopair in self.pseudopairs:
            thesentry={}
            thisitem={}
            for atype in self.pseudodict.keys():

                pseudopair.votes[atype]=0.0
                thisitem[atype]=pseudopair.get(atype)
                thesentry[atype]=self.pseudodict[atype][thisitem[atype]]
                #print thesentry[atype].neighbours
                for neigh in thesentry[atype].neighbours:
                    neighvectorentry=self.vectordict[neigh]
                    diff=neighvectorentry.relfeatdict[pseudopair.get('choice1')]-neighvectorentry.relfeatdict[pseudopair.get('choice2')]
                    #print neigh, neighvectorentry.relfeatdict[pseudopair.get('choice1')], neighvectorentry.relfeatdict[pseudopair.get('choice2')]
                    if diff>0:
                        pseudopair.votes[atype]+=1
                        #print "Plus"
                    elif diff<0:
                        pseudopair.votes[atype]-=1
                        #print "Minus"
                if pseudopair.votes[atype]>0:
                    totals[atype]+=1.0
                elif pseudopair.votes[atype]==0:
                    totals[atype]+=0.5  #random guess

            processed+=1
            if self.parameters['testing']:
                pseudopair.display()
            if processed%100==0 and self.parameters['testing']:
                break
        print "Total processed = "+str(processed)
        print "Correct",totals



def go_neighs(parameters):


    #print pseudopath,neighpath
    mypseudo=PseudoDisambiguator(parameters)
    mypseudo.processneighbours()
    mypseudo.processconstituents()
    mypseudo.evaltask()

def go_vectors(parameters):
    mypseudo=PseudoDisambiguator(parameters)
    #mypseudo.k=1
    mypseudo.makeselfneigh()
    mypseudo.processneighbours()
    mypseudo.processconstituents()
    mypseudo.evaltask()

if __name__=='__main__':

    parameters = configure(sys.argv)

    if parameters['run_neighs']:
        go_neighs(parameters)
    elif parameters['run_vectors']:
        go_vectors(parameters)
