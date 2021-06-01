'''
This script is a pipeline for Sentinel-1 data preprocessing
Jingliang Hu. 01.06.2021
'''
import os

'''
!!! Install ESA SNAP software, and set the directory to gpt as the environment variable 'gpt'
'''
os.environ['gpt'] = '/home/hu/snap/bin/gpt'

# Take city lagos as an example
city = '00042_20480_Chengdu'



# SNAP GPT processing templates
process_template_lee = 'templates/gpt_template_preprocessing_lee_KML_UTM.xml'
process_template_spk = 'templates/gpt_template_preprocessing_unfilt_KML_UTM.xml'

roi = '../../data/ROI/UN_city_list_rect_buff.kml'

directory_to_city = os.path.join('../../data/Sentinel-1',city)


# call processing modules with LEE speckle reduction
command = ['python geocoding_core.py',directory_to_city,process_template_lee,roi]
os.system(' '.join(command))
command = ['python mosaic_core.py',directory_to_city,process_template_lee,roi]
os.system(' '.join(command))

# call processing modules with no speckle reduction
command = ['python geocoding_core.py',directory_to_city,process_template_spk,roi]
os.system(' '.join(command))
command = ['python mosaic_core.py',directory_to_city,process_template_spk,roi]
os.system(' '.join(command))





