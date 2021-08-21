#### Helping ALMA to gain scientific insights from their observations

The ALMA observatory in Chile produces ~800GB of data/day. This small webapp, helps them visualize results of observations for the Astronomer on Duty (AoD).


#### Usage

Install the requirements in the parent folder. Then run the web-app with:
```
python dash_alma_qa0.py
```
The terminal should spit out a localhost link where you can open the webapp.

The actual webapp used in production is the dss file, which additionally allows selection from 800 UIDs and relies partly on postgresql queries as the production is too large for pandas.
