for file in $(find . -maxdepth 2 -type f -name "params.json" -exec ls -t {} +)
do
    f1=$(basename $(dirname $file))
    echo | awk -v file=$f1 '{print "\"" file "\","}'
done 
