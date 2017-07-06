#!/usr/bin/python3.5
#reads the BASIC output files and creates json files

#change directory to be launched by crontab
import os
os.chdir('/home/augustinm/Desktop/Dev/profiles')

basic_path='/disk1/augustinm/BASIC_out/out/'
output_path='./json/'

dds=["%.2d" % i for i in range(31+1)]
mms=["%.2d" % i for i in range(12+1)]
yrs=['2017']

mms=['','07']
yyyys=['2017']


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

            calmap={}

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

            obj_ext={}
            obj_scn={}

            #reads each basic_out file
            #/disk1/augustinm/BASIC_out/out/Oslo/1706/14/sa_50/Oslo170614_INV
            #Time(UT)        aod@1064        SI      clear_nb        total_nb        Sa(sr)  15      30      45      60
            import csv
            for i, stat in enumerate(statname):
                basicfile=basic_path+statname[i]+'/'+yy+mm+'/'+dd+'/'+'sa_50'+'/'+statname[i]+yy+mm+dd+'_INV';
                import os.path
                if os.path.isfile(basicfile):
                    readCSV = csv.reader(open(basicfile), delimiter='\t')
                else:
                    break

                j = 0
                TIME, AOD, SI, CLEAR_FRAC, SA, EXT = [], [], [], [], [], []
                for row in readCSV:
                    if j==0:
                        head=row
                    if j>0: # 1 header line
                        time=float(row[0])
                        aod=float(row[1])
                        si=float(row[2])
                        clear_nb=int(row[3])
                        total_nb=int(row[4])
                        sa=float(row[5])
                        ext=[float(val) for val in row[6:-1]]
                        #append
                        TIME.append(time)
                        AOD.append(aod)
                        SI.append(si)
                        CLEAR_FRAC.append(clear_nb/total_nb)
                        SA.append(sa)
                        EXT.append(ext)
                    j += 1

                z_agl=[int(val) for val in head[6:-1]]
                #flag values
                TIME=np.array(TIME)
                AOD=np.array(AOD)
                SI=np.array(SI)
                CLEAR_FRAC=np.array(CLEAR_FRAC)
                SA=np.array(SA)
                EXT=np.array(EXT)
                AOD[AOD<=fillval]=np.nan
                SI[SI<=fillval]=np.nan
                EXT[EXT<=fillval]=np.nan


                #hourly averages
                hTIME=np.arange(0,24)
                hAOD, hSI, hCLEAR_FRAC, hSA, hEXT, hSCENE = [], [], [], [], [], []


                for t in hTIME:
                    itime=np.where(abs(TIME-(t+0.5))<=0.5)
                    haod=np.nanmean(AOD[itime])
                    hsi=np.nanmean(SI[itime])
                    hclear_frac=np.nanmean(CLEAR_FRAC[itime])
                    hsa=np.nanmean(SA[itime])
                    hext=np.nanmean(EXT[itime,:],axis=1)
                    #append
                    hAOD.append(haod)
                    hSI.append(hsi)
                    hCLEAR_FRAC.append(hclear_frac)
                    hSA.append(hsa)
                    hEXT.append(hext)
                    if hclear_frac>=fracaer:
                        hSCENE.append('aer')
                    else:
                        hSCENE.append('cloud')
                #remove the one dimension
                hEXT=np.squeeze(hEXT)

                output_path='./json/'

                #makedir
                import os
                os.makedirs(output_path+yyyy+mm+'/ext/', exist_ok=True)

                #write the file
                outf=output_path+yyyy+mm+'/ext/'+statname[i]+'_'+yyyy+mm+dd+'_ceilo'+'.json'

                data={}
                #header
                data["station"]={}
                data["station"]["name"]=str(statname[i])
                data["station"]["wav"]=str(statwav[i])
                data["station"]["lat"]=str(statlat[i])
                data["station"]["lon"]=str(statlon[i])
                data["station"]["ele"]=str(statele[i])


                #data
                data[str(yyyy+mm+dd)]={}
                data[str(yyyy+mm+dd)]["z"]=z_agl

                hEXT=np.array(hEXT)
                maxext=[]
                for j, t in enumerate(hTIME):
                    data[str(yyyy+mm+dd)][str(t).zfill(2)]={}

                    strext=[round(val,5) for val in hEXT[j,:]]
                    strext2= [str(txt).replace('nan','-99').replace("'", "") for txt in strext]
                    data[str(yyyy+mm+dd)][str(t).zfill(2)]["ext"]=[float(txt) for txt in strext2]
                    data[str(yyyy+mm+dd)][str(t).zfill(2)]["scene"]=hSCENE[j]
                    maxext.append(np.nanmax([float(txt) for txt in strext2]))
                with open(outf, 'w') as outfile:
                    json.dump(data, outfile)
                
                
                #put arrays in objects
                obj_scn[stat]=data[str(yyyy+mm+dd)][str(t).zfill(2)]["scene"]=hSCENE
                obj_ext[stat]=maxext
        
            #creates directory
            import os
            os.makedirs(output_path+yyyy+mm+'/calmap/', exist_ok=True)
        
            #write the file
            outf2=output_path+yyyy+mm+'/calmap/'+yyyy+mm+'.json'

            #test opening file
            import os.path
            if os.path.isfile(outf2):
                with open(outf2) as data_file:
                    calmap = json.load(data_file)
            else:
                #if fail
                for i, stat in enumerate(statname):
                    calmap[statname[i]]={}
                    calmap[statname[i]]["name"]=str(statname[i])
                    calmap[statname[i]]["wav"]=str(statwav[i])
                    calmap[statname[i]]["lat"]=str(statlat[i])
                    calmap[statname[i]]["lon"]=str(statlon[i])
                    calmap[statname[i]]["ele"]=str(statele[i])

            #wether the file existed or not, append the day result
            #for each day, arrays of horly ext and scenes
            for i, stat in enumerate(statname):
                if stat in obj_scn:
                    calmap[statname[i]][str(dd).zfill(2)]={}
                    calmap[statname[i]][str(dd).zfill(2)]['scene']=obj_scn[stat]
                    calmap[statname[i]][str(dd).zfill(2)]['max_ext']=obj_ext[stat]

            with open(outf2, 'w') as outfile2:
                json.dump(calmap, outfile2)


