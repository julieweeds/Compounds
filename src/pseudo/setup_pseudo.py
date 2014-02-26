__author__ = 'juliewe'

from conf import configure
import sys,os,random

class FeatureVector:
    deps=['nn-DEP']

    def __init__(self,name,featuredict={},features=[]):
        self.name=name
        nameparts=name.split(':')
        if len(nameparts)>1:
            self.type=str(nameparts[1])
        else:
            self.type='word'
        self.empty=True
        self.reversedict={}
        if self.type in FeatureVector.deps:
            self.featuredict=dict(featuredict)
            self.addfeatures(features)
            if len(self.featuredict.keys())>0:
                self.empty=False
        else:
            self.featuredict={}
            self.empty=True

    def addfeatures(self,featurelist):

        while(len(featurelist)>0):
            try:
                score=int(featurelist.pop())
                feature=featurelist.pop()
                forder=len(feature.split(':'))-1
                if forder<2: #ignore any higher order features
                    self.featuredict[feature]=score
            except Exception:
                print "Length of featurelist for "+self.name+" is not even in length"

    def toString(self):

        mystring=self.name
        for feature in self.featuredict.keys():
            mystring+="\t"+feature+"\t"+str(self.featuredict[feature])
        mystring+="\n"
        return mystring

    def writeout(self,outstream):

        outstream.write(self.toString())

    def filter(self,avector):

        #newdict={}
        for feature in self.featuredict.keys():
            trainingscore = avector.featuredict.get(feature,-1)
            if trainingscore>-1:
                self.featuredict.__delitem__(feature)

        return

    def findequals(self):
        for (feature,score) in self.featuredict.items():
            if self.reversedict.get(score,None)==None:
                listsofar=[]
            else:
                listsofar=self.reversedict[score]
            listsofar.append(feature)
            self.reversedict[score]=listsofar

    def findmatch(self,feature,trainvector):
        score=self.featuredict.get(feature,0)
        match=feature
        if score>0:
            possmatches=self.reversedict[score]

            while len(possmatches)>0 and match==feature:
                #print feature,possmatches, score
                random.shuffle(possmatches)
                match=possmatches[0]
                possmatches=possmatches[1:]
                if match in trainvector.featuredict.keys():
                    match=feature
                    print "Discarded match due to presence with phrase in training: "+match
            if match==feature:
                possmatches=[]
                for i in range(9*score/10,10*score/9,1):
                    possmatches+=self.reversedict.get(i,[])
                #print possmatches
                while len(possmatches)>0 and match==feature:
                    random.shuffle(possmatches)
                    match=possmatches[0]
                    possmatches=possmatches[1:]
                    if match in trainvector.featuredict.keys():
                        match=feature
                        print "Discarded match due to presence with phrase in training: "+match

        else:
            match=feature #may happen that feature doesn't occur with head in training data
            print feature+" doesn't occur with "+self.name
        #print match
        return match

    def makepairs(self,headvector,trainvector,outstream):

        for feature in self.featuredict.keys():
            match=headvector.findmatch(feature,trainvector)
            if match!=feature:
                outstream.write(self.name+'\t'+feature+'\t'+match+'\n')

class PseudoBuilder:

    def __init__(self,parameters):

        self.parameters=parameters
        FeatureVector.deps=self.parameters['deps']
        self.trainingvectors={}
        self.testvectors={}
        self.constituentvectors={}
        self.parameters['vectorfiles']['filtered']=self.parameters['vectorfiles']['test']+'.filtered'

    def filter(self):

        self.trainingvectors=self.loadvectors('train')
        self.testvectors=self.loadvectors('test')
        self.filtertestvectors()
        return

    def loadvectors(self,type):
        vectors={}
        inputfile= os.path.join(self.parameters['compdatadir'],self.parameters['vectorfiles'][type])
        print "Processing "+inputfile
        with open(inputfile,'r') as instream:

            for line in instream:
                fields=line.rstrip().split('\t')

                avector=FeatureVector(fields[0],features=fields[1:])
                if not avector.empty:
                    vectors[fields[0]]=avector
        print "Loaded "+str(len(vectors.keys()))+" vectors"
        if self.parameters['testing']:
            print vectors.keys()

        return vectors


    def filtertestvectors(self):
        outfile=os.path.join(self.parameters['compdatadir'],self.parameters['vectorfiles']['filtered'])

        with open(outfile,'w') as outstream:
            print "Writing "+outfile
            for phrase in self.testvectors.keys():
                trainingvector=self.trainingvectors.get(phrase,None)
                if trainingvector != None:
                    self.testvectors[phrase].filter(trainingvector)
                self.testvectors[phrase].writeout(outstream)


        return

    def findequals(self):

        for cvector in self.constituentvectors.values():
            cvector.findequals()
            #if self.parameters['testing']:
             #   print cvector.name, cvector.reversedict.keys()


    def setup(self):

        outfile=os.path.join(self.parameters['compdatadir'],'pseudopairs')
        with open(outfile,'w') as outstream:
            self.testvectors=self.loadvectors('filtered')
            self.constituentvectors=self.loadvectors('constituents')
            self.trainingvectors=self.loadvectors('train')
            self.findequals()
            for testvector in self.testvectors.values():
                head=testvector.name.split(':')[0]
                testvector.makepairs(self.constituentvectors[head],self.trainingvectors[testvector.name],outstream)
                #if self.parameters['testing']:
                 #   exit()
        return


if __name__=='__main__':

    parameters=configure(sys.argv)
    random.seed(parameters['seed'])

    myBuilder = PseudoBuilder(parameters)
    if parameters['filter']:
        myBuilder.filter()
    elif parameters['setup']:
        myBuilder.setup()