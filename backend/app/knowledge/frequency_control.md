# Frequency Control & Load Shedding

## Normal Band
50Hz nominal, tolerance 49.5-50.5Hz (or 60Hz in US, here we standardize 50 for simplicity, 60Hz documented as 59.5-60.5).

## Emergency Bands
- 49.5Hz: Warning, reduce non-critical loads 10%
- 49.0Hz: Shed 25% loads, L3 residential first non-critical
- 48.5Hz: Shed 50%, protect industrial critical
- 47.5Hz: Island and trip.

## Recovery Load Blocks
Max 5MW or 10% of online capacity per 5 minutes.

## V2G Support
EV fleet can provide up to 3MW V2G if SoC >60% and approved by owner. Use only after step 4.

## Battery Role
Batt-1 provides fast frequency response: droop 5%, respond within 200ms.

## Communication
If SCADA lost (cyber outage), switch to manual voice and log.
