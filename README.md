SMA calibration scripts. 

Note: on COMPASS-derived products --
COMPASS v.0.11 provides pre-flagged, flux-calibrated and bandpass-calibrated solutions.
If you do not have COMPASS-derived SMA products, the 'scriptForReduction.12316.py' file will not correctly calibrate your data; this script simply applies the gain solutions to the data.

For standard SMA Archive measurement set outputs, the more extensive scriptForReduction.full.py file is required with flags.txt and the general sma_reduction package (TO BE ADDED HERE SOON).
