#Dependency parser for Dutch#

This module implements a dependency parser for Dutch based on the Alpino parser. The input/output format is KAF/NAF format (a description of the KAF format
can be found at https://github.com/opener-project/kaf/wiki/KAF-structure-overview). This is the specification of the input/output:
* Input: a valid KAF/NAF file at least with the `<text>` and `<term>` layer
* Output: the input KAF/NAF file extended with dependencies (`<deps>` layer)

#Installation#

This module is fully implemented using Python, so you will need to have it installed on your machine (recommented version 2.7). There are some requirements:
* Alpino parser: the Alpino parser needs to be installed on your machine (http://www.let.rug.nl/vannoord/alp/Alpino/)
* KafNafParser: our parser for reading and writing KAF/NAF files (http://github.com/cltl/KafNafParserPy)
* lxml: a Python library for managing XML files, required by the KafNafParser (http://lxml.de/)

These are the steps recommend for the installation. You can skip any step if that tool/library is already installed on your machine.

##1 Install the Alpino parser##

To install the Alpino parser we recommend to download the binary package that suits your system (http://www.let.rug.nl/vannoord/alp/Alpino/binary/)

##2 Install the lxml library##

If you have "pip" install on your machine, for installing lxml you just have to run:
````shell
pip install lxml
````

You can check the installation procesure at http://lxml.de/installation.html

##3 Install the KafNafParser##

This is a python module, and you will need just to clone it in order to have it installed. Execute this command:
````shell
git clone https://github.com/cltl/KafNafParserPy.git
````

##4 Install the dependency parser##

Again only cloning the repository from our CLTL github account is required:
````shell
git clone https://github.com/cltl/dependency-parser-nl.git
````

##5 Setting up##

The dependency parser needs to know where Alpino and the KafNafParser were installed. So you will have to specify the path to these tools in the file config.cfg.
Open it with a text editor and set the paths to the correct paths where you installed Alpino and KafNafParser in your local machine. If Alpino has been installed on
"/Users/ruben/NLP_tools/Alpino" and the KafNafParser on "/Users/ruben/cltl_github/KafNafParserPy" this is an example of configuration file:
````shell
[general]
alpino_home = /Users/ruben/NLP_tools/Alpino/
kaf_naf_parser_path = /Users/ruben/cltl_github/
````

Note than the name of the repository must be excluded from the variable kaf_naf_parser_path.


#Running#

The main script is the file alpino_dependency_parser.py. This script reads a KAF/NAF from the standard input and writes the resulting KAF/NAF on the standard output,
generating some log information on the standard error. These are some examples:
````shell
$ cat input.kaf | alpino_dependency_parser.py > output.kaf 2> output.err
$ cat input.naf | python alpino_dependency_parser.py > output.naf 2> /dev/null
````

If the first call doesn't work in your case, try calling "python" specifically, as in the second example.


#Contact#

* Ruben Izquierdo Bevia
* ruben.izquierdobevia@vu.nl
* Vrije University of Amsterdam

#License#

Sofware distributed under GPL.v3, see LICENSE file for details.
