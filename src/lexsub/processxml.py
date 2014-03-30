__author__ = 'juliewe'

#aim is to process the xml data files for the lexical substitution task

import sys,os,io
from conf import configure
import xml.etree.ElementTree as ET


if __name__=='__main__':
    parameters=configure(sys.argv)
    filepath=os.path.join(parameters['datadir'],parameters['datafile'])
    #print "Processing file "+filepath

    if parameters['testing']:
        instream=open(filepath,'r')
        instream.close()
        print 'File present'

    sentencepath=filepath+'.sents'
    targetpath=filepath+'.targs'

    tree = ET.parse(filepath)
    doc=tree.getroot()

    with open(sentencepath,'w') as sstream:
        with open(targetpath,'w') as tstream:


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
                                currentposition=1
                                currentsentence=head.text
                            if head.tail is not None:
                                currentsentence+=head.tail


                            print currenttarget,currentid,currenthead,currentposition
                            tstream.write(currenttarget+'\t'+str(currentid)+'\t'+currenthead+'\t'+str(currentposition)+'\n')
                            print currentsentence
                            output=currentsentence.encode('utf-8')+'\n'
                            sstream.write(output)

    # print doc.findall(".")
    #
    # heads= doc.findall("./lexelt/instance/context/head")
    # for head in heads:
    #     print head.tag,head.attrib
