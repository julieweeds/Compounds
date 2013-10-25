__author__ = 'Julie'

import conf,os,sys
from compose import Composer

class Grapher(Composer):
    def makegraphs(self):
        filepath = os.path.join(self.parameters['datadir'],'stats'+self.whoami+'.csv')
        self.metrics=[]
        self.phrases=[]
        self.pmis=[]
        self.scores=[]
        with open(filepath,'r') as instream:
            print "Reading filepath"
            metricline=instream.readline().rstrip()

if __name__ == "__main__":
    parameters=conf.configure(sys.argv)
    mygrapher=Grapher()
    mygrapher.makegraphs()