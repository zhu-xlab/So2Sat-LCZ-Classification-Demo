# DLR-TUM SiPEO TEAM
# So2Sat Project
# Sentinel-1 data sets download prototype
# PhD Candidate: Jingliang Hu
# Email: jingliang.hu@dlr.de
# 19.12.2017
# reorganized in 09.2020
# modified in 05.2021
import os
import logging
import glob
from shapely.wkt import loads
from osgeo import ogr,osr,gdal
import pandas as pd
from sentinelsat.sentinel import SentinelAPI
import sentinelsat
import numpy as np
print(sentinelsat.__file__)



def run_download_from_pool(product_id, out_dir, username, password):
    url = 'https://scihub.copernicus.eu/dhus'
    d_api = SentinelAPI(username, password, url)
    try:
        download_info = d_api.download(product_id, directory_path=out_dir)
    except:
        print('Server connection error')
        return 0
    if os.path.exists(out_dir+'/'+download_info['title']+'.zip'):
        os.mknod(out_dir+'/'+download_info['title']+'.ok')
        print('data_downloaded')
        #os.remove(out_dir+'data_product_id')
    elif download_info['Online']:
        # os.mknod(out_dir+"online_not_downloaded.ok")
        print('online_but_not_downloaded')
    elif not download_info['Online']:
        retrievel_code = d_api._trigger_offline_retrieval(download_info['url'])
        # check https://scihub.copernicus.eu/userguide/LongTermArchive#HTTP_Status_codes
        if retrievel_code == 202:
            # os.mknod(out_dir+"retrieval_accepted.ok")
            print("offline product retrieval accepted")
        elif retrievel_code == 403:
            # os.mknod(out_dir+"requests_exceed_quota.ok")
            print("offline product requests exceed quota")
        elif retrievel_code == 503:
            # os.mknod(out_dir+"retrieval_not_accepted.ok")
            print("offline product retrieval not accepted")
    return download_info


     

def run_download(product_id, out_dir, username, password):
    # start the downloading with the data id, output directory, and sentinelsat api
    #file_object = open(out_dir+'data_product_id',"w")
    #file_object.write(product_id)
    #file_object.close()
    url = 'https://scihub.copernicus.eu/dhus'
    d_api = SentinelAPI(username, password, url)
    try:
        download_info = d_api.download(product_id['uuid'], directory_path=out_dir)
    except:
        print('Server connection error')
        return 0

    if os.path.exists(out_dir+download_info['title']+'.zip'):
        os.mknod(out_dir+download_info['title']+'_data_downloaded.ok')
        print('data_downloaded')
        retrievel_code = 1
        #os.remove(out_dir+'data_product_id')
    elif download_info['Online']:
        # os.mknod(out_dir+"online_not_downloaded.ok")
        print('online_but_not_downloaded')
    elif not download_info['Online']:
        retrievel_code = d_api._trigger_offline_retrieval(download_info['url'])
        # check https://scihub.copernicus.eu/userguide/LongTermArchive#HTTP_Status_codes
        if retrievel_code == 202:
            # os.mknod(out_dir+"retrieval_accepted.ok")
            print("offline product retrieval accepted")
        elif retrievel_code == 403:
            # os.mknod(out_dir+"requests_exceed_quota.ok")
            print("offline product requests exceed quota")
        elif retrievel_code == 503:
            # os.mknod(out_dir+"retrieval_not_accepted.ok")
            print("offline product retrieval not accepted")
    return retrievel_code

def roi_footprint(coordinate):
    xmin = coordinate[0]
    xmax = coordinate[1]
    ymin = coordinate[2]
    ymax = coordinate[3]

    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(xmin,ymin)
    ring.AddPoint(xmax,ymin)
    ring.AddPoint(xmax,ymax)
    ring.AddPoint(xmin,ymax)
    ring.AddPoint(xmin,ymin)
    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)
    footprint = poly.ExportToWkt()
    roiPolygon = loads(footprint)
    return footprint, roiPolygon


def roi_buffer_footprint(coordinate):
    x_buffer = (coordinate[1]-coordinate[0])/10
    y_buffer = (coordinate[3]-coordinate[2])/10
    xmin = coordinate[0] - x_buffer
    xmax = coordinate[1] + x_buffer
    ymin = coordinate[2] - y_buffer
    ymax = coordinate[3] + y_buffer

    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(xmin,ymin)
    ring.AddPoint(xmax,ymin)
    ring.AddPoint(xmax,ymax)
    ring.AddPoint(xmin,ymax)
    ring.AddPoint(xmin,ymin)
    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)
    footprint = poly.ExportToWkt()
    roiPolygon = loads(footprint)
    return footprint, roiPolygon

def multiple_data_of_same_orbit_cover_roi(products, roiPolygon):
    roi = loads(roiPolygon)
    orbit_numbers = np.unique(products.orbitnumber)
    for idx in range(len(orbit_numbers)):
        orbitData = products[products.orbitnumber == orbit_numbers[idx]]
        targetData = pd.DataFrame()
        for idx, orbit_row in orbitData.iterrows():
            scenePolygon = loads(orbit_row['footprint'])
            if roi.intersects(scenePolygon):
                targetData = targetData.append(orbit_row)
                if 'join_area' in locals():
                    join_area = join_area.union(scenePolygon)
                else:
                    join_area = scenePolygon
                if join_area.contains(roi):
                    return targetData
    return 0


def multiple_data_of_same_direction_cover_roi(products, roiPolygon):
    roi = loads(roiPolygon)
    orbit_directions = np.unique(products.orbitdirection)
    for idx in range(len(orbit_directions)):
        orbitData = products[products.orbitdirection == orbit_directions[idx]]
        targetData = pd.DataFrame()
        for idx, orbit_row in orbitData.iterrows():
            scenePolygon = loads(orbit_row['footprint'])
            if roi.intersects(scenePolygon):
                targetData = targetData.append(orbit_row)
                if 'join_area' in locals():
                    join_area = join_area.union(scenePolygon)
                else:
                    join_area = scenePolygon
                if join_area.contains(roi):
                    return targetData
    return 0


def single_data_cover_roi_loopin(products, roiPolygon):
    for index, row in products.iterrows():
        data_footprint = loads(row['footprint'])
        if data_footprint.contains(roiPolygon):
            return row
    return 0


def single_data_cover_roi(data_record, roi_footprint):
    data_footprint = loads(data_record['footprint'])
    if data_footprint.contains(roi_footprint):
        data_tbd = data_record
    else:
        data_tbd = 0
    return data_tbd

def data_record_orbit_sorting(products):
    # First descending orbit, then ascending orbit 
    products.sort_values(['orbitdirection'],ascending = [False])
    return products


def retrieve_mata_data(filename,username,password):
    url = 'https://scihub.copernicus.eu/dhus'
    info = filename.split('_')
    satellite = info[0]
    mode = info[1]
    product = info[2]
    orbitnumber = np.int(info[7])
    time_start = np.int(info[5].split('T')[0])-1
    time_end = str(np.int(time_start+2))
    time_start = str(time_start)

    api = SentinelAPI(username, password, url)
    products = api.query(
                         beginposition=(time_start,time_end),
                         platformname='Sentinel-1',
                         producttype=product,
                         sensoroperationalmode=mode,
                         polarisationmode='VV VH',
                         orbitnumber=orbitnumber
                         )

    products_df  = api.to_dataframe(products)
    index = -1
    for i in range(len(products_df)):
        if products_df['title'][i] in filename:
            index = i

    return products_df.iloc[index]
