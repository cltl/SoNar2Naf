#import general modules
import os
import sys
import Queue
import argparse

#import modules in this folder
import utils
from queue import Worker
'''
this module makes it possible to:
    (1) convert all folia to naf (including senses and odwn senses)
'''


#ARGPARSE
cwd        = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
extention  = ".bz2"
path_mapping_cornetto_odwn = os.path.join(cwd,"resources/cdb_syn_FILT.xml.lu-map")

if len(sys.argv) <= 2:
    print '''for help run: \n
    python main.py -h
    or on local machine on which it was created:
    python main.py -b %s -o %s -w %s -p %s -r %s
    ''' % ("/Users/marten/Desktop/Corpora/DutchSemCor",
           "/Users/marten/Desktop/Corpora/DutchSemCor_NAF/",
           "10",
           "{http://ilk.uvt.nl/folia}",
           "yes")

parser = argparse.ArgumentParser(description='Convert SoNaR to Folia')
parser.add_argument('-b','-base_dir',     dest='base_dir',     help ='input directory DutchSemCor',              required=True)
parser.add_argument('-o','-output_dir',   dest='output_dir',   help ='output directory NAF',                     required=True)
parser.add_argument('-c','-workers',      dest='workers',      help ='number of parallel processes',             required=True)
parser.add_argument('-k','-prefix_folia', dest='prefix_folia', help = 'prefix folia {http://ilk.uvt.nl/folia}',  required=True)
parser.add_argument('-r','-overwrite'   , dest='overwrite',    help = "overwrite output files (yes or no)",                  required=True)
args = parser.parse_args().__dict__

#extract from argparse
base_dir     = args['base_dir']
output_dir   = args['output_dir']
WORKERS      = int(args['workers'])
prefix_folia = args['prefix_folia']
overwrite    = args['overwrite']

#LOAD DATA

#load mapping cornetto odwn
mapping_cornetto_odwn = utils.load_mapping_cornetto_odwn(path_mapping_cornetto_odwn)

#obtain generator of all paths
paths = utils.path_generator(base_dir, extention)

#RUN CONVERSION

#instance workers
queue = Queue.Queue(10)
for i in range(WORKERS): 
    Worker(queue).start() # start a worker

#loop through paths
for counter,path in enumerate(paths):
    item = {'path'                  : path,
            'prefix_folia'          : prefix_folia,
            'cwd'                   : cwd,
            'mapping_cornetto_odwn' : mapping_cornetto_odwn,
            'base_dir'              : base_dir,
            'output_dir'            : output_dir,
            'overwrite'             : overwrite}
    queue.put(item)
    
    if counter == 10:
        break 
    
#add end-of-queue markers    
for i in range(WORKERS): 
    queue.put(None) # add end-of-queue markers