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
        while len(features)>0:
            score=float(features.pop())
            feat=features.pop()
            if score>0:
                self.featuredict[feat]=score

    def add(self,avector):
        newvector=FeatureVector(self.signifier+'+'+avector.signifier,features=[],fdict=self.featuredict)

        for feature in avector.featuredict.keys():
            newvector.featuredict[feature]=newvector.featuredict.get(feature,0)+avector.featuredict[feature]
        return newvector

    def mult(self,avector):
        newvector=FeatureVector(self.signifier+'*'+avector.signifier,features=[],fdict={})

        for feature in self.featuredict.keys():
            if avector.featuredict.get(feature,0)>0:
                newvector.featuredict[feature]=self.featuredict[feature]*avector.featuredict[feature]

        return newvector

    def selecthead(self,avector):
        newvector=FeatureVector(self.signifier+'@h@'+avector.signifier,fdict=self.featuredict)
        return newvector

    def selectmod(self,avector):
        newvector=FeatureVector(self.signifier+'@m@'+avector.signifier,fdict=avector.featuredict)
        return newvector

    def recall(self,avector):
        num=0
        den=0
        for feature in avector.featuredict.keys():
            den += avector.featuredict[feature]
            if self.featuredict.get(feature)>0:
                num+=avector.featuredict[feature]
            #else:
            #    print "Not found "+feature
        print str(den)
        if den>0:
            return num/den
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
            self.computedlength=True
            total=0
            for feat in self.featuredict.keys():
                score=self.featuredict[feat]
                total+=score*score
            self.length=math.pow(total,0.5)
            return self.length
    def cosine(self,avector):
        total=0
        for feature in self.featuredict.keys():
            total+=self.featuredict[feature]*avector.featuredict.get(feature,0)
        sim = total / (self.computelength() * avector.computelength())
        return sim

    def toString(self):
        res=self.signifier+'('+str(len(self.featuredict.keys()))+')'
#        for feat in self.featuredict.keys():
#            res+='\t'+feat+'\t'+str(self.featuredict[feat])
#        res+='\n'
        return res


class Composer:

    def __init__(self,parameters):
        self.parameters=parameters
        self.collocdict={}
        self.headdict={}
        self.moddict={}
        self.whoami='.'+self.parameters['compop']
        if self.parameters['mod']:
            self.whoami=self.whoami+".mod"
        else:
            self.whoami=self.whoami+'.nomod'
        if self.parameters['diff']:
            self.whoami=self.whoami+'.diff'
        else:
            self.whoami=self.whoami+'.nodiff'
        self.statsreq=True

        self.readcomps()
        self.makecaches()
        self.resultspath=os.path.join(self.parameters['datadir'],'results.csv')

    def readcomps(self):

        with open(self.parameters['mwpath'],'r') as instream:
            print "Reading "+self.parameters['mwpath']
            for line in instream:
                fields=line.rstrip().split('\t')
                self.collocdict[fields[0]]=float(fields[2])
                parts=fields[0].split(':')
                try:
                    head = untag(parts[0])[0]
                    mod=parts[2]
                    self.headdict[head]=self.headdict.get(head,0)+1
                    self.moddict[mod]=self.moddict.get(mod,0)+1
                except TaggingError:
                    print "Error untagging "+parts[0]

        print "Number of collocations is "+str(len(self.collocdict.keys()))
        print "Number of heads is "+str(len(self.headdict.keys()))
        print "Number of modifiers is "+str(len(self.headdict.keys()))
        self.collocorder=sorted(self.collocdict.keys())
        return

    def makecaches(self):

        self.parameters['phrasalcache']=os.path.join(self.parameters['datadir'],'phrasal.cache'+self.whoami)
        self.parameters['headcache']=os.path.join(self.parameters['datadir'],'head.cache'+self.whoami)
        self.parameters['modcache']=os.path.join(self.parameters['datadir'],'mod.cache'+self.whoami)

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
                        #else:
                        #   print "Not added vector for "+fields[0]
                    if self.parameters['testing'] and linesread%1000==0:print "Read "+str(linesread)+" lines and copying "+str(added)+" vectors"

                print "Read "+str(linesread)+" lines"
                print "Copying "+str(added)+" vectors"

            with open(self.parameters['phrasalcache'],'w') as outstream:
                for colloc in self.collocorder:
                    outstream.write(vectordict[colloc])



            #head
            vectordict={}
            #print self.headdict.keys()

            with open(self.parameters['headpath'],'r') as instream:
                print "Reading "+self.parameters['headpath']
                linesread=0
                added=0
                for line in instream:
                    linesread+=1
                    fields=line.split('\t')
                    try:
                        if self.parameters['diff']:
                            (headmatch,collocmatch)=untag(fields[0],'!')
                            isheadmatch=untag(collocmatch.split(':')[0])[0]

                        else:
                            headmatch=untag(fields[0])[0]
                            collocmatch=headmatch
                            isheadmatch=headmatch

                        if headmatch==isheadmatch and self.headdict.get(headmatch,0)>0:
                            vectordict[collocmatch]=line
                            added+=1
                    except TaggingError:
                        print "Ignoring "+fields[0]
                    #else:
                        #print "No match for "+headmatch
                    if self.parameters['testing'] and linesread%1000==0:print "Read "+str(linesread)+" lines and copying "+str(added)+" vectors"
            print "Read "+str(linesread)+" lines"
            print "Copying "+str(added)+" vectors"

            with open(self.parameters['headcache'],'w') as outstream:

                for colloc in self.collocorder:

                    if self.parameters['diff']:
                        collocmatch=colloc
                    else:
                        collocmatch=untag(colloc.split(':')[0])[0]
                    outstream.write(vectordict[collocmatch])


            #mod
            vectordict={}

            with open(self.parameters['modpath'],'r') as instream:
                print "Reading "+self.parameters['modpath']
                linesread=0
                added=0
                #print self.moddict.keys()
                for line in instream:
                    linesread+=1
                    fields=line.split('\t')
                    try:
                        if self.parameters['diff']:
                            (modmatch,collocmatch)=untag(fields[0],'!')
                            if self.parameters['mod']:
                                modmatch = modmatch.split(':')[1]

                            ismodmatch=collocmatch.split(':')[2]
                        else:
                            modmatch=fields[0]
                            if self.parameters['mod']:
                                modmatch = modmatch.split(':')[1]
                            else:
                                modmatch = untag(modmatch)[0]
                            ismodmatch=modmatch
                            collocmatch=modmatch
                        if modmatch==ismodmatch and self.moddict.get(modmatch,0)>0:
                            vectordict[collocmatch]=line
                            added+=1
                        #else:
                            #print "No match for "+modmatch
                    except TaggingError:
                        print "Ignoring "+fields[0]
                    if self.parameters['testing'] and linesread%1000==0:print "Read "+str(linesread)+" lines and copying "+str(added)+" vectors"
            print "Read "+str(linesread)+" lines"
            print "Copying "+str(added)+" vectors"

            with open(self.parameters['modcache'],'w') as outstream:
                for colloc in self.collocorder:
                    if self.parameters['diff']:
                        collocmatch=colloc
                    else:
                        collocmatch=colloc.split(':')[2]
                    outstream.write(vectordict[collocmatch])

    def process(self):

        with open(self.parameters['phrasalcache'],'r') as phrasalstream:
            with open(self.parameters['headcache'],'r') as headstream:
                with open(self.parameters['modcache'],'r') as modstream:

                    xs=[]
                    ys=[]
                    phrases=[]
                    done=0
                    for line in phrasalstream:
                        phrasefields=line.rstrip().split('\t')
                        headfields=headstream.readline().rstrip().split('\t')
                        modfields=modstream.readline().rstrip().split('\t')
                        phraseVector=FeatureVector(phrasefields[0],phrasefields[1:])
                        headVector=FeatureVector(headfields[0],headfields[1:])
                        modVector=FeatureVector(modfields[0],modfields[1:])

                        composedVector=self.compose(headVector,modVector)
                        if self.parameters['testing']:
                            print phraseVector.toString()
                            print headVector.toString()
                            print modVector.toString()
                            print composedVector.toString()
                        scores =self.compare(composedVector,phraseVector)
                        if self.parameters['testing']:
                            print scores

                        phrases.append(phrasefields[0])
                        xs.append(self.collocdict[phrasefields[0]])
                        ys.append(scores)
                        done+=1
                        if done % 1000 == 0:
                            print "Processed "+str(done)+"phrasal expressions"
                        if self.parameters['testing'] and done%10==0:
                            print "Processed "+str(done)+" phrasal expressions"
                            break
        self.computestats(xs,ys,phrases)

    def compose(self,head,mod):
        compfunct=getattr(self,'_compose_'+self.parameters['compop'])
        return compfunct(head,mod)
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
                    outstream.write(metric+'\t')
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

            correlation=stats.spearmanr(np.array(xs),np.array(zs))
            print "Correlation with PMI is: ", correlation
            (c1,c2)=correlation
            with open(self.resultspath,'a') as outstream:
                if parameters['mod']:
                    outstream.write('mod,')
                else:
                    outstream.write('nomod,')
                if parameters['diff']:
                    outstream.write('diff,')
                else:
                    outstream.write('nodiff,')
                outstream.write(parameters['compop']+',')
                outstream.write(metric+','+str(mean)+','+str(sd)+','+str(c1)+','+str(c2)+'\n')

        return

    def _compose_add(self,head,modifier):
        return head.add(modifier)

    def _compose_mult(self,head,modifier):
        return head.mult(modifier)

    def _compose_selecthead(self,head,modifier):
        return head.selecthead(modifier)

    def _compose_selectmod(self,head,modifier):
        return head.selectmod(modifier)

    def _compare_recall(self,hypothesis,target):
        return hypothesis.recall(target)

    def _compare_precision(self,hypothesis,target):
        return hypothesis.precision(target)

    def _compare_f(self,hypothesis,target):
        return hypothesis.fscore(target)

    def _compare_cosine(self,hypothesis,target):
        return hypothesis.cosine(target)

def go(parameters):
    myComposer=Composer(parameters)
    myComposer.process()


if __name__=='__main__':
    parameters=conf.configure(sys.argv)
    print "Metrics:",parameters['metric']
    print "MOD:",parameters['mod']
    print "DIFF:",parameters['diff']
    print "Composition Operation:",parameters['compop']
    go(parameters)

