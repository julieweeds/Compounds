__author__ = 'juliewe'
#A possible solution for lab 4: extracting dependency parse information from an XML file

import xml.etree.ElementTree as ET

class Sentence:

    #the use of the Sentence object means that the XML for each sentence will only be processed once

    def __init__(self,id):
        self.id=id  #store the sentence id
        self.nounids=[] #initialise list of noun ids in the sentence
        self.lemmas={} #dictionary indexed by id to lemma
        self.deps=[]  #initialise list of dependencies where each dependency is a a tuple of (type, gov, dep)


    def process(self,sentence):
        #process the xml sentence and store relevant parts in the object for future reference
        for child in sentence:
            #print child.tag
            if child.tag=='tokens':
                #print child.attrib,child.text
                for token in child:
                    #print token.tag,token.attrib
                    id = int(token.attrib['id'])
                    for label in token:
                        #if label.tag=='lemma' or label.tag=='POS':
                        #    print label.tag,label.text
                        if label.tag=='lemma':
                            self.lemmas[id]=label.text
                        if label.tag=='POS' and label.text[0]=='N':
                            self.nounids.append(id)


            elif child.tag=='basic-dependencies':
                #print child.attrib,child.text
                for dep in child:
                    type=dep.attrib['type']
                    #if dep.attrib['type']=='dobj':
                    #    print dep.tag,dep.attrib
                    #    for label in dep:
                    #        print label.tag, label.attrib, label.text
                    for label in dep:
                        tag = label.tag
                        if tag == 'governor':
                            thisdepgov=int(label.attrib['idx'])
                        elif tag=='dependent':
                            thisdepdep=int(label.attrib['idx'])
                    if thisdepgov in self.nounids:
                        self.deps.append((type+'-HEAD',thisdepgov,thisdepdep))
                    if thisdepdep in self.nounids:
                        self.deps.append((type+'-DEP',thisdepdep,thisdepgov))

    def listnouns(self):
        #assuming the XML has already been processed, print out the lemmas associated with the nounids

        for id in self.nounids:
            print self.lemmas[id]

    def writenouns(self,outstream):
        #write the nouns in the sentence to the output stream specified
        if len(self.nounids) > 0:
            nounstring=self.lemmas[self.nounids[0]] #initialise output string with the first noun lemma
            for nid in self.nounids:
                nounstring+='\t'+self.lemmas[nid] #add a tab and the next noun lemma
        else:
            nounstring=''
        nounstring+='\n'
        output=nounstring.encode('utf-8')
        outstream.write(output)

    def printrels(self,rel):
        for (type,gov,dep) in self.deps:
            if type ==rel:
                print gov, self.lemmas[gov],':'+type+':',dep,self.lemmas[dep]

    def writerels(self,rel,outstream):
        for (type,gov,dep) in self.deps:
            if type == rel:

                outputstring= self.lemmas[gov]+'\t'+type+'\t'+self.lemmas[dep]+'\n'
                output=outputstring.encode('utf-8')
                outstream.write(output)



if __name__=='__main__':

    sentencepath='/Users/juliewe/Documents/workspace/Compounds/data/lexsub/trial/lexsub_trial.parsed.xml'
    print sentencepath
    sentids=['1','2']  #sentence ids I am interested in
    mysentences={}  #dictionary to store sentences in
    doall=True  #True if I want to process the whole file
    rels=['dobj-DEP']  #list of relations to extract


    xmltree=ET.parse(sentencepath)
    root = xmltree.getroot()

    for doc in root:
        #print doc.tag
        for item in doc:
            if item.tag == "sentences":
                for sentence in item:
                    id=sentence.attrib['id']
                    if id in sentids or doall: # is this a sentence I want to process
                        thissentence=Sentence(id)  #create new Sentence object
                        thissentence.process(sentence) #process the xml and store it in the sentence object
                        mysentences[id]=thissentence #store in dictionary using sentence id as key

    print "Stored "+str(len(mysentences.keys()))+" sentences"

    outpath=sentencepath+'.nouns'
    outpath2=sentencepath+'.rels'
    with open(outpath,'w') as outstream:
        with open(outpath2,'w') as outstream2:
            for id in mysentences.keys():
                thissentence= mysentences[id]

                print "Nouns in sentence id: "+str(id)
                thissentence.listnouns()
                thissentence.writenouns(outstream)
                print "Extracted relations:"
                for rel in rels:
                    thissentence.printrels(rel)
                    thissentence.writerels(rel,outstream2)

