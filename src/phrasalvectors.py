__author__ = 'juliewe'

import sys,os,math

from conf import configure
from collocate import untag
import re



class VectorExtractor:



    def __init__(self,config):

        self.parameters=config
        self.datadir=os.path.join(self.parameters['parentdir'],self.parameters['datadir'])
        self.altdatadir=os.path.join(self.parameters['parentdir'],self.parameters['altdatadir'])
        #self.entrydict={}
        self.collocdict={}
        #self.headdict={}
        self.featdict={}
        self.featdict['left']={}  #features of leftmost constituent i.e., features of adjectives
        self.featdict['right']={}  #features of rightmost constituent i.e., features of nouns
        self.featuretotal={'left':0,'right':0}

        self.deppath = os.path.join(self.datadir,self.parameters['depfile']) #for first POS (e.g., J in ANcompounds)
        if self.parameters['adjlist']:
            self.altdeppath = os.path.join(self.parameters['parentdir'],self.parameters['altdatadir'],self.parameters['altdepfile'])  #for other POS (e.g., N in ANcompounds)
            self.deppaths=[self.deppath,self.altdeppath]
        else:
            self.deppaths=[self.deppath]
        self.phrasal_path = self.deppath+'_'+self.parameters['featurematch']+'_phrases'
        self.constituent_path=self.deppath+'_'+self.parameters['featurematch']+'_constituents'
        #self.nfmod_path=self.deppath+'_'+self.parameters['featurematch']+'_NFmods'
        #self.headvectordict={}
        self.worddict={}
        self.worddict['left']={}
        self.worddict['right']={}
        self.positions=['left','right']# #for adjectives and nouns - have corresponding dependency files in self.deppaths
        self.fmatch=[self.parameters['featurematch'],self.parameters['inversefeatures'][self.parameters['featurematch']]] #for corresponding features to match in these files
        self.tags=['J','N']
        self.miroflag=self.parameters['miroflag']

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
                if self.miroflag:
                    #AN:black/J_swan/N
                    parts=collocate.split(':')
                    words=parts[1].split('_')
                    left=words[0]
                    right=words[1]
                    dep=self.parameters['featurematch']
                    collocate=left+':'+dep+':'+right
                    self.collocdict[collocate]=1
                else:
                    if len(fields)>1:
                        self.collocdict[collocate]=fields[2]#store PMI
                    else:
                        self.collocdict[collocate]=1
                    parts=collocate.split(':')
                    left=parts[0] #black/J
                    right=parts[2] #swan/N
                self.worddict['left'][left]=self.worddict['left'].get(left,0)+1
                self.worddict['right'][right]=self.worddict['right'].get(right,0)+1
                linesread+=1
            print "Read "+str(linesread)+" lines"




    def loadfeaturecounts(self):

        filepaths = [os.path.join(self.datadir,self.parameters['featurefile']),os.path.join(self.altdatadir,self.parameters['featurefile'])]
        for i,filepath in enumerate(filepaths):
            with open(filepath,'r') as instream:
                print "Reading "+filepath
                linesread=0
                for line in instream:
                    fields=line.rstrip().split('\t')
                    feature=fields[0]
                    self.featdict[self.positions[i]][feature]=float(fields[1])
                    self.featuretotal[self.positions[i]]+=float(fields[1])
                    linesread+=1
                print "Read "+str(linesread)+" lines"

    def extractfromfile(self):


        with open(self.phrasal_path,'w') as outstream1:
            with open(self.constituent_path,'w') as outstream2:

                for i,deppath in enumerate(self.deppaths):  #go through adjs file then nouns file - if you don't want modifiers of modifier then just need second run through nouns file
                    with open(deppath,'r') as instream:
                        print "Reading "+deppath
                        linesread=0

                        for line in instream:
                            linesread+=1
                            if linesread%100000==0:
                                print "Read "+str(linesread)+" lines"
                                if self.parameters['testing'] and linesread%1000000:break
                            fields=line.rstrip().split('\t')
                            entry=fields[0]  #e.g., "African/J"
                            #(word,tag) =untag(entry)

                            if self.worddict[self.positions[i]].get(entry,0)>0:  #if we care about this word
                                newfields=self.depfilter(fields)  #filter to interesting dependencies
                                self.writeoutput(entry,newfields,outstream2,'')  #conventional dependency features (1st order)

                            for index,feature in enumerate(fields[1:]):  #get each feature and its position
                                parts = feature.split(':')  #split into feature type and word

                                if parts[0] == self.fmatch[i] and self.worddict[self.positions[i]].get(entry,0)>0: #correct feature (given file) and we care about the entry word
                                    phrase=entry+':'+feature
                                    newfields=fields[1:index+1]+fields[index+2:len(fields)]
                                    newfields=self.depfilter(newfields)
                                    self.writeoutput(phrase,newfields,outstream1,'')  #1st order phrasal dependencies of the entry in the context of the feature
                                    self.writeoutput(parts[1],newfields,outstream2,self.fmatch[(i+1)%2]+':') #2nd order dependencies of the feature word when used as this type of feature
                                   # self.writeoutput(entry+':'+parts[0],newfields.append(fields[index]),outstream2,'1st') #1st order dependencies of entry when it has this type of feature


    def depfilter(self,fields):
        newfields=[]

        for field in fields:
            parts=field.split(':')
            if parts[0] in parameters['deplist']:
                newfields.append(field)
        return newfields


    def writeoutput(self,head,features,outstream,tag=''):

        if len(features)>0:
            outstream.write(head)
            for feature in features:
                outstream.write('\t'+tag+feature)
            outstream.write('\n')



class FeatureVector:

    firstorderPATT = re.compile('([^:]+-[^:]+):(.*)')
    secondorderPATT = re.compile('([^:]+-[^:]+):([^:]+-[^:]+):(.*)')

    @staticmethod
    def strip(feat):
        parts=feat.split(':')
        res=parts[1]
        for part in parts[2:]:
            res=res+':'+part
        return res

    def __init__(self,word='',windows=False):

        self.featdict={}
        self.word=word
        self.total=0
        self.indict={}
        self.windows=windows

    def addfeats(self,fields):
        #assuming new format where features are labelled head and mod
        while len(fields)>0:
            field=fields.pop()
            self.featdict[field]=self.featdict.get(field,0)+1
            self.total+=1

    def addfeaturecounts(self,featurecounts):
        while len(featurecounts)>0:
            count=float(featurecounts.pop())
            feature=featurecounts.pop()
            self.featdict[feature]=count
            self.total+=count
    def findorder(self,feat):
        order=len(feat.split(':'))-1
        matchobj=FeatureVector.secondorderPATT.match(feat)
        if matchobj:
            order=2
        else:
            matchobj=FeatureVector.firstorderPATT.match(feat)
            if matchobj:
                order=1
            else:
                print "Warning: unmatched feature: ",feat,str(order)

        return order

    def finddiff(self,avector):
        #return (positive) difference between self and avector
        #self will be constituent vector, avector is phrase vector
        #need to check 1st and 2nd order dependencies

        result=FeatureVector(self.word+'!'+avector.word)
        for feat in self.featdict.keys():
            order=self.findorder(feat)

            if order ==1:
                if avector.word.split(':')[0] == self.word: #1st order features match between word and left constituent
                    remove=avector.featdict.get(feat,0)
                else:
                    remove =0
            elif order ==2:
                if avector.word.split(':')[2] == self.word: #2nd order features match between word and right constituent

                    fofeat=FeatureVector.strip(feat)
                         #strip off 1st bit of feature name as 2nd order constituent feature matches 1st order phrase feature
                    remove=avector.featdict.get(fofeat,0)
                else:
                    remove=0
            else:
                print "Warning: not expecting features of order higher than 2 - assuming 2nd order: ", feat, str(order)
                if avector.word.split(':')[2] == self.word:
                    fofeat=FeatureVector.strip(feat)
                    remove=avector.featdict.get(fofeat,0)
                else:
                    remove=0

            score=self.featdict[feat]-remove
            if score > 0:
                result.featdict[feat]=score
                result.total+=score
            #else:
             #   print "Removing feature "+feat+':'+str(self.featdict[feat])+':'+str(avector.featdict.get(feat,0))
        return result

    def finalise(self,featdict1,featdict2,outstream):
        #basically just filters low frequency features and then writes to file

        oldwidth=len(self.featdict.keys())
        for feature in self.featdict.keys():
            order=self.findorder(feature)
            if order>1: #check these in the other featdict
                feattot=featdict2.get(FeatureVector.strip(feature))
            else: #check first order features in their featdict
                feattot=featdict1.get(feature,0)
            if feattot>0:
                self.indict[feature]=self.featdict[feature]  #still need to check feattot>0 to ensure that the feature wasn't filtered out on low frequency


        newwidth=len(self.indict.keys())
        #print self.word,oldwidth,newwidth
        if newwidth==0:
            print self.featdict
        self.featdict=dict(self.indict)
        self.indict={}

        self.writetofile(outstream)


    def writetofile(self,outstream):
        if len(self.featdict.keys())>0:
            outstream.write(self.word)
            for feature in self.featdict.keys():
                outstream.write('\t'+feature+'\t'+str(self.featdict[feature]))
            outstream.write('\n')
        else:
            print "Warning: no vector for "+self.word

class VectorBuilder(VectorExtractor):

    flags={'left':'right','right':'left'}

    def finalise(self,currentvector):
        self.inwordflag='none'
        if self.flag=='constituents':
            if self.worddict['left'].get(currentvector.word,0)>0:
                self.inwordflag='left'
            elif self.worddict['right'].get(currentvector.word,0)>0:self.inwordflag='right'
            if self.inwordflag !='none':
                print "Doing differences for ",currentvector.word,str(self.inwordflag)
                self.makedifferences(currentvector)  #do differences with phrases
        else:  #self.flag=="phrases"
            #print "Checking "+currentvector.word
            if self.collocdict.get(currentvector.word,0)>0:self.inwordflag='left'
            else:
                parts=currentvector.word.split(':')
                if len(parts)>2:
                    invphrase=parts[2]+':'+self.parameters['inversefeatures'][parts[1]]+':'+parts[0]
                    #print "Checking "+invphrase
                    if self.collocdict.get(invphrase,0)>0:self.inwordflag='right'
            if self.inwordflag!='none':
                self.phrasevectordict[currentvector.word]=currentvector  #store phrasevector for differences on constituents run
                #print "storing vector for "+currentvector.word


        if self.inwordflag !='none':
            #print "Outputting vector for "+currentvector.word
            currentvector.finalise(self.featdict[self.inwordflag],self.featdict[VectorBuilder.flags[self.inwordflag]],self.outstream) #finalise and output currentvector
        else:
            #print "Ignoring vector for "+currentvector.word
            pass
        return

    def build(self,filepath,flag):


        if flag=='phrase':
            self.phrasevectordict={}
        else:
            diffpath = self.constituent_path+'_diff'
            self.diffstream=open(diffpath,'w')

        outpath=filepath+'_vectors'
        currentvector=FeatureVector()
        self.flag=flag

        with open(filepath,'r') as instream:
            print "Reading "+filepath
            with open(outpath,'w') as self.outstream:
                linesread=0
                for line in instream:
                    linesread+=1
                    if linesread%100000==0:
                        print "Read "+str(linesread)+" lines"
                        #if self.parameters['testing']:
                        if self.parameters['testing'] and flag == 'constituents':
                            exit()

                    fields=line.rstrip().split('\t')
                    thisword=fields[0]
                    #if flag=='mod':
                    #    thisword=thisword.split(':')[0]
                    if thisword==currentvector.word:
                        currentvector.addfeats(fields[1:])
                    else:
                        #finish off last vector
                        self.finalise(currentvector)

                        #start new vector with current line
                        if flag=='constituents':
                            thisword=thisword.split(':')[0]
                        currentvector=FeatureVector(thisword)
                        currentvector.addfeats(fields[1:])

                #do last vector
                self.finalise(currentvector)


    def makedifferences(self,constituent_vector):
        #black/J:amod-HEAD:swan  => black in context of swan
        #swan/N:amod-DEP:black  => swan in context of black
        #non-functional is now just 1st order dependencies so don't need to do this separately
        #need to find all phrases in self.collocdict, subtract phrase and inverse from constituent and then finalise

        constituent = constituent_vector.word
        mycollocs=[]
        for colloc in self.collocdict.keys():
            parts=colloc.split(':')
            if (self.inwordflag=='left' and parts[0]==constituent) or (self.inwordflag=='right' and parts[2]==constituent):
                mycollocs.append(colloc)
        print mycollocs
        for colloc in mycollocs:
            parts=colloc.split(':')
            invcolloc=parts[2]+':'+self.parameters['inversefeatures'][parts[1]]+':'+parts[0]
            diffvector=constituent_vector.finddiff(self.phrasevectordict.get(colloc,FeatureVector(colloc)))  #swan!black swan - could be a zero vector
            diffvector=diffvector.finddiff(self.phrasevectordict.get(invcolloc,FeatureVector(invcolloc)))    #swan!swan black - could be a zero vector
            diffvector.finalise(self.featdict[self.inwordflag],self.featdict[VectorBuilder.flags[self.inwordflag]],self.diffstream)

        return



def extract(parameters):
    if parameters['windows']:
        print "Windows not supported currently"
        return
        #myExtractor=WindowVectorExtractor(parameters)
    else:
        myExtractor=VectorExtractor(parameters)
    myExtractor.loadphrases()
    myExtractor.extractfromfile()

def gobuild(parameters):

    myBuilder=VectorBuilder(parameters)
    myBuilder.loadphrases()
    myBuilder.loadfeaturecounts()

    myBuilder.build(myBuilder.phrasal_path+'.sorted','phrase') #do phrases first so both can be taken away from a single constituent
    myBuilder.build(myBuilder.constituent_path+'.sorted','constituents') #constituents formally mod


if __name__ == '__main__':
    parameters = configure(sys.argv)
    print parameters
    if parameters['extract']:
        extract(parameters)
    if parameters['build']:
        gobuild(parameters)