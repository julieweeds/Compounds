__author__ = 'juliewe'

import os

def configure(args):
    parameters={}

    #defaults
    parameters['testing']=False
    parameters['diff']=False
    parameters['funct']=False
    parameters['mod']=False
    parameters['metric']=['cosine']
    #parameters['datadir']='/Volumes/LocalScratchHD/juliewe/Documents/workspace/Compounds/data/wiki_nounsdeps'
    parameters['compop']='add'
    parameters['cached']=False
    parameters['apollo']=False
    parameters['athome']=False
    parameters['usefile']='train'
    parameters['ftype']='deps'
    parameters['pmi']=False
    parameters['inversefeatures']={'nn-DEP':'nn-HEAD','nn-HEAD':'nn-DEP','amod-DEP':'amod-HEAD','amod-HEAD':'amod-DEP','':''}
    parameters['featurematch']='amod-HEAD'
    parameters['association']='pmi'
    parameters['composefirst']=True
    parameters['output']='new_results.csv'
    parameters['graphing']=False
    parameters['miroflag']=False
    parameters['NNcompflag']=False
    parameters['switch']=False
    parameters['literalityscore']='compound'
    parameters['msource']='r8'
    parameters['freqfile']='vectors.train.PHRASES.entries.strings'
    parameters['wn_wiki']=False
    parameters['wins']=False
    parameters['collocatefile']='multiwords.'

    for arg in args:
        if arg=='testing':parameters['testing']=True
        elif arg=='diff': parameters['diff']=True
        elif arg=='funct':
            parameters['funct']=True
            parameters['mod']=True  #funct and mod are aliases for same 'functional modifier' parameter
        elif arg=='nonfunct':
            parameters['funct']=False
            parameters['mod']=False
        elif arg=='nodiff':parameters['diff']=False
        elif arg=='mod':
            parameters['mod']=True
            parameters['funct']=True
        elif arg=='switch':
            parameters['switch']=True
        elif arg=='leftliteral':
            parameters['literalityscore']='left'
        elif arg=='rightliteral':
            parameters['literalityscore']='right'
        elif arg=='compliteral':
            parameters['literalityscore']='compound'
        elif arg=='NNcomp':
            parameters['NNcompflag']=True
            parameters['usefile']='all'
            parameters['compop']='mult'
            parameters['funct']=True
            parameters['mod']=True #obsolete
            parameters['association']='pmi'
            parameters['composefirst']=False
            parameters['composesecond']=True
            parameters['diff']=False
            parameters['featurematch']='nn-HEAD'
            parameters['phrasetype']='NNs'
            parameters['postype']='nouns'
            parameters['altpostype']='nouns'
        elif arg=='wn_wiki':
            parameters['wn_wiki']=True
            parameters['usefile']=parameters['phrasetype']
            parameters['compop']='gm'
            parameters['funct']=True
            parameters['association']='pmi'
            parameters['diff']=True
            parameters['composefirst']=True
            parameters['composesecond']=False
            parameters['collocatefile']='multiwords.wn_wiki.'


        elif arg=='train':
            parameters['vsource']='train'
            if parameters['switch']:
                parameters['vsource2']='test'
            else:
                parameters['vsource2']='train'
        elif arg=='test':
            parameters['vsource']='test'
            if parameters['switch']:
                parameters['vsource2']='train'
            else:
                parameters['vsource2']='test'
        elif arg=='mult':parameters['compop']='mult'
        elif arg=="selectself":parameters['compop']='selectself'
        elif arg=="selectother":parameters['compop']='selectother'
        elif arg=='add':parameters['compop']='add'
        elif arg=='gm':parameters['compop']='gm'
        elif arg=="min":parameters['compop']='min'
        elif arg=='max':parameters['compop']='max'
        elif arg=='cached':parameters['cached']=True
        elif arg=='f':parameters['metric']=setadd(parameters['metric'],'f')
        elif arg=='precision':parameters['metric']=setadd(parameters['metric'],'precision')
        elif arg=='recall':parameters['metric']=setadd(parameters['metric'],'recall')
        elif arg=='cosine':parameters['metric']=setadd(parameters['metric'],'cosine')
        elif arg=='weighted_recall':parameters['metric']=setadd(parameters['metric'],'weighted_recall')
        elif arg=='weighted_precision':parameters['metric']=setadd(parameters['metric'],'weighted_precision')
        elif arg=='apollo':parameters['apollo']=True
        elif arg=='athome':parameters['athome']=True
        elif arg=='wins':parameters['ftype']='wins'
        elif arg=='pmi':parameters['association']='pmi'
        elif arg=='composefirst':parameters['composefirst']=True
        elif arg=='composesecond':parameters['composefirst']=False
        elif arg=='lmi':parameters['association']='lmi'
        elif arg=='npmi':parameters['association']='npmi'
        elif arg=='raw':parameters['association']='raw'
        elif arg=='graphing':parameters['graphing']=True
        elif arg=='miro':
            parameters['miroflag']=True
            parameters['association']='raw'
            parameters['funct']=True
            parameters['mod']=True #obsolete
            parameters['compop']='mult'
            parameters['diff']=False
            parameters['composesecond']=True
            parameters['usefile']='all'
            parameters['vsource']='giga'
        elif arg=="NNs":
            parameters['featurematch']='nn-HEAD'
            parameters['phrasetype']='NNs'
            parameters['postype']='nouns'
            parameters['altpostype']='nouns'
        elif arg=="ANs":
            parameters['featurematch']='amod-HEAD'
            parameters['phrasetype']='ANs'
            parameters['postype']='adjs'
            parameters['altpostype']='nouns'
        elif arg=="wiki":
            parameters['vsource']='wikiPOS'
        elif arg=='giga':
            parameters['vsource']='exp10'
        elif arg=='movies':
            parameters['msource']='movies'
        elif arg=='r8':
            parameters['msource']=='r8'
        elif arg=='wins':
            parameters['wins']=True

    parameters = setfilenames(parameters)

    return parameters

def setfilenames(parameters):
    basename='vectors.'+parameters['usefile']
    basename2=basename
    parentdir='/Volumes/LocalScratchHD/juliewe/Documents/workspace/Compounds/data/'
    if parameters['athome']:
        parentdir='/Users/juliewe/Documents/workspace/Compounds/data/'
    if parameters['apollo']:
        parentdir='/mnt/lustre/scratch/inf/juliewe/Compounds/data/'

    parameters['datadir']=parentdir+'ANcompounds/'+parameters['ftype']+'/adjs'
    parameters['altdatadir']=parentdir+'ANcompounds/'+parameters['ftype']+'/nouns'
    if parameters['NNcompflag']:
        parameters['datadir']=parentdir+'ijcnlp_compositionality_data/NNs/nouns'
        parameters['altdatadir']=parameters['datadir']
        basename='vectors.'+parameters['vsource']
        basename2='vectors.'+parameters['vsource2']
    if parameters['miroflag']:
        parentdir+='miro0314/'
        if parameters['msource']=='movies':
            parentdir+='movies/'
        parameters['datadir']=parentdir+parameters['phrasetype']+'/'+parameters['postype']
        parameters['altdatadir']=parentdir+parameters['phrasetype']+'/'+parameters['postype']
        basename=basename+'.'+parameters['vsource']
        basename2=basename
    if parameters['wn_wiki']:
        parameters['datadir']=parentdir+'WNcompounds/'+parameters['phrasetype']+'/'+parameters['postype']
        parameters['altdatadir']=parentdir+'WNcompounds/'+parameters['phrasetype']+'/'+parameters['altpostype']
        if parameters['wins']:
            parameters['vsource']="wins"
        else:
            parameters['vsource']="deps"
        basename=basename+'.'+parameters['vsource']
        basename2=basename

    parameters['phrasalpath']=os.path.join(parameters['datadir'],basename2+'.PHRASES')
    if parameters['diff']:
        parameters['constituentfile']=basename+'.CONSTITUENTS.DIFF'
    else:
        parameters['constituentfile']=basename+'.CONSTITUENTS'
    parameters['constituentpath']=os.path.join(parameters['datadir'],parameters['constituentfile'])
    parameters['mwpath']=os.path.join(parameters['datadir'],parameters['collocatefile']+parameters['usefile'])


    parameters['featurefile']='features.strings'
    if parameters['miroflag']:
        parameters['featurefile']=parameters['vsource']+'.'+parameters['featurefile']
    if parameters['NNcompflag']:
        parameters['featurefile']='wikiPOS.'+parameters['vsource']+'.'+parameters['featurefile']
    parameters['freqfile']=basename2+'.PHRASES.entries.strings'

    #parameters['featurepath']=os.path.join(parameters['altdatadir'],parameters['featurefile'])

    return parameters

def setadd(myset,item):

    if item not in myset:
        myset.append(item)
    return myset