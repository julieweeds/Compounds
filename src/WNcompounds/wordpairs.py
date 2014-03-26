__author__ = 'juliewe'

import sys,os,inspect
from conf import configure
from nltk.corpus import wordnet as wn

class PairGenerator:

    GO_P='_run_'

    def __init__(self,parameters):
        self.parameters=parameters
        self.n=100
        self.ANpath=os.path.join(self.parameters['compdatadir'],'wn.ANs.txt')
        self.NNpath=os.path.join(self.parameters['compdatadir'],'wn.NNs.txt')
        self.NNfiltpath=os.path.join(self.parameters['compdatadir'],'wn_wiki.NNs.txt')
        self.ANfiltpath=os.path.join(self.parameters['compdatadir'],'wn_wiki.NNs.txt')
        self.wikiNpath=os.path.join(self.parameters['compdatadir'],'wikiPOS_nounsdeps.events.strings')
        self.ANs=[]
        self.NNs=[]
        self.headdict={}
        self.freqthresh=100

    @staticmethod
    def getpos(word):
        pos=[]
        #test noun
        ss=wn.synsets(word,pos=wn.NOUN)
        #print ss
        if len(ss)>0:
            pos.append('N')

        ss=wn.synsets(word,pos=wn.ADJ)
        if len(ss)>0:
            pos.append('J')
        return pos

    def _run_readfile(self):
        print "Reading AN and NN files"
        self.ANs=[]
        self.NNs=[]
        with open(self.ANpath,'r') as instream:
            for line in instream:
                self.ANs.append(line.rstrip())
        with open(self.NNpath,'r') as instream:
            for line in instream:
                self.NNs.append(line.rstrip())
        print 'NNs',len(self.NNs)
        print 'ANs',len(self.ANs)
        return

    def _run_extract(self):
        #extract all 2 word AN and NN compounds from WN and write to file
        print "Extracting noun compounds from WN"


        discards=[]
        allsynsets=list(wn.all_synsets(self.parameters['pos']))
        if not self.parameters['testing']:
            self.n=len(allsynsets)
        for synset in list(wn.all_synsets(self.parameters['pos']))[:self.n]:
            for lemma in synset.lemmas:  #walk over all lemmas for all synsets
                #print lemma.name
                words=lemma.name.split('_')
                if len(words)==2:#check 2 words
                    poslist=[]
                    for word in words:
                        poslist.append(PairGenerator.getpos(word))#generate a PosList List for this pair of words
                    #print words,poslist
                    headpos=poslist.pop()
                    if 'N' in headpos:#is 'N' a possible part of speech for the head word (last word in the list)
                        phrase=words.pop()+'/N'
                        modpos=poslist.pop()
                        mod=words.pop()
                        if 'N' in modpos: #is 'N' a poss part of speech for mod
                            NNphrase=phrase+":nn-DEP:"+mod+'/N'
                            self.NNs.append(NNphrase)
                        if 'J' in modpos:#is 'J' a poss part of speech for mod
                            ANphrase=phrase+":amod-DEP:"+mod+'/J'
                            self.ANs.append(ANphrase)

                        if len(modpos)==0:#only considering J and N for mod
                            #print "Discarding "+lemma.name
                            discards.append(lemma.name)
                    else:#only considering N for head
                        #print "Discarding "+lemma.name
                        discards.append(lemma.name)

        print len(self.NNs),self.NNs
        print len(self.ANs),self.ANs
        print len(discards),discards
        #write lists to file
        with open(self.ANpath,'w') as outstream:
            for AN in self.ANs:
                outstream.write(AN+'\n')
        with open(self.NNpath,'w') as outstream:
            for NN in self.NNs:
                outstream.write(NN+'\n')
        return

    def _run_filter(self):
        print "Running filter"
        if self.parameters['comptype']=='NNs':
            complist=list(self.NNs)
        elif self.parameters['comptype']=='ANs':
            complist=list(self.ANs)
        else:
            complist=[]

        self.headdict={}
        print "Building phrase dictionary"
        for comp in complist:  #set up hashes for checking data file against
            parts=comp.split(':')
            thisentry=self.headdict.get(parts[0],None)
            if thisentry==None:
                thisentry=[]
            thisentry.append(self.parameters['featurematch'][self.parameters['comptype']]+parts[2])
            self.headdict[parts[0]]=thisentry
        print self.headdict
        print "Processing event file "+self.wikiNpath
        newlist=[]
        linesread=0
        with open(self.wikiNpath,'r') as instream:

            for line in instream:
                linesread+=1
                fields=line.rstrip.split('\t')
                headtomods=self.headdict.get(fields[0],None)
                if headtomods!=None:
                    for i in range(1,len(fields),2):
                        if fields[i] in headtomods:
                            freq=fields[i+1]
                            if freq>self.freqthresh:
                                phrase=fields[0]+self.parameters['featurematch'][self.parameters['comptype']]+fields[i]
                                newlist.append(phrase)
                else:
                    #don't care about this head so discard line
                    pass
                if self.parameters['testing'] and linesread%100==0:
                    break

        print newlist
        return

    def get_names(self):
        members = inspect.getmembers(self, predicate=inspect.ismethod)
        return [x[0][len(PairGenerator.GO_P):]
                for x in members
                if x[0].startswith(PairGenerator.GO_P)]

    def run(self):
        gonames=self.get_names()
        print self.parameters['run']
        for runp in self.parameters['run']:
            #print runp
            if runp in gonames:

                method=getattr(self,PairGenerator.GO_P+runp)
                method()
            else:
                print "No method defined for "+self.parameters['run']

if __name__=='__main__':
    myGen=PairGenerator(configure(sys.argv))
    myGen.run()