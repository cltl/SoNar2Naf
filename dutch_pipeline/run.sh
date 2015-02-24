
#check if enough arguments are passed
if [ $# -eq 0 ];
then
    echo
    echo "Usage:                  : $0 input_file output_file"
    echo
    echo "input_file:             : full path to NAF file with text and terms layers"
    echo "output_file:            : full path to output file"
    echo
    exit -1;
fi
 
#assign command line arguments to variables and obtain basename
input_file=$1
output_file=$2
basename=$(basename $input_file)
cwd=/${PWD#*/}
tmp=$cwd/tmp/
tmp_folder=$tmp$basename
base_naf=$tmp_folder/$basename

#rm if exists and create tmp folder based on basename
rm -rf $tmp_folder && mkdir $tmp_folder

#call dep
cd $cwd/dependency-parser-nl/
cat $input_file | python alpino_dependency_parser.py > $base_naf.dep    2> /dev/null
cd $cwd

#NOT WORKING: call const
#export ALPINO_HOME=/home/izquierdo/tools/Alpino
#cd constituent-parser-nl/core/
#echo $base_naf.dep
#cat $base_naf.dep | python alpino_parser.py          > $base_naf.dep.con
#cd $cwd

#call dproc starting from the lower layers of NAF

#mv final output to output_file

#rm tmp file (TODO: uncomment)
#rm -rf $tmp_folder
