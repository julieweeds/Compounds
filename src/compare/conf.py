__author__ = 'juliewe'

import os

def configure(args):
    parameters={}

    #defaults
    parameters['testing']=False
    parameters['diff']=False
    parameters['mod']=False
    parameters['metric']='recall'
    parameters['datadir']='/Volumes/LocalScratchHD/juliewe/Documents/workspace/Compounds/data/wiki_nounsdeps'
    parameters['compop']='add'
    parameters['cached']=False

    for arg in args:
        if arg=='testing':parameters['testing']=True
        elif arg=='diff': parameters['diff']=True
        elif arg=='mod':parameters['mod']=True
        elif arg=='mult':parameters['compop']='mult'
        elif arg=='cached':parameters['cached']=True
        elif arg=='f':parameters['metric']='f'
        elif arg=='cosine':parameters['metric']='cosine'
    parameters = setfilenames(parameters)


    return parameters

def setfilenames(parameters):
    basename='vectors'
    parameters['phrasalpath']=os.path.join(parameters['datadir'],basename+'.phrases')
    if parameters['diff']:
        parameters['headfile']=basename+'.heads.diff'
        if parameters['mod']:
            parameters['modfile']=basename+'.mod.diff'
        else:
            parameters['modfile']=basename+'.heads.diff'
    else:
        parameters['headfile']=basename+'.heads'
        if parameters['mod']:
            parameters['modfile']=basename+'.mod'
        else:
            parameters['modfile']=basename+'.heads'
    parameters['headpath']=os.path.join(parameters['datadir'],parameters['headfile'])
    parameters['modpath']=os.path.join(parameters['datadir'],parameters['modfile'])
    parameters['mwpath']=os.path.join(parameters['datadir'],'multiwords_nn-DEP')
    return parameters