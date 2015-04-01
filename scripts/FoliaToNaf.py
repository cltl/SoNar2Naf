#python modules
from lxml import etree
import sys
import os
import argparse

#modules in this folder
from get_folia_pos_and_morphofeat import analyzepos
import utils

class FoliaToNaf():
    
    '''
    This Module converts a SoNar file in folia XML to NAF.
    
    @requires: lxml.etree (3.3.5)
    
    @type  path: string
    @param path: absolute path to SoNar file in folia xml
    
    @type  output: string
    @param output: absolute path where the output needs to be stored
    
    @type  cwd: str
    @param cwd: current working directory
    
    @type  prefix: string
    @param prefix: prefix of all xml elements
    
    @type  mapping_cornetto_odwn: dict
    @param mapping_cornetto_odwn: mapping from cornetto to odwn identifier
    
    @type  mapping_allwords_annotations: dict
    @param mapping_allwords_annotations: mapping from folia token_id to
    cornetto sense identifier
    '''
    
    def __init__(self,
                      path,
                      output,
                      cwd,
                      prefix,
                      mapping_cornetto_odwn,
                      mapping_allwords_annotations):
        
        #set args to class attributes
        [setattr(self, name, value) for name,value in [('path',    path),
                                                       ('output',  output),
                                                       ('prefix',  prefix),
                                                       ('mapping', mapping_cornetto_odwn),
                                                       ('allwords',mapping_allwords_annotations)]
         ]
        
        #parse basenaf
        self.basenaf = utils.parse_base_naf(cwd)
        
        #counters are set
        self.set_counters()
        
        #main function is called
        self.loop()
        
        #output is written to file
        with open(output,"w") as outfile:
            self.outputdoc.write(outfile,pretty_print=True,
                                 xml_declaration=True,
                                 encoding='utf-8')

    def set_counters(self):
        '''
        method reads self.path into memory and
        sets all kinds of counters relevant for conversion
        
        '''
        #parse folia
        self.doc              = etree.parse(self.path).getroot()
        
        #set word_number to index 1 and offset to 0
        self.word_number      = 1
        self.offset           = 0
        #set self.basenaf to self.outputdoc
        self.outputdoc         = self.basenaf
        
        #make wf and term els of self.outputdoc class attributes
        self.w_els             = self.outputdoc.find('text')
        self.t_els             = self.outputdoc.find("terms")
        
    def add_word_element(self,word,par,sent):
        '''
        given a word, a paragraph number and a sentence number
        the wf element is created.
        
        @type  word: str
        @param word: a word
        
        @type  par: str
        @param par: paragraph number
        
        @type  sent: str
        @param sent: sentence number
        '''
        #create wf element and add all attributes
        new_w_el                  = etree.SubElement(self.w_els, "wf")
        new_w_el.attrib['id']     = unicode("w%s" % self.word_number)
        new_w_el.attrib['length'] = unicode(len(word))
        new_w_el.attrib['offset'] = unicode(self.offset)
        new_w_el.attrib['para']   = unicode("%s" % par)
        new_w_el.attrib['sent']   = unicode(sent)
        new_w_el.text             = word
        
        #increase offset with word length + 1
        self.offset +=len(word)+1
    
    def add_term_element(self,word,
                              lemma,
                              pos,
                              morphofeat,
                              gram_class,
                              identifier,
                              w_el):
        '''
        given the all kinds if linguistic information, the term element
        is created
        
        @type  word: str
        @param word: a word
        
        @type  lemma: str
        @param lemma: a lemma

        @type  pos: str
        @param pos: pos
        
        @type  morphofeat: str
        @param morphofeat: morphofeat
        
        @type  gram_class: str
        @param gram_class: gram_class
        
        @type  identifier: str
        @param identifier: identifier of w_el
        
        @type  w_el: lxml.etree._Element
        @param w_el: lxml w_el element (<w element in folia)
        '''
        
        #put quotes on hyphen, because it's forbidden in xml
        word = word.replace("-","\"-\"")

        #create new element and add attributes
        new_t_el                      = etree.SubElement(self.t_els, "term")
        new_t_el.append(etree.Comment(word))
        new_t_el.attrib['id']         = "t_%s" % self.word_number
        new_t_el.attrib['pos']        = pos
        new_t_el.attrib['type']       = gram_class
        new_t_el.attrib['lemma']      = lemma
        new_t_el.attrib['morphofeat'] = morphofeat
        
        #add span
        new_span_el                = etree.SubElement(new_t_el,"span")
        new_target_el              = etree.SubElement(new_span_el,"target")
        new_target_el.attrib["id"] = unicode("w%s" % self.word_number)

        #add senses in folia to external references NAF
        new_external_references_el = etree.SubElement(new_t_el, "externalReferences")
        for sense_el in w_el.iterfind("{prefix}sense".format(prefix=self.prefix)):
            
            #obtain relevant info to put in ext_ref_el
            reference      = sense_el.get('class')
            annotator_type = sense_el.get("annotatortype")
            annotator      = sense_el.get("annotator")
            
            #create
            ext_ref_el_cornetto,ext_ref_el_odwn = utils.create_new_ext_ref_el(reference,
                                                                              annotator_type,
                                                                              annotator,
                                                                              self.mapping,
                                                                             new_external_references_el)
            for el in [ext_ref_el_cornetto,ext_ref_el_odwn]:
                if el is not False:
                    new_external_references_el.insert(0,el)
        
        #check if identifier in all words and cornetto and odwn sense
        
        if identifier in self.allwords:
            ext_ref_el_cornetto,ext_ref_el_odwn = utils.create_new_ext_ref_el(self.allwords[identifier],
                                                                             'manual',
                                                                             'unknown',
                                                                             self.mapping,
                                                                             new_external_references_el)
            
            for el in [ext_ref_el_cornetto,ext_ref_el_odwn]:
                if el is not False:
                    new_external_references_el.insert(0,el)
            
            
                
            
              
    def process_w_el(self,w_el):
        '''
        given a w_el, this method extract the sentence and paragraph number
        and call add_word_elememt
        
        @type  w_el: lxml.etree._Element
        @param w_el: lxml w_el element (<w element in folia)
        '''
        #obtain paragraph and sentence
        identifier = w_el.get("{http://www.w3.org/XML/1998/namespace}id")
        par,sent   = utils.par_sent_number(identifier)
        
        #obtain linguistic info
        word       =  w_el.find("{prefix}t".format(prefix=self.prefix)).text
        lemma = w_el.find("{prefix}lemma".format(prefix=self.prefix)).get("class")
        d = analyzepos(w_el.find("{prefix}pos".format(prefix=self.prefix)))
        pos,morphofeat,gram_class = d['pos'],d['morphofeat'],d['gramclass']
        
        #add wf element
        self.add_word_element(word,par,sent)
        
        #add term element
        self.add_term_element(word,
                              lemma,
                              pos,
                              morphofeat,
                              gram_class,
                              identifier,
                              w_el)
    

    def loop(self):
        ''' 
        method loops through paragraphs,sentences and words
        and calls to self.process_w_el
        '''
        
        #create string to find element in folia
        #with one variable to be filled base on whether is a CGN file or not
        string = "/".join([self.prefix+"text",
                           "%s",
                           self.prefix+"s",
                               ])
        in_between = ""
        
        if all(["CGN-comp" not in self.path,
                os.path.basename(self.path).startswith("allwords") == False]):
            in_between = "/".join([self.prefix+"div",
                                   self.prefix+"p"])
            
        
        #loop through words
        for w_el in self.doc.iterfind("/".join([string % in_between,
                                                self.prefix+"w"])):
            
            #increment self.word_number and process it
            self.process_w_el(w_el)
            self.word_number+=1
        

if __name__ == "__main__":
    if len(sys.argv) <= 2:
        print '''for help run: \n
        python FoliaToNaf.py -h
        
        example of call
        python FoliaToNaf.py -i %s -o %s -p %s
        ''' % ("/Users/marten/Desktop/test.folia.xml",
               "/Users/marten/Desktop/test.naf",
               "{http://ilk.uvt.nl/folia}")

    parser = argparse.ArgumentParser(description='Convert Folia to NAF')
    parser.add_argument('-i','-input_file',     dest='input_file',   help ='full path to file in folia xml',                   required=True)
    parser.add_argument('-o','-output_file',    dest='output_file',  help ='full path to output path NAF file',                required=True)
    parser.add_argument('-p','-prefix_folia',   dest='prefix_folia', help = 'prefix folia probably{http://ilk.uvt.nl/folia}',  required=True)
    args = parser.parse_args().__dict__
    
    cwd                        = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
    path_mapping_cornetto_odwn = os.path.join(cwd,"resources/cdb_syn_FILT.xml.lu-map")
    mapping_cornetto_odwn      = utils.load_mapping_cornetto_odwn(path_mapping_cornetto_odwn)
    
    #load all words mapping
    path_allwords_annotations    = os.path.join(cwd,"resources/1.3.1.ALLWORDS_DSC")
    mapping_allwords_annotations = utils.load_mapping_allwords(path_allwords_annotations)
    

    FoliaToNaf(args['input_file'], 
               args['output_file'], 
               cwd, 
               args['prefix_folia'], 
               mapping_cornetto_odwn,
               mapping_allwords_annotations)

