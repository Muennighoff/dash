### Dash App for Alma's Astronomer on Duty, who performs Quality Assurance 0 Tasks ###

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objs as go

import utils.dash_reusable_components as drc

import pandas as pd
import numpy as np

app = dash.Dash(__name__)

### DEFINITIONS ###
# Using a single DataFrame saves memory
# Get DF via SQL from database in actual application
df = pd.read_csv("dataiku_alma/ALMA_Xf27c.csv")

# Via SQL on entire table in actual application
uids = df["uid"].unique().tolist()

### LAYOUT ###
# Note that we are using several pre-defined classes commonly used in plotly
# They are defined in CSS files in assets


def panel_layout():
    """Layout for the upper-left Panel"""
    return html.Div(
        id="left-column",
        children=[
            drc.Card(
                id="first-card",
                children=[
                    ### UID ###
                    drc.NamedDropdown(
                        name="Select Observation UID",
                        id="dropdown-select-uid",
                        options=[{"label": i.strip("uid://"), "value": i} for i in uids],
                        clearable=False,
                        searchable=False,
                        value=uids[0],
                    ),
                    ### ANTENNAS ###
                    # TODO: Possibly add this component to drc
                    html.Div(
                        id="antenna-select-outer",
                        className="control-row-2",
                        style={"padding": "20px 10px 25px 4px"},
                        children=[
                            html.Label("Pick Antennas"),
                            html.Div(
                                id="antenna-checklist-container",
                                children=dcc.Checklist(
                                    id="antenna-select-all",
                                    options=[{"label": "Select All Antennas", "value": "All"}],
                                    value=[],
                                ),
                            ),
                            html.Div(
                                id="antenna-select-dropdown-outer",
                                children=dcc.Dropdown(
                                    id="antenna-select",
                                    multi=True,
                                    searchable=True,
                                ),
                            ),
                        ],
                    ),
                    ### BASEBANDS ###
                    html.Div(
                        id="baseband-select-outer",
                        className="control-row-2",
                        style={"padding": "20px 10px 25px 4px"},
                        children=[
                            html.Label("Pick Basebands"),
                            html.Div(
                                id="baseband-checklist-container",
                                children=dcc.Checklist(
                                    id="baseband-select-all",
                                    options=[{"label": "Select All Basebands", "value": "All"}],
                                    value=[],
                                ),
                            ),
                            html.Div(
                                id="baseband-select-dropdown-outer",
                                children=dcc.Dropdown(
                                    id="baseband-select",
                                    multi=True,
                                    searchable=True,
                                ),
                            ),
                        ],
                    ),
                    ### SCAN ###
                    html.Div(
                        id="scan-select-outer",
                        className="control-row-2",
                        style={"padding": "20px 10px 25px 4px"},
                        children=[
                            html.Label("Pick Scan for Spectrum Graph"),
                            html.Div(
                                id="scan-checklist-container",
                                children=dcc.Checklist(
                                    id="scan-select-all",
                                    options=[{"label": "Select All Scans", "value": "All"}],
                                    value=[],
                                ),
                            ),
                            html.Div(
                                id="scan-select-dropdown-outer",
                                children=dcc.Dropdown(
                                    id="scan-select",
                                    multi=True,
                                    searchable=True,
                                ),
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def graph_layout():
    """Layout for the graphs"""
    return html.Div(
        id="graphs-container",
        children=[
            dcc.Loading(
                className="graph-wrapper",
                children=dcc.Graph(
                    id="summary-graph",
                ),
            ),
            dcc.Loading(
                className="graph-wrapper",
                children=dcc.Graph(
                    id="spectrum-graph",
                ),
            ),
        ],
    )


def full_layout():
    """Full app layout"""
    return html.Div(
        children=[
            html.Div(
                className="banner",
                children=[
                    html.Div(
                        className="container scalable",
                        children=[
                            html.H2(
                                "ALMA QA0 Exploration",
                                id="banner-title",
                                style={
                                    "text-decoration": "none",
                                    "color": "inherit",
                                },
                            ),
                            html.Img(
                                src=app.get_asset_url("alma-logo.jpg"),
                                style={
                                    "height": "5%",
                                    "width": "5%",
                                },
                            ),
                        ],
                    ),
                ],
            ),
            html.Div(
                id="body",
                className="container scalable",
                children=[
                    html.Div(
                        id="app-container",
                        children=[
                            panel_layout(),
                            graph_layout(),
                        ],
                    ),
                ],
            ),
        ],
    )


app.layout = full_layout()


### Panel callbacks ###


@app.callback(
    [
        Output("antenna-select", "value"),
        Output("antenna-select", "options"),
    ],
    [
        Input("dropdown-select-uid", "value"),
        Input("antenna-select-all", "value"),
    ],
)
def update_antenna_dropdown(uid, antenna_select_all):
    """Update the antennas available in the dropdown"""

    antennas = df.loc[df.uid == uid, "antennaname"].unique().tolist()
    options = [{"label": i, "value": i} for i in antennas]

    # Check if the callback was triggered by the select-all button
    # See: https://dash.plotly.com/advanced-callbacks
    ctx = dash.callback_context
    if ctx.triggered[0]["prop_id"].split(".")[0] == "antenna-select-all":
        if antenna_select_all == ["All"]:
            value = [i["value"] for i in options]
        else:
            value = dash.no_update
    # Otherwise it can only be due to a change in UID - In that case also select all by default
    else:
        value = [i["value"] for i in options]

    return (
        value,
        options,
    )


@app.callback(
    [
        Output("baseband-select", "value"),
        Output("baseband-select", "options"),
    ],
    [
        Input("dropdown-select-uid", "value"),
        Input("antenna-select", "value"),
        Input("baseband-select-all", "value"),
    ],
)
def update_baseband_dropdown(uid, antennas, baseband_select_all):
    """Update the basebands available in the dropdown"""

    basebands = (
        df.loc[(df.uid == uid) & (df.antennaname.isin(antennas)), "basebandname"].unique().tolist()
    )

    options = [{"label": i, "value": i} for i in basebands]

    # Check if the callback was triggered by the select-all button
    # See: https://dash.plotly.com/advanced-callbacks
    ctx = dash.callback_context
    if ctx.triggered[0]["prop_id"].split(".")[0] == "baseband-select-all":
        if baseband_select_all == ["All"]:
            value = [i["value"] for i in options]
        else:
            value = dash.no_update
    # Otherwise it can only be due to a change in UID/Antenna - In that case also select all by default
    else:
        value = [i["value"] for i in options]

    return (
        value,
        options,
    )


@app.callback(
    [
        Output("scan-select", "value"),
        Output("scan-select", "options"),
    ],
    [
        Input("dropdown-select-uid", "value"),
        Input("antenna-select", "value"),
        Input("baseband-select", "value"),
        Input("scan-select-all", "value"),
    ],
)
def update_scan_dropdown(uid, antennas, basebands, scan_select_all):
    """Update the Scans available in the dropdown"""

    # Note that scans == caldataid ~= startvalidtime
    scans = (
        df.loc[
            (df.uid == uid) & (df.antennaname.isin(antennas)) & (df.basebandname.isin(basebands)),
            "caldataid",
        ]
        .unique()
        .tolist()
    )

    options = [{"label": i, "value": i} for i in scans]

    # Check if the callback was triggered by the select-all button
    # See: https://dash.plotly.com/advanced-callbacks
    ctx = dash.callback_context
    if ctx.triggered[0]["prop_id"].split(".")[0] == "scan_select_all":
        if scan_select_all == ["All"]:
            value = [i["value"] for i in options]
        else:
            value = dash.no_update
    # Otherwise it can only be due to a change in UID/Antenna - In that case also select all by default
    else:
        value = [i["value"] for i in options]

    return (
        value,
        options,
    )


### Graph callbacks ###

transparent_layout = go.Layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")


@app.callback(
    Output("summary-graph", "figure"),
    [
        Input("dropdown-select-uid", "value"),
        Input("antenna-select", "value"),
        Input("baseband-select", "value"),
    ],
)
def update_summary_graph(
    uid,
    antennas,
    basebands,
):
    """Creates facet graph based on UID, Antenna & BBand selection"""
    graph_df = df.loc[
        (df.uid == uid) & (df.antennaname.isin(antennas)) & (df.basebandname.isin(basebands))
    ]

    # Return an empty graph if e.g. no antenna is selected
    if len(graph_df) == 0:
        return {
            "data": [],
            "layout": transparent_layout,
        }

    fig = px.scatter(
        graph_df,
        x="startvalidtime",
        y=["trec_x", "trec_y"],  # TODO: Let user select
        facet_col="basebandname",
        facet_col_wrap=2,
        labels={
            "trec_x": "Trx Pol X",
            "trec_y": "Trx Pol Y",
            "startvalidtime": "Scan Timestamp",
            "basebandname": "BaseBand",
            "antennaname": "Antenna",
            "value": "Temperature",
            "variable": "Polarization",
        },
        render_mode="webgl",
        hover_name="antennaname",
        hover_data={
            "frequency_mid": ":.2f",
            "startvalidtime": False,
            "caldataid": True,
            "value": ":.2f [K]",
        },
        custom_data=["frequency_mid"],
        template="plotly_dark",
    )

    fig.update_yaxes(rangemode="tozero")

    # Make it transparent
    fig.update_layout(transparent_layout)
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="White")
    fig.update_yaxes(showgrid=True, rangemode="tozero", gridwidth=1, gridcolor="White")

    return fig


@app.callback(
    Output("spectrum-graph", "figure"),
    [
        Input("dropdown-select-uid", "value"),
        Input("antenna-select", "value"),
        Input("baseband-select", "value"),
        Input("scan-select", "value"),
    ],
)
def update_spectrum_graph(
    uid,
    antennas,
    basebands,
    scans,
):
    """Creates scatter plot based on UID, Antenna, BBand & Scan selection"""

    sub_cols = ["frequencyspectrum", "trecspectrum_x", "trecspectrum_y"]

    graph_df = df.loc[
        (df.uid == uid)
        & (df.antennaname.isin(antennas))
        & (df.basebandname.isin(basebands))
        & (df.caldataid.isin(scans))
    ][sub_cols]

    graph_df = graph_df.applymap(lambda arr: np.array(arr.split(",")[5:-5]).astype(float))

    # print("DF: ", graph_df.head(5))

    graph_df = graph_df.explode(sub_cols)
    # For older pandas versions, we must explode each column individually (DSS is still using an older pandas)
    # graph_df = pd.DataFrame({col: graph_df[[col]].explode(col).squeeze() for col in sub_cols})

    # Turn into GHz
    graph_df["frequencyspectrum"] = graph_df["frequencyspectrum"] * 1e-9

    fig = px.scatter(
        graph_df,
        x="frequencyspectrum",
        y=["trecspectrum_x", "trecspectrum_y"],
        labels={
            "variable": "Polarization",
            "value": "Temperature",
            "frequencyspectrum": "Frequency Spectrum (GHz)",
        },
        render_mode="webgl",
        template="plotly_dark",
    )

    # Make it transparent
    fig.update_layout(transparent_layout)
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="White")
    fig.update_yaxes(showgrid=True, rangemode="tozero", gridwidth=1, gridcolor="White")

    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
