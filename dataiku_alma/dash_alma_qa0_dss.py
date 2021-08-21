### Dash App for Alma's Astronomer on Duty, who performs Quality Assurance 0 Tasks ###

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objs as go

import numpy as np
import pandas as pd

from dataiku import SQLExecutor2

import utils.dash_reusable_components as drc

### DEFINITIONS ###

# The app is pre-initialized in Dataiku DSS
app.config.external_stylesheets = [
    "https://muennighoff.github.io/csstemplates/alma/base-styles.css",
    "https://muennighoff.github.io/csstemplates/alma/custom-styles.css",
]

EXECUTOR = SQLExecutor2(dataset="raw_cal_joined")

DATASET_NAME = "TRENDANALYSISANDOUTLIERDETECTION_raw_cal_joined"

# SQL Queries
# Qotes needed due to caps
unique_uid_query = """
SELECT DISTINCT uid
FROM "%s"
ORDER BY uid DESC
"""

# Somehow uid needs single quotes
uid_subset_query = """
SELECT *
FROM "%s"
WHERE uid = '%s'
"""

# Get all possible UIDs from table
uid_options = [
    {"label": i.strip("uid://"), "value": i}
    for i in EXECUTOR.query_to_df(unique_uid_query % (DATASET_NAME)).uid.values.tolist()
]

summary_graph_options = [
    {
        "label": "Scan vs Receiver Temperature X/Y",
        "value": "startvalidtime,trec_x,trec_y",
    },
    {"label": "Scan vs System Temperature X/Y", "value": "startvalidtime,tsys_x,tsys_y"},
    {"label": "Scan vs Atmosphere Temperature X/Y", "value": "startvalidtime,tatm_x,tatm_y"},
    {"label": "Scan vs Tau", "value": "startvalidtime,tau"},
    {"label": "Scan vs Water", "value": "startvalidtime,water"},
    {"label": "Receiver Temp. X vs Receiver Temp. Y", "value": "trec_x,trec_y"},
    {"label": "System Temp. X vs System Temp. Y", "value": "tsys_x,tsys_y"},
]

spectrum_graph_options = [
    {
        "label": "Frequency Spectrum vs Receiver Temperature X/Y",
        "value": "frequencyspectrum,trecspectrum_x,trecspectrum_y",
    },
    {
        "label": "Frequency Spectrum vs System Temperature X/Y",
        "value": "frequencyspectrum,tsysspectrum_x,tsysspectrum_y",
    },
]

graph_labels = {
    "startvalidtime": "Scan Timestamp",
    "antennaname": "Antenna",
    "basebandname": "BaseBand",
    "trec_x": "Receiver Temp. X (K)",
    "trec_y": "Receiver Temp. Y (K)",
    "trec_x,trec_y": "Temperature",
    "tsys_x": "System Temp. X (K)",
    "tsys_y": "System Temp. Y (K)",
    "tsys_x,tsys_y": "Temperature",
    "water": "Water",
    "tatm_x,tatm_y": "Temperature",
    "tau": "Tau",  # TODO: Is this a shortcut?
    "frequencyspectrum": "Frequency Spectrum (GHz)",
}


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
                        options=uid_options,
                        clearable=False,
                        searchable=False,
                        value=uid_options[0]["value"],
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
                    ### SUMMARY GRAPH TYPE ###
                    drc.NamedDropdown(
                        name="Select Summary Graph",
                        id="dropdown-select-summary-graph",
                        options=summary_graph_options,
                        clearable=False,
                        searchable=False,
                        value=summary_graph_options[0]["value"],
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
                    ### SPECTRUM GRAPH TYPE ###
                    drc.NamedDropdown(
                        name="Select Spectrum Graph",
                        id="dropdown-select-spectrum-graph",
                        options=spectrum_graph_options,
                        clearable=False,
                        searchable=False,
                        value=spectrum_graph_options[0]["value"],
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


def about_layout():
    """Layout for About section"""
    return html.Div(
        children=[
            html.H4("About"),
            html.P(
                [
                    """Combine different datapoints from the left-hand panel. You can use the graph featurs to zoom in, save a snapshot & sub-select. If you sub-select using the Lasso or Box selection tools on the upper-graph, the lower graph will zoom in if they graph the same y-axis. To un-select double-click the selection. If you changed the UID without un-selecting, just re-select and un-select to reset the lower graph.""",
                    html.Br(),
                    """Made with ❤️ for ALMA & Astrophysics - Niklas Muennighoff.""",
                ]
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
                                src="https://muennighoff.github.io/csstemplates/alma/alma-logo.jpg",
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
                    html.Div(
                        children=[
                            about_layout(),
                        ]
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

    # Get df of currently selected UID
    df = EXECUTOR.query_to_df(uid_subset_query % (DATASET_NAME, uid))

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

    # Get df of currently selected UID
    df = EXECUTOR.query_to_df(uid_subset_query % (DATASET_NAME, uid))

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

    # Get df of currently selected UID
    df = EXECUTOR.query_to_df(uid_subset_query % (DATASET_NAME, uid))

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
    if ctx.triggered[0]["prop_id"].split(".")[0] == "scan-select-all":
        if scan_select_all == ["All"]:
            value = [i["value"] for i in options]
        else:
            value = dash.no_update
    # Otherwise it can only be due to a change in UID/Antenna - In that case also select the first by default
    else:
        value = [i["value"] for i in options[:1]]

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
        Input("dropdown-select-summary-graph", "value"),
    ],
)
def update_summary_graph(
    uid,
    antennas,
    basebands,
    graph_type,
):
    """Creates facet graph based on UID, Antenna & BBand selection"""

    # Get df of currently selected UID
    df = EXECUTOR.query_to_df(uid_subset_query % (DATASET_NAME, uid))

    graph_df = df.loc[
        (df.uid == uid) & (df.antennaname.isin(antennas)) & (df.basebandname.isin(basebands))
    ]

    # Return an empty graph if e.g. no antenna is selected
    if len(graph_df) == 0:
        return {
            "data": [],
            "layout": transparent_layout,
        }

    x, y = graph_type.split(",")[0], graph_type.split(",")[1:]
    # X/Y dependent labels:
    value_label = graph_labels.get(",".join(y), "Unknown")
    var_label = "Polarization" if value_label == "Temperature" else "Variable"
    add_labels = {"value": value_label, "variable": var_label}

    fig = px.scatter(
        graph_df,
        x=x,
        y=y,  # TODO: Let user select
        facet_col="basebandname",
        facet_col_wrap=2,
        labels={**add_labels, **graph_labels},
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
        Input("summary-graph", "selectedData"),
        Input("dropdown-select-spectrum-graph", "value"),
    ],
    State("dropdown-select-summary-graph", "value"),
)
def update_spectrum_graph(
    uid,
    antennas,
    basebands,
    scans,
    summary_selected,
    graph_type,
    summary_graph_type,
):
    """Creates scatter plot based on UID, Antenna, BBand, Scan & Summary graph selection"""

    # Get df of currently selected UID
    df = EXECUTOR.query_to_df(uid_subset_query % (DATASET_NAME, uid))

    cols = graph_type.split(",")
    x, y = cols[0], cols[1:]

    graph_df = df.loc[
        (df.uid == uid)
        & (df.antennaname.isin(antennas))
        & (df.basebandname.isin(basebands))
        & (df.caldataid.isin(scans))
    ]

    # If rectangle/lasso select has been used to select points from the upper graph, subselect
    if summary_selected:
        # Get y-axis of the summary graph
        y_summary = summary_graph_type.split(",")[1:]
        # Only filter if their y-axes match
        if y[0].replace("spectrum", "") == y_summary[0]:
            # Select caldataid as the x-axis representative as startvalidtime has formatting changes
            x_selected = set(sub_dict["customdata"][-1] for sub_dict in summary_selected["points"])
            y_selected = set(sub_dict["y"] for sub_dict in summary_selected["points"])

            # Filter df according to selection
            graph_df = graph_df.loc[
                (graph_df.caldataid.isin(x_selected))
                & (
                    graph_df[y_summary[0]].isin(y_selected)
                    | graph_df[y_summary[-1]].isin(y_selected)
                )
            ]

    graph_df = graph_df[cols].applymap(lambda arr: np.array(arr.split(",")[5:-5]).astype(float))

    # graph_df = graph_df.explode(cols)
    # For older pandas versions, we must explode each column individually (DSS is still using an older pandas)
    graph_df = pd.DataFrame({col: graph_df[[col]].explode(col).squeeze() for col in cols})

    # Turn into GHz
    if x == "frequencyspectrum":
        graph_df["frequencyspectrum"] = graph_df["frequencyspectrum"] * 1e-9

    fig = px.scatter(
        graph_df,
        x=x,
        y=y,
        labels={"variable": "Polarization", "value": "Temperature", **graph_labels},
        render_mode="webgl",
        template="plotly_dark",
    )

    # Make it transparent
    fig.update_layout(transparent_layout)
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="White")
    fig.update_yaxes(showgrid=True, rangemode="tozero", gridwidth=1, gridcolor="White")

    return fig
