__author__ = 'juliewe'

def configure(args):

    parameters={}
    parameters['pos']='N'
    parameters['testing']=False
    parameters['local']=True
    parameters['apollo']=False
    parameters['athome']=False
    parameters['featurematch']='nn-DEP'
    parameters['seed']=37
    parameters['inversefeatures']={'nn-DEP':'nn-HEAD','nn-HEAD':'nn-DEP','amod-DEP':'amod-HEAD','amod-HEAD':'amod-DEP','':''}
    parameters['featurematch']='nn-DEP'
    parameters['k']=5
    parameters['mwfile']='multiwords.all'
    parameters['neighsource']=''
    parameters['NNcompflag']=True
    parameters['literalityscore']='compound'
    parameters['wnsim']='path'
    parameters['dohead']=False
    parameters['domod']=False
    parameters['typelist']=['phrase','head','mod']
    parameters['random']=False
    parameters['vsource']='deps'
    parameters['phrasetype']='NNs'

    #parameters['typelist']=['phrase']

    for i,arg in enumerate(args):
        if arg=='nouns' or arg=='N': #obsolete - use NNs or ANs
            parameters['pos']='N'
            parameters['posword']='noun'
        elif arg=='adjs' or arg=='J':
            parameters['pos']='J'
            parameters['posword']='adj'
        elif arg=='NNs':
            parameters['phrasetype']='NNs'
            parameters['pos']='N'
            parameters['posword']='noun'
            parameters['altpos']='N'
            parameters['altposword']='noun'
        elif arg=='ANs':
            parameters['phrasetype']='ANs'
            parameters['pos']='N'
            parameters['posword']='noun'
            parameters['altpos']='J'
            parameters['altposword']='adj'

        elif arg=='testing':
            parameters['testing']=True
        elif arg=='filter':
            parameters['filter']=True
        elif arg=='setup':
            parameters['setup']=True
            parameters['deps'].append('word')
        elif arg=='local':
            parameters['local']=True
            parameters['apollo']=False
            parameters['athome']=False
        elif arg=='athome':
            parameters['athome']=True
            parameters['local']=False
            parameters['apollo']=False
        elif arg=='apollo':
            parameters['apollo']=True
            parameters['local']=False
            parameters['athome']=False
        elif arg=='obs' or arg =='observed':
            parameters['neighsource']='observed'
        elif arg=='comp_mult':
            parameters['neighsource']='comp_mult'
        elif arg=='comp_gm':
            parameters['neighsource']='comp_gm'
        elif arg=='comp_min':
            parameters['neighsource']='comp_min'
        elif arg=='comp_nfmult':
            parameters['neighsource']='comp_nfmult'
        elif arg=='diffcomp_min':
            parameters['neighsource']='diffcomp_min'
        elif arg=='diffcomp_mult':
            parameters['neighsource']='diffcomp_mult'
        elif arg=='diffcomp_gm':
            parameters['neighsource']='diffcomp_gm'
        elif arg=='diffcomp_nfgm':
            parameters['neighsource']='diffcomp_nfgm'
        elif arg=='diffcomp_nfmult':
            parameters['neighsource']='diffcomp_nfmult'
        elif arg=='unigram':
            parameters['neighsource']='unigram'
            parameters['typelist']=['head']
 #           parameters['dohead']=True
            parameters['unigram']=True
        elif arg=='setk':
            parameters['k']=int(args[i+1])
        elif arg=='lin':
            parameters['wnsim']='lin'
        elif arg=='jcn':
            parameters['wnsim']='jcn'
        elif arg=='head':
            parameters['dohead']=True
            parameters['dopos']=parameters['posword']
        elif arg=='mod':
            parameters['domod']=True
            parameters['dopos']=parameters['altposword']
        elif arg=='random':
            parameters['random']=True
        elif arg=='wn_wiki':
            parameters['wn_wiki']=True
        elif arg=='deps':
            parameters['vsource']='deps'
        elif arg=='wins':
            parameters['vsource']='wins'

    parameters=setfilenames(parameters)
    return parameters

def setfilenames(parameters):

    if parameters['apollo']:
        parameters['datadir']='/mnt/lustre/scratch/inf/juliewe/FeatureExtractionToolkit/feoutput-deppars'
        parameters['compoundparentdir']='/mnt/lustre/scratch/inf/juliewe/Compounds/data/'
    if parameters['local']:
        parameters['compoundparentdir']='/Volumes/LocalScratchHD/juliewe/Documents/workspace/Compounds/data/'

    if parameters['athome']:
        parameters['compoundparentdir']='/Users/juliewe/Documents/workspace/Compounds/data/'

    if parameters['wn_wiki']:
        parameters['compdatadir']=parameters['compoundparentdir']+'WNcompounds/'+parameters['vsource']+'/'+parameters['phrasetype']+'/'+parameters['dopos']+'s/'
        parameters['mwfile']='multiwords.wn_wiki.'+parameters['phrasetype']
    else:
        parameters['compdatadir']=parameters['compoundparentdir']+'ijcnlp_compositionality_data/NNs/nouns/'
    parameters['neighfile']=parameters['neighsource']+'.neighbours.strings'


    return parameters
