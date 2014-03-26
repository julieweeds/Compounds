__author__ = 'juliewe'

def configure(args):

    parameters={}
    parameters['pos']='n'
    parameters['testing']=False
    parameters['local']=True
    parameters['apollo']=False
    parameters['athome']=False
    parameters['featurematch']={'NNs':'nn-DEP','ANs':'amod-DEP'}
    parameters['seed']=37
    parameters['inversefeatures']={'nn-DEP':'nn-HEAD','nn-HEAD':'nn-DEP','amod-DEP':'amod-HEAD','amod-HEAD':'amod-DEP','':''}
    parameters['headpos']={'NNs':'N','ANs':'N'}
    parameters['modpos']={'NNs':'N','ANs':'J'}
    parameters['run']=[]
    parameters['comptype']='NNs'

    for i,arg in enumerate(args):
        if arg=='nouns' or arg=='N':
            parameters['pos']='N'
       # elif arg=='adjs' or arg=='J':
        #    parameters['pos']='J'
        elif arg=='testing':
            parameters['testing']=True
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
        elif arg=='extract':
            parameters['run'].append('extract')
        elif arg=='filter':
            parameters['run'].append('filter')
        elif arg=='readfile':
            parameters['run'].append('readfile')
        elif arg=='NNs':
            parameters['comptype']='NNs'
        elif arg=='ANs':
            parameters['comptype']='ANs'


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

    parameters['compdatadir']=parameters['compoundparentdir']+'WNcompounds/NNs/nouns/'



    return parameters
