#!/bin/bash

#run the python script
./home/augustinm/Desktop/Dev/profiles/basic2json_ystd.py

#rsync the directories
dirin_json='/home/augustinm/Desktop/Dev/profiles/json/'
dirout_json='/lustre/storeA/project/aerocom/aerocom_img/web/Ceilometer/profiles/json/'
`rsync -r $dirin_json vis-m1:$dirout_json`
