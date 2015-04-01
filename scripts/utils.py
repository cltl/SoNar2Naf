import os
import glob
import subprocess
from lxml import etree

'''
this module contains many different useful methods for the conversion.
'''

def parse_base_naf(current):
    '''
    base naf is parsed and returned
    
    @type  current: str
    @param current: full path to base naf
    
    @rtype: lxml.etree._Element
    @return: base naf
    '''
    base_naf         = os.path.join(current,'resources/base_naf.xml')
    parser           = etree.XMLParser(remove_blank_text=True)
    outputdoc        = etree.parse(base_naf,parser)
    return outputdoc

def path_generator(base_dir,extention):
    '''
    given a base directory containing possible subdirectories
    this method returns a generator with all paths with a certain extention.
    
    @type  base_dir: str
    @param base_dir: full path to directory
    
    @type  extention: str
    @param extention: wanted extention, for example '.bz2'
    
    @rtype:  generator
    @return: generator all paths with param extention
    ''' 
    for (dirpath, dirnames, filenames) in os.walk(base_dir):
        for filename in filenames:
            if filename.endswith(extention): 
                yield os.sep.join([dirpath, filename])

def b_un_zip2(path,zip_it):
    '''
    given a path, this method uses the subprocess.chech_call method
    to bzip2 or bunzip2 the file and only returns after it has been completed
    
    @type  path: str
    @param path: full path to regular file or .bzip2 file
    
    @type  zip_it: boolean
    @param zip_it: True: bunzip2, False: bzip2
    '''
    #decide on to unzip or zip
    call    = "bunzip2"
    if zip_it:
        call = "bzip2"
    
    #create command
    command = "{call} -f {path}".format(call=call,
                                     path=path)
    
    #call subprocess
    subprocess.check_call(command,shell=True)
    


def load_mapping_cornetto_odwn(path_mapping):
    '''
    given the mapping between cornetto and odwn in param
    path_mapping (tab separated)
    
    @type  path_mapping: str
    @param path_mapping: full path to mapping cornetto -> odwn
    
    @rtype: dict
    @return: mapping from cornetto to odwn
    '''
    mapping = {line.strip().split("\t")[0]:line.strip().split("\t")[1]
               for line in open(path_mapping)
               }
    return mapping
    
def output_path(input_path,base_dir,output_dir):
    '''
    given an input_path and an output_dir the output_path is returned
    and the directory of the output_path is created if it did not exists
    
    @type  input_path: str
    @param input_path: input_path (.folia.xml)
    
    @type  base_dir: str
    @param base_dir: base directory of dutchsemcor
    
    @type  output_dir: str
    @param output_dir: output directory (the main directory)
    
    @rtype: str
    @return: output_path
    '''
    #create output_path and obtain directory
    output_path = input_path.replace(base_dir,output_dir)
    directory   = os.path.dirname(output_path)
    
    #create directory if it does not exist
    if os.path.exists(directory) == False:
        os.makedirs(directory)
    
    #add .naf to output_path if needed
    if output_path.endswith(".naf") == False:
        output_path = output_path + ".naf"
        
    return output_path
    

def par_sent_number(identifier):
    '''
    given a path like 
    CGN-comp-a_fn000248.s.1.w.1 or CGN-comp-a_fn000248.p.1.s.1.w.1 
    this method extract the paragraph and sentence number
    
    @type  identifier: str
    @param identifier: identifier in folia
    
    @rtype: tuple
    @return: tuple (par,sent) both integers
    '''
    par = 1
    strip = identifier.split(".")
    
    if "p." in identifier:
        par,sent = strip[2],strip[4]
    else:
        sent     = strip[2]
        
    return par,sent


def load_mapping_allwords(all_words_folder):
    '''
    given three xml files containing the all words annotations in DutchSemcor
    this method create a mapping from the identifier to the Cornetto sense
    
    @type  all_words_folder: str
    @param all_words_folder: full path to all_words_folder
    
    @rtype: dict
    @return: mappping from identifier to cornetto sense
    '''
    #set mapping
    prefixes = {'allwords': all_words_folder}
    mapping  = {}
    
    #loop files
    for xml_file in glob.glob("{allwords}/*.xml".format(**prefixes)):
        
        #parse doc
        doc = etree.parse(xml_file)
        
        #update dict
        for token_el in doc.iterfind("token"):

            #extract token_id and sense from token_el xml element
            token_id = token_el.get("token_id")
            sense    = token_el.get('sense')
            
            #update mapping
            mapping[token_id] = sense
    
    return mapping


def create_new_ext_ref_el(reference,
                          annotator_type,
                          annotator,
                          mapping,
                          new_external_references_el):
    '''
    new external reference el is created
    
    @type  reference: str
    @param reference: cornetto sense
    
    @type  annotator_type: str
    @param annotator_type: manual | auto
    
    @type  annotator: str
    @param annotator: person or system who annotated the sense
    
    @type  mapping: dict
    @param mapping: mapping from cornetto sense to odwn sense
    
    @type  new_external_references_el: lxml.etree element
    @param new_external_references_el: lxml.etree element in which a new child
    will be created
    
    @rtype: tuple
    @return: (ext_ref_el_cornetto,ext_ref_el_odwn), if no succes, elements value
    is False.
    '''
    ext_ref_el_cornetto = False
    ext_ref_el_odwn     = False
    
    #set attributes
    attributes = {'resource'      : 'Cornetto',
              'reference'         : reference,
              'confidence'        : "1.0",
              'annotatortype'     : annotator_type,
              'annotator'         : annotator}
    
    #create new ext_ref_el
    ext_ref_el_cornetto = new_external_references_el.makeelement('externalRef',
                                                            attrib=attributes)
    
    #also add mapped odwn reference
    if reference in mapping:
        attributes['resource']  = 'ODWN1.0'
        attributes['reference'] = mapping[reference]
        ext_ref_el_odwn = new_external_references_el.makeelement('externalRef',
                                                                attrib=attributes)
    
    return (ext_ref_el_cornetto,ext_ref_el_odwn)
    
    
