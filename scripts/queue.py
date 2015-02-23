#import general modules
import threading
import os

#import modules from this folder
import utils
from FoliaToNaf import FoliaToNaf

class Worker(threading.Thread):
    '''
    this is a class which makes it multiples to run multiple 
    files in parallel
    '''
    def __init__(self, queue):
        self.__queue = queue
        threading.Thread.__init__(self)

    def run(self):
        while 1:
            item = self.__queue.get()
            if item is None:
                break # reached end of queue
            
            #do the magic here
            
            #extract variables from 'item'
            path                  = item['path'][:-4]
            output                = utils.output_path(path, 
                                                      item['base_dir'], 
                                                      item['output_dir'])
            cwd                   = item['cwd']
            mapping_cornetto_odwn = item['mapping_cornetto_odwn']
            prefix_folia          = item['prefix_folia']
            overwrite             = item['overwrite']
            
            #convert to NAF if output does not exist and/or overwrite is true
            if any([overwrite == 'yes',
                    os.path.exists(output+".bz2") == False
                    ]):
                
                
                #unzip input_file
                utils.b_un_zip2(path+".bz2", False)

                FoliaToNaf(path, 
                           output, 
                           cwd,
                           prefix_folia,
                           mapping_cornetto_odwn)
            
                #bzip2 input_file
                utils.b_un_zip2(path,  True)
                
                #bzip2 output_file
                utils.b_un_zip2(output,True)