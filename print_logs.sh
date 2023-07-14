cd out

for file in $(ls -rt *.json | tail -n $1)
do
    f1="${file%.*}"
    echo | awk -v file=$f1 '{print "\"" file "\","}'
done 
cd ..
