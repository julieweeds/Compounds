__author__ = 'juliewe'

import os

def configure(args):
    parameters={}

    #defaults
    parameters['testing']=False
    parameters['diff']=False
    parameters['funct']=True
    parameters['mod']=False
    parameters['metric']=['recall','precision','cosine','weighted_recall']
    #parameters['datadir']='/Volumes/LocalScratchHD/juliewe/Documents/workspace/Compounds/data/wiki_nounsdeps'
    parameters['compop']='add'
    parameters['cached']=False
    parameters['apollo']=False
    parameters['athome']=False
    parameters['usefile']='train'
    parameters['ftype']='deps'
    parameters['pmi']=False
    parameters['inversefeatures']={'nn-DEP':'nn-HEAD','nn-HEAD':'nn-DEP','amod-DEP':'amod-HEAD','amod-HEAD':'amod-DEP'}

    for arg in args:
        if arg=='testing':parameters['testing']=True
        elif arg=='diff': parameters['diff']=True
        elif arg=='funct':
            parameters['funct']=True
            parameters['mod']=True  #funct and mod are aliases for same 'functional modifier' parameter
        elif arg=='mod':
            parameters['mod']=True
            parameters['funct']=True
        elif arg=='mult':parameters['compop']='mult'
        elif arg=="selecthead":parameters['compop']='selecthead'
        elif arg=="selectmod":parameters['compop']='selectmod'
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
        elif arg=='pmi':parameters['pmi']=True #compute PPMI then compose (alternative: compose then compute PPMI)
    parameters = setfilenames(parameters)

    return parameters

def setfilenames(parameters):
    basename='vectors.'+parameters['usefile']
    parameters['datadir']='/Volumes/LocalScratchHD/juliewe/Documents/workspace/Compounds/data/ANcompounds/'+parameters['ftype']+'/adjs'
    if parameters['apollo']:
        parameters['datadir']='/mnt/lustre/scratch/inf/juliewe/Compounds/data/ANcompounds/'+parameters['ftype']+'/adjs'
    if parameters['athome']:
        parameters['datadir']='C:/Users/Julie/Documents/Github/Compounds/data/wiki_nounsdeps/'
    parameters['phrasalpath']=os.path.join(parameters['datadir'],basename+'.PHRASES')
    if parameters['diff']:
        parameters['constituentfile']=basename+'.CONSTITUENTS.DIFF'
    else:
        parameters['constituentfile']=basename+'.CONSTITUENTS'
    parameters['constituentpath']=os.path.join(parameters['datadir'],parameters['constituentfile'])
    parameters['mwpath']=os.path.join(parameters['datadir'],'multiwords.'+parameters['usefile']+'.tagged')

    parameters['altdatadir']='/Volumes/LocalScratchHD/juliewe/Documents/workspace/Compounds/data/ANcompounds/'+parameters['ftype']+'/nouns'
    parameters['featurefile']='events.strings_depcol'
    parameters['featurepath']=os.path.join(parameters['altdatadir'],parameters['featurefile'])

    return parameters

def setadd(myset,item):

    if item not in myset:
        myset.append(item)
    return myset