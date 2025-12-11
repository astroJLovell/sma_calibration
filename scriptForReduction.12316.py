'''
October  2024, Clara Ross  -- original calibration script [applycal commands]
January  2025, Josh Lovell -- updated to add in plotms checks
November 2025, Josh Lovell -- updated for more generic usage, outputting calibrated MS files
Apply COMPASS-derived Calibration solutions to MS

This is an example for the calibration of SMA Obsid 12316
'''
import os
import numpy as np
from casatasks import (listobs, delmod, flagdata, setjy, bandpass, gaincal,
                       applycal, blcal, fluxscale, flagmanager)
from casaplotms import plotms

#settings
checkFlags_chan = True
checkFlags_time = True

# define obs & ms ids -- make sure these match your data
sma_spChans = 16384
rebin = 2
Nspws = 12
NchansData = int(sma_spChans/rebin)
myvis = '230825_12:48:49_bin2.cp.ms'
obsid = '12316'
dataID = 'SUB.351'
fieldnames = ['3c84','bllac','Callisto','mwc349a','Uranus','0102+584','DraChi']

# define cal source names & ids
# note some of these may need turning off dependent on how many cal sources you have... 
bpcal1 = fieldnames[0]
bpcal2 = fieldnames[1]
bothbpcal = f"{bpcal1},{bpcal2}"
bandpass1_selfcal = f'{obsid}_{bpcal1}_selfcal_solns.ms'
bandpass2_selfcal = f'{obsid}_{bpcal2}_selfcal_solns.ms'
bothbpcalid = [bandpass1_selfcal,bandpass2_selfcal]

flux1 = fieldnames[2]
flux2 = fieldnames[3]
flux3 = fieldnames[4]
bothflux = f"{flux1},{flux2},{flux3}"
flux1_selfcal = f'{obsid}_{str.lower(flux1)}_selfcal_solns.ms'
flux2_selfcal = f'{obsid}_{str.lower(flux2)}_selfcal_solns.ms'
flux3_selfcal = f'{obsid}_{str.lower(flux3)}_selfcal_solns.ms'
bothfluxid = [flux1_selfcal,flux2_selfcal,flux3_selfcal]

pcal1 = fieldnames[5]
bothpcal  = f"{pcal1}"
amp_soln = f'{obsid}_amp_solns.ms'
pha_soln = f'{obsid}_pha_solns.ms'

## JOIN ALL CALFIELDS
calfields = ",".join([bothbpcal, bothpcal, bothflux])

scifield1 = fieldnames[6]
science_fields = ",".join([scifield1])
fieldname = scifield1


# check results
print('Bandpass cal:',bothbpcal)
print('Flux cals:',bothflux)
print('Phase cals:',bothpcal)
print('Science target/s:',science_fields)
input(f"Is that correct? If not: Kill the script!!")  # FOR python 3 (CASA 6)

input(f"Did you comment out previous flags? If not: Kill the script!!")  # FOR python 3 (CASA 6)
#flagdata(vis=myvis, mode='manual', timerange='2024/07/31/10:08:40~2024/07/31/10:09:40', field='bllac') ## example flag

# check flagging manually
# frequencies/channels
if checkFlags_chan == True:
  for myfield in calfields.split(","):
    plotms(vis=myvis, xaxis='channel',
           yaxis='amp',field=myfield, avgtime='1e8', avgscan=False,
           coloraxis='ant1',iteraxis='spw', ydatacolumn='data',
           gridrows=4, gridcols=3, yselfscale=True, showgui=True)
    input(f"Done checking  freq. flags for {myfield}?")  # FOR python 3 (CASA 6)

  #time outliers
if checkFlags_time == True:
  for myfield in calfields.split(","):
    plotms(vis=myvis, xaxis='time',
           yaxis='amp',field=myfield, avgchannel=str(NchansData),
           coloraxis='ant1',iteraxis='spw', ydatacolumn='data',
           gridrows=4, gridcols=3, yselfscale=True, showgui=True)
    input(f"Done checking time flags for {myfield}?")  # FOR python 3 (CASA 6)

print('All calibrator flagging checked... Moving to calibration...')
input(f"If flags need adding: KILL SCRIPT NOW!")  # FOR python 3 (CASA 6)


#############################
### apply amp/phase solns ###
#############################
# Apply solutions to phase calibrators
applycal(myvis,
         field=bothpcal,
         spw="",
         gaintable=[amp_soln,pha_soln],
         gainfield=['nearest','nearest'], # nearest on sky for gcal
         interp=['linear,linear',         # linear in time, linear in freq
                 'linear,linear'],
         calwt=True)
print('Calibration applied to: ',bothpcal)

# Apply solutions to science targets
for scifield in science_fields.split(","):
  applycal(vis=myvis,
           field=scifield,
           spw="",
           gaintable=[amp_soln,pha_soln],
           interp=['linear,linear','linear,linear'],
           calwt=True)
  print('Calibration applied to: ',scifield)

# Apply self-calibration solutions

# bandpass
i=0
for bpcals in bothbpcal.split(","):
  applycal(myvis,
           field=bpcals,
           spw='',
           gaintable=bothbpcalid[i],
           interp=['linear,linear'],
           calwt=True)
  print('Calibration applied to: ',bothbpcalid[i])
  i+=1

# flux
i=0
for fluxcal in bothflux.split(","):
  applycal(myvis,
           field=fluxcal,
           spw="",
           gaintable=bothfluxid[i],
           interp=['linear,linear'],
           calwt=True)
  print('applied gaincal to: ',bothfluxid[i])
  i+=1

flagmanager(vis=myvis, mode='save', versionname='afterapplycal')

print('#####')
print('#####')
print('#####')
print('Calibration complete! Now producing summary plots...')
print('#####')
print('#####')
print('#####')


## produce corrected measurement sets
for scifield in science_fields.split(","):
  mstransform(vis=myvis, field=scifield, datacolumn='corrected', outputvis=f'{scifield}.{dataID}.cal.cor.fullres.ms')
  bins = [NchansData/2]*Nspws
  for i in range(len(bins)):
    bins[i] = int(bins[i])
  mstransform(vis=myvis, field=scifield, datacolumn='corrected', outputvis=f'{scifield}.{dataID}.cal.cor.cont.ms', chanaverage=True, chanbin=bins)


## produce summary plotms of final results
plotms(vis=myvis,xaxis='Time',yaxis='phase',
       field=bothpcal,avgchannel=str(NchansData),
       avgfield=True,coloraxis='baseline',iteraxis='antenna',ydatacolumn='corrected',
       plotfile=myvis+'.aftercal.gainpha.png',gridrows=3,gridcols=3)
input(f"Done viewing data?")  # FOR python 3 (CASA 6)

plotms(vis=myvis,xaxis='freq',
         yaxis='amp',field=bothpcal,avgtime='1e8',avgscan=True,
         coloraxis='spw',iteraxis='antenna',ydatacolumn='corrected',
         plotfile=myvis+'.aftercal.specamp.png',gridrows=3,gridcols=3)
input(f"Done viewing data?")  # FOR python 3 (CASA 6)

plotms(vis=myvis,xaxis='freq',
         yaxis='phase',field=bothpcal,avgtime='1e8',avgscan=True,
         coloraxis='spw',iteraxis='antenna',ydatacolumn='corrected',
         plotfile=myvis+'.aftercal.specpha.png',gridrows=3,gridcols=3)
input(f"Done viewing data?")  # FOR python 3 (CASA 6)


## View science data per spw
print('Plotting corrected science data...')
for scifield in science_fields.split(","):
  print('Plotting ',scifield)
  plotms(vis=myvis,yaxis='amp',xaxis='freq',avgtime='1e8',avgscan=True,field=scifield,
         coloraxis='spw',iteraxis='spw', ydatacolumn='corrected')
  input(f"Done viewing data?")  # FOR python 3 (CASA 6)
