#!/usr/bin/python
#! -*- encoding: utf-8 -*-
# openmvg Examples of use 
# usage : python tutorial_demo.py

import os
import subprocess
import sys
import pathlib

# openmvg compile bin Catalog ( can cp -p To /usr/local/bin/)
OPENMVG_SFM_BIN = "/home/andrey/openMVG_Build/Linux-x86_64-RELEASE"
# pmvs compile bin Catalog ( can cp -p To /usr/local/bin/)
PMVS_BIN = "/home/andrey/CMVS-PMVS/build/main"
# openmvg Camera parameter catalog 
CAMERA_SENSOR_WIDTH_DIRECTORY = "/home/andrey/openMVG/src/openMVG/exif/sensor_width_database"

def getPhotos(data_dir, input_dir, matches_dir, output_dir):
    # 0.  Download test photos 
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # data_dir = os.path.abspath("./book")
    
    if not os.path.exists(data_dir):
        raise IOError
    print ("Using input dir  : ", input_dir)
    print ("      output_dir : ", output_dir)
    
    if not os.path.exists(matches_dir):
        os.mkdir(matches_dir)

def generateSceneDescription(input_dir, matches_dir, camera_file_params):
    # 1.  Generate scene description file from image dataset sfm_data.json
    print ("----------1. Intrinsics analysis----------")
    pIntrisics = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_SfMInit_ImageListing"),  "-i", input_dir, "-o", matches_dir + "/", "-d", camera_file_params, "-c", "3"] )
    #* notes ： If the output is sfm_data.json in intrinsics Content is empty , Usually in the picture there is no exif Information leads to a loss of camera focus 、ccd Size and other parameters , Band exif The original picture can be .
    pIntrisics.wait()

def calculateImageFeatures(matches_dir):
    # 2.  Calculate image features 
    print ("----------2. Compute features----------")
    pFeatures = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeFeatures"),  "-i", matches_dir+"/sfm_data.json", "-o", matches_dir, "-m", "SIFT", "-f" , "1"] )
    pFeatures.wait()

def calculateGeometricMatches(matches_dir):
    # 3.  Calculating geometric matching 
    print ("----------3. Compute matches----------")
    pMatches = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeMatches"),  "-i", matches_dir+"/sfm_data.json", "-o", matches_dir + "/match.txt", "-f", "1", "-n", "ANNL2"] )
    pMatches.wait()

def runSequentialReconstruction(matches_dir, reconstruction_dir):
    # 4.  Perform incremental 3D reconstruction 
    print ("----------4. Do Incremental/Sequential reconstruction----------") #set manually the initial pair to avoid the prompt question
    pRecons = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_SfM"),  "-i", matches_dir+"/sfm_data.json", "--match_file", matches_dir + "/match.txt", "-o", reconstruction_dir] )
    pRecons.wait()

def calculateSceneStrctureColor(reconstruction_dir):
    # 5.  Calculate the scene structure color 
    print ("----------5. Colorize Structure----------")
    pRecons = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeSfM_DataColor"),  "-i", reconstruction_dir+"/sfm_data.bin", "-o", os.path.join(reconstruction_dir,"colorized.ply")] )
    pRecons.wait()

def measureRobustTriangles(matches_dir, reconstruction_dir):
    # 6.  Measuring robust triangles 
    print ("----------6. Structure from Known Poses (robust triangulation)----------")
    pRecons = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeStructureFromKnownPoses"),  "-i", reconstruction_dir+"/sfm_data.bin", "-m", matches_dir, "-o", os.path.join(reconstruction_dir,"robust.ply")] )
    pRecons.wait()

'''
#  Use global SfM Pipeline reconstruction Reconstruction for the global SfM pipeline
# 3.1  overall situation sfm Pipe geometry matching 
print ("----------3.1. Compute matches (for the global SfM Pipeline)----------")
pMatches = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeMatches"),  "-i", matches_dir+"/sfm_data.json", "-o", matches_dir + "/matches_global.txt", "-r", "0.8", "-g", "e"] )
pMatches.wait()

# 4.1  Perform global 3D reconstruction 
reconstruction_dir = os.path.join(output_dir,"reconstruction_global")
print ("----------4.1. Do Global reconstruction----------")
pRecons = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_SfM"),  "-i", matches_dir+"/sfm_data.json", "--match_file", matches_dir + "/matches_global.txt", "-o", reconstruction_dir] )
pRecons.wait()

# 5.1  Calculate the scene structure color 
print ("----------5.1. Colorize Structure----------")
pRecons = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeSfM_DataColor"),  "-i", reconstruction_dir+"/sfm_data.bin", "-o", os.path.join(reconstruction_dir,"colorized.ply")] )
pRecons.wait()

# 6.1  Measuring robust triangles 
print ("----------6.1. Structure from Known Poses (robust triangulation)----------")
pRecons = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_ComputeStructureFromKnownPoses"),  "-i", reconstruction_dir+"/sfm_data.bin", "-m", matches_dir, "-o", os.path.join(reconstruction_dir,"robust.ply")] )
pRecons.wait()
'''

def exportToPmvs(reconstruction_dir):
    # 7.  hold openMVG Generated SfM_Data To apply to PMVS Input format file 
    print ("----------7. Export to PMVS/CMVS----------")
    pRecons = subprocess.Popen( [os.path.join(OPENMVG_SFM_BIN, "openMVG_main_openMVG2PMVS"),  "-i", reconstruction_dir+"/sfm_data.bin", "-o", reconstruction_dir] )
    pRecons.wait()
    #* notes ： After implementation, it will be in -o Generate a PMVS Catalog , contain  models, txt, visualize  Three subdirectories ：models It's empty ;txt Containing the corresponding image txt file , There is one in each 3x4 Matrix , It's probably the camera position ;visualize contain 11 Zhang image , It's not sure if it's the original image or the corrected image 

def rebuildDensePointCloud(reconstruction_dir):
    # 8.  Use PMVS Rebuild dense point clouds 、 The surface of the 、 texture 
    print ("----------8. pmvs2----------")
    pRecons = subprocess.Popen( [os.path.join(PMVS_BIN, "pmvs2"),  reconstruction_dir+"/PMVS/", "pmvs_options.txt"] )  #  notes ： Do not modify pmvs_options.txt file name 
    pRecons.wait()
    #* notes ： After implementation, it will be in ./PMVS/models Generate one in the folder pmvs_options.txt.ply Point cloud file , use meshlab Open to see the reconstructed color dense point cloud .

def getSfmData(data_dir):
    print("----------9. old openMVG Generated SfM_Data To apply to PMVS Input format file----------")
    os.chdir(os.path.abspath(data_dir + "/reconstruction_sequential/"))
    pRecons = subprocess.Popen([os.path.join("openMVG_main_openMVG2PMVS"), "-i", "sfm_data.bin", "-o", "./"])
    pRecons.wait()

def pmvsRebuildDensePointCloud(data_dir):
    print("----------Use PMVS Rebuild dense point clouds, The surface of the texture----------")
    pRecons = subprocess.Popen([os.path.join("pmvs2"), data_dir + "/reconstruction_sequential/PMVS/", "pmvs_options.txt"])
    pRecons.wait()

def runReconstruction(data_dir):
    # data_dir = os.path.abspath("./ImageDataset")
    print('running reconstruction')
    print('current directory = ' + str(pathlib.Path(__file__).parent.resolve()))
    print('DATADIR: ' + data_dir)
    input_dir = os.path.join(data_dir, "images")
    output_dir = data_dir
    matches_dir = os.path.join(output_dir, "matches")
    reconstruction_dir = os.path.join(output_dir,"reconstruction_sequential")
    camera_file_params = os.path.join(CAMERA_SENSOR_WIDTH_DIRECTORY, "sensor_width_camera_database.txt")    # Camera parameters 
    getPhotos(data_dir, input_dir, matches_dir, output_dir)
    generateSceneDescription(input_dir, matches_dir, camera_file_params)
    calculateImageFeatures(matches_dir)
    calculateGeometricMatches(matches_dir)
    runSequentialReconstruction(matches_dir, reconstruction_dir)
    calculateSceneStrctureColor(matches_dir)
    measureRobustTriangles(matches_dir, reconstruction_dir)
    exportToPmvs(reconstruction_dir)
    rebuildDensePointCloud(reconstruction_dir)
    getSfmData(data_dir)
    pmvsRebuildDensePointCloud(data_dir)

# if __name__ == '__main__':
#     print('running reconstruction...')
#     runReconstruction('/home/andrey/Java-project-server/resources/09c76690-b20f-4ddb-bd63-9dd1c66bbb5c')
