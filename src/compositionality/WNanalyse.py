__author__ = 'juliewe'

from ijcnlpReader import IjcnlpReader
from nltk.corpus import wordnet as wn
import sys,os
from conf import configure

class Analyser:

    wnmapping={'N':wn.NOUN,'V':wn.VERB,'J':wn.ADJ,'R':wn.ADV}

    def __init__(self,filepath):
        self.myReader=IjcnlpReader(filepath)

    def getsynlists(self,alist):

        incount=0
        total=0
        synsetslists=[]
        for token in alist:
            total+=1
            (lex,tag)=token.split('/')
            compsynsets=wn.synsets(lex,pos=Analyser.wnmapping[tag])
            if len(compsynsets)>0:
                incount+=1
            synsetslists.append(compsynsets)
        print "Proportion of list with one entry in WN is "+str(incount)+" out of "+str(total)
        return synsetslists

    def checkcomposition(self,comp_synlist,word_synlist):
        #check compositionality of comp with respect to word
        #check over all pairings of senses - compositional if at least one sense pairing suggests compositional

        result=False
        for csyn in comp_synlist:
            for wsyn in word_synlist:
                if wsyn == csyn:  #both in same synset
                    result=True

                elif wsyn in csyn.lowest_common_hypernyms(wsyn):#check if lowest common hypernym is word
                        result=True

                #need to check dictionary definition too

        return result






    def analyse(self):

        comps= self.myReader.getWNComps()
        words=[self.myReader.getWNwords(1),self.myReader.getWNwords(2)]

        compsynsets=self.getsynlists(comps)
        wordsynsets=[self.getsynlists(words[0]),self.getsynlists(words[1])]

        count=0
        word1comps=[]
        word2comps=[]
        neithercomps=[]
        bothcomps=[]
        for (phrase,comp,word1,word2) in zip(comps,compsynsets,wordsynsets[0],wordsynsets[1]):
            print "Checking "+phrase
            w1=self.checkcomposition(comp,word1)
            w2=self.checkcomposition(comp,word2)

            #print "With respect to word1: "+str(w1)
            #print "With respect to word2: "+str(w2)
            if w1:
                count+=1
                word1comps.append(phrase)
                if w2:
                    count+=1
                    word2comps.append(phrase)
                    bothcomps.append(phrase)
            elif w2:
                count+=1
                word2comps.append(phrase)
            else:
                neithercomps.append(phrase)

        print "Total score is: "+str(count)
        print len(bothcomps),bothcomps
        print len(word1comps),word1comps
        print len(word2comps),word2comps
        print len(neithercomps),neithercomps


if __name__=='__main__':
    parameters=configure(sys.argv)
    filepath=os.path.join(parameters['parentdir'],parameters['datadir'],parameters['datafile'])

    myAnalyser=Analyser(filepath)
    myAnalyser.analyse()

