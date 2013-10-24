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
        self.headdict={}
        self.featdict={}
        self.featuretotal=0
        self.deppath = os.path.join(self.datadir,self.parameters['depfile'])
        self.phrasal_path = self.deppath+'_'+self.parameters['featurematch']+'_phrases'
        self.modifier_path=self.deppath+'_'+self.parameters['featurematch']+'_modifiers'
        self.headvectordict={}


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
                head = untag(parts[0])[0]
                self.headdict[head]=self.headdict.get(head,0)+1
                self.entrydict[feature]=self.entrydict.get(feature,0)+1
                linesread+=1
            print "Read "+str(linesread)+" lines"

        #print self.headdict.get('childhood',0)
        #print self.entrydict.get('nn-DEP:childhood',0)
        #exit()


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


    def loadheadvectors(self):
        filepath=os.path.join(self.datadir,self.parameters['freqfile'])
        with open(filepath,'r') as instream:
            print "Reading "+filepath
            linesread=0
            loaded=0
            for line in instream:
                fields=line.rstrip().split('\t')
                try:
                    head=untag(fields[0])[0]
                    if self.headdict.get(head,self.entrydict.get(self.parameters['featurematch']+':'+head,0))>0:
                        #print "Loading head vector for "+head
                        loaded+=1
                        self.headvectordict[head]=FeatureVector(head)
                        self.headvectordict[head].addfeaturecounts(fields[1:])
                except:
                    print "Warning: unable to untag "+fields[0]
                linesread+=1
                if linesread%10000==0:print "Read "+str(linesread)+" lines"
            print "Loaded "+str(loaded)+" head vectors"

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
                            #print invertedfeature,self.entrydict.get(invertedfeature,0)
                            if parts[0] == self.parameters['featurematch'] and self.entrydict.get(feature,0)>0:
                                phrase=fields[0]+':'+feature
                                newfields=fields[1:index+1]+fields[index+2:len(fields)]
                                newfields=self.depfilter(newfields)
                                self.writeoutput(phrase,newfields,outstream1,'head')
                                self.writeoutput(feature,newfields,outstream2,'head')
                            elif parts[0] == self.parameters['inversefeatures'][self.parameters['featurematch']] and self.entrydict.get(invertedfeature,0)>0:
                                #print "Found inverse match"
                                phrase=parts[1]+'/N:'+self.parameters['featurematch']+':'+word
                                newfields=fields[1:index+1]+fields[index+2:len(fields)]
                                newfields=self.depfilter(newfields)
                                self.writeoutput(phrase,newfields,outstream1,'mod')
                                self.writeoutput(invertedfeature,newfields,outstream2,'mod')
    def depfilter(self,fields):
        newfields=[]

        for field in fields:
            parts=field.split(':')
            if parts[0] in parameters['deplist']:
                newfields.append(field)
        return newfields


    def writeoutput(self,head,features,outstream,tag):

        if len(features)>0:
            outstream.write(head)
            for feature in features:
                outstream.write('\t'+feature+'\t'+tag)
            outstream.write('\n')


class FeatureVector:

    def __init__(self,word=''):

        self.featdict={}
        self.headfeatdict={}
        self.word=word
        self.total=0
        self.pmidict={}

    def addfeats(self,fields):
        #assuming new format where features are labelled head and mod
        while len(fields)>0:
            type=fields.pop()
            field=fields.pop()
            self.featdict[field]=self.featdict.get(field,0)+1
            if type=='head':
                self.headfeatdict[field]=self.headfeatdict.get(field,0)+1
            self.total+=1

    def addfeaturecounts(self,featurecounts):
        while len(featurecounts)>0:
            count=float(featurecounts.pop())
            feature=featurecounts.pop()
            self.featdict[feature]=count
            self.total+=count

    def finddiff(self,avector,type='all'):
        #return (positive) difference between self and avector
        #type is 'head', 'mod' or 'all' to label type of self and therefore which features of avector you should be subtracting
        result=FeatureVector(self.word+'!'+avector.word)
        for feat in self.featdict.keys():
            if type=='head':
                remove = avector.headfeatdict.get(feat,0)
            elif type=='mod':
                remove = avector.featdict.get(feat,0)-avector.headfeatdict.get(feat,0)
            elif type=='all':
                remove = avector.featdict.get(feat,0)
            else:
                print "Warning: Unknown vector type "+type

            score=self.featdict[feat]-remove
            if score > 0:
                result.featdict[feat]=score
                result.total+=score
            #else:
             #   print "Removing feature "+feat+':'+str(self.featdict[feat])+':'+str(avector.featdict.get(feat,0))
        return result

    def finalise(self,allfeatdict,featuretotal,outstream):

        for feature in self.featdict.keys():
            feattot=allfeatdict.get(feature,0)
            if feattot>0:
                ratio = (self.featdict[feature]*featuretotal)/(self.total*feattot)
                pmi = math.log(ratio)
                if pmi>0:
                    self.pmidict[feature] = math.log(ratio)
                #else:
                #    print "Ignoring feature "+feature

        self.writetofile(outstream)
    def writetofile(self,outstream):
        if len(self.pmidict.keys())>0:
            outstream.write(self.word)
            for feature in self.pmidict.keys():
                outstream.write('\t'+feature+'\t'+str(self.pmidict[feature]))
            outstream.write('\n')
class VectorBuilder(VectorExtractor):

    def build(self,filepath,flag):

        if flag=='mod':
            self.modvectordict={}
        else:
            moddiffpath=self.deppath+'_moddiff'
            headdiffpath=self.deppath+'_headdiff'
            moddiffstream=open(moddiffpath,'w')
            headdiffstream=open(headdiffpath,'w')
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
                        if self.parameters['testing'] and flag == 'phrase':
                            exit()

                    fields=line.rstrip().split('\t')
                    thisword=fields[0]
                    if thisword==currentvector.word:
                        currentvector.addfeats(fields[1:])
                    else:
                        if currentvector.word in self.entrydict.keys() or currentvector.word in self.collocdict.keys():
                            if flag=='mod':
                                self.modvectordict[currentvector.word]=currentvector
                            else:
                                self.makedifferences(currentvector,moddiffstream,headdiffstream)
                            currentvector.finalise(self.featdict,self.featuretotal,outstream)

                        #else:

                            #print "Ignoring word "+currentvector.word
                        currentvector=FeatureVector(thisword)
                        currentvector.addfeats(fields[1:])
                if currentvector.word in self.entrydict.keys() or currentvector.word in self.collocdict.keys():
                    #do last vector
                    if flag=='mod':
                        self.modvectordict[currentvector.word]=currentvector
                    else:
                        self.makedifferences(currentvector,moddiffstream,headdiffstream)
                    currentvector.finalise(self.featdict,self.featuretotal,outstream)


    def makedifferences(self,phrasevector,mstream,hstream):
        phrase=phrasevector.word.split(':')
        mod=phrase[1]+':'+phrase[2]
        try:
            head=untag(phrase[0])[0]
        except:
            print "Warning: unable to untag "+phrase[0]
            head=phrase[0]

        moddiffvector=self.modvectordict[mod].finddiff(phrasevector,type='all')
        moddiffvector.finalise(self.featdict,self.featuretotal,mstream)
        headdiffvector=self.headvectordict[head].finddiff(phrasevector,type='head')
        headdiffvector.finalise(self.featdict,self.featuretotal,hstream)
        headdiffvector=self.headvectordict[phrase[2]].finddiff(phrasevector,type='mod')
        headdiffvector.finalise(self.featdict,self.featuretotal,hstream)
        return


def extract(parameters):
    myExtractor=VectorExtractor(parameters)
    myExtractor.loadphrases()
    myExtractor.extractfromfile()

def gobuild(parameters):
    myBuilder=VectorBuilder(parameters)
    myBuilder.loadphrases()
    myBuilder.loadfeaturecounts()
    myBuilder.loadheadvectors()
    myBuilder.build(myBuilder.modifier_path+'.sorted','mod')
    myBuilder.build(myBuilder.phrasal_path+'.sorted','phrase')




if __name__ == '__main__':
    parameters = configure(sys.argv)

    if parameters['extract']:
        extract(parameters)
    if parameters['build']:
        gobuild(parameters)