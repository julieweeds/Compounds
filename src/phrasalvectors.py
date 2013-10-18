__author__ = 'juliewe'

import sys,os,math

from conf import configure
from collocate import untag



class VectorExtractor:

    def __init__(self,config):

        self.parameters=config
        self.datadir=os.path.join(self.parameters['parentdir'],self.parameters['datadir'])
        self.entrydict={}
        self.collocdict={}
        self.featdict={}
        self.featuretotal=0
        self.deppath = os.path.join(self.datadir,self.parameters['depfile'])
        self.phrasal_path = self.deppath+'_'+self.parameters['featurematch']+'_phrases'
        self.modifier_path=self.deppath+'_'+self.parameters['featurematch']+'_modifiers'


    def loadphrases(self):
        filepath = os.path.join(self.datadir,self.parameters['collocatefile'])
        with open(filepath,'r') as instream:
            print "Reading "+filepath
            linesread=0
            for line in instream:
                fields=line.rstrip().split('\t')
                collocate=fields[0]
                self.collocdict[collocate]=fields[2]
                parts=collocate.split(':')
                feature=parts[1]+':'+parts[2]
                #self.entrydict[parts[0]]+= self.entrydict.get(parts[0],0)
                self.entrydict[feature]=self.entrydict.get(feature,0)+1
                linesread+=1
            print "Read "+str(linesread)+" lines"


    def loadfeaturecounts(self):
        filepath = os.path.join(self.datadir,self.parameters['featurefile'])
        with open(filepath,'r') as instream:
            print "Reading "+filepath
            linesread=0
            for line in instream:
                fields=line.rstrip().split('\t')
                feature=fields[0]
                self.featdict[feature]=float(fields[1])
                self.featuretotal+=float(fields[1])
                linesread+=1
            print "Read "+str(linesread)+" lines"


    def extractfromfile(self):

        with open(self.deppath,'r') as instream:
            with open(self.phrasal_path,'w') as outstream1:
                with open(self.modifier_path,'w') as outstream2:
                    print "Reading "+self.deppath
                    linesread=0
                    for line in instream:
                        linesread+=1
                        if linesread%100000==0:
                            print "Read "+str(linesread)+" lines"
                            if self.parameters['testing']:exit()
                        fields=line.rstrip().split('\t')
                        word =untag(fields[0])[0]
                        for index,feature in enumerate(fields[1:]):
                            parts = feature.split(':')
                            invertedfeature=self.parameters['featurematch']+':'+word
                            print invertedfeature,self.entrydict.get(invertedfeature,0)
                            if parts[0] == self.parameters['featurematch'] and self.entrydict.get(feature,0)>0:
                                phrase=untag(fields[0])[0]+':'+feature
                                newfields=fields[1:index+1]+fields[index+2:len(fields)]
                                newfields=self.depfilter(newfields)
                                self.writeoutput(phrase,newfields,outstream1)
                                self.writeoutput(feature,newfields,outstream2)
                            elif parts[0] == self.parameters['inversefeatures'][self.parameters['featurematch']] and self.entrydict.get(invertedfeature,0)>0:
                                print "Found inverse match"
                                invertedfeature=self.parameters['featurematch']+word
                                phrase=parts[1]+':'+self.parameters['featurematch']+word
                                newfields=fields[1:index+1]+fields[index+2:len(fields)]
                                newfields=self.depfilter(newfields)
                                self.writeoutput(phrase,newfields,outstream1)
                                self.writeoutput(invertedfeature,newfields,outstream2)
    def depfilter(self,fields):
        newfields=[]

        for field in fields:
            parts=field.split(':')
            if parts[0] in parameters['deplist']:
                newfields.append(field)
        return newfields


    def writeoutput(self,head,features,outstream):

        if len(features)>0:
            outstream.write(head)
            for feature in features:
                outstream.write('\t'+feature)
            outstream.write('\n')


class FeatureVector:

    def __init__(self,word=''):

        self.featdict={}
        self.word=word
        self.total=0
        self.pmidict={}

    def addfeats(self,fields):
        for field in fields:
            self.featdict[field]=self.featdict.get(field,0)+1
            self.total+=1

    def finalise(self,allfeatdict,featuretotal,outstream):

        for feature in self.featdict.keys():
            feattot=allfeatdict.get(feature,0)
            if feattot>0:
                ratio = (self.featdict[feature]*featuretotal)/(self.total*feattot)
                pmi = math.log(ratio)
                if pmi>0:
                    self.pmidict[feature] = math.log(ratio)

        self.writetofile(outstream)
    def writetofile(self,outstream):
        if len(self.pmidict.keys())>0:
            outstream.write(self.word)
            for feature in self.pmidict.keys():
                outstream.write('\t'+feature+'\t'+str(self.pmidict[feature]))
            outstream.write('\n')
class VectorBuilder(VectorExtractor):

    def build(self,filepath):

        outpath=filepath+'_vectors'
        currentvector=FeatureVector()

        #print self.entrydict.keys()
        #print self.collocdict.keys()

        with open(filepath,'r') as instream:
            print "Reading "+filepath
            with open(outpath,'w') as outstream:
                linesread=0
                for line in instream:
                    linesread+=1
                    if linesread%100000==0:
                        print "Read "+str(linesread)+" lines"
                        if self.parameters['testing']:
                            exit()
                    fields=line.rstrip().split('\t')
                    thisword=fields[0]
                    if thisword==currentvector.word:
                        currentvector.addfeats(fields[1:])
                    else:
                        if currentvector.word in self.entrydict.keys() or currentvector.word in self.collocdict.keys():
                            currentvector.finalise(self.featdict,self.featuretotal,outstream)
                        else:
                            print "Ignoring word "+currentvector.word
                        currentvector=FeatureVector(thisword)
                        currentvector.addfeats(fields[1:])



def extract(parameters):
    myExtractor=VectorExtractor(parameters)
    myExtractor.loadphrases()
    myExtractor.extractfromfile()

def gobuild(parameters):
    myBuilder=VectorBuilder(parameters)
    myBuilder.loadphrases()
    myBuilder.loadfeaturecounts()
    myBuilder.build(myBuilder.phrasal_path+'.sorted')
    myBuilder.build(myBuilder.modifier_path+'.sorted')



if __name__ == '__main__':
    parameters = configure(sys.argv)

    if parameters['extract']:
        extract(parameters)
    if parameters['build']:
        gobuild(parameters)