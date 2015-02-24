#!/usr/bin/env python

import sys
import getopt
import os
import logging
import re
import ConfigParser
import argparse


from lxml import etree
from subprocess import Popen,PIPE



## LAST CHANGES ##
# 22-jan=2014: created repository
# 8-april-2014: direction of the relations reversed


last_modified='23Jan2014'
version="0.2"
this_name = 'Alpino KAF/NAF dependency parser'
this_layer = 'deps'
config_filename = 'config.cfg'


logging.basicConfig(stream=sys.stderr,format='%(asctime)s - %(levelname)s - %(message)s',level=logging.DEBUG)
__module_dir = os.path.dirname(__file__)


class Calpino_dependency:
    def __init__(self,line):
        self.ok = True
        self.begin_from = self.begin_to = self.end_from = self.end_to = self.sentence = ''
        fields = line.split('|')
        if len(fields) == 4:
            token_to = fields[0]
            match =  re.match(r'(.+)/\[(\d+),(\d+)\]', token_to)
            if match is not None:
                self.lemma_to = match.group(1)
                self.begin_to = int(match.group(2))
                self.end_to = int(match.group(3))
                
                token_from = fields[2]
                match2 =  re.match(r'(.+)/\[(\d+),(\d+)\]', token_from)
                if match2 is not None:
                    self.lemma_from = match2.group(1)
                    self.begin_from = int(match2.group(2))
                    self.end_from = int(match2.group(3))
                    self.relation = fields[1]
                    self.sentence = int(fields[3])
                else:
                    self.ok = False
            else:
                self.ok = False
        else:
            self.ok = False
    
    def get_sentence(self):
        return self.sentence
    
    def is_ok(self):
        return self.ok
            
    def __repr__(self):
        r = 'From: %d-%d to %d-%d' % (self.begin_from,self.end_from,self.begin_to,self.end_to)
        return r
    
    def generate_dependencies(self, list_term_ids):
        # This will creathe dependency
        dependencies = []
        try:
            terms_from = [ list_term_ids[idx] for idx in range(self.begin_from,self.end_from) ]
            terms_to = [ list_term_ids[idx] for idx in range(self.begin_to,self.end_to) ]
            for t_from in terms_from:
                for t_to in terms_to:
                    ##Creating comment
                    str_comment = ' '+self.relation+'('+self.lemma_to+','+self.lemma_from+') '
                    
                    my_dep = Cdependency()
                    my_dep.set_from(t_to)
                    my_dep.set_to(t_from)
                    my_dep.set_function(self.relation)
                    my_dep.set_comment(str_comment)
                    
                    dependencies.append(my_dep)
        except Exception as e:
            print>>sys.stderr,str(e)
        return dependencies
        


argument_parser = argparse.ArgumentParser(description='Alpino dependency parser. Required input stream, KAF file with text and term layer',
                                          usage='cat myfile.kaf | '+sys.argv[0]+' [options]')
argument_parser.add_argument('-no_time',dest='my_time_stamp', action='store_false',help='No timestamp in the header')
argument_parser.add_argument('-rm_deps', dest='remove_deps', action='store_true',help='To remove the dependencies already existing')


arguments = argument_parser.parse_args()  


     

if not sys.stdin.isatty(): 
    ## READING FROM A PIPE
    pass
else:
    argument_parser.print_help()
    sys.exit(-1)

  
my_config = ConfigParser.ConfigParser()
config_file = os.path.join(__module_dir, config_filename)
if not os.path.exists(config_file):
    print>>sys.stderr,'Config file not found in ',config_file
    print>>sys.stderr,'Create this file with this info:\n[general]\nalpino_home = PATH_TO_YOUR_ALPINO\n'
    sys.exit(-1)
my_config.read(config_file)
ALPINO_HOME = my_config.get('general','alpino_home')
os.environ['SP_CTYPE']='utf8'
os.environ['SP_CSETLEN']='212'

if not os.path.exists(ALPINO_HOME):
    print>>sys.stderr,'ALPINO not found in: ',ALPINO_HOME
    print>>sys.stderr,'Set the path to Alpino properly on the configuration filename ('+config_filename+') or install Alpino'
    sys.exit(-1)
    
    
##Trying to import from KafNafParserPy import *
if my_config.has_option('general','kaf_naf_parser_path'):
    sys.path.append(my_config.get('general','kaf_naf_parser_path'))

from KafNafParserPy import *
                      
  
logging.debug('Loading and parsing KAF file ...')
my_knaf = KafNafParser(sys.stdin)

if arguments.remove_deps:
    logging.debug("Dependency layer removed from the input KAF file (if exists)")
    my_knaf.remove_dependency_layer()

lang = my_knaf.get_language()
if lang != 'nl':
  print>>sys.stdout,'ERROR! Language is ',lang,' and must be nl (Dutch)'
  sys.exit(-1)
  
logging.debug('Extracting sentences from the '+my_knaf.get_type())
sentences = []
current_sent = [] 
term_ids = []
current_sent_tid = []

    
lemma_for_termid = {}
termid_for_token = {}

for term in my_knaf.get_terms():
    term_id = term.get_id()
    lemma = term.get_lemma()
    lemma_for_termid[term_id] = lemma
    tokens_id = term.get_span().get_span_ids()
    for token_id in tokens_id:
        termid_for_token[token_id] = term_id
 

previous_sent = None
for token_obj in my_knaf.get_tokens():
  token = token_obj.get_text()
  sent = token_obj.get_sent()
  token_id = token_obj.get_id()
  
  ##To avoid using tokens that have no term linked
  if token_id not in termid_for_token:
    continue
  if sent != previous_sent and previous_sent!=None:
    sentences.append(current_sent)
    current_sent = [token]
    term_ids.append(current_sent_tid)
    current_sent_tid = [termid_for_token[token_id]]
  else:
    current_sent.append(token)
    current_sent_tid.append(termid_for_token[token_id])
  previous_sent = sent
  
if len(current_sent) !=0:
  sentences.append(current_sent)
  term_ids.append(current_sent_tid)
  
  

logging.debug('Calling to Alpino parser in '+ALPINO_HOME)

## CALL TO ALPINO
alpino_bin = os.path.join(ALPINO_HOME,'bin','Alpino')
cmd = alpino_bin+' -parse'
os.environ['ALPINO_HOME']=ALPINO_HOME
alpino_pro = Popen(cmd,stdout=PIPE,stdin=PIPE,stderr=sys.stderr,shell=True)

str_input = ''
for num_sentence, sentence in enumerate(sentences):
  str_input +=str(num_sentence)+'|'
  for token in sentence:
    token = token.replace('[','\[')
    token = token.replace(']','\]')
    token = token.replace('|','')
    str_input+=token.encode('utf-8')+' '
  str_input+='\n'

alpino_out, alpino_err = alpino_pro.communicate(str_input)
#alpino_pro.stdin.write(str_input)

'''
for num_sentence, sentence in enumerate(sentences):
  alpino_pro.stdin.write(str(num_sentence)+'|')
  #print str(num_sentence)+'|',
  for token in sentence:
    token = token.replace('[','\[')
    token = token.replace(']','\]')
    token = token.replace('|','')
    alpino_pro.stdin.write(token.encode('utf-8')+' ')
    #print token.encode('utf-8'),
  alpino_pro.stdin.write('\n')
  #print 
  #print>>sys.stderr
alpino_pro.stdin.close()
'''
#logging.debug('Alpino log out:\n'+alpino_pro.stderr.read())

# As we are not reading the stdout or stderr of the process, if we dont wait to it to be done
# the parent will keep running without alpino be completed, and we will get empty XML files
# If the parent reads from stdout or stderr, it waits to the child to be completed before keep running
#alpino_pro.wait()

#for line in alpino_pro.stdout:
for line in alpino_out.splitlines():
    line = line.strip().decode('utf-8')
    my_dep = Calpino_dependency(line)
    if my_dep.is_ok():
        my_sentence_index = my_dep.get_sentence()
        list_term_ids = term_ids[my_sentence_index]
        deps = my_dep.generate_dependencies(list_term_ids)
        for d in deps:
            my_knaf.add_dependency(d)
            
my_lp = Clp()
my_lp.set_name(this_name)
my_lp.set_version(version+'_'+last_modified)
if arguments.my_time_stamp:
    my_lp.set_timestamp()
else:
    my_lp.set_timestamp('*')
    
my_knaf.add_linguistic_processor(this_layer,my_lp)
my_knaf.dump()
        
sys.exit(0)
