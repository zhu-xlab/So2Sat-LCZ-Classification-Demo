The script "sentinel_1_download.py" downloads sentinel-1 data automatically.

Inputs:
	- roi files:	--"kml" or "tiff" files, save in '/data/ROI'
	- others: 	-- various inputs setting: line 20 to line 50

Outputs:
	- S1 data	-- data saved in /data/Sentinel-1/, set by "outdir"


Run the download:
source activate sipeo_so2sat_demo
python sentinel_1_download.py
