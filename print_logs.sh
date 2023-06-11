cd out

ls -rt | tail -n $1 | awk '{print "\"" $1 "\","}'

cd ..
