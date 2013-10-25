__author__ = 'Julie'

import conf,os,sys
from compose import Composer

class Grapher(Composer):
    def makegraphs(self):
        if self.parameters['athome']:
            filepath=self.parameters['datadir']+'stats'+self.whoami+'.csv'
        else:
            filepath = os.path.join(self.parameters['datadir'],'stats'+self.whoami+'.csv')
        self.scores={}
        with open(filepath,'r') as instream:
            print "Reading filepath"
            metricline=instream.readline().rstrip()
            self.metrics=metricline.split(',')
            if len(self.metrics)<2:
                self.metrics=metricline.split('\t')
            phrasesline=instream.readline().rstrip()
            self.phrases=phrasesline.split(',')
            pmiline=instream.readline().rstrip()
            self.pmis=pmiline.split(',')
            for metric in self.metrics:
                scoreline=instream.readline().rstrip()
                self.scores[metric]=(scoreline.split(','))

            print "Metrics: "+str(len(self.metrics))
            print "Phrases: "+str(len(self.phrases))
            print "PMIs: "+str(len(self.pmis))
            for metric in self.metrics:
                print "Scores for "+metric+": "+str(len(self.scores[metric]))



if __name__ == "__main__":
    parameters=conf.configure(sys.argv)
    mygrapher=Grapher(parameters)
    mygrapher.makegraphs()