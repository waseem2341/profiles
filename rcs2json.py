#!/usr/bin/python3.5
#reads the RCS files (LOA format) and creates json files

#change directory to be launched by crontab
import os
os.chdir('/home/augustinm/Desktop/Dev/profiles')

basic_path='/disk1/augustinm/Data/Lidar/'
output_path='./json/'

dds=["%.2d" % i for i in range(31+1)]
mms=["%.2d" % i for i in range(12+1)]
yrs=['2017']
'''
dd='02'
mm='06'
yyyy='2017'
'''
mms=['','07']

fillval=-9.9
fracaer=1.0 #fraction nb_cøear/nb_tot considered as aerosol scene. Clouds below this fraction

#required modules
import numpy as np
import time
from datetime import datetime


for yyyy in yrs:
    for mm in mms[1:]:
        for dd in dds[1:]:
            print(yyyy+'/'+mm+'/'+dd)
            yy=yyyy[2:]


            print('stations files reading')
            import json
            sitesfile='./sites.json'
            statname, statlat, statlon, statele, statwav = [], [], [], [], []
            with open(sitesfile) as data_file:
                data = json.load(data_file)

            for stat in data['station']:
                statname.append(stat['name'])
                statlat.append(stat['lat'])
                statlon.append(stat['lon'])
                statele.append(stat['ele'])
                statwav.append(stat['wav'])


            #reads each basic_out file
            #/disk1/augustinm/Data/Lidar/Oslo/2017/06
            #Time (UT)     Range (km)            RCS
            print('rcs file reading',statwav)
            import csv
            for i, stat in enumerate(statname):
                basicfile=basic_path+statname[i]+'/'+yyyy+'/'+mm+'/'+statname[i]+'_'+str(statwav[i])+'_'+yyyy+mm+dd+'.txt';
                import os.path
                if os.path.isfile(basicfile):
                    readCSV = csv.reader(open(basicfile), delimiter='\t')
                else:
                    break

                j = 0
                prev_z, prev_time = -99, -99
                n_z, n_time = 0, 0
                TIME, Z, RCS = [], [], []
                for row in readCSV:
                    if j==0:
                        head=row
                    if j>0: # 1 header line
                        time=float(row[0].split()[0])
                        z=float(row[0].split()[1])
                        rcs=float(row[0].split()[2])
                        
                        #append
                        if time>prev_time:
                            TIME.append(time)
                        if z>prev_z and n_z==0:
                            Z.append(z*1e3)
                        else:
                            n_z+=1
                        
                        RCS.append(rcs)
                         
                        prev_time=time
                        prev_z=z
                    j += 1


                #creates array of z_agl and time
                 
                

                #makedir
                import os
                os.makedirs(output_path+yyyy+mm+'/rcs/', exist_ok=True)

                #write the file
                outf=output_path+yyyy+mm+'/rcs/'+statname[i]+'_'+yyyy+mm+dd+'_ceilo'+'.json'

                data={}
                #header
                data["station"]={}
                data["station"]["name"]=str(statname[i])
                data["station"]["wav"]=str(statwav[i])
                data["station"]["lat"]=str(statlat[i])
                data["station"]["lon"]=str(statlon[i])
                data["station"]["ele"]=str(statele[i])

                #send only altitudes below zmax
                zmax=10000#en m
                Z=np.array(Z)
                idx_zmax=np.where(Z<zmax)
                lidx_zmax=idx_zmax[0][-1]+1
               
                step=5
                #data
                data[str(yyyy+mm+dd)]={}
                data[str(yyyy+mm+dd)]["z"]=Z[0:lidx_zmax:step].tolist()
                for j, t in enumerate(TIME):
                    #reduce size by selecting only odd indexes
                    if j%step==0:
                        fmt_t=str('{:06.3f}'.format(t))
                        strrcs=[round(val,5) for val in RCS[j*len(Z):(j+1)*len(Z)]]
                        data[str(yyyy+mm+dd)][fmt_t]=strrcs[0:lidx_zmax:step]
                
                with open(outf, 'w') as outfile:
                    json.dump(data, outfile)


