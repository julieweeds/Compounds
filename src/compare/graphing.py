__author__ = 'Julie'

import conf,os,sys
import numpy as np
from compose import Composer
import pylab as pl

def listfloat(inlist):
    outlist=[]
    for item in inlist:
        outlist.append(float(item))
    return outlist

class Grapher(Composer):
    k = 5
    def makegraphs(self):
        if self.parameters['athome']:
            filepath=self.parameters['datadir']+'stats'+self.whoami+'.csv'
        else:
            filepath = os.path.join(self.parameters['datadir'],'stats'+self.whoami+'.csv')
        self.scores={}
        with open(filepath,'r') as instream:
            print "Reading "+filepath
            metricline=instream.readline().rstrip()
            self.metrics=metricline.split(',')
            if len(self.metrics)<2:
                self.metrics=metricline.split('\t')
            phrasesline=instream.readline().rstrip()
            self.phrases=phrasesline.split(',')[0:-1]
            pmiline=instream.readline().rstrip()
            self.pmis=listfloat(pmiline.split(',')[0:-1])
            for metric in self.metrics:
                scoreline=instream.readline().rstrip()
                self.scores[metric]=listfloat((scoreline.split(','))[0:-1])

            print "Metrics: "+str(len(self.metrics))
            print "Phrases: "+str(len(self.phrases))
            print "PMIs: "+str(len(self.pmis))
            for metric in self.metrics:
                print "Scores for "+metric+": "+str(len(self.scores[metric]))
                self.bookends(metric)
                self.scatter(self.pmis,self.scores[metric],metric)



    def scatter(self,xlist,ylist,info):
        #xp = np.linspace(xs)
        xs =np.array(xlist)
        ys =np.array(ylist)
        #print xs
        #print ys
        pl.scatter(xs,ys)
        v=pl.axis()
        newv=[0,v[1],0,v[3]]
        pl.axis(newv)
        pl.xlabel('PPMI')
        pl.ylabel(info)
        pl.title(self.whoami)
        pl.show()

    def bookends(self,metric):

        tuples=sorted([t for t in zip(self.scores[metric],self.phrases,self.pmis)])
        print tuples[0:Grapher.k]
        print tuples[-Grapher.k:-1],tuples[-1]

if __name__ == "__main__":
    parameters=conf.configure(sys.argv)
    mygrapher=Grapher(parameters)
    mygrapher.makegraphs()