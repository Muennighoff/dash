## Dash Notes

- Python interface for a mix of react js, Flask
- Two parts:
    - Layout
        - dash_core_components 
            - Higher-level, e.g. Graph for interactive components
            - https://dash.plotly.com/dash-core-components
        - dash_html_components
            - All Html attributes, e.g. Div, H1
            - https://dash.plotly.com/dash-html-components
        - Can define your own
    - Interactivity
        - Callbacks - Triggering functions when properties change
        - Graph component

## Plotly specifics

- Python (plotly.py) / Javascript (plotly.js) Library to be used as a graphing component for Dash
- plotly.express "px" > Fast graphs
    - Uses plotly.graph_objects "go" under the hood > Direclty use go for complex graphs
    - Defaults can always be overwritten
    - Can do basic animations



