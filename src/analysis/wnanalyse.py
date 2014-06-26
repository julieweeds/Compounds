__author__ = 'juliewe'

import sys,ConfigParser,ast,os,numpy as np
import scipy.stats as stats
import pylab as pb

class Correlates:

    def __init__(self,configfile):

        config=ConfigParser.RawConfigParser()
        config.read(configfile)
        self.datadir=ast.literal_eval(config.get('default','datadir'))
        self.datafiles=ast.literal_eval(config.get('correlate','datafiles'))
        if config.get('default','testing')=='True':
            self.verbose=1
        else:
            self.verbose=0
        if config.get('default','graphing')=='True':
            self.graphing=True
        else:
            self.graphing=False
        self.headscores={}
        self.phrasescores={}
        self.neighbours={}


    def readafile(self,datafile):

        datapath=os.path.join(self.datadir,datafile)

        self.headscores[datafile]={}
        self.phrasescores[datafile]={}
        self.neighbours[datafile]={}
        with open(datapath) as instream:
            linesread=0
            for line in instream:
                line=line.rstrip()
                linesread+=1
                fields=line.split('\t')
                if len(fields)==4:
                    phrase=fields[0]
                    self.phrasescores[datafile][phrase]=float(fields[1])
                    self.headscores[datafile][phrase]=float(fields[2])
                    self.neighbours[datafile][phrase]=ast.literal_eval(fields[3])

                elif self.verbose>2:
                    print "Ignoring ",line
            print "Read "+str(linesread)+" lines from "+datafile
            print "Length of phrasescores dictionary is "+str(len(self.phrasescores[datafile]))


    def correlate(self,df):
        print "Processing "+df
        xs=[]
        ys=[]
        for phrase in self.phrasescores[df].keys():
            xs.append(self.phrasescores[df][phrase])
            ys.append(self.headscores[df][phrase])

        self.dostats(xs,ys)

    def dostats(self,xs,ys):

        xarray=np.array(xs)
        yarray=np.array(ys)

        xmean=np.mean(xarray)
        xstdev=np.std(xarray)
        ymean=np.mean(yarray)
        ystdev=np.std(yarray)
        print "Mean and standard deviation for xs",xmean,xstdev
        print "Mean and standard deviation for ys",ymean,ystdev

        pearsonr=stats.pearsonr(xarray,yarray)
        spearmanr=stats.spearmanr(xarray,yarray)
        print "Pearson correlation coefficient is",pearsonr
        print "Spearman correlation coefficient is",spearmanr

        if self.graphing:
            pb.scatter(xarray,yarray)
            pb.show()

    def crosscorrelate(self,df1,df2):
        print "Cross-correlating",df1,df2

        xs=[]
        ys=[]
        for phrase in self.phrasescores[df1].keys():
            if self.phrasescores[df2].get(phrase)!=None:
                xs.append(self.phrasescores[df1][phrase])
                ys.append(self.phrasescores[df2][phrase])

        self.dostats(xs,ys)


        print "Differencing phrasescores and headscores",df1,df2
        xs=[]
        ys=[]
        for phrase in self.phrasescores[df1].keys():
            if self.phrasescores[df2].get(phrase)!=None:
                xs.append(self.phrasescores[df1][phrase]-self.headscores[df1][phrase])
                ys.append(self.phrasescores[df2][phrase]-self.headscores[df2][phrase])
        self.dostats(xs,ys)


    def run(self):

        for df in self.datafiles:
            self.readafile(df)
            self.correlate(df)

        for i in range(0,len(self.datafiles),1):
            for j in range(i+1,len(self.datafiles),1):
                print i,j
                self.crosscorrelate(self.datafiles[i],self.datafiles[j])



if __name__=='__main__':

    myCorrelates=Correlates(sys.argv[1])
    myCorrelates.run()