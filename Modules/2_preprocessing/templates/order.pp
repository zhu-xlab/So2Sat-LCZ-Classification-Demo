# File              : order.pp
# Author            : Yuanyuan Wang <y.wang@tum.de>
# Date              : 12.05.2018 13:15:02
# Last Modified Date: 12.05.2018 13:15:02
# Last Modified By  : Yuanyuan Wang <y.wang@tum.de>
#
# this is the sample order file for SEN1  preprocessing
# -----------------------------------------------------
#
########################################################

# Last modified: 12.05.2018 13:15:35 Yuanyuan Wang
# Last modified: 12.05.2018 17:47:51 Yuanyuan Wang
# added the path for the ROI KML file

# Last modified: 13.05.2018 21:13:24 Yuanyuan Wang
# add order_type to use a single order file for either LCZ42 and production

# Last modified: 04.07.2018 16:57:54 Yuanyuan Wang
# changed order_type to refer to what processing, added cnn_model_path

# ---------------------------------------------------------------------------------------------
# PROCESSING IDENTIFICATION
# ---------------------------------------------------------------------------------------------

job_name                SEN1_1700
email                   yuanyuan.wang@dlr.de

# ---------------------------------------------------------------------------------------------
# CONFIGURATION PARAMETERS
# ---------------------------------------------------------------------------------------------

order_type		PREPROCESSING 
dataset			production

# ---------------------------------------------------------------------------------------------
# INPUT/PROCESSING/OUTPUT DIRECTORIES/FILES
# ---------------------------------------------------------------------------------------------

working_directory	/datastore/exchange/sentinel/LCZ42_SEN1
roi_file_path		/home/wang/sentinel_test/auxdata/UN_city_list_rect.kml	
ground_truth_directory  /datastore/DATA/classification/LCZ42_ORIGIANL_LABEL/LCZ42
cnn_model_path		/home/hu/sen1_cnn_model/resnet_dB_feat7.h5


# ---------------------------------------------------------------------------------------------
# # PARAMETERS AND KEYS
# # ---------------------------------------------------------------------------------------------
#
# order_type: determine what processing to perform
#	
#	It takes only the following strings
#	a. PREPROCESSING
#	b. CLASSIFICATION
#	c. ALL
# 
# dataset: what type of dataset, lcz42 or production?
#	a. lcz42
#	b. production
#
# job_name: an arbitary identifier to distinguish different processing, e.g. LCZ42_NO_LEE_FILTER
#
#
# email: your email address for notification. 
#	 you can disable the email notification by commenting out the "email_error.sh" "email_ok.sh"
#	 in "s1p.sh"
#	 Note: somehow LRZ emails (@tum.de, @lrz.de, etc.) does not accept emails send out by our server.
#	 Please use DLR email
#
# working_directory: the directory with the SEN1 images of different cities, you must have write 
#	permission
#
#
# roi_file_path: the KML file defines the ROI for each city
#
#
# ground_truth_dir: the direcotry with the ground truth label of all 42 cities
#
#
#
#
#
#
#
##################################################################################################

