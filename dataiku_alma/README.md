#### Helping ALMA to gain scientific insights from their observations

The ALMA observatory in Chile produces ~800GB of data/day. This small webapp, helps them visualize results of observations for the Astronomer on Duty (AoD).


#### Usage

Install the requirements in the parent folder. Then run the web-app with:
```
python dash_alma_qa0.py
```
The terminal should spit out a localhost link where you can open the webapp.

The actual webapp used in production is the dss file, which additionally allows selection from 800 UIDs and relies partly on postgresql queries as the production dataset of >10GB is too large for pandas. Once the UID has been selected via SQL, however, it shrinks down to a couple thousand rows doable with pandas.


#### Basic glossary

* **ALMA Calibrator Source Catalog (ALMA SC)**: The ALMA Calibrator Source Catalogue is a database of astronomical measurements of calibrator sources, mostly bright quasars in the mm and sub-mm regime. It contains over 11000 ALMA measurements of over 1800 sources (1 July 2015). The most important properties are flux density with uncertainty at a given frequency. A main use of the database is to allow the selection of bandpass and phase calibrators for science observations. It also contains a set of ~30 quasars, **grid sources** evenly distributed over the sky, which are monitored regularly enough to provide amplitude (flux or brightness) calibration in addition to solar system objects.

* **Grid sources**: the set of circa 30 quasars that are regularly used to calibrate the flux density scale, or brightness, of the astronomical objectes observed with ALMA. **This is the subset of sources that we will use for the challenge**.

* **Source**: in radioastronomy jargon, any object in the sky that emmits energy (brights) in the radio frequencies. For this particular challenge, we will use *Calibrator* sources.

* **Scheduling Block (SB)**: is the set of instructions that are given to the ALMA system in order to make an observation. It contains the coordinates of the target sources, the frequency to be used when observing, the observing plan, etc. One SB can be used multiple times to make multiple observations.

* **Execution Block (EB)**: is the observation originated by a the execution of a Scheduling Block instructions. A acience observation is composed by a list of "scans" or steps that are made to obtain not only the science data, but also the data that is requried to reduce and calibrate this science data.

* **ALMA Science Data Model (ASDM)**: The data model used by ALMA to store the data collected by an Execution Block, or observation. It is a set of xml files organized in folders, and it contains not only the "raw data" (or the signal collected from the sky) but also the "metadata" which provides information about the data collected and the data used for calibration purposes. This metadata is used also to make a quality check or quaity assurance of the data obtained. 

* **Antenna**: a radio telescope and radio receiver system used to detect radio waves from astronomical radio sources in the sky. Each antenna has a reflector that performs the same function as a mirror in an optical telescope: capturing radiation from distant astronomical objects and directing it towards a Receiver that measures the levels of that radiation in a particular frequency.

* **Receiver**: The electronic instrument that transforms the incoming signal from a radio source into information that can be stored and analyzed. A receiver will detect signals only in particular frequency ranges, or band.

* **Band**: a range of frequencies that can be observed with a receiver. Currenly ALMA observes in 8 bands (ALMA Bands 3 to 10), and each band has its own kind of receiver.

* **Baseband**: Each band doesn't not observe a frequency range in a continuum manner. This is because of technical reason that we won't explain here, but you need to know that a band will observe in 4 basebands or frequency ranges at any time. Each baseband has a frequency range.

* **Aperture synthesis or synthesis imaging**: is a type of interferometry that mixes signals from a collection of telescopes (antennas) to produce images having the same angular resolution as an instrument the size of the entire collection. ALMA has a collection of 66 antennas that are used to make this kind of interferometry.

* **Correlator**: The computer that combines the signal of each pair of antennas. The combination of these signals (or correlation) is called interferometry.

* **Baseline**: Each antenna pair is called a baseline. The number of baselines in a correlator, or the total number of antenna pairs that can be made,  given N antennas is N * (N-1) / 2. For example, with 10 antennas you get 45 baselines and with 43 antennas the number rises to 903.

* **Interferometry**: if you are interested in a deeper understanding, you can start with [wikipedia](https://en.wikipedia.org/wiki/Interferometry)
