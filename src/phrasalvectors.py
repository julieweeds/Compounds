__author__ = 'juliewe'

import sys,os,math

from conf import configure
from collocate import untag



class VectorExtractor:

    def __init__(self,config):

        self.parameters=config
        self.datadir=os.path.join(self.parameters['parentdir'],self.parameters['datadir'])
        self.altdatadir=os.path.join(self.parameters['parentdir'],self.parameters['altdatadir'])
        self.entrydict={}
        self.collocdict={}
        self.headdict={}
        self.featdict={}
        self.featuretotal=0
        self.deppath = os.path.join(self.datadir,self.parameters['depfile']) #for first POS (e.g., J in ANcompounds)
        if self.parameters['adjlist']:
            self.altdeppath = os.path.join(self.parameters['parentdir'],self.parameters['altdatadir'],self.parameters['altdepfile'])  #for other POS (e.g., N in ANcompounds)
            self.deppaths=[self.deppath,self.altdeppath]
        else:
            self.deppaths=[self.deppath]
        self.phrasal_path = self.deppath+'_'+self.parameters['featurematch']+'_phrases'
        self.modifier_path=self.deppath+'_'+self.parameters['featurematch']+'_modifiers'
        self.nfmod_path=self.deppath+'_'+self.parameters['featurematch']+'_NFmods'
        self.headvectordict={}


    def loadphrases(self):
        if self.parameters['adjlist']:
            filename='multiwords.'+self.parameters['usefile']
        else:
            filename=self.parameters['collocatefile']
        filepath = os.path.join(self.datadir,filename)
        with open(filepath,'r') as instream:
            print "Reading "+filepath
            linesread=0
            for line in instream:
                fields=line.rstrip().split('\t')
                collocate=fields[0] #black/J:amod-HEAD:swan
                self.collocdict[collocate]=fields[2]  #store PMI
                parts=collocate.split(':')
                feature=parts[1]+':'+parts[2] #amod-HEAD:swan
                #self.entrydict[parts[0]]+= self.entrydict.get(parts[0],0)
                #head = untag(parts[0])[0] #black
                head = parts[0] #black/J
                self.headdict[head]=self.headdict.get(head,0)+1
                self.entrydict[feature]=self.entrydict.get(feature,0)+1
                linesread+=1
            print "Read "+str(linesread)+" lines"

        #print self.headdict.get('childhood',0)
        #print self.entrydict.get('nn-DEP:childhood',0)
        #exit()


    def loadfeaturecounts(self):
        if self.parameters['adjlist']:
            #features of ANcompounds are features of Ns
            filepath = os.path.join(self.altdatadir,self.parameters['featurefile'])

        else:
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
        if self.parameters['adjlist']:

            filepath=os.path.join(self.altdatadir,self.parameters['freqfile'])
        else:
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

    def cacheheadvectors(self):

        filepath=os.path.join(self.datadir,self.parameters['freqfile']+'_headvectors')
        with open(filepath,'w') as outstream:
            print "Writing "+filepath

            for featurevector in self.headvectordict.values():
                featurevector.finalise(self.featdict,self.featuretotal,outstream)



    def extractfromfile(self):


        nfmodifier_path=self.nfmod_path

        phrasal_path=self.phrasal_path
        modifier_path=self.modifier_path
        #print self.headdict

        for i,deppath in enumerate(self.deppaths):
            with open(deppath,'r') as instream:
                if i==0:code='w'
                else:code='a'
                with open(phrasal_path,code) as outstream1:
                    with open(modifier_path,code) as outstream2:
                        with open(nfmodifier_path,code) as outstream3:
                            print "Reading "+deppath
                            linesread=0
                            for line in instream:
                                linesread+=1
                                if linesread%100000==0:
                                    print "Read "+str(linesread)+" lines"
                                    if self.parameters['testing']:break
                                fields=line.rstrip().split('\t')
                                word =untag(fields[0])[0]
                                if self.parameters['nfmod'] and i == 0:
                                    if self.headdict.get(fields[0],0)>0:
                                        newfields=self.depfilter(fields)
                                        self.writeoutput(word+'/J',newfields,outstream3,'f')
                                for index,feature in enumerate(fields[1:]):
                                    parts = feature.split(':')
                                    #invertedfeature=self.parameters['featurematch']+':'+word
                                    #print invertedfeature,self.entrydict.get(invertedfeature,0)
                                    #if parts[0] == self.parameters['featurematch'] and self.entrydict.get(feature,0)>0:  #for NN compounds
                                    if parts[0] == self.parameters['featurematch'] and self.headdict.get(fields[0],0)>0: #for ANs, extract all phrases with word (J) leading
                                        phrase=fields[0]+':'+feature
                                        newfields=fields[1:index+1]+fields[index+2:len(fields)]
                                        newfields=self.depfilter(newfields)
                                        self.writeoutput(phrase,newfields,outstream1,'f')
                                        self.writeoutput(fields[0]+':'+self.parameters['featurematch'],newfields,outstream2,'f')
                                    #elif parts[0] == self.parameters['inversefeatures'][self.parameters['featurematch']] and self.entrydict.get(invertedfeature,0)>0:
                                    elif parts[0] == self.parameters['inversefeatures'][self.parameters['featurematch']] and self.headdict.get(parts[1]+'/J',0)>0:
                                        #print "Found inverse match"
                                        phrase=parts[1]+'/J:'+self.parameters['featurematch']+':'+word
                                        newfields=fields[1:index+1]+fields[index+2:len(fields)]
                                        newfields=self.depfilter(newfields)
                                        self.writeoutput(phrase,newfields,outstream1,'b')
                                        if i==1:
                                            self.writeoutput(parts[1]+'/J:'+self.parameters['featurematch'],newfields,outstream2,'b')


    def depfilter(self,fields):
        newfields=[]

        for field in fields:
            parts=field.split(':')
            if parts[0] in parameters['deplist']:
                newfields.append(field)
        return newfields


    def writeoutput(self,head,features,outstream,tag='f'):

        if len(features)>0:
            outstream.write(head)
            for feature in features:
                outstream.write('\t'+feature+'\t'+tag)
            outstream.write('\n')


class WindowVectorExtractor(VectorExtractor):



    def extractfromfile(self):
            #needs updating for windows with a single dependency path
            self.deppaths=[self.deppath]  # single file for dependencies

            nfmodifier_path=self.nfmod_path #output paths
            phrasal_path=self.phrasal_path
            modifier_path=self.modifier_path
            #print self.headdict

            for i,deppath in enumerate(self.deppaths):
                with open(deppath,'r') as instream:
                    if i==0:code='w'
                    else:code='a'
                    with open(phrasal_path,code) as outstream1:
                        with open(modifier_path,code) as outstream2:
                            with open(nfmodifier_path,code) as outstream3:
                                print "Reading "+deppath
                                linesread=0
                                for line in instream:
                                    linesread+=1
                                    if linesread%100000==0:
                                        print "Read "+str(linesread)+" lines"
                                        if self.parameters['testing']:break
                                    fields=line.rstrip().split('\t')
                                    #(word,pos) =untag(fields[0])
                                    if self.headdict.get(fields[0],0)>0:  #POS tagged
                                        newfields=self.depfilter(fields)
                                        self.writeoutput(fields[0],newfields,outstream3,'f')
                                        for index,feature in enumerate(fields[1:]):
                                            parts = feature.split(':')
                                            if parts[0] == self.parameters['featurematch']: #for ANs, extract all phrases with word (J) leading
                                                phrase=fields[0]+':'+feature
                                                newfields=fields[1:index+1]+fields[index+2:len(fields)]
                                                newfields=self.depfilter(newfields)
                                                newfields=self.headfilter(newfields,parts[1])
                                                self.writeoutput(phrase,newfields,outstream1,'f')
                                                self.writeoutput(fields[0]+':'+self.parameters['featurematch'],newfields,outstream2,'f')

    def headfilter(self,fields,head):
        #to remove 1 window occurrence of head from phrasal vector
        newfields=[]
        found=0
        for field in fields:
            parts=field.split(':')
            if parts[1]==head:
                found+=1
                if found>1:
                    newfields.append(field)
            else:
                newfields.append(field)
        return newfields

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
            if type=='head' or type=='f':
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
            if type=='head' or type =='f':
                remove = avector.headfeatdict.get(feat,0)
            elif type=='mod' or type =='b':
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
        else:
            print "Warning: no vector for "+self.word

class VectorBuilder(VectorExtractor):

    def build(self,filepath,flag):


        if flag=='mod':
            self.modvectordict={}
        #elif flag=='nfmod':
            #self.nfmodvectordict={}
        else:
            moddiffpath=self.deppath+'_moddiff'  #for functional vectors
            headdiffpath=self.deppath+'_headdiff'  #for non-functional vectors (i.e., plain vectors)
            #nfmoddiffpath=self.deppath+'_nfmoddiff'
            moddiffstream=open(moddiffpath,'w')  #functional
            headdiffstream=open(headdiffpath,'w')  #non-functional (both words)
            #nfmoddiffstream=open(nfmoddiffpath,'w')
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
                    if flag=='mod':
                        thisword=thisword.split(':')[0]
                    if thisword==currentvector.word:
                        currentvector.addfeats(fields[1:])
                    else:
                        if currentvector.word in self.headdict.keys() or currentvector.word in self.collocdict.keys():
                            if flag=='mod':
                                self.modvectordict[currentvector.word]=currentvector
                            elif flag=='nfmod':
                                self.headvectordict[currentvector.word]=currentvector
                            else:
                                self.makedifferences(currentvector,moddiffstream,headdiffstream)
                            currentvector.finalise(self.featdict,self.featuretotal,outstream)

                        #else:

                            #print "Ignoring word "+currentvector.word
                        if flag=='mod':
                            thisword=thisword.split(':')[0]
                        currentvector=FeatureVector(thisword)
                        currentvector.addfeats(fields[1:])
                if currentvector.word in self.headdict.keys() or currentvector.word in self.collocdict.keys():
                    #do last vector
                    if flag=='mod':
                        self.modvectordict[currentvector.word]=currentvector
                    elif flag=='nfmod':
                        self.headvectordict[currentvector.word]=currentvector
                    else:
                        self.makedifferences(currentvector,moddiffstream,headdiffstream)
                    currentvector.finalise(self.featdict,self.featuretotal,outstream)


    def makedifferences(self,phrasevector,mstream,hstream):
        #black/J:amod-HEAD:swan  => want functional vector for black and non-functional for black and swan
        phrase=phrasevector.word.split(':')
        feature=phrase[1]+':'+phrase[2] #feature = 'amod-HEAD:swan'
        #try:
        #    target=untag(phrase[0])[0]  #head = 'black'
        #except:
        #    print "Warning: unable to untag "+phrase[0]
        #    target=phrase[0]
        target=phrase[0]

        moddiffvector=self.modvectordict[target].finddiff(phrasevector,type='all')#f modifier
        moddiffvector.finalise(self.featdict,self.featuretotal,mstream)
        headdiffvector=self.headvectordict[target].finddiff(phrasevector,type='f')#nf modifier
        headdiffvector.finalise(self.featdict,self.featuretotal,hstream)
        headdiffvector=self.headvectordict[phrase[2]].finddiff(phrasevector,type='b')#nf head
        headdiffvector.finalise(self.featdict,self.featuretotal,hstream)
        return


def extract(parameters):
    if parameters['windows']:
        myExtractor=WindowVectorExtractor(parameters)
    else:
        myExtractor=VectorExtractor(parameters)
    myExtractor.loadphrases()
    myExtractor.extractfromfile()

def gobuild(parameters):
    myBuilder=VectorBuilder(parameters)
    myBuilder.loadphrases()
    myBuilder.loadfeaturecounts()
    myBuilder.loadheadvectors()
    myBuilder.cacheheadvectors()
    myBuilder.build(myBuilder.nfmod_path+'.sorted','nfmod')
    myBuilder.build(myBuilder.modifier_path+'.sorted','mod')
    myBuilder.build(myBuilder.phrasal_path+'.sorted','phrase')

if __name__ == '__main__':
    parameters = configure(sys.argv)

    if parameters['extract']:
        extract(parameters)
    if parameters['build']:
        gobuild(parameters)