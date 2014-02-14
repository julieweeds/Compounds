__author__ = 'juliewe'

import os

def configure(args):
    parameters={}

    #defaults
    parameters['testing']=False
    parameters['diff']=False
    parameters['funct']=False
    parameters['mod']=False
    parameters['metric']=['recall','precision','cosine']
    #parameters['datadir']='/Volumes/LocalScratchHD/juliewe/Documents/workspace/Compounds/data/wiki_nounsdeps'
    parameters['compop']='add'
    parameters['cached']=False
    parameters['apollo']=False
    parameters['athome']=False
    parameters['usefile']='train'
    parameters['ftype']='deps'
    parameters['pmi']=False
    parameters['inversefeatures']={'nn-DEP':'nn-HEAD','nn-HEAD':'nn-DEP','amod-DEP':'amod-HEAD','amod-HEAD':'amod-DEP'}
    parameters['featurematch']='amod-HEAD'
    parameters['association']='pmi'
    parameters['composefirst']=True
    parameters['output']='more_results.csv'
    parameters['graphing']=False
    parameters['miroflag']=False

    for arg in args:
        if arg=='testing':parameters['testing']=True
        elif arg=='diff': parameters['diff']=True
        elif arg=='funct':
            parameters['funct']=True
            parameters['mod']=True  #funct and mod are aliases for same 'functional modifier' parameter
        elif arg=='nonfunct':
            parameters['funct']=False
            parameters['mod']=False
        elif arg=='mod':
            parameters['mod']=True
            parameters['funct']=True
        elif arg=='mult':parameters['compop']='mult'
        elif arg=="selectself":parameters['compop']='selectself'
        elif arg=="selectother":parameters['compop']='selectother'
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
            parameters['composefirst']=True
            parameters['usefile']='all'
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
    parameters = setfilenames(parameters)

    return parameters

def setfilenames(parameters):
    basename='vectors.'+parameters['usefile']
    parameters['datadir']='/Volumes/LocalScratchHD/juliewe/Documents/workspace/Compounds/data/ANcompounds/'+parameters['ftype']+'/adjs'
    parameters['altdatadir']='/Volumes/LocalScratchHD/juliewe/Documents/workspace/Compounds/data/ANcompounds/'+parameters['ftype']+'/nouns'
    if parameters['apollo']:
        parameters['datadir']='/mnt/lustre/scratch/inf/juliewe/Compounds/data/ANcompounds/'+parameters['ftype']+'/adjs'
        parameters['altdatadir']='/mnt/lustre/scratch/inf/juliewe/Compounds/data/ANcompounds/'+parameters['ftype']+'/nouns'
    if parameters['athome']:
        #parameters['datadir']='C:/Users/Julie/Documents/Github/Compounds/data/wiki_nounsdeps/'
        parameters['datadir']='/Users/juliewe/Documents/workspace/Compounds/data/ANcompounds/'+parameters['ftype']+'/adjs'
    if parameters['miroflag']:
        parameters['datadir']='/mnt/lustre/scratch/inf/juliewe/Compounds/data/miro/'+parameters['phrasetype']+'/'+parameters['postype']
        parameters['altdatadir']='/mnt/lustre/scratch/inf/juliewe/Compounds/data/miro/'+parameters['phrasetype']+'/'+parameters['postype']
        basename=basename+'.'+parameters['vsource']
    parameters['phrasalpath']=os.path.join(parameters['datadir'],basename+'.PHRASES')
    if parameters['diff']:
        parameters['constituentfile']=basename+'.CONSTITUENTS.DIFF'
    else:
        parameters['constituentfile']=basename+'.CONSTITUENTS'
    parameters['constituentpath']=os.path.join(parameters['datadir'],parameters['constituentfile'])
    parameters['mwpath']=os.path.join(parameters['datadir'],'multiwords.'+parameters['usefile'])


    parameters['featurefile']='features.strings'
    #parameters['featurepath']=os.path.join(parameters['altdatadir'],parameters['featurefile'])

    return parameters

def setadd(myset,item):

    if item not in myset:
        myset.append(item)
    return myset