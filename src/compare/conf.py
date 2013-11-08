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
    parameters['datadir']='/Volumes/LocalScratchHD/juliewe/Documents/workspace/Compounds/data/wiki_nounsdeps'
    parameters['compop']='add'
    parameters['cached']=False
    parameters['apollo']=False
    parameters['athome']=False

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
        elif arg=='cached':parameters['cached']=True
        elif arg=='f':parameters['metric']=setadd(parameters['metric'],'f')
        elif arg=='precision':parameters['metric']=setadd(parameters['metric'],'precision')
        elif arg=='recall':parameters['metric']=setadd(parameters['metric'],'recall')
        elif arg=='cosine':parameters['metric']=setadd(parameters['metric'],'cosine')
        elif arg=='apollo':parameters['apollo']=True
        elif arg=='athome':parameters['athome']=True
    parameters = setfilenames(parameters)

    return parameters

def setfilenames(parameters):
    basename='vectors'
    if parameters['apollo']:
        parameters['datadir']='/mnt/lustre/scratch/inf/juliewe/Compounds/data/wiki_nounsdeps'
    if parameters['athome']:
        parameters['datadir']='C:/Users/Julie/Documents/Github/Compounds/data/wiki_nounsdeps/'
    parameters['phrasalpath']=os.path.join(parameters['datadir'],basename+'.phrases')
    if parameters['diff']:
        parameters['headfile']=basename+'.NF.DIFF'
        if parameters['funct']:
            parameters['modfile']=basename+'.FMOD.DIFF'
        else:
            parameters['modfile']=basename+'.NF.DIFF'
    else:
        parameters['headfile']=basename+'.NFHEAD'
        if parameters['funct']:
            parameters['modfile']=basename+'.FMOD'
        else:
            parameters['modfile']=basename+'.NFMOD'
    parameters['headpath']=os.path.join(parameters['datadir'],parameters['headfile'])
    parameters['modpath']=os.path.join(parameters['datadir'],parameters['modfile'])
    parameters['mwpath']=os.path.join(parameters['datadir'],'multiwords_nn-DEP')
    return parameters

def setadd(myset,item):

    if item not in myset:
        myset.append(item)
    return myset