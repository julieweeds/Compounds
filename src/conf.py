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
    parameters['sample']=1500
    parameters['entrythresh']=10000
    parameters['stopwordlimit']=3
    parameters['featurematch']='nn-DEP'
    parameters['inversefeatures']={'nn-DEP':'nn-HEAD','nn-HEAD':'nn-DEP','amod-DEP':'amod-HEAD','amod-HEAD':'amod-DEP'}
    parameters['testing']=False
    parameters['deplist']=['amod-DEP','dobj-HEAD','conj-DEP','iobj-HEAD','nsubj-HEAD','nn-DEP','nn-HEAD','pobj-HEAD']

    parameters['collocatefile']='multiwords_'+parameters['featurematch']
    parameters['depfile']='wikipedia_nounsdeps_t100.pbfiltered'
    parameters['extract']=False
    parameters['build']=False
    parameters['usesource']=False
    parameters['source']='none'
    parameters['allheads']=False
    parameters['adjlist']=False

    for arg in args:
        if arg=='testing':
            parameters['testing']=True
        elif arg =='extract':
            parameters['extract']=True
        elif arg =='build':
            parameters['build']=True
        elif arg =='boleda':
            parameters['usesource']=True
            parameters['source']='boleda.txt'
            parameters['datadir']='data/ANcompounds'
            parameters['featurematch']='amod-DEP'
            parameters['freqthresh']=0
            parameters['mergefile']='multiwords_boleda'
            parameters['collocatefile']='multiwords_amod-DEP_boleda'

        elif arg =='Jboleda':
            parameters['usesource']=True
            parameters['source']='boleda.txt'
            parameters['datadir']='data/ANcompounds/deps/adjs'
            parameters['featurematch']='amod-HEAD'
            parameters['freqthresh']=0
            parameters['mergefile']='multiwords_boleda'
            parameters['collocatefile']='multiwords_amod-HEAD_boleda'
            parameters['allheads']=True

        elif arg == 'Jextract':
            parameters['datadir']='data/ANcompounds/deps/adjs'
            parameters['featurematch']='amod-HEAD'
            parameters['freqthresh']=100
            parameters['upperfreqthresh']=100
            parameters['collocatefile']='multiwords_amod-HEAD'
            parameters['allheads']=True

        elif arg =='Jlist':
            parameters['usesource']=True
            parameters['source']='adjs32'
            parameters['datadir']='data/ANcompounds/deps/adjs'
            parameters['adjlist']=True
            parameters['allheads']=True
            parameters['collocatefile']=['multiwords.train','multiwords.test']
            parameters['freqthresh']=100
            parameters['featurematch']='amod-HEAD'
    return parameters
