#!/usr/bin/env python

import sys
import getopt
import codecs
import os

from lxml import etree
import tempfile
from subprocess import Popen,PIPE
import shutil
import glob
import logging

from convert_penn_to_kaf import convert_penn_to_kaf_with_numtokens
try:
    from libs.KafNafParserPy import *
except:
    from KafNafParserPy import *
    
    
last_modified='27Feb2015'
version="1.0"
this_name = 'alpino KAF/NAF constituency parser'
this_layer = 'constituents'




#### SET THIS VARIABLE TO YOUR LOCAL FOLDER OF ALPINO
ALPINO_HOME = '/home/izquierdo/tools/Alpino'
#ALPINO_HOME = '/Users/ruben/NLP_tools/Alpino'

logging.basicConfig(stream=sys.stderr,format='%(asctime)s - %(levelname)s - %(message)s',level=logging.DEBUG)

__module_dir = os.path.dirname(__file__)

## Function to convert to penn treebank bracketd format 
def node_to_penn(node):
  children = node.getchildren()
  if len(children) == 0:
    word = node.get('word',None)
    if word is not None:
      #The attribute begin gives you the number of the token
      word = word.replace('(','-LRB')
      word = word.replace(')','-RRB-')
      
      
      num_token = node.get('begin')

      word = num_token+'#'+word
      if node.get('rel') == 'hd': 
        head = '=H'
      else: 
        head = ''
      return '('+node.get('pos')+head+' '+word.encode('utf-8')+')'
    else:
      return ''
  else:
    str = '('+node.get('cat')+' '
    for n in children:
      str+=node_to_penn(n)
    str+=')'
    return str

    
def xml_to_penn(filename):
    
  ## Under certain condition, there is know bug of Alpino, it sets the encoding in the XML
  ## to iso-8859-1, but the real encoding is UTF-8. So we need to force to use this encoding
  
  parser = etree.XMLParser(encoding='UTF-8')
  tree = etree.parse(filename,parser)
  
  str = node_to_penn(tree.find('node'))
  return str

if not sys.stdin.isatty(): 
    ## READING FROM A PIPE
    pass
else:
    print>>sys.stderr,'Input stream required in KAF format at least with the text layer.'
    print>>sys.stderr,'The language encoded in the KAF has to be Dutch, otherwise it will raise an error.'
    print>>sys.stderr,'Example usage: cat myUTF8file.kaf.xml |',sys.argv[0]
    sys.exit(-1)

my_time_stamp = True
try:
  opts, args = getopt.getopt(sys.argv[1:],"",["no-time"])
  for opt, arg in opts:
    if opt == "--no-time":
      my_time_stamp = False
except getopt.GetoptError:
  pass
  
  
logging.debug('Loading and parsing KAF file ...')
knaf_obj = KafNafParser(sys.stdin)

lang = knaf_obj.get_language()
if lang != 'nl':
  print>>sys.stdout,'ERROR! Language is ',lang,' and must be nl (Dutch)'
  sys.exit(-1)
  
logging.debug('Extracting sentences from the %s' % knaf_obj.get_type())
sentences = []
current_sent = [] 
term_ids = []
current_sent_tid = []

    
lemma_for_termid = {}
termid_for_token = {}

for term in knaf_obj.get_terms():
    lemma_for_termid[term.get_id()] = term.get_lemma()
    tokens_id = term.get_span().get_span_ids()
    for token_id in tokens_id:
        termid_for_token[token_id] = term.get_id()
 


previous_sent = None
for token in knaf_obj.get_tokens():
    token_id = token.get_id()
    sent = token.get_sent()
    text = token.get_text()
    ##To avoid using tokens that have no term linked
    if token_id not in termid_for_token:
        continue
    if sent != previous_sent and previous_sent!=None:
        sentences.append(current_sent)
        current_sent = [text]
        term_ids.append(current_sent_tid)
        current_sent_tid = [termid_for_token[token_id]]
    else:
        current_sent.append(text)
        current_sent_tid.append(termid_for_token[token_id])
    previous_sent = sent
  
if len(current_sent) !=0:
  sentences.append(current_sent)
  term_ids.append(current_sent_tid)

out_folder_alp = tempfile.mkdtemp()

logging.debug('Calling to Alpino parser in '+ALPINO_HOME)
logging.debug('Temporary folder: '+out_folder_alp)

## CALL TO ALPINO
alpino_bin = os.path.join(ALPINO_HOME,'bin','Alpino')
cmd = alpino_bin+' end_hook=xml -flag treebank '+out_folder_alp+' -parse'
os.environ['ALPINO_HOME']=ALPINO_HOME
alpino_pro = Popen(cmd,stdout=PIPE,stdin=PIPE,stderr=PIPE,shell=True)

for sentence in sentences:
  for token in sentence:
    token = token.replace('[','\[')
    token = token.replace(']','\]')
    token = token.replace('|','\|')
    #print>>sys.stderr,token.encode('utf-8'),
    alpino_pro.stdin.write(token.encode('utf-8')+' ')
  alpino_pro.stdin.write('\n')
  #print>>sys.stderr
alpino_pro.stdin.close()

#print>>sys.stderr,alpino_pro.stderr.read()

# As we are not reading the stdout or stderr of the process, if we dont wait to it to be done
# the parent will keep running without alpino be completed, and we will get empty XML files
# If the parent reads from stdout or stderr, it waits to the child to be completed before keep running
alpino_pro.wait()


## There should be as many files as number of sentences in the KAF

const = etree.Element('constituency')

#for xml_file in glob.glob(os.path.join(out_folder_alp,'*.xml')):
cnt_t = cnt_nt = cnt_edge = 0
for num_sent in range(len(sentences)):
  xml_file = os.path.join(out_folder_alp,str(num_sent+1)+'.xml')    
  if os.path.exists(xml_file):
    logging.debug('Converting alpino XML to pennTreebank, sentence num '+str(num_sent+1))
    penn_str = xml_to_penn(xml_file)
    tree_node,cnt_t,cnt_nt,cnt_edge = convert_penn_to_kaf_with_numtokens(penn_str,term_ids[num_sent],logging,lemma_for_termid,cnt_t,cnt_nt,cnt_edge)
  else:
    tree_node = etree.Element('tree') #empty
  const.append(tree_node)

knaf_obj.root.append(const)

#my_kaf.tree.getroot().append(const)
my_lp = Clp()
my_lp.set_name(this_name)
my_lp.set_version(version+'_'+last_modified)
my_lp.set_timestamp()
knaf_obj.add_linguistic_processor(this_layer, my_lp)
knaf_obj.dump()
logging.debug('Number of sentences in the input KAF:  '+str(len(sentences)))
logging.debug('PROCESS DONE')

##Remove temporary stuff
#print 'Temp stuff in ', out_folder_alp
shutil.rmtree(out_folder_alp)
#print out_folder_alp
sys.exit(0)