#!/bin/bash
# File              : all2utm.sh
# Author            : Chunping Qiu
# Date              : 06.07.2018 12:07:22


#the dir of the original tif files (in WGS82 projection)
#tifDir='/datastore/DATA/classification/SEN2/global_processing/0test'

#tarSave='/datastore/DATA/classification/SEN2/global_utm'
export tarSave=$1

# I changed it to run inside each city dir. Y. Wang
export CITY_DIR=`pwd`
export CITY_NAME=`basename $CITY_DIR`

export f=$CITY_NAME


echo $f
code=${f#*_}
code=${code%_*}
echo $code

echo $ROI
# get utm projection ref
utmProj="$(python $P_UTIL/readROI2UTM.py $CITY_DIR $ROI)"
#echo $utmProj

# get ROI extent
utmPoints="$(python $P_UTIL/readROI2xyMinMax.py $CITY_DIR $ROI)"
#echo $utmPoints

# separate 2 corners
xmin=${utmPoints%% *}
#echo $xmin

ymin=${utmPoints#* }
ymin=${ymin%% *}
#echo $ymin

xmax=${utmPoints#* }
xmax=${xmax#* }
xmax=${xmax%% *}
#echo $xmax

ymax=${utmPoints##* }
echo "INFO:	Project to UTM Zone: $utmProj"
echo "INFO:	UTM extent: x = $xmin to $xmax, y = $ymin to $ymax"

seasons=$(ls -d {"spring","summer","autumn","winter"})

#if seasons not 4, then write to log (warning! tbd)
for seas in $seasons; do

	# target tif path
	utmFile=$tarSave/$f/$seas/$code'_'$seas.tif

	mkdir -p $tarSave/$f/$seas

	echo $utmFile

	# find number of tif under each season
	num=$(find $CITY_DIR/$seas -type f | wc -l)
	#echo $num


	# ls all tifs
	files=$(find $CITY_DIR/$seas/ -name '*.tif')

	#echo $tarFile
	echo $files

	gdalwarp -overwrite -multi -wo "NUM_THREADS=4" -t_srs "$utmProj" -tr 10 10 -r cubic -te $xmin $ymin $xmax $ymax $files $utmFile


	# check if the file was written, exit if not
	if [ ! -f $utmFile ]; then
		exit 1
	fi
done

# if the last file was written, then write ok file
if [ -f $utmFile ]; then
	printf '%s' "0" > OK.utm_translate
else
        exit 1
fi
