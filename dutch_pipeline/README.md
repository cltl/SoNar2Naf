#WARNING
The contents of this folder work only on our personal server.

#Dutch Pipeline

The main goal of this folder is:
* input: naf (converted folia) with wf and term layer
* output: naf with ned, nel, dep, const, srl, timex ..

## Requirements
* pipedemo
* https://github.com/cltl/dependency-parser-nl
* NOT WORKING:https://github.com/opener-project/constituent-parser-nl

##USAGE
* bash run.sh input_file output_file
* the input file (wf and term layer) will first be passed to dep and const
and then to the other layers of the pipedemo. During the process, a tmp folder
will be created that will be removed afterwards.

## Info about installing
* dependency parser:
    * git clone https://github.com/cltl/dependency-parser-nl.git
    * mv config.kyoto.cfg config.cfg
    * cat input.naf | python alpino_dependency_parser.py > output.naf 2> /dev/null


