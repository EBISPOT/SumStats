 #!/bin/bash
 
file=$1

if [[ $file != */* ]];
then
    echo $file
    exit
fi

i=1
if [[ $file == /* ]] ;
then
    i=2
fi
filename=$(echo "$file" | cut -d"/" -f $i)
while [ -n "$filename" ];
do
    i=$(( i + 1  ))
    filename=$(echo "$file" | cut -d"/" -f $i)
done
if [ $i -gt 1 ]; then

	i=$(( i - 1  ))
fi
filename=$(echo "$file" | cut -d"/" -f $i)

echo $filename
