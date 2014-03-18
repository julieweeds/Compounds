__author__ = 'juliewe'

#aim is to process the xml data files for the lexical substitution task

import sys,os,io
from conf import configure
import xml.etree.ElementTree as ET

def findlength(sentence):
        #process the xml sentence and compute length
        count=0
        for child in sentence:
            #print child.tag
            if child.tag=='tokens':
                #print child.attrib,child.text
                for token in child:
                    #print token.tag,token.attrib
                    id = int(token.attrib['id'])
                    count+=1
        return count

if __name__=='__main__':
    parameters=configure(sys.argv)
    filepath=os.path.join(parameters['datadir'],parameters['datafile'])
    parsepath=os.path.join(parameters['datadir'],parameters['parsefile'])
    #print "Processing file "+filepath

    if parameters['testing']:
        instream=open(filepath,'r')
        instream.close()
        print 'File present'

    outpath=filepath+'.map'

    tree = ET.parse(filepath)
    doc=tree.getroot()


    instances={}
    idorder=[]
    for item in doc:
        #print item.tag, item.attrib
        currenttarget=item.attrib['item']
        for id in item:
            #print '\t',id.tag,id.attrib
            currentid=id.attrib['id']
            for context in id:
                #print '\t\t',context.tag, context.attrib,context.text
                for head in context:
                    #print '\t\t\t',head.tag,head.attrib,head.text,head.tail
                    currenthead=head.text
                    #currentsentence=str(context.text)+str(head.text)+str(head.tail)
                    if context.text is not None:
                        currentposition=len(context.text.split(' '))
                        currentsentence=context.text+head.text
                    else:
                        currentposition=0
                        currentsentence=head.text
                    if head.tail is not None:
                        currentsentence+=head.tail


                    #print currenttarget,currentid,currenthead,currentposition
                  #  tstream.write(currenttarget+'\t'+str(currentid)+'\t'+currenthead+'\t'+str(currentposition)+'\n')
                    #print currentsentence
                    instances[currentid]=len(currentsentence.split(' '))
                    idorder.append(currentid)
                    output=currentsentence.encode('utf-8')+'\n'
                  #  sstream.write(output)

    listids=list(idorder)
    idorder.reverse()
    #print idorder


    #print '1', instances['1']
    #print '2', instances['2']
    xmltree=ET.parse(parsepath)
    root = xmltree.getroot()

    currentid=idorder.pop()
    mapids={}
    currentmap=[]
    addon=0

    for doc in root:
        #print doc.tag
        for item in doc:
            if item.tag == "sentences":
                for sentence in item:
                    id=sentence.attrib['id']
                    #print id, findlength(sentence)
                    instancelength=instances[currentid]
                    sentencelength=findlength(sentence)
                    currentmap.append(id)
                    diff=instancelength-(sentencelength+addon)


                    print currentid,str(sentencelength+addon),instancelength,diff,currentmap
                    if diff<5 or len(currentmap)>7:
                        mapids[currentid]=currentmap
                        if len(idorder)>0:
                            currentid=idorder.pop()

                        currentmap=[]
                        addon=0
                    else:
                        #print currentid
                        addon+=sentencelength

    #print mapids
    #print currentid
    with open(outpath,'w') as outstream:
        for id in listids:
            outstream.write(id+'\t::')
            for sid in mapids[id]:
                outstream.write('\t'+sid)
            outstream.write('\n')

    # print doc.findall(".")
    #
    # heads= doc.findall("./lexelt/instance/context/head")
    # for head in heads:
    #     print head.tag,head.attrib
