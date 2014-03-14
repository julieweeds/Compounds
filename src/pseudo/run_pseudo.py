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
        elif atype=='mod':
            return self.phrase.split(':')[2]
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
            self.neighbours.append(stripdiffp(scoredlist[i]))
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
        elif atype=='mod':
            self.neighbours.append(self.name.split(':')[2])
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
        self.freqdict={}
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
        if 'mod' in self.pseudodict.keys():
            self.domod=True
        else:
            self.domod=False

        self.loadfreqs()
        self.loadpairs()


    def loadpairs(self):
        pairindex=len(self.pseudopairs)
        with open(self.pseudopath,'r') as instream:
            print "Reading "+self.pseudopath
            for line in instream:
                fields=line.rstrip().split('\t')
                if self.freqdict.get(fields[0],-1) >-1:
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

    def loadfreqs(self):

        freqpath=os.path.join(self.parameters['compdatadir'],self.parameters['freqfile'])
        print parameters['usefreqthresh'],parameters['freqthresh']
        with open(freqpath,'r') as instream:

            for line in instream:

                fields=line.rstrip().split('\t')
                phrase=fields[0]
                freq=float(fields[1])
                if phrase.split(':')[1]=='nn-DEP':
                    diff=freq-self.parameters['freqthresh']
                    if self.parameters['usefreqthresh']=='above' and diff>0:
                        self.freqdict[fields[0]]=freq
                    elif self.parameters['usefreqthresh']=='below' and diff<0:
                        self.freqdict[fields[0]]=freq
                    elif self.parameters['usefreqthresh']=='none':
                        self.freqdict[fields[0]]=freq
    def processneighbours(self):

        linesread=0
        with open(self.neighpath,'r') as instream:
            print "Reading "+self.neighpath

            for line in instream:
                fields=line.rstrip().split('\t')
                if self.parameters['neighsource']=='observed':
                    name=fields[0]
                else:
                    name=stripdiffp(fields[0])
                if self.dophrase:
                    mythes=self.pseudodict['phrase'].get(name,None)

                    if mythes==None and self.dohead:
                        mythes=self.pseudodict['head'].get(name,None)
                        if mythes==None and self.domod:
                            mythes=self.pseudodict['mod'].get(name,None)
                    elif mythes==None and self.domod:
                        mythes=self.pseudodict['mod'].get(name,None)



                elif self.dohead:
                    mythes=self.pseudodict['head'].get(name,None)
                    if mythes==None and self.domod:
                        mythes=self.pseudodict['mod'].get(name,None)
                elif self.domod:
                    mythes=self.pseudodict['mod'].get(name,None)


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
                if linesread%10000==0:
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
        if self.parameters['neighsource']=='unigram':
            vectorpaths=[self.constitpath]
        else:
            vectorpaths=[self.constitpath,self.phrasepath]
        #vectorpaths=[self.constitpath]
        for vectorpath in vectorpaths:
            with open(vectorpath,'r') as instream:
                print "Reading "+vectorpath
                linesread=0
                for line in instream:
                    fields=line.rstrip().split('\t')
                    name=stripdiffp(fields[0])
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
                    if linesread%10000==0:
                        print "Processed "+str(linesread)+" lines"
                        if self.parameters['testing']:
                            break

    def evaltask(self):

        processed=0
        totals={}
        accs={}
        for atype in self.pseudodict.keys():
            totals[atype]=0

        for pseudopair in self.pseudopairs:
            thesentry={}
            thisitem={}
            processed+=1
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
                        if parameters['freqdiff']:
                            pseudopair.votes[atype]+=diff
                        else:
                            pseudopair.votes[atype]+=1
                        #print "Plus"
                    elif diff<0:
                        if parameters['freqdiff']:
                            pseudopair.votes[atype]+=diff
                        else:
                            pseudopair.votes[atype]-=1
                        #print "Minus"
                if pseudopair.votes[atype]>0:
                    totals[atype]+=1.0
                elif pseudopair.votes[atype]==0:
                    totals[atype]+=0.5  #random guess
                accs[atype]=float(totals[atype])/float(processed)


            if self.parameters['testing']:
                pseudopair.display()
            if processed%100==0 and self.parameters['testing']:
                break
        print "Total processed = "+str(processed)+" with k = "+str(self.k)+" in neighbour file "+self.parameters['neighsource']
        print "Correct",totals
        print "Accuracy", accs
        mystream=parameters['outputstream']


        # phraseacc=float(totals['phrase'])/float(processed)
        # headacc=float(totals['head'])/float(processed)
        # modacc=float(totals['mod'])/float(processed)
        mystring=self.parameters['neighsource']+','+str(self.k)+','+self.parameters['usefreqthresh']+' '+str(self.parameters['freqthresh'])
        for key in accs.keys():
            mystring+=','+str(accs[key])
        mystring+='\n'
        mystream.write(mystring)



def go_neighs(parameters):


    #print pseudopath,neighpath
    mypseudo=PseudoDisambiguator(parameters)
    mypseudo.processneighbours()
    mypseudo.processconstituents()
    mypseudo.evaltask()

def go_vectors(parameters):
    while len(parameters['ks'])>0:
        parameters['k']=parameters['ks'].pop()
        #print parameters['ks'], parameters['k']
        mypseudo=PseudoDisambiguator(parameters)
        #mypseudo.k=1
        mypseudo.makeselfneigh()
        mypseudo.processneighbours()
        mypseudo.processconstituents()
        mypseudo.evaltask()

if __name__=='__main__':

    parameters = configure(sys.argv)
    outfile=os.path.join(parameters['compdatadir'],'results.csv')
    with open(outfile,'a') as outstream:
        parameters['outputstream']=outstream
        if parameters['run_neighs']:
            go_neighs(parameters)
        elif parameters['run_vectors']:
            go_vectors(parameters)
