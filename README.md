since 20-02-2015

## AUTHORS
* Marten Postma        (martenp@gmail.com)
* Emiel van Miltenburg (emielonline@gmail.com)
 
## GOAL
the SoNaR corpus is a large Dutch corpus (http://tst-centrale.org/producten/corpora/sonar-corpus/6-85)
, of which a part has been annotated
with Cornetto senses (http://www2.let.vu.nl/oz/cltl/cornetto/)
 in the DutchSemcor project (http://www2.let.vu.nl/oz/cltl/dutchsemcor/).
the goal of this project is to:
* COMPLETED:convert each file from Folia xml (http://proycon.github.io/folia/) to NAF (http://www.newsreader-project.eu/files/2013/01/techreport.pdf) 
* COMPLETED:include the dutchsemcor annotations 
* COMPLETED:add the Open Source Dutch Wordnet annotations
* TODO:run Dutch pipeline to add NER, NEL, newest alpino, SRL, timex and many more..

## USAGE
There are two main purposes of this github:
* convert a folia xml file to NAF containing wf and term layer.
cd to the scripts folder and call python FoliaToNaf.py -h for information
on how to use it.
* convert DutchSemcor to NAF. cd to the scripts folder and call python main.py -h
for more information on how to use it.

## Contents
Contents of this github:
* folder 'scripts': contains python scripts to perform conversion
* folder 'resources': contains 'base_naf.xml' which is used for the NAF conversion
and 'cdb_syn_FILT.xml.lu-map', which is a mapping from Cornetto to ODWN1.0. It also contains
the allwords xml files and its annotations. The folder allwords_NAF contains the processed all words files with annotations in naf.
* folder 'dutch_pipeline': contains scripts to run naf file through dutch pipeline. only created for use
on our personal server.

## TODO list (in this order)
TODO list includes:
* run full conversion to naf with pipeline (to be set up)

## Code Documentation
All python code has been documented with the epydoc package (http://epydoc.sourceforge.net/)
open script/html/index.html to inspect the documentation.
