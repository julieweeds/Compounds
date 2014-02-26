__author__ = 'juliewe'

from conf import configure
import sys,os

class Compound:

    tagmatching={'n':'N','v':'V','a':'J','r':'R'}

    def __init__(self,compstring,wdelim=' ',tdelim='-'):

        self.compstring=compstring
        self.constituents=[]
        words=self.compstring.split(wdelim)

        for word in words:
            parts=word.split(tdelim)
            self.constituents.append((parts[0],parts[1]))

    def getToken(self,which=1):

        return self.constituents[which-1][0]+'/'+Compound.tagmatching[self.constituents[which-1][1]]

    def getDisplay(self):
        #print self.constituents
        #print self.constituents[0], self.constituents[1]
        mydisplay=self.constituents[0][0]+'/'+Compound.tagmatching[self.constituents[0][1]]
        for constituent in self.constituents[1:]:
            mydisplay+='\t'+constituent[0]+'/'+Compound.tagmatching[constituent[1]]
        return mydisplay

    def getWNcomp(self):

        comp = self.constituents[0][0]
        for constituent in self.constituents[1:]:
            comp+='_'+constituent[0]
        tag=Compound.tagmatching[self.constituents[-1][1]]
        return comp+'/'+tag




class IjcnlpReader:

    def __init__(self,filepath):

        self.filepath=filepath
        self.scores={}
        self.loadfile()

    def loadfile(self):

        with open(self.filepath,'r') as instream:
            linesread=0
            for line in instream:
                linesread+=1
                if linesread>1:  #ignore header line
                    fields=line.rstrip().split('\t')
                    compstring=fields[0]
                    self.scores[compstring]={}
                    for (label,score) in zip(self.labels,fields[1].split(' ')):
                        #print compstring,label,score
                        self.scores[compstring][label]=float(score)
                else:
                    fields=line.rstrip().split('\t')
                    self.labels=fields[1].split(' ')


    def display(self,label='Cpd_mean'):
        for key in self.scores.keys():

            text=Compound(key).getWNcomp()
            text+='\t'+str(self.scores[key][label])
            print text

    def getScores(self,inlist,label='Cpd_mean'):
        scores=[]
        for key in self.scores.keys():
            text=Compound(key).getWNcomp()
            if text in inlist:
                scores.append((text,self.scores[key][label]))
        return scores

    def getWNComps(self):

        comps=[]
        for key in self.scores.keys():
            comps.append(Compound(key).getWNcomp())
        return comps

    def getWNwords(self,which):

        words=[]
        for key in self.scores.keys():
            words.append(Compound(key).getToken(which=which))
        return words


if __name__=='__main__':

    parameters=configure(sys.argv)

    filepath=os.path.join(parameters['parentdir'],parameters['datadir'],parameters['datafile'])
    myReader=IjcnlpReader(filepath)
    myReader.display()