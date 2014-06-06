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
    parameters['k']=5
    parameters['ks']=[1,2,3,4,5,10,15,20]
    parameters['mwfile']='multiwords.all'
    parameters['neighsource']=''
    parameters['NNcompflag']=True
    parameters['literalityscore']='compound'
    parameters['wnsim']='path'
    parameters['dohead']=False
    parameters['domod']=False
    parameters['typelist']=['phrase','head','mod']
    parameters['random']=False
    parameters['rflag']='knn'
    parameters['vsources']=[]
    parameters['vsource']='deps'
    parameters['phrasetype']='NNs'
    parameters['unigram']=False
    parameters['wn_wiki']=True
    parameters['baseline']=False
    parameters['metric']='lin'
    parameters['bigram']=False #can phrases be counted as valid neighbours

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
            parameters['featurematch']='nn-DEP'
        elif arg=='ANs':
            parameters['phrasetype']='ANs'
            parameters['pos']='N'
            parameters['posword']='noun'
            parameters['altpos']='J'
            parameters['altposword']='adj'
            parameters['featurematch']='amod-DEP'

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
        elif arg=='diffcomp_nfadd':
            parameters['neighsource']='diffcomp_nfadd'
        elif arg=='diffcomp_nfmin':
            parameters['neighsource']='diffcomp_nfmin'
        elif arg=='diffcomp_add':
            parameters['neighsource']='diffcomp_add'
        elif arg=='diffcomp_ngadd':
            parameters['neighsource']='diffcomp_nfadd'
        elif arg=='diffcomp_cs_gm':
            parameters['neighsource']='diffcomp_cs_gm'
        elif arg=='diffcomp_cs_add':
            parameters['neighsource']='diffcomp_cs_add'
        elif arg=='diffcomp_cs_min':
            parameters['neighsource']='diffcomp_cs_min'
        elif arg=='diffcomp_cs_mult':
            parameters['neighsource']='diffcomp_cs_mult'
        elif arg=='diffcomp_cs_nfgm':
            parameters['neighsource']='diffcomp_cs_nfgm'
        elif arg=='diffcomp_cs_nfmin':
            parameters['neighsource']='diffcomp_cs_nfmin'
        elif arg=='diffcomp_cs_nfmult':
            parameters['neighsource']='diffcomp_cs_nfmult'
        elif arg=='diffcomp_cs_nfadd':
            parameters['neighsource']='diffcomp_cs_nfadd'
        elif arg=='unigram':
            parameters['neighsource']='unigram'
            parameters['typelist']=['head']
            parameters['dohead']=True
            parameters['unigram']=True
            parameters['dopos']=parameters['posword']
        elif arg=='setk':
            parameters['k']=int(args[i+1])
        elif arg=='lin':
            parameters['wnsim']='lin'
        elif arg=='jcn':
            parameters['wnsim']='jcn'
        elif arg=='baseline':
            parameters['baseline']=True
        elif arg=='phrase':
            parameters['typelist']=['phrase']
            parameters['dopos']=parameters['posword']
        elif arg=='head':
            parameters['typelist']=['head']
            parameters['dohead']=True
            parameters['dopos']=parameters['posword']
        elif arg=='mod':
            parameters['typelist']=['mod']
            parameters['domod']=True
            parameters['dohead']=False
            parameters['dopos']=parameters['altposword']
        elif arg=='random':
            parameters['random']=True
            parameters['rflag']='random'
        elif arg=='wn_wiki':
            parameters['wn_wiki']=True
        elif arg=='deps':
            parameters['vsources'].append('deps')
        elif arg=='wins':
            parameters['vsources'].append('wins')
        elif arg=='cospmi':
            parameters['metric']='cospmi'
        elif arg=='bigram':
            parameters['bigram']=True

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

    if parameters['metric']=='cospmi':
        parameters['neighsource']+='.cospmi'

    if parameters['wn_wiki']:
        parameters['compdatadirs']=[]
        for vsource in parameters['vsources']:
            parameters['compdatadirs'].append(parameters['compoundparentdir']+'WNcompounds/'+vsource+'/'+parameters['phrasetype']+'/'+parameters['dopos']+'s/')

        parameters['mwfile']='multiwords.wn_wiki.'+parameters['phrasetype']
    else:
        parameters['compdatadirs']=[parameters['compoundparentdir']+'ijcnlp_compositionality_data/NNs/nouns/']
    parameters['compdatadir']=parameters['compdatadirs'][0]
    parameters['neighfile']=parameters['neighsource']+'.neighbours.strings'
    parameters['outfile']=parameters['compoundparentdir']+'WNcompounds/results.csv'


    return parameters
