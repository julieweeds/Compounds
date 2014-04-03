__author__ = 'juliewe'

import conf,sys,os,math
import scipy.stats as stats
import numpy as np
import re
import matplotlib.pyplot as plt

class TaggingError(Exception):
    pass

def untag(astring,achar='/'):
    parts=astring.split(achar)
    if len(parts)==2:
        return(parts[0],parts[1])
    else:
        raise TaggingError

def drawscatter(x,y,poly,title,ytitle,pr,xl,yl):
    xp=np.linspace(0,xl,100)
    #print poly
    #print poly(xp)
    plt.plot(x,y,'.',xp,poly(xp),'-')
    plt.ylim(0,yl)
    plt.title(title)
    plt.xlabel("PPMI")
    plt.ylabel(ytitle)
    mytext1="srcc = "+str(pr[0])
    mytext2="p = "+str(pr[1])
    plt.text(0.05,yl*0.9,mytext1)
    plt.text(0.05,yl*0.8,mytext2)
    plt.show()

class FeatureVector:
    firstorderPATT = re.compile('([^:]+-[^:]+):(.*)')
    secondorderPATT = re.compile('([^:]+-[^:]+):([^:]+-[^:]+):(.*)')
    compareUptoOrder = 1
    miroflag=False

    @staticmethod
    def strip(feat):
        parts=feat.split(':')
        res=parts[1]
        for part in parts[2:]:
            res=res+':'+part
        return res

    @staticmethod
    def feattype(feat):
        return feat.split(':')[0]

    @staticmethod
    def findorder(feat):
        #establish order of given feature
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

    def __init__(self,signifier,functional=True,features=[],fdict={}):
        self.signifier=signifier
        self.featuredict=dict(fdict)
        self.computedlength=False
        self.length=-1
        self.sum=-1
        self.functional=functional
        #print signifier, str(len(features))
        while len(features)>0:
            score=float(features.pop())
            feat=features.pop()
            if score>0:
                if not functional:
                    #print "Order of "+feat+" is "+str(self.findorder(feat))
                    if FeatureVector.findorder(feat)>1:
                         #print "Ignoring "+feat+" order "+str(self.findorder(feat))
                         pass #ignore higher order features in non-functional vectors
                    else:
                        self.featuredict[feat]=score
                else:
                    self.featuredict[feat]=score
        self.normalised=False



    def add(self,avector,ftag=''):
        if FeatureVector.miroflag:
            ctag=':'
        else:
            ctag=':+:'

        newvector=FeatureVector(self.signifier+ctag+ftag+':'+avector.signifier,features=[],fdict=self.featuredict)
        if not self.functional:

            for feature in avector.featuredict.keys():
                newvector.featuredict[feature]=newvector.featuredict.get(feature,0)+avector.featuredict[feature]
        else:
            for feature in avector.featuredict.keys():
                aorder=FeatureVector.findorder(feature)
                if aorder>1:
                    fofeat=FeatureVector.strip(feature)
                    if FeatureVector.feattype(feature)==FeatureVector.inversefeatures[ftag]:
                        newvector.featuredict[fofeat]=newvector.featuredict.get(fofeat,0)+avector.featuredict[feature]

        return newvector

    def max(self,avector,ftag=''):
        if FeatureVector.miroflag:
            ctag=':'
        else:
            ctag=':max:'
        newvector=FeatureVector(self.signifier+ctag+ftag+':'+avector.signifier,features=[],fdict=self.featuredict)
        if not self.functional:

            for feature in avector.featuredict.keys():
                newvector.featuredict[feature]=max(newvector.featuredict.get(feature,0),avector.featuredict[feature])

        else:
            for feature in avector.featuredict.keys():
                aorder=FeatureVector.findorder(feature)
                if aorder>1:
                    fofeat=FeatureVector.strip(feature)
                    if FeatureVector.feattype(feature)==FeatureVector.inversefeatures[ftag]:
                        newvector.featuredict[fofeat]=max(newvector.featuredict.get(fofeat,0),avector.featuredict[feature])
        return newvector

    def mult(self,avector,ftag=''):
        if FeatureVector.miroflag:
            ctag=':'
        else:
            ctag=':*:'
        newvector=FeatureVector(self.signifier+ctag+ftag+':'+avector.signifier,features=[],fdict={})
        if not self.functional:

            for feature in self.featuredict.keys():
                if avector.featuredict.get(feature,0)>0:
                    newvector.featuredict[feature]=self.featuredict[feature]*avector.featuredict[feature]

        else:
            #combine my 1st order features with avector's second order features
            #my 2nd order features would be combined with avector's 3rd order features ... smoothing ... may want different operations

            for feature in avector.featuredict.keys():
                aorder=FeatureVector.findorder(feature) #actually can do for all orders. order 1 won't match when stripped.
                #print feature,aorder
                if aorder>1:
                    fofeat=FeatureVector.strip(feature) #what is left after stripping first level of path dsecription
                    #but first level of path description needs to match the current dependency.  It should be the inverse of ftag
                    feattype=FeatureVector.feattype(feature)
                    if feattype==FeatureVector.inversefeatures[ftag]:
                        #print fofeat, self.featuredict.get(fofeat,0),avector.featuredict[feature]
                        if self.featuredict.get(fofeat,0)>0:
                            newvector.featuredict[fofeat]=self.featuredict[fofeat]*avector.featuredict[feature]
                            #print newvector.featuredict[fofeat]
                        else:
                           pass
                    else:
                        #print feattype, ftag, FeatureVector.inversefeatures[ftag]
                        pass
            #would need to generate 2nd order features if going to recurse. Not for comparison with observed first order features
        return newvector

    def gm(self,avector,ftag=''):
        #geometric mean of feature values i.e., multiply and sqrt to return into same number space
        if FeatureVector.miroflag:
            ctag=':'
        else:
            ctag=':gm:'
        newvector=FeatureVector(self.signifier+ctag+ftag+':'+avector.signifier,features=[],fdict={})
        if not self.functional:

            for feature in self.featuredict.keys():
                if avector.featuredict.get(feature,0)>0:
                    newvector.featuredict[feature]=math.sqrt(self.featuredict[feature]*avector.featuredict[feature])

        else:
            #combine my 1st order features with avector's second order features
            #my 2nd order features would be combined with avector's 3rd order features ... smoothing ... may want different operations

            for feature in avector.featuredict.keys():
                aorder=FeatureVector.findorder(feature) #actually can do for all orders. order 1 won't match when stripped.
                if aorder>1:
                    fofeat=FeatureVector.strip(feature)
                    feattype=FeatureVector.feattype(feature)
                    if feattype==FeatureVector.inversefeatures[ftag]:
                        if self.featuredict.get(fofeat,0)>0:
                            newvector.featuredict[fofeat]=math.sqrt(self.featuredict[fofeat]*avector.featuredict[feature])
                        else:
                           pass

            #would need to generate 2nd order features if going to recurse. Not for comparison with observed first order features
        return newvector

    def min(self,avector,ftag=''):
        if FeatureVector.miroflag:
            ctag=':'
        else:
            ctag=':min:'
        newvector=FeatureVector(self.signifier+ctag+ftag+':'+avector.signifier,features=[],fdict={})
        if not self.functional:
            for feature in self.featuredict.keys():
                if avector.featuredict.get(feature,0)>0:
                    newvector.featuredict[feature]=min(self.featuredict[feature],avector.featuredict.get(feature,0))
            #print newvector.signifier, len(newvector.featuredict.keys()), len(self.featuredict.keys()), len(avector.featuredict.keys())
        else:
            for feature in avector.featuredict.keys():
                aorder=FeatureVector.findorder(feature)
                if aorder>1:
                    fofeat=FeatureVector.strip(feature)
                    if FeatureVector.feattype(feature) == FeatureVector.inversefeatures[ftag]:
                        if self.featuredict.get(fofeat,0)>0:
                            newvector.featuredict[fofeat]=min(self.featuredict[fofeat],avector.featuredict.get(feature,0))


        return newvector

    def selectself(self,avector,ftag=''):
        #return first order features of self - doesn't matter because cosine only compares upto and order anyway
        if FeatureVector.miroflag:
            ctag=':'
        else:
            ctag=':ss:'
        newvector=FeatureVector(self.signifier+ctag+ftag+':'+avector.signifier,features=[],fdict=self.featuredict)
        #for feature in self.featuredict.keys():
        #    aorder=FeatureVector.findorder(feature)
        #    if aorder==1:
        #        newvector.featuredict[feature]=self.featuredict[feature]

        return newvector

    def selectother(self,avector,ftag=''):
        if FeatureVector.miroflag:
            ctag=':'
        else:
            ctag=':so:'

        if not self.functional:
            newvector=FeatureVector(self.signifier+ctag+ftag+avector.signifier,fdict=avector.featuredict)
        else:
            newvector=FeatureVector(self.signifier+ctag+ftag+avector.signifier,features=[],fdict={})

            for feature in avector.featuredict.keys():
                aorder=FeatureVector.findorder(feature)
                if aorder>1:
                    fofeat=FeatureVector.strip(feature)
                    if FeatureVector.feattype(feature)==FeatureVector.inversefeatures[ftag]:
                        newvector.featuredict[fofeat]=avector.featuredict[feature]
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
            aorder=FeatureVector.findorder(feature)
            if aorder<=FeatureVector.compareUptoOrder:
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
            self.sum={}
            self.computedlength=True
            total=0
            for feat in self.featuredict.keys():
                aorder=FeatureVector.findorder(feat)
                score=self.featuredict[feat]
                if aorder <= FeatureVector.compareUptoOrder:

                    total+=score*score
                self.sum[aorder]=self.sum.get(aorder,0)+score
            self.length=math.pow(total,0.5)
            return self.length

    def cosine(self,avector):
        total=0
        for feature in self.featuredict.keys():
            aorder=FeatureVector.findorder(feature)
            if aorder<=FeatureVector.compareUptoOrder:
                total+=self.featuredict[feature]*avector.featuredict.get(feature,0)

        if self.computelength()==0:
            if avector.computelength()==0:
                sim=1
                print "WARNING: empty vectors for "+self.signifier
            else:
                sim=0
        elif avector.computelength()==0:
            sim=0
        else:
            sim = total / (self.computelength() * avector.computelength())
        return sim

    def normalise(self):
        #make scores sum to 1
        if self.normalised:
            return
        else:
            self.normalised=True
            self.computelength() #ensures sums are computed as well as length
            for feat in self.featuredict.keys():
                aorder=FeatureVector.findorder(feat)
                self.featuredict[feat]=self.featuredict[feat]/self.sum[aorder]

            self.computelength() #recomputes length and sums
            return

    def transform(self,featdictlist,featuretotallist,association='pmi'):
        #transform raw featurecounts into association values
        if association=='raw':
            return
        else:
            self.computelength()
            self.rawdict=dict(self.featuredict)
            self.featuredict={}
            for feature in self.rawdict.keys():
                aorder=FeatureVector.findorder(feature)
                storedorder=aorder-1
                fofeat=feature
                while aorder>1:
                    fofeat=FeatureVector.strip(fofeat)
                    aorder=aorder-1
                feattot=featdictlist[storedorder].get(fofeat,0)
                if feattot>0:
                    ratio = (self.rawdict[feature]*featuretotallist[storedorder])/(self.sum[storedorder+1]*feattot)
                    pmi = math.log(ratio)

                    if pmi>0:
                        if association=='pmi':
                            self.featuredict[feature] = pmi
                        elif association=='lmi':
                            lmi = pmi * self.rawdict[feature]  #dividing by featuretotal won't make any difference as it is a constant and will just make numbers tiny - really?
                            self.featuredict[feature]=lmi
                        elif association=='npmi':
                            npmi=pmi/(-math.log(self.rawdict[feature]/featuretotallist[storedorder]))
                            self.featuredict[feature]=npmi
                        else:
                            print "Warning: unknown association measure"+association

                else:
                    #print "Warning "+feature+" not in feature dict"
                    pass
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

    def writeout(self,outstream):

        outstream.write(self.signifier)
        for feat in self.featuredict.keys():
            outstream.write('\t'+feat+'\t'+str(self.featuredict[feat]))
        outstream.write('\n')


class Composer:

    chunkSize=6000

    def __init__(self,parameters):
        self.parameters=parameters
        self.positions=['left','right']# #for adjectives and nouns - have corresponding dependency files in self.deppaths
        self.collocdict={}
        self.freqdict={}
        self.rightdict={}
        self.leftdict={}
        self.featdict={}
        self.featdict['left']={}  #features of leftmost constituent i.e., features of adjectives
        self.featdict['right']={}  #features of rightmost constituent i.e., features of nouns
        self.featuretotal={'left':0,'right':0}
        if self.parameters['diff']:
            self.whoami='.diff'
        else:
            self.whoami='.nodiff'
        self.whoami+='.'+parameters['vsource']
        self.completewhoami=self.whoami+'.'+self.parameters['compop']
        if self.parameters['funct']:
            self.completewhoami=self.completewhoami+'.funct'
        else:
            self.completewhoami=self.completewhoami+'.nofunct'
        self.statsreq=True
        self.association=parameters['association']
        self.completewhoami+='.'+self.association
        self.miroflag=self.parameters['miroflag']
        FeatureVector.miroflag=self.miroflag
        FeatureVector.inversefeatures=self.parameters['inversefeatures']

        self.readcomps()
        self.readfreqs()
        self.makecaches()
        self.resultspath=os.path.join(self.parameters['datadir'],self.parameters['output'])


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
                collocate=fields[0]
                if self.miroflag and False:  #obsolete miro format
                    #AN:black/J_swan/N
                    parts=collocate.split(':')
                    words=parts[1].split('_')
                    left=words[0]
                    right=words[1]
                    dep=self.parameters['featurematch']
                    collocate=left+':'+dep+':'+right
                    self.collocdict[collocate]=float(hash(collocate))

                else:
                    if len(fields)>1:
                        if self.parameters['NNcompflag']:
                            if self.parameters['literalityscore']=='compound':
                                self.collocdict[collocate]=float(fields[1]) #compound literality score
                            elif self.parameters['literalityscore']=='right':
                                self.collocdict[collocate]=float(fields[3]) #right word literality score
                            elif self.parameters['literalityscore']=='left':
                                self.collocdict[collocate]=float(fields[2])
                            else:
                                self.collocdict[collocate]=1
                        elif self.parameters['wn_wiki']:
                            self.collocdict[collocate]=float(fields[1]) #store frequency
                        else:
                            self.collocdict[collocate]=float(fields[2])#store PMI
                    else:
                        self.collocdict[collocate]=float(hash(collocate))
                    parts=collocate.split(':')
                    if parts[1]==self.parameters['featurematch']:
                        left=parts[0] #black/J
                        right=parts[2] #swan/N
                    elif parts[1]==self.parameters['inversefeatures'][self.parameters['featurematch']]:
                        left = parts[2]
                        right=parts[0]
                #print "mod: ",mod,"head: ",head
                self.leftdict[left]=self.leftdict.get(left,0)+1
                self.rightdict[right]=self.rightdict.get(right,0)+1


        print "Number of collocations is "+str(len(self.collocdict.keys()))
        print "Number of right heads is "+str(len(self.rightdict.keys()))
        print "Number of left modifiers is "+str(len(self.leftdict.keys()))
        self.collocorder=sorted(self.collocdict.keys())
        return

    def readfreqs(self):

        freqpath=os.path.join(self.parameters['datadir'],self.parameters['freqfile'])
        with open(freqpath,'r') as instream:

            for line in instream:

                fields=line.rstrip().split('\t')
                self.freqdict[fields[0]]=float(fields[1])
        print self.collocdict
        print self.freqdict
        self.freq_correlate()
        #self.freqdict={}  NEED THIS - can't wipe it!


    def freq_correlate(self):
        xs=[]  #human score
        ys=[]  #left freq
        zs=[]  #right freq

        for key in self.collocdict.keys():
            xs.append(self.collocdict[key])
            ys.append(self.freqdict.get(key,0))
            parts=key.split(':')
            rel = parts[1]
            invrel=self.parameters['inversefeatures'][rel]
            inverted=parts[2]+':'+invrel+':'+parts[0]
            zs.append(self.freqdict.get(inverted,0))

        print xs
        print ys
        print zs
        xarray=np.array(xs)
        yarray=np.array(ys)
        zarray=np.array(zs)
        leftcorr=stats.spearmanr(xarray,yarray)
        rightcorr=stats.spearmanr(xarray,zarray)
        print "Correlation with left frequency ",leftcorr
        print "Correlation with right frequency ",rightcorr
        if self.parameters['wn_wiki']:
            self.freqthresh=stats.cmedian(yarray)
            print "Median left frequency ",self.freqthresh
        else:
            self.freqthresh=stats.cmedian(zarray)
            print "Median right frequency ",self.freqthresh

        if self.parameters['diff']:
            self.chunkthresh=[stats.cmedian(xarray),np.max(xarray)]  #for chunking the input into len(self.chunkthresh) chunks  - needs work for generalisation to more than 2 chunks
        else:
            self.chunkthresh=[np.max(xarray)]


    def makecaches(self):

        self.parameters['phrasalcache']=os.path.join(self.parameters['datadir'],'phrasal.cache'+self.whoami)
        self.parameters['rightcache']=os.path.join(self.parameters['datadir'],'right.cache'+self.whoami)
        self.parameters['leftcache']=os.path.join(self.parameters['datadir'],'left.cache'+self.whoami)
        self.parameters['outcache']=os.path.join(self.parameters['datadir'],'comp.cache'+self.completewhoami)

        if not self.parameters['cached']:
            #phrasal
            vectordict={}

            for i,maxthresh in enumerate(self.chunkthresh):
                if i==0:
                    writemode='w'
                else:
                    writemode='a'

                minthresh=self.chunkthresh[i-1]
                if minthresh>=maxthresh:
                    minthresh=-1

                with open(self.parameters['phrasalpath'],'r') as instream:
                    print "Reading "+self.parameters['phrasalpath']
                    linesread=0
                    added=0
                    for line in instream:
                        linesread+=1
                        fields=line.split('\t')

                        collocscore=self.collocdict.get(fields[0],-1)
                        invcollocscore=self.collocdict.get(self.inverse(fields[0]),-1)

                        if collocscore>minthresh and collocscore<=maxthresh:
                            vectordict[fields[0]]=line
                            added+=1
                        elif invcollocscore>minthresh and collocscore <=maxthresh:
                            vectordict[fields[0]]=line
                            added+=1
                        else:
                            #   print "Not added vector for "+fields[0]
                            pass
                        if self.parameters['testing'] and linesread%1000==0:print "Read "+str(linesread)+" lines and copying "+str(added)+" vectors"

                    print "Read "+str(linesread)+" lines"
                    print "Copying "+str(added)+" vectors"

                with open(self.parameters['phrasalcache'],writemode) as outstream:
                    print "Writing "+self.parameters['phrasalcache']
                    for colloc in self.collocorder:
                        collocscore=self.collocdict.get(colloc,-1)
                        if collocscore>minthresh and collocscore <=maxthresh:
                            outstream.write(vectordict.get(colloc,colloc+'\n'))
                            inverted = self.inverse(colloc)
                            outstream.write(vectordict.get(inverted,inverted+'\n'))

                vectordict={} #free memory
                #load constituents

                leftvectordict={}   #store collocate --> linenumber for output on left stream
                rightvectordict={}  #store collocate-->linenumber for output on right stream
                linedict={}  #store linenumber-->line

                with open(self.parameters['constituentpath'],'r') as instream:
                    print "Reading "+self.parameters['constituentpath']
                    linesread=0
                    added=0
                    for line in instream:
                        linesread+=1

                        fields=line.rstrip().split('\t')
                        if self.parameters['diff']:
                            (headmatch,collocmatch,invmatch)=fields[0].split('!')
                            collocscore=self.collocdict.get(collocmatch,-1)
                            if collocscore>minthresh and collocscore < maxthresh:
                                collocparts=collocmatch.split(':')
                                if self.leftdict.get(headmatch,-1)>-1 and headmatch==collocparts[2]:
                                    linedict[linesread]=line
                                    leftvectordict[invmatch]=linesread
                                    rightvectordict[collocmatch]=linesread
                                    added+=2
                                if self.rightdict.get(headmatch,-1)>-1 and headmatch==collocparts[0]:
                                    linedict[linesread]=line
                                    rightvectordict[invmatch]=linesread
                                    leftvectordict[collocmatch]=linesread
                                    added+=2
                            #else:
                            #    print "Warning: ignoring "+headmatch
                        else:
                            headmatch = fields[0]
                            if self.leftdict.get(headmatch,-1)>-1:
                                linedict[linesread]=line
                                leftvectordict[headmatch]=linesread
                                rightvectordict[headmatch]=linesread
                                added+=2
                            if self.rightdict.get(headmatch,-1)>-1:
                                linedict[linesread]=line
                                rightvectordict[headmatch]=linesread
                                leftvectordict[headmatch]=linesread
                                added+=2

                             #   print "Warning: ignoring "+headmatch
                        if self.parameters['testing'] and linesread%1000==0:
                            print "Read "+str(linesread)+" lines and copied "+str(added)+" vectors"
                    print "Read "+str(linesread)+" lines and copied "+str(added)+" vectors"

                #print leftvectordict
                #print rightvectordict
                #test1='absorber/N'
                #test2='shock/N'

                with open(self.parameters['leftcache'],writemode) as leftstream:
                    with open(self.parameters['rightcache'],writemode) as rightstream:
                        print "Writing "+self.parameters['leftcache']+" and "+self.parameters['rightcache']
                        for colloc in self.collocorder:
                            collocscore=self.collocdict.get(colloc,-1)
                            if collocscore > minthresh and collocscore <= maxthresh:

                                if self.parameters['diff']:
                                    leftstream.write(linedict.get(leftvectordict.get(colloc,-1),colloc+'\n'))
                                    rightstream.write(linedict.get(rightvectordict.get(colloc,-1),colloc+'\n'))
                                else:
                                    parts=colloc.split(':')
                                    left=parts[0]
                                    right=parts[2]
                                    leftstream.write(linedict.get(leftvectordict.get(left,-1),left+'\t\n'))
                                    rightstream.write(linedict.get(rightvectordict.get(right,-1),right+'\t\n'))
                                #inverse collocation
                                inverted=self.inverse(colloc)
                                if self.parameters['diff']:
                                    leftstream.write(linedict.get(leftvectordict.get(inverted,-1),inverted+'\n'))
                                    rightstream.write(linedict.get(rightvectordict.get(inverted,-1),inverted+'\n'))
                                else:
                                    parts=inverted.split(':')
                                    left=parts[0]
                                    right=parts[2]
                                    leftstream.write(linedict.get(rightvectordict.get(left,-1),left+'\t\n'))
                                    rightstream.write(linedict.get(leftvectordict.get(right,-1),right+'\t\n'))


    def loadfeaturefile(self):
        #read in feature totals for pmi calculations

        filepaths = [os.path.join(self.parameters['datadir'],self.parameters['featurefile']),os.path.join(self.parameters['altdatadir'],self.parameters['featurefile'])]
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

    def process(self):

        with open(self.parameters['phrasalcache'],'r') as phrasalstream:
            with open(self.parameters['leftcache'],'r') as leftstream:
                with open(self.parameters['rightcache'],'r') as rightstream:

                    vectorstream=open(self.parameters['outcache'],'w')
                    allxs=[]
                    allys=[]
                    allphrases=[]
                    leftxs=[]
                    leftys=[]
                    leftphrases=[]
                    rightxs=[]
                    rightys=[]
                    rightphrases=[]
                    allfreqs=[]
                    rightfreqs=[]
                    leftfreqs=[]
                    done=0
                    right_ignored=0
                    left_ignored=0
                    for line in phrasalstream:
                        done+=1

                        phrasefields=line.rstrip().split('\t')
                        rightfields=rightstream.readline().rstrip().split('\t')
                        leftfields=leftstream.readline().rstrip().split('\t')
                        phraseVector=FeatureVector(phrasefields[0],features=phrasefields[1:],functional=self.parameters['funct'])
                        rightVector=FeatureVector(rightfields[0],features=rightfields[1:],functional=self.parameters['funct'])
                        leftVector=FeatureVector(leftfields[0],features=leftfields[1:],functional=self.parameters['funct'])
                        #print "Processing "+str(done)+":"+phrasefields[0]

                        phraseparts=phrasefields[0].split(':')
                        if len(phraseparts)<2:
                            print "Error with line "+line
                        else:
                            if phraseparts[1]==self.parameters['featurematch']:
                                inverted=False
                            elif phraseparts[1]==self.parameters['inversefeatures'][self.parameters['featurematch']]:
                                inverted=True
                            else:
                                print "Warning: non-matching featuretype in phrase "+phrasefields[0]
                                print phraseparts[1],self.parameters['featurematch'],self.parameters['inversefeatures'][self.parameters['featurematch']]
                                exit(1)

                        if self.parameters['testing']:
                            print phraseVector.toString()
                            print rightVector.toString()
                            print leftVector.toString()
                        if not self.parameters['composefirst']:
                            #transform to pmi values before composition
                            if inverted:
                                rightVector.transform([self.featdict['left'],self.featdict['right']],[self.featuretotal['left'],self.featuretotal['right']],association=self.association)
                                leftVector.transform([self.featdict['right'],self.featdict['left']],[self.featuretotal['right'],self.featuretotal['right']],association=self.association)
                            else:
                                rightVector.transform([self.featdict['right'],self.featdict['left']],[self.featuretotal['right'],self.featuretotal['left']],association=self.association)
                                leftVector.transform([self.featdict['left'],self.featdict['right']],[self.featuretotal['left'],self.featuretotal['right']],association=self.association)
                            #phraseVector.transform(self.featdict,self.featuretotal)
                        else: #normalise to probabilities before composing
                            #rightVector.normalise()
                            #leftVector.normalise()
                            pass

                        composedVector=self.compose(leftVector,rightVector,ftag=phraseparts[1])
                        if composedVector.computelength()>0:
                            composedVector.writeout(vectorstream)  #save untransformed raw frequencies for input to byblo
                        if self.parameters['testing']:
                            print composedVector.toString()
                        if self.parameters['composefirst']:
                            if inverted:
                                composedVector.transform([self.featdict['right']],[self.featuretotal['right']],association=self.association)
                            else:
                                composedVector.transform([self.featdict['left']],[self.featuretotal['left']],association=self.association)  #phrases have features of the left most constituent

                        if inverted:
                            phraseVector.transform([self.featdict['right']],[self.featuretotal['right']],association=self.association)
                        else:
                            phraseVector.transform([self.featdict['left']],[self.featuretotal['left']],association=self.association)  #phrases have features of the left most constituent

                        if self.parameters['testing']:
                            print phraseVector.toString()
                            print rightVector.toString()
                            print leftVector.toString()
                            #print leftVector.featuredict
                            print composedVector.toString()
                        if phraseVector.computelength()==0:
                            print "Ignore phrase with empty observed vector: "+phraseVector.signifier
                            if inverted:
                                right_ignored+=1
                            else:
                                left_ignored+=1
                        else:
                            scores =self.compare(composedVector,phraseVector)
                            if self.parameters['testing']:
                                print scores

                            allphrases.append(phrasefields[0])
                            allys.append(scores)
                            leftpmi=self.collocdict.get(self.inverse(phrasefields[0]),-1)
                            rightpmi=self.collocdict.get(phrasefields[0],-1)
                            leftfreq=self.freqdict.get(phrasefields[0],-1)
                            rightfreq=self.freqdict.get(phrasefields[0],-1)
                            if rightfreq<1:
                                print "No right freq for "+phrasefields[0]
                            if inverted:
                                allxs.append(rightpmi)
                                rightxs.append(rightpmi)
                                allfreqs.append(rightfreq)
                                rightfreqs.append(rightfreq)
                                rightphrases.append(phrasefields[0])
                                rightys.append(scores)
                            else:
                                allxs.append(leftpmi)
                                leftxs.append(leftpmi)
                                allfreqs.append(leftfreq)
                                leftfreqs.append(leftfreq)
                                leftphrases.append(phrasefields[0])
                                leftys.append(scores)

                        if done % 100 == 0:
                            print "Processed "+str(done)+" phrasal expressions"
                        if self.parameters['testing'] and done%50==0:
                            print "Processed "+str(done)+" phrasal expressions"
                            break
                    vectorstream.close()
        print "Ignored "+str(right_ignored)+" phrases of type head"
        print "Ignored "+str(left_ignored)+" phrases of type mod"
        #self.computestats(allxs,allys,allphrases,'all')
        #self.computestats(leftxs,leftys,leftphrases,'left')

        #print self.collocdict.keys(),rightphrases
        self.computestats(rightxs,rightys,rightphrases,'head')
        self.computestats(leftxs,leftys,leftphrases,'mod')
        #self.computestats(rightfreqs,rightys,rightphrases,'headfreq')

    def compose(self,left,right,ftag=''):
        compfunct=getattr(self,'_compose_'+self.parameters['compop'])
        #right.normalise()  #makes no difference to normalise vectors before composition
        #left.normalise()
        return compfunct(left,right,ftag=ftag)
    def compare(self,composed,phrasal):
        res=[]

        for metric in self.parameters['metric']:
            simfunct=getattr(self,'_compare_'+metric)
            res.append(simfunct(composed,phrasal))

        return res

    def writestats(self,xs,ys,phrases):
        if self.statsreq:
            if self.parameters['composefirst']:
                detail='.compfirst.'+self.parameters['association']
            else:
                detail='.compsecond.'+self.parameters['association']
            statspath=os.path.join(self.parameters['datadir'],'stats'+self.completewhoami+detail+'.csv')
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

    def computestats(self,xs,ys,phrases,type='all'):

        #if type=='right' or type=='rightfreq':
        #print phrases,xs,ys
        self.writestats(xs,ys,phrases)

        for i,metric in enumerate(self.parameters['metric']):
            total=0
            totalsquared=0
            variance=0
            zs=[]
            for y in ys:
                #print y
                z=y[i]
                zs.append(z)
                total+=z
                totalsquared+=z*z
            if len(zs)>0:
                mean = total/len(zs)
                variance = totalsquared/len(zs)-mean*mean
                if variance>0:
                    sd = math.pow(variance,0.5)
                else:
                    sd=0
            else:
                mean=0
                sd=0
            print type+" :mean "+metric+" score is "+str(mean)+", sd is "+str(sd)
            #zarray=np.array(zs)
            #print "np check "+type+" : mean "+metric+" score is "+ str(np.mean(zarray))+", sd is "+str(np.std(zarray))

            if variance>0:
                x=np.array(xs)
                y=np.array(zs)
                correlation=stats.spearmanr(x,y)
                if self.parameters['graphing']:

                    title="Scatter Graph for "+metric+" Against PPMI"
                    drawscatter(x,y,np.poly1d(np.polyfit(x,y,1)),title,metric,correlation,10,1)
            else:
                correlation=(float('nan'),float('nan'))
            print "Correlation with PMI is: ", correlation
            (c1,c2)=correlation
            with open(self.resultspath,'a') as outstream:
                outstream.write(self.parameters['usefile']+','+type+','+self.parameters['vsource']+',')
                if self.parameters['funct']:
                    outstream.write('funct,')
                else:
                    outstream.write('non-funct,')
                if self.parameters['diff']:
                    outstream.write('diff,')
                else:
                    outstream.write('nodiff,')

                if self.parameters['composefirst']:
                    outstream.write('compose->'+parameters['association']+',')
                else:
                    outstream.write(parameters['association']+'->compose,')

                outstream.write(self.parameters['compop']+',')
                outstream.write(metric+','+str(mean)+','+str(sd)+','+str(c1)+','+str(c2)+'\n')

        return

    def _compose_add(self,left,right,ftag=''):
        return left.add(right,ftag=ftag)

    def _compose_mult(self,left,right,ftag=''):
        return left.mult(right,ftag=ftag)

    def _compose_selectself(self,left,right,ftag=''):
        return left.selectself(right,ftag=ftag)

    def _compose_selectother(self,left,right,ftag=''):
        return left.selectother(right,ftag=ftag)

    def _compose_min(self,left,right,ftag=''):
        return left.min(right,ftag=ftag)

    def _compose_max(self,left,right,ftag=''):
        return left.max(right,ftag=ftag)

    def _compose_gm(self,left,right,ftag=''):
        return left.gm(right,ftag=ftag)

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
    myComposer.loadfeaturefile()
    myComposer.process()


if __name__=='__main__':
    parameters=conf.configure(sys.argv)
    print "Metrics:",parameters['metric']
    print "FUNCT:",parameters['funct']
    print "DIFF:",parameters['diff']
    print "Compose first:",parameters['composefirst']
    print "Association:",parameters['association']
    print "Composition Operation:",parameters['compop']
    go(parameters)

