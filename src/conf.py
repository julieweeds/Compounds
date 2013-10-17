__author__ = 'juliewe'

def configure(args):

    parameters={}
    parameters['parentdir']='/Volumes/LocalScratchHD/juliewe/Documents/workspace/Compounds'

    parameters['datadir']='data/Wiki_nounsdeps'
    parameters['freqfile']='events.strings'
    parameters['assocfile']='events.strings_mi'
    parameters['entryfile']='events.strings_deprow'
    parameters['featurefile']='events.strings_depcol'
    parameters['freqthresh']=100
    parameters['sample']=1000
    parameters['entrythresh']=50000
    parameters['stopwordlimit']=3
    parameters['featurematch']='nn-DEP'
    parameters['testing']=False
    parameters['deplist']=['amod-DEP','dobj-HEAD','conj-DEP','iobj-HEAD','nsubj-HEAD','nn-DEP','nn-HEAD','pobj-HEAD']

    parameters['collocatefile']='multiwords_'+parameters['featurematch']
    parameters['depfile']='wikipedia_nounsdeps_t100.pbfiltered'
    parameters['extract']=False
    parameters['build']=False

    for arg in args:
        if arg=='testing':
            parameters['testing']=True
        elif arg =='extract':
            parameters['extract']=True
        elif arg =='build':
            parameters['build']=True

    return parameters
