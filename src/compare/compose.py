__author__ = 'juliewe'

import conf,sys,os,math
import scipy.stats as stats
import numpy as np

class TaggingError(Exception):
    pass

def untag(astring,achar='/'):
    parts=astring.split(achar)
    if len(parts)==2:
        return(parts[0],parts[1])
    else:
        raise TaggingError

class FeatureVector:

    def __init__(self,signifier,features=[],fdict={}):
        self.signifier=signifier
        self.featuredict=dict(fdict)
        self.computedlength=False
        self.length=-1
        self.sum=-1
        while len(features)>0:
            score=float(features.pop())
            feat=features.pop()
            if score>0:
                self.featuredict[feat]=score
        self.normalised=False

    def add(self,avector):
        newvector=FeatureVector(self.signifier+'+'+avector.signifier,features=[],fdict=self.featuredict)

        for feature in avector.featuredict.keys():
            newvector.featuredict[feature]=newvector.featuredict.get(feature,0)+avector.featuredict[feature]
        return newvector

    def max(self,avector):
        newvector=FeatureVector(self.signifier+'@MAX@'+avector.signifier,features=[],fdict=self.featuredict)
        for feature in avector.featuredict.keys():
            newvector.featuredict[feature]=max(self.featuredict.get(feature,0),avector.featuredict[feature])

        return newvector

    def mult(self,avector):
        newvector=FeatureVector(self.signifier+'*'+avector.signifier,features=[],fdict={})

        for feature in self.featuredict.keys():
            if avector.featuredict.get(feature,0)>0:
                newvector.featuredict[feature]=self.featuredict[feature]*avector.featuredict[feature]

        return newvector

    def min(self,avector):
        newvector=FeatureVector(self.signifier+'@MIN@'+avector.signifier,features=[],fdict={})

        for feature in self.featuredict.keys():
            if avector.featuredict.get(feature,0)>0:
                newvector.featuredict[feature]=min(self.featuredict[feature],avector.featuredict.get(feature,0))
        #print newvector.signifier, len(newvector.featuredict.keys()), len(self.featuredict.keys()), len(avector.featuredict.keys())
        return newvector

    def selectright(self,avector):
        newvector=FeatureVector(self.signifier+'@h@'+avector.signifier,fdict=self.featuredict)
        return newvector

    def selectleft(self,avector):
        newvector=FeatureVector(self.signifier+'@m@'+avector.signifier,fdict=avector.featuredict)
        return newvector

    def weighted_recall(self,avector): #weighted recall#
        self.normalise()
        avector.normalise()
        num=0
        den=0
        for feature in avector.featuredict.keys():
            den += avector.featuredict[feature]
            if self.featuredict.get(feature)>0:
                num+=min(avector.featuredict[feature],self.featuredict.get(feature,0))
            #else:
            #    print "Not found "+feature
        #print str(den)
        if den>0:
            return num/den
        else:
            return 0

    def weighted_precision(self,avector):
        self.normalise()
        avector.normalise()
        return avector.weighted_recall(self)

    def recall(self,avector):
        num=0
        den=0
        for feature in avector.featuredict.keys():
            den+=1
            if self.featuredict.get(feature)>0:
                num+=1
        #print self.signifier, num, den
        if den>0:
            return float(num)/float(den)
        else:
            return 0

    def precision(self,avector):
        return avector.recall(self)

    def fscore(self,avector):
        rec=self.recall(avector)
        pre=self.precision(avector)
        if rec+pre > 0:
            return 2*rec*pre/(rec+pre)
        else:
            return 0

    def computelength(self):
        if self.computedlength:
            return self.length
        else:
            self.sum=0
            self.computedlength=True
            total=0
            for feat in self.featuredict.keys():
                score=self.featuredict[feat]
                total+=score*score
                self.sum+=score
            self.length=math.pow(total,0.5)
            return self.length
    def cosine(self,avector):
        total=0
        for feature in self.featuredict.keys():
            total+=self.featuredict[feature]*avector.featuredict.get(feature,0)

        if self.computelength()==0:
            if avector.computelength()==0:
                sim=1
            else:
                sim=0
        else:
            sim = total / (self.computelength() * avector.computelength())
        return sim

    def normalise(self):
        if self.normalised:
            return
        else:
            self.normalised=True
            self.computelength()
            for feat in self.featuredict.keys():
                self.featuredict[feat]=self.featuredict[feat]/self.sum

            self.sum=1.0
            return

    def transform(self,featdict,featuretotal):
        #transform raw featurecounts into ppmi values
        self.computelength()
        self.rawdict=dict(self.featuredict)
        self.featuredict={}
        for feature in self.rawdict.keys():
            feattot=featdict.get(feature,0)
            if feattot>0:
                ratio = (self.rawdict[feature]*featuretotal)/(self.sum*feattot)
                pmi = math.log(ratio)
                if pmi>0:
                    self.featuredict[feature] = math.log(ratio)
            else:
                print "Warning "+feature+" not in feature dict"
        self.computedlength=False
        self.computelength()

    def toString(self):
        res=self.signifier+'('+str(len(self.featuredict.keys()))+')'
        width=0
        for feat in self.featuredict.keys():
            #res+='\t'+feat+'\t'+str(self.featuredict[feat])
            if self.featuredict[feat]>0: width+=1
        res+='\t'+str(width)
        #res+='\n'
        return res


class Composer:

    def __init__(self,parameters):
        self.parameters=parameters
        self.collocdict={}
        self.rightdict={}
        self.leftdict={}
        if self.parameters['diff']:
            self.whoami=self.whoami+'.diff'
        else:
            self.whoami=self.whoami+'.nodiff'

        self.statsreq=True

        self.readcomps()
        self.makecaches()
        self.resultspath=os.path.join(self.parameters['datadir'],'results.csv')

    def inverse(self,colloc):
        try:
            parts = colloc.split(':')
            inverted = parts[2]+':'+self.parameters['inversefeatures'][parts[1]]+':'+parts[0]
            return inverted
        except IndexError:
            print "Error inverting "+colloc
            return colloc


    def readcomps(self):

        with open(self.parameters['mwpath'],'r') as instream:
            print "Reading "+self.parameters['mwpath']
            for line in instream:
                fields=line.rstrip().split('\t')
                self.collocdict[fields[0]]=float(fields[2])
                parts=fields[0].split(':')
                left = parts[0]
                right=parts[2]
                #print "mod: ",mod,"head: ",head
                self.leftdict[left]=self.leftdict.get(left,0)+1
                self.rightdict[right]=self.rightdict.get(right,0)+1


        print "Number of collocations is "+str(len(self.collocdict.keys()))
        print "Number of right heads is "+str(len(self.rightdict.keys()))
        print "Number of left modifiers is "+str(len(self.leftdict.keys()))
        self.collocorder=sorted(self.collocdict.keys())
        return

    def makecaches(self):

        self.parameters['phrasalcache']=os.path.join(self.parameters['datadir'],'phrasal.cache'+self.whoami)
        self.parameters['rightcache']=os.path.join(self.parameters['datadir'],'right.cache'+self.whoami)
        self.parameters['leftcache']=os.path.join(self.parameters['datadir'],'left.cache'+self.whoami)

        if not self.parameters['cached']:
            #phrasal
            vectordict={}

            with open(self.parameters['phrasalpath'],'r') as instream:
                print "Reading "+self.parameters['phrasalpath']
                linesread=0
                added=0
                for line in instream:
                    linesread+=1
                    fields=line.split('\t')

                    if self.collocdict.get(fields[0],-1)>-1:
                        vectordict[fields[0]]=line
                        added+=1
                    elif self.collocdict.get(self.inverse(fields[0]),-1)>-1:
                        vectordict[fields[0]]=line
                        added+=1
                    else:
                        #   print "Not added vector for "+fields[0]
                        pass
                    if self.parameters['testing'] and linesread%1000==0:print "Read "+str(linesread)+" lines and copying "+str(added)+" vectors"

                print "Read "+str(linesread)+" lines"
                print "Copying "+str(added)+" vectors"

            with open(self.parameters['phrasalcache'],'w') as outstream:
                for colloc in self.collocorder:
                    outstream.write(vectordict.get(colloc,'\n'))
                    outstream.write(vectordict.get(self.inverse(colloc),'\n'))

            vectordict={} #free memory
            #load constituents

            leftvectordict={}
            rightvectordict={}

            with open(self.parameters['constituentpath'],'r') as instream:
                print "Reading "+self.parameters['constituentpath']
                linesread=0
                added=0
                for line in instream:
                    linesread+=1
                    fields=line.rstrip().split('\t')
                    if self.parameters['diff']:
                        (headmatch,collocmatch,invmatch)=fields[0].split('!')
                        if self.leftdict.get(headmatch,-1)>-1:
                            leftvectordict[collocmatch]=line
                            rightvectordict[invmatch]=line
                            added+=2
                        elif self.rightdict.get(headmatch,-1)>-1:
                            rightvectordict[collocmatch]=line
                            leftvectordict[invmatch]=line
                            added+=2
                        else:
                            print "Warning: ignoring "+headmatch
                    else:
                        headmatch = fields[0]
                        if self.leftdict.get(headmatch,-1)>-1:
                            leftvectordict[headmatch]=line
                            added+=1
                        elif self.rightdict.get(headmatch,-1)>-1:
                            rightvectordict[headmatch]=line
                            added+=1
                        else:
                            print "Warning: ignoring "+headmatch
                print "Read "+str(linesread)+" lines and copied "+str(added)+" vectors"

            with open(self.parameters['leftcache'],'w') as leftstream:
                with open(self.parameters['rightcache'],'w') as rightstream:
                    for colloc in self.collocorder:
                        if self.parameters['diff']:
                            leftstream.write(leftvectordict[colloc])
                            rightstream.write(rightvectordict[colloc])
                        else:
                            parts=colloc.split(':')
                            left=parts[0]
                            right=parts[2]
                            leftstream.write(leftvectordict[left])
                            rightstream.write(rightvectordict[right])
                        #inverse collocation
                        inverted=self.inverse(colloc)
                        if self.parameters['diff']:
                            leftstream.write(leftvectordict[inverted])
                            rightstream.write(rightvectordict[inverted])
                        else:
                            parts=inverted.split(':')
                            left=parts[0]
                            right=parts[2]
                            leftstream.write(rightvectordict[left])
                            rightstream.write(leftvectordict[right])


    def loadfeaturefile(self):
        #read in feature totals for pmi calculations
        self.featdict={}
        self.featuretotal=0
        with open(self.parameters['featurepath'],'r') as instream:
            print "Reading "+self.parameters['featurepath']
            linesread=0
            for line in instream:
                fields=line.rstrip().split('\t')
                feature=fields[0]
                self.featdict[feature]=float(fields[1])
                self.featuretotal+=float(fields[1])
                linesread+=1
        print "Read "+str(linesread)+" lines"

        return

    def process(self):

        with open(self.parameters['phrasalcache'],'r') as phrasalstream:
            with open(self.parameters['leftcache'],'r') as leftstream:
                with open(self.parameters['rightcache'],'r') as rightstream:

                    xs=[]
                    ys=[]
                    phrases=[]
                    done=0
                    for line in phrasalstream:
                        phrasefields=line.rstrip().split('\t')
                        rightfields=rightstream.readline().rstrip().split('\t')
                        leftfields=leftstream.readline().rstrip().split('\t')
                        phraseVector=FeatureVector(phrasefields[0],phrasefields[1:])
                        rightVector=FeatureVector(rightfields[0],rightfields[1:])
                        leftVector=FeatureVector(leftfields[0],leftfields[1:])
                        if self.parameters['testing']:
                            print phraseVector.toString()
                            print rightVector.toString()
                            print leftVector.toString()
                        if self.parameters['pmi']:
                            rightVector.transform(self.featdict,self.featuretotal)
                            leftVector.transform(self.featdict,self.featuretotal)
                            phraseVector.transform(self.featdict,self.featuretotal)
                        else: #normalise to probabilities before composing
                            rightVector.normalise()
                            leftVector.normalise()
                        composedVector=self.compose(rightVector,leftVector)
                        if self.parameters['testing']:
                            print composedVector.toString()
                        if self.parameters['raw'] and not self.parameters['pmi']:
                            composedVector.transform(self.featdict,self.featuretotal)
                            phraseVector.transform(self.featdict,self.featuretotal)
                        if self.parameters['testing']:
                            print phraseVector.toString()
                            print rightVector.toString()
                            print leftVector.toString()
                            #print leftVector.featuredict
                            print composedVector.toString()

                        scores =self.compare(composedVector,phraseVector)
                        if self.parameters['testing']:
                            print scores

                        phrases.append(phrasefields[0])
                        xs.append(self.collocdict[phrasefields[0]])
                        ys.append(scores)
                        done+=1
                        if done % 1000 == 0:
                            print "Processed "+str(done)+" phrasal expressions"
                        if self.parameters['testing'] and done%3==0:
                            print "Processed "+str(done)+" phrasal expressions"
                            break
        self.computestats(xs,ys,phrases)

    def compose(self,right,left):
        compfunct=getattr(self,'_compose_'+self.parameters['compop'])
        #right.normalise()  #makes no difference to normalise vectors before composition
        #left.normalise()
        return compfunct(right,left)
    def compare(self,composed,phrasal):
        res=[]

        for metric in self.parameters['metric']:
            simfunct=getattr(self,'_compare_'+metric)
            res.append(simfunct(composed,phrasal))

        return res

    def writestats(self,xs,ys,phrases):
        if self.statsreq:
            statspath=os.path.join(parameters['datadir'],'stats'+self.whoami+'.csv')
            with open(statspath,'w') as outstream:
                for metric in self.parameters['metric']:
                    outstream.write(metric+',')
                outstream.write('\n')
                for phrase in phrases:
                    outstream.write(phrase+',')
                outstream.write('\n')
                for x in xs:
                    outstream.write(str(x)+',')
                outstream.write('\n')
                for i,metric in enumerate(self.parameters['metric']):
                    for y in ys:
                        outstream.write(str(y[i])+',')
                    outstream.write('\n')
        else:
            return

    def computestats(self,xs,ys,phrases):

        self.writestats(xs,ys,phrases)

        for i,metric in enumerate(self.parameters['metric']):
            total=0
            totalsquared=0
            zs=[]
            for y in ys:
                #print y
                z=y[i]
                zs.append(z)
                total+=z
                totalsquared+=z*z
            mean = total/len(zs)
            variance = totalsquared/len(zs)-mean*mean
            if variance>0:
                sd = math.pow(variance,0.5)
            else:
                sd=0
            print "Mean "+metric+" score is "+str(mean)+", sd is "+str(sd)

            if variance>0:
                correlation=stats.spearmanr(np.array(xs),np.array(zs))
            else:
                correlation=(float('nan'),float('nan'))
            print "Correlation with PMI is: ", correlation
            (c1,c2)=correlation
            with open(self.resultspath,'a') as outstream:
                outstream.write(parameters['usefile']+',')
                if parameters['left']:
                    outstream.write('funct,')
                else:
                    outstream.write('nofunct,')
                if parameters['diff']:
                    outstream.write('diff,')
                else:
                    outstream.write('nodiff,')
                if parameters['raw']:
                    if parameters['pmi']:
                        outstream.write('PPMI->compose,')
                    else:
                        outstream.write('compose->PPMI,')
                else:
                    outstream.write('ppmi,')
                outstream.write(parameters['compop']+',')
                outstream.write(metric+','+str(mean)+','+str(sd)+','+str(c1)+','+str(c2)+'\n')

        return

    def _compose_add(self,right,leftifier):
        return right.add(leftifier)

    def _compose_mult(self,right,leftifier):
        return right.mult(leftifier)

    def _compose_selectright(self,right,leftifier):
        return right.selectright(leftifier)

    def _compose_selectleft(self,right,leftifier):
        return right.selectleft(leftifier)
    def _compose_min(self,right,leftifier):
        return right.min(leftifier)

    def _compose_max(self,right,leftifier):
        return right.max(leftifier)

    def _compare_recall(self,hypothesis,target):
        return hypothesis.recall(target)

    def _compare_precision(self,hypothesis,target):
        return hypothesis.precision(target)

    def _compare_weighted_recall(self,hypothesis,target):
        return hypothesis.weighted_recall(target)

    def _compare_weighted_precision(self,hypothesis,target):
        return hypothesis.weighted_precision(target)

    def _compare_f(self,hypothesis,target):
        return hypothesis.fscore(target)

    def _compare_cosine(self,hypothesis,target):
        return hypothesis.cosine(target)

def go(parameters):
    myComposer=Composer(parameters)
    if parameters['testing']:
        exit(0)
    #working up to this point.  Need to change loadfeaturefile to load both featurefiles into left and right worddicts
    myComposer.loadfeaturefile()
    myComposer.process()


if __name__=='__main__':
    parameters=conf.configure(sys.argv)
    print "Metrics:",parameters['metric']
    print "FUNCT:",parameters['funct']
    print "DIFF:",parameters['diff']
    print "Composition Operation:",parameters['compop']
    go(parameters)

