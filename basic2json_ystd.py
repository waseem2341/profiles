#!/usr/bin/python3.5
#similar to basic2json for yesterday (useful for cron)

basic_path='/disk1/augustinm/BASIC_out/out/'
output_path='./json/'

#get yesterday date
import datetime
ystd = datetime.datetime.now() - datetime.timedelta(days=1)
year = ystd.year
month = ystd.month
day = ystd.day

yyyy='%4d' % year
mm='%02d' % month
dd='%02d' % day


fillval=-9.9
fracaer=0.8 #fraction nb_cøear/nb_tot considered as aerosol scene. Clouds below this fraction

#required modules
import numpy as np
import time
from datetime import datetime


#for yyyy in yrs:
#    for mm in mms[1:]:
#        for dd in dds[1:]:
print(yyyy+'/'+mm+'/'+dd)
yy=yyyy[2:]

import csv
sitesfile='./sites.csv'
statname, statlat, statlon, statele, statwav = [], [], [], [], []
readCSV = csv.reader(open(sitesfile), delimiter=',')
i = 0
for row in readCSV:
    if i>0: # 1 header line
        print(row)
        statname.append(row[0])
        statlat.append(float(row[1]))
        statlon.append(float(row[2]))
        statele.append(float(row[3]))
        statwav.append(float(row[4]))
    i += 1


#reads each basic_out file
#/disk1/augustinm/BASIC_out/out/Oslo/1706/14/sa_50/Oslo170614_INV
#Time(UT)        aod@1064        SI      clear_nb        total_nb        Sa(sr)  15      30      45      60

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
    os.makedirs(output_path+yyyy+mm, exist_ok=True)

    #write the file
    outfile=output_path+yyyy+mm+'/'+statname[i]+'_'+yyyy+mm+dd+'_ceilo'+'.json'
    f = open(outfile, 'w')

    #header
    f.write('{'+'\n')
    f.write('"station": {'+'\n')
    f.write('"name": "'+str(statname[i])+'"'+','+'\n')
    f.write('"wav": "'+str(statwav[i])+'",'+'\n')
    f.write('"lat": "'+str(statlat[i])+'",'+'\n')
    f.write('"lon": "'+str(statlon[i])+'",'+'\n')
    f.write('"ele": "'+str(statele[i])+'"'+'\n')
    f.write('},'+'\n')

    f.write('"'+yyyy+mm+dd+'": {'+'\n')
    f.write('"z": '+str(z_agl)+','+'\n')

    hEXT=np.array(hEXT)
    for j, t in enumerate(hTIME):
        f.write('"'+str(t).zfill(2)+'": {'+'\n')
        strext=[round(val,5) for val in hEXT[j,:]]
        strext2= [str(txt).replace('nan','-99') for txt in strext]
        f.write('"ext": '+str([txt for txt in strext2]).replace("'", "")+','+'\n')
        f.write('"scene": "'+str(hSCENE[j])+'"\n')
        #the last } must have no comma
        if j<len(hTIME)-1:
            f.write('},'+'\n')
        else:
            f.write('}'+'\n')

    f.write('}'+'\n')
    f.write('}'+'\n')
    f.close()




#example of valid json file
'''
{
"station": {
"name": "Oslo",
"lat": "xx",
"lon": "yy",
"ele": "zz"
},

"20170605": {
"z": [0.10, 0.15, 0.30],
"00": {
"ext": [0.10, 0.15, 0.30],
"typ": "aer"
},
"01": {
"ext": [0.10, 0.15, 0.30],
"typ": "cloud"
},
"02": {
"ext": [0.10, 0.15, 0.30],
"typ": "aer"
}
}
}
'''
