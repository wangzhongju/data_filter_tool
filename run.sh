#! /usr/bin/env bash

# compile the project folder
if [ ! -d "./build" ]; then
	mkdir build
fi
cd build && cmake ..
make
cd ../
# compile end

# parameter
usage="Usage: `basename $0` (img_filter) parameter1(imgPath) parameter2(whether untar)"
imgPath=$1
command=$2

# function define
function untar()
{
    if [ ! -d "./data/tar" ];then
        echo "folder './data/tar do not exist'"
        return
    fi
    if [ ! -d "./data/untar" ];then
        echo "untar start"
        mkdir ./data/untar
        sleep 1
    fi
    for i in `ls ./data/tar/*.tar.gz`
    do
        tar zxvf $i -C ./data/untar/
    done
}

function mvimg()
{
    for i in `ls ./data/untar/`
    do
        cp ./data/untar/$i/leftimg/*.jpg $imgPath
    done
}

function choose()
{
    echo "start"
    sleep 2
    untar
    echo "cp img to $imgPath"
    sleep 2
    mvimg
}

# start run project
if [ ! -d $imgPath ];then
    echo "now mkdir $imgPath"
    mkdir $imgPath
fi
case $command in
  (untar)
     choose
     ;;
  ('')
    echo "do not need untar, please sure the folder $imgPath exist"
    ;;
esac
echo "First -->>> filter images between brightness and canny"
sleep 1
python3 ./python/python.py $imgPath

echo "Next -->>> filter images by similarity, this step will take some time!"
sleep 1
./build/img_filter --img_path $imgPath

echo "End -->>> compare bbox between v2 and v3, wait for a moment"
python3 ./v3_detect.py $imgPath
python3 ./v2_detect.py $imgPath
python3 ./compare_bbox.py $imgPath

echo "Now write all results to txt file"
python3 ./python/filter_res.py $imgPath

echo "All pass, you can check the result in ./data/result/{the_folder_you_define}/ && ./res/{the_folder_you_define}/"
# the end
