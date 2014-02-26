__author__ = 'juliewe'
import sys,os
from conf import configure
import xml.etree.ElementTree as ET

if __name__=='__main__':
    #parameters=configure(sys.argv)
    #sentencefile=parameters['basename']+'.parsed.xml'
    #sentencepath=os.path.join(parameters['datadir'],sentencefile)
    sentencepath='/Users/juliewe/Documents/workspace/Compounds/data/lexsub/trial/lexsub_trial.parsed.xml'
    print sentencepath

    xmltree=ET.parse(sentencepath)
    root = xmltree.getroot()

    for doc in root:
        #print doc.tag
        for item in doc:
            if item.tag == "sentences":
                for sentence in item:
                    nounids=[]
                    lemmas={}
                    deps=[]
                    if sentence.attrib['id']=='1':
                        print sentence.attrib
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
                                            lemmas[id]=label.text
                                        if label.tag=='POS' and label.text[0]=='N':
                                            nounids.append(id)


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
                                    if thisdepgov in nounids:
                                        deps.append((type+'-HEAD',thisdepgov,thisdepdep))
                                    if thisdepdep in nounids:
                                        deps.append((type+'-DEP',thisdepdep,thisdepgov))
                        for id in nounids:
                            print lemmas[id]

                        for (type,gov,dep) in deps:
                            if type =='dobj-DEP':

                                print gov, lemmas[gov],type+':'+lemmas[dep]
                            if type =='nsubj-DEP':
                                print gov, lemmas[gov],type+':'+lemmas[dep]

