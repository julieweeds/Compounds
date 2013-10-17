__author__ = 'juliewe'

import sys,os,random
from operator import itemgetter

from conf import configure


class TaggingException(Exception):
    pass

def untag(astring):
    parts=astring.split('/')
    if len(parts)==2:
        return(parts[0],parts[1])
    else:
        raise TaggingException

class Collocates:

    def __init__(self,config):
        self.clist=[]
        self.fdict={}
        #self.midict={}
        self.entrylist=[]
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
            self.linestop=1000
        random.seed(42)
        self.sorted=False

    def processfreqfile(self):

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
                                    if parts[0]==self.featurematch and parts[1] in self.entrylist:
                                        label=entry+':'+feature
                                        self.fdict[label]=freq
                    except TaggingException:
                        print "Warning: ignoring ",line
                        continue
                    linesread+=1
                    if linesread%self.linestop==0:
                        print "Read "+str(linesread)+" lines"
                        if self.testing:
                            break

        return

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
                                    #self.midict[label]=score
                                    self.clist.append((label,freq,score))
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
        if not self.sorted:
            self.clist.sort(key=itemgetter(2),reverse=True)
            self.sorted=True
        filepath=os.path.join(parameters['parentdir'],parameters['datadir'],parameters['collocatefile'])
        with open(filepath,'w') as outstream:
            for tuple in self.clist:
                outstream.write(tuple[0]+'\t'+str(tuple[1])+'\t'+str(tuple[2])+'\n')


def go(parameters):
    mycollocates = Collocates(parameters)
    mycollocates.processentries()
    print mycollocates.entrylist
    #exit()
    mycollocates.processfreqfile()
    mycollocates.processassocfile()
    mycollocates.viewlist()
    mycollocates.outputlist()


if __name__=='__main__':

    parameters=configure(sys.argv)
    go(parameters)


