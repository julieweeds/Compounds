__author__ = 'juliewe'

import sys,os,random
from operator import itemgetter

from conf import configure


class TaggingException(Exception):
    pass

def untag(astring,achar='/'):
    parts=astring.split(achar)
    if len(parts)==2:
        return(parts[0],parts[1])
    elif len(parts)>1:
        tag=parts.pop()
        word=parts[0]
        for part in parts[1:]:
            word = word+'-'+part
        return (word,tag)
    else:
        raise TaggingException

class Collocates:

    def __init__(self,config):
        self.clist=[]
        self.fdict={}
        #self.midict={}
        self.moddict={}
        self.modfdict={}
        self.entrylist=[]
        self.entrydict={}
        self.noundict={}
        self.freqthresh=config['freqthresh']
        self.entrythresh=config['entrythresh']
        self.featurematch=config['featurematch']
        self.stopwordlimit=config['stopwordlimit']
        self.testing=config['testing']
        self.sample=config['sample']
        self.parameters=config
        if self.testing:
            self.linestop=10
        else:
            self.linestop=100
        random.seed(42)
        self.sorted=False

    def makemoddict(self):
        filepath=os.path.join(self.parameters['parentdir'],self.parameters['altdatadir'],self.parameters['freqfile'])
        with open(filepath,'r') as instream:
            print "Reading "+filepath
            linesread=0
            for line in instream:
                linesread+=1
                fields=line.rstrip().split('\t')
                try:
                    noun = untag(fields[0])[0]
                    self.moddict[noun]=1
                    if self.noundict.get(noun,0)>0:
                        while len(fields[1:])>0:
                            freq=float(fields.pop())
                            feature=fields.pop()
                            if freq>self.freqthresh:
                                parts=feature.split(':')
                                if parts[0]==self.parameters['inversefeatures'][self.featurematch] and self.entrydict.get(parts[1],0)>0:
                                    label=parts[1]+'/J:'+self.featurematch+':'+noun
                                    self.modfdict[label]=freq
                except TaggingException:
                    print "Ignoring "+line
                if linesread%self.linestop==0:
                    print "Read "+str(linesread)+" lines"
                    if self.testing: break
            print "Size of mod freq dict is "+str(len(self.modfdict.keys()))

    def processfreqfile(self):
        if len(self.moddict.keys())>0:
            usemoddict=True
        else:
            usemoddict=False
        filepath = os.path.join(self.parameters['parentdir'],self.parameters['datadir'],self.parameters['freqfile'])

        outpath = filepath+".cached"
        print "Reading "+filepath
        linesread=0
        with open(filepath,'r') as instream:
            with open(outpath,'w')as outstream:
                for line in instream:
                    fields=line.rstrip().split('\t')
                    entry=fields[0]
                    try:
                        if untag(entry)[0] in self.entrylist:
                            outstream.write(line)
                            while len(fields[1:])>0:
                                freq=float(fields.pop())
                                feature=fields.pop()
                                if freq> self.freqthresh:
                                    parts=feature.split(':')

                                    if parts[0]==self.featurematch and (self.parameters['allheads'] or parts[1] in self.entrylist):
                                        if not usemoddict or (usemoddict and self.moddict.get(parts[1],0)>0):
                                            label=entry+':'+feature
                                            self.fdict[label]=freq
                                            self.noundict[parts[1]]=1
                    except TaggingException:
                        print "Warning: ignoring ",line
                        continue
                    linesread+=1
                    if linesread%self.linestop==0:
                        print "Read "+str(linesread)+" lines"
                        if self.testing:
                            break

        print "Size of freq dict is "+str(len(self.fdict))
        print "Size of noun dict is "+str(len(self.noundict))
        print self.noundict

    def processassocfile(self):

        filepath=os.path.join(self.parameters['parentdir'],self.parameters['datadir'],self.parameters['assocfile'])

        outpath=filepath+".cached"
        print "Reading "+filepath
        linesread=0
        with open(filepath,'r') as instream:
            with open(outpath,'w') as outstream:
                for line in instream:
                    fields=line.rstrip().split('\t')
                    entry=fields[0]
                    try:
                        if untag(entry)[0] in self.entrylist:
                            outstream.write(line)
                            while len(fields[1:])>0:
                                score=float(fields.pop())
                                feature=fields.pop()
                                parts=feature.split(':')
                                if parts[0]==self.featurematch:
                                    label=entry+':'+feature
                                    freq=self.fdict.get(label,0)

                                    if freq>self.freqthresh:
                                        altfreq=self.modfdict.get(label,0)
                                        if altfreq>self.freqthresh:
                                            #self.midict[label]=score
                                            self.clist.append((label,freq,score))
                                        else:
                                            print "Ignoring "+label+" f1 = "+str(freq)+" f2 = "+str(altfreq)
                    except (TaggingException):
                        print "Warning: ignoring ",line
                        continue
                    linesread+=1
                    if linesread%self.linestop==0:
                        print "Read "+str(linesread)+" lines"
                        if self.testing:
                            break


    def processentries(self):
        filepath=os.path.join(self.parameters['parentdir'],self.parameters['datadir'],self.parameters['entryfile'])
        print "Reading "+filepath
        linesread=0
        mylist=[]
        with open(filepath,'r') as instream:
            for line in instream:
                try:
                    fields=line.rstrip().split('\t')
                    if float(fields[1])>self.entrythresh:
                        entry=untag(fields[0])[0]
                        if len(entry)>self.stopwordlimit:
                            mylist.append(entry)
                except TaggingException:
                    print "Warning: ignoring ",line
                    continue
                linesread+=1
                #if linesread%10000==0:
                    #print "Read "+str(linesread)+" lines"
        print str(len(mylist))+" words over entry threshold"
        random.shuffle(mylist)
        self.entrylist=list(mylist[0:self.sample])
        return



    def viewlist(self):
        total= len(self.clist)
        print total
        if not self.sorted:
            self.clist.sort(key=itemgetter(2),reverse=True)
            self.sorted=True
        print "Top 10: ", self.clist[0:10]
        print "Bottom 10: ", self.clist[total-10:total]

    def outputlist(self):
        headdict={}
        headover={}
        thresh=self.parameters['upperfreqthresh']
        if not self.sorted:
            self.clist.sort(key=itemgetter(2),reverse=True)
            self.sorted=True
        filepath=os.path.join(parameters['parentdir'],parameters['datadir'],parameters['collocatefile'])
        with open(filepath,'w') as outstream:
            for tuple in self.clist:
                label=tuple[0]
                head=label.split(':')[0]
                outstream.write(label+'\t'+str(tuple[1])+'\t'+str(tuple[2])+'\n')
                headdict[head]=headdict.get(head,0)+1
                if tuple[1] > thresh-1:
                    headover[head]=headover.get(head,0)+1
        print "Number of phrases per head"
        print len(headdict.keys()),headdict
        print "Number of phrases with frequency over "+str(thresh)+" per head"
        print len(headover.keys()),headover
        soverlist=[]
        for adj in headdict.keys():
            if headdict[adj]>100:
                soverlist.append(adj)
        print "Adjectives with more than 100 phrases with frequency over "+str(self.freqthresh)+": " +str(len(soverlist))
        print soverlist


        soverlist=[]
        for adj in headover.keys():
            if headover[adj]>100:
                soverlist.append(adj)
        print "Adjectives with more than 100 phrases with frequency over 100: " +str(len(soverlist))
        print soverlist
        opath=os.path.join(self.parameters['parentdir'],self.parameters['datadir'],'adjectives')
        with open(opath,'w') as outstream:
            for adj in soverlist:
                outstream.write(adj+'\n')



class SourceCollocates(Collocates):

    def processboledaline(self,line):
        fields=line.rstrip().split('\t')
        phrase=fields[0]
        type=fields[1]
        parts=phrase.split('_')
        mod=parts[0]
        head=parts[1]
        try:
            noun=untag(head,'-')[0]
            adj=untag(mod,'-')[0]
            if self.parameters['featurematch']=='amod-DEP':
                label=noun+'/N:'+self.parameters['featurematch']+':'+adj
                if not self.parameters['allheads']:
                    self.entrylist.append(adj)
                self.entrylist.append(noun)
            elif self.parameters['featurematch']=='amod-HEAD':
                label=adj+'/J:'+self.parameters['featurematch']+':'+noun
                if not self.parameters['allheads']:
                    self.entrylist.append(noun)
                self.entrylist.append(adj)
                #print label
            #self.srcdict[label]=type
            self.srcposdict[label]=self.linesread
            self.revposdict[self.linesread]=label
            self.srctypedict[label]=type


            #self.modlist.append(adj)
        except TaggingException:
            print "Ignoring "+line

    def processlistline(self,line):
        fields=line.rstrip().split(' ')
        try:
            adj=untag(fields[0])[0]
            type=fields[1]
            self.entrylist.append(adj)
            self.entrydict[adj]=1
            self.srcposdict[adj]=self.linesread
            self.revposdict[self.linesread]=adj
            self.srctypedict[adj]=type
        except TaggingException:
            print "Ignoring "+line



    def processsource(self):
        self.srctypedict={}
        self.srcposdict={}
        self.revposdict={}
        self.entrylist=[]
        #self.modlist=[]
        filepath=os.path.join(self.parameters['parentdir'],self.parameters['datadir'],self.parameters['source'])
        with open(filepath,'r') as instream:
            print "Reading "+filepath
            self.linesread=0
            for line in instream:
                self.linesread+=1
                if self.parameters['adjlist']:
                    self.processlistline(line)
                else:
                    self.processboledaline(line)

        self.largest=self.linesread

    def mergelists(self):

        reslist=[]

        for (label,freq,pmi) in self.clist:
            pos = self.srcposdict.get(label,0)
            if pos > 0:
                type = self.srctypedict[label]
                reslist.append((pos,label,freq,pmi,type))

        reslist.sort()

        filepath=os.path.join(self.parameters['parentdir'],self.parameters['datadir'],self.parameters['mergefile'])
        counter=1
        missinglist=[]
        under100=[]
        with open(filepath,'w') as outstream:
            for tuple in reslist:
                while counter<tuple[0]:
                    label=self.revposdict[counter]
                    if self.testing:
                        print label, self.srctypedict[label],0,0
                    outstream.write(label+'\t'+self.srctypedict[label]+'\t0\t0\n')
                    counter+=1
                    missinglist.append(label)
                outstream.write(tuple[1]+'\t'+tuple[4]+'\t'+str(tuple[2])+'\t'+str(tuple[3])+'\n')
                if tuple[2] < 100:
                    under100.append(label)
                if self.testing:
                    print tuple[1],tuple[4],tuple[2],tuple[3]
                counter+=1
            while counter<self.largest+1:
                label=self.revposdict[counter]
                if self.testing:
                    print label, self.srctypedict[label],0,0
                outstream.write(label+'\t'+self.srctypedict[label]+'\t0\t0\n')
                counter+=1
                missinglist.append(label)
        print "Missing phrases: "+str(len(missinglist))
        print missinglist
        print "Frequency under 100: "+str(len(under100))
        print under100

    def divide(self):
        #self.clist contains (label,freq,pmi) where label is adj:rel:noun where adj is in list

        #convert to matrix
        cmat=[]
        row=[]
        adj=''
        for (label,freq,pmi) in self.clist:
            parts=label.split(':')
            thisadj=parts[0]
            if thisadj != adj and len(row)>0:
                cmat.append(row)
                row=[]
            adj=thisadj
            row.append((label,freq,pmi))
        if len(row)>0:
            cmat.append(row)
        print len(cmat)
        trainingpath=os.path.join(self.parameters['parentdir'],self.parameters['datadir'],self.parameters['collocatefile'][0])
        testingpath=os.path.join(self.parameters['parentdir'],self.parameters['datadir'],self.parameters['collocatefile'][1])
        sparepath=os.path.join(self.parameters['parentdir'],self.parameters['datadir'],self.parameters['collocatefile'][2])
        with open(trainingpath,'w') as training:
            with open(testingpath,'w') as testing:
                with open(sparepath,'w') as sparestream:
                    for row in cmat:
                        print len(row), row[0]
                        random.shuffle(row)
                        self.writetofile(row[0:50],training)
                        self.writetofile(row[50:100],testing)
                        self.writetofile(row[100:],sparestream)

    def writetofile(self,alist,outstream):
        if len(alist)==0:
            return
        else:
            try:
                adj=untag(alist[0][0].split(':')[0])[0]
                type = self.srctypedict[adj]
                for (label,freq,pmi) in alist:
                    outstream.write(label+'\t'+str(freq)+'\t'+str(pmi)+'\t'+type+'\n')
            except TaggingException:
                print "Tagging error ",alist


def go(parameters):
    mycollocates = Collocates(parameters)
    mycollocates.processentries()
    print mycollocates.entrylist
    #exit()
    mycollocates.processfreqfile()
    mycollocates.processassocfile()
    mycollocates.viewlist()
    mycollocates.outputlist()


def analyse(parameters):
    mycollocates=SourceCollocates(parameters)
    mycollocates.processsource()

    mycollocates.processfreqfile()
    if mycollocates.parameters['adjlist']:
        mycollocates.makemoddict()
    mycollocates.processassocfile()

    if mycollocates.parameters['adjlist']:
        mycollocates.divide()
    else:
        mycollocates.viewlist()
        mycollocates.mergelists()
        mycollocates.outputlist()

if __name__=='__main__':

    parameters=configure(sys.argv)
    if parameters['usesource']:
        analyse(parameters)
    else:
        go(parameters)


