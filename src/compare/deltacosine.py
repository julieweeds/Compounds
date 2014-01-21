__author__ = 'juliewe'

import sys,conf,os
import numpy as np

class scoretable:
    def __init__(self,filename):
        self.name=filename

    def loadfile(self):

        self.metrics=['PPMI']
        phrases=[]
        lines=[]
        with open(self.name,'r') as instream:
            for line in instream:
                lines.append(line.rstrip())

        #process line0

        fields=lines[0].split(',')
        self.metrics=self.metrics+list(fields[:-1])
        #print len(metrics),metrics

        #process line 1
        #print lines[1]
        self.phrases=list(lines[1].split(',')[:-1])

        #process rest
        self.scores={}
        for i,metric in enumerate(self.metrics):
            self.scores[metric]=[]
            lineno=i+2
            #print metric
            fields=lines[lineno].split(',')
            #print fields
            self.scores[metric] = list(fields[:-1])

    def minus(self,atable):
        for metric in self.metrics:
            for i, score in enumerate(self.scores[metric]):
                self.scores[metric][i]=float(score)-float(atable.scores[metric][i])

    def average(self,tag,metric):

        scorelist=[]
        for i,phrase in enumerate(self.phrases):
            parts=phrase.split(':')
            ptag=parts[0].split('/')[1]
            if ptag==tag:
                scorelist.append(float(self.scores[metric][i]))
        scorearray=np.array(scorelist)
        print "Mean is "+str(np.mean(scorearray))
        print "SD is "+str(np.std(scorearray))
class analyser:

    def __init__(self,parameters):
        self.parameters=parameters
        self.myfiles={}

    def loadfile(self,filename):
        filepath=os.path.join(self.parameters['datadir'],filename)
        print "Processing "+filepath

        self.myfiles[filename]=scoretable(filepath)
        self.myfiles[filename].loadfile()

    def test(self,tag,metric,bf,fn):
        self.myfiles[fn].minus(self.myfiles[bf])
        self.myfiles[fn].average(tag,metric)

if __name__=="__main__":
    parameters=conf.configure(sys.argv)
    myAnalyser=analyser(parameters)
    basefilename='stats.diff.csv'
    otherfiles=['stats.diff.csv']
    tags=['N']
    metric='cosine'
    myAnalyser.loadfile(basefilename)
    for filename in otherfiles:
        myAnalyser.loadfile(filename)
        for tag in tags:
            print "Analysing for "+tag
            myAnalyser.test(tag,metric,basefilename,filename)