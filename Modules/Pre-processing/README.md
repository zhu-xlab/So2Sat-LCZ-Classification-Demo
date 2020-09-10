Run the following codes:

python geocoding_core.py ../../data/Sentinel-1/00331_204371_Munich templates/gpt_template_preprocessing_lee_KML_UTM.xml UN_city_list_rect.kml

python geocoding_core.py ../../data/Sentinel-1/00331_204371_Munich templates/gpt_template_preprocessing_unfilt_KML_UTM.xml  UN_city_list_rect.kml
 

python mosaic_core.py ../../data/Sentinel-1/00331_204371_Munich gpt_template_preprocessing_lee_KML_UTM.xml UN_city_list_rect.kml

python mosaic_core.py ../../data/Sentinel-1/00331_204371_Munich gpt_template_preprocessing_unfilt_KML_UTM.xml UN_city_list_rect.kml





