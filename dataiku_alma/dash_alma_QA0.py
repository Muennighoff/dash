### Dash App for Alma's Astronomer on Duty, who performs Quality Assurance 0 Tasks ###

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objs as go

import numpy as np
import pandas as pd

import utils.dash_reusable_components as drc

# In Dataiku DSS added the stylesheets to github
# See https://community.dataiku.com/t5/Using-Dataiku-DSS/Pass-argument-to-Dash-object/m-p/14853
app = dash.Dash(__name__)

### DEFINITIONS ###

# Using a single DataFrame saves memory
# Get DF via SQL from database in actual application
df = pd.read_csv("dataiku_alma/ALMA_Xf27c.csv")

# Via SQL on entire table in actual application
min_date, max_date = df.startvalidtime.min(), df.startvalidtime.max()

SUMMARY_GRAPH_OPTIONS = [
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


SUMMARY_SPECTRUM_MAP = {
    "trec_x": "trecspectrum_x",
    "trec_y": "trecspectrum_y",
    "tsys_x": "tsysspectrum_x",
    "tsys_y": "tsysspectrum_y",
}


GRAPH_LABELS = {
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
    "tau": "Tau",
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
                    ### DATE ###
                    html.Div(
                        id="date-select-outer",
                        className="control-row-2",
                        style={"margin": "10px 0px"},
                        children=[
                            html.Label(
                                "Select Date Range",
                                style={"margin-left": "3px"},
                            ),
                            html.Div(
                                id="date-container",
                                children=[
                                    dcc.DatePickerRange(
                                        id="date-picker-range",
                                        min_date_allowed=min_date,
                                        max_date_allowed=max_date,
                                        start_date=max_date,
                                        end_date=max_date,
                                    )
                                ],
                            ),
                        ],
                    ),
                    ### UID ###
                    drc.NamedDropdown(
                        name="Select Observation UID",
                        id="dropdown-select-uid",
                        clearable=False,
                        searchable=False,
                    ),
                    ### ANTENNAS ###
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
                        options=SUMMARY_GRAPH_OPTIONS,
                        clearable=False,
                        searchable=False,
                        value=SUMMARY_GRAPH_OPTIONS[0]["value"],
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
                    ### DOWNLOAD BUTTON ###
                    html.Div(
                        style={"margin": "40px 0px"},
                        children=[
                            html.Button("Download CSV", id="btn", style={"color": "lightblue"}),
                            dcc.Download(id="download"),
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
                    config={
                        "modeBarButtonsToAdd": [
                            "drawline",
                            "drawopenpath",
                            "drawrect",
                            "eraseshape",
                        ]
                    },
                ),
            ),
            dcc.Loading(
                className="graph-wrapper",
                children=dcc.Graph(
                    id="spectrum-graph",
                    config={
                        "modeBarButtonsToAdd": [
                            "drawline",
                            "drawopenpath",
                            "drawrect",
                            "eraseshape",
                        ]
                    },
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
                    """Combine different datapoints from the left-hand panel. You can use the graph features to zoom in, save a snapshot, draw forms & sub-select. If you sub-select using the Lasso or Box selection tools on the upper-graph, the lower graph will zoom in if they graph the same y-axis. To un-select double-click the selection. If you changed the UID without un-selecting, just re-select and un-select to reset the lower graph. To export your project, we recommend to scroll to the top of the left-hand panel, print your screen as PDF selecting Layout: Landscape, Scale: Customised (50%). When sharing insights via e.g. a graph png, it is recommended to also download a data snapshot.""",
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
        Output("dropdown-select-uid", "value"),
        Output("dropdown-select-uid", "options"),
    ],
    [
        Input("date-picker-range", "start_date"),
        Input("date-picker-range", "end_date"),
    ],
)
def update_uid_dropdown(start_date, end_date):
    """Update the UIDs available in the dropdown based on date range"""

    uids = (
        df.loc[(df.startvalidtime >= start_date) & (df.startvalidtime <= end_date), "uid"]
        .unique()
        .tolist()
    )
    options = [{"label": i.strip("uid://"), "value": i} for i in uids]

    return (
        options[-1]["value"],
        options,
    )


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
        Input("summary-graph", "selectedData"),
    ],
)
def update_scan_dropdown(uid, antennas, basebands, scan_select_all, summary_selected):
    """Update the Scans available in the dropdown"""

    # If rectangle/lasso select has been used to select points from the upper graph, subselect
    if summary_selected:
        # caldataid is the last custom data we present (via hover in the summary graph)
        scans = set(sub_dict["customdata"][-1] for sub_dict in summary_selected["points"])
    else:
        # Note that scans == caldataid ~= startvalidtime
        scans = (
            df.loc[
                (df.uid == uid)
                & (df.antennaname.isin(antennas))
                & (df.basebandname.isin(basebands)),
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
    elif ctx.triggered[0]["prop_id"].split(".")[0] == "summary-graph":
        value = [i["value"] for i in options]
    # Otherwise it can only be due to a change in UID/Antenna - In that case also select the first by default
    else:
        value = [i["value"] for i in options[:1]]

    return (
        value,
        options,
    )


### Graph callbacks ###

# transparent_layout = go.Layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
# Select Layout with the same color as background to have background when exporting
transparent_layout = go.Layout(paper_bgcolor="rgba(41,43,56,1)", plot_bgcolor="rgba(41,43,56,1)")


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
    value_label = GRAPH_LABELS.get(",".join(y), "Unknown")
    var_label = "Polarization" if value_label == "Temperature" else "Variable"
    add_labels = {"value": value_label, "variable": var_label}

    fig = px.scatter(
        graph_df,
        x=x,
        y=y,
        facet_col="basebandname",
        facet_col_wrap=2,
        labels={**add_labels, **GRAPH_LABELS},
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

    # Make it transparent, drawings via the drawing tool in cyan & box-select as default tool
    fig.update_layout(
        transparent_layout, newshape=dict(line=dict(color="cyan", width=5)), dragmode="select"
    )
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
        Input("dropdown-select-summary-graph", "value"),
    ],
)
def update_spectrum_graph(
    uid,
    antennas,
    basebands,
    scans,
    summary_selected,
    summary_graph_type,
):
    """Creates scatter plot based on UID, Antenna, BBand, Scan & Summary graph selection"""

    # Get X Variable
    x = "frequencyspectrum"
    # Get Y Variable(s)
    y_summary = summary_graph_type.split(",")[1:]
    # Check if valid selection for plotting lower graph
    if not (set(y_summary) <= set(SUMMARY_SPECTRUM_MAP.keys())):
        return {
            "data": [],
            "layout": transparent_layout,
        }

    y_spectrum = [SUMMARY_SPECTRUM_MAP[y_str] for y_str in y_summary]

    # Drop the index so lateron no pandas copy warning is raised
    graph_df = df.loc[
        (df.uid == uid)
        & (df.antennaname.isin(antennas))
        & (df.basebandname.isin(basebands))
        & (df.caldataid.isin(scans))
    ].reset_index(drop=True)

    explode_cols = [x] + y_spectrum
    add_cols = [
        "antennaname",
        "basebandname",
        "caldataid",
    ]

    # If rectangle/lasso select has been used to select points from the upper graph, subselect
    if summary_selected:
        # Select caldataid as the x-axis representative as startvalidtime has formatting changes
        x_selected = set(sub_dict["customdata"][-1] for sub_dict in summary_selected["points"])
        y_selected = set(sub_dict["y"] for sub_dict in summary_selected["points"])

        # Filter df according to selection
        graph_df = graph_df.loc[
            (graph_df.caldataid.isin(x_selected))
            & (graph_df[y_summary[0]].isin(y_selected) | graph_df[y_summary[-1]].isin(y_selected))
        ]

    graph_df.loc[:, explode_cols] = graph_df.loc[:, explode_cols].applymap(
        lambda arr: np.array(arr.split(",")[5:-5]).astype(float)
    )

    # graph_df = graph_df.explode(explode_cols)
    # For older pandas v's, we must explode each column individually & deduplicate (DSS is still uses older pandas)
    graph_df = pd.concat([graph_df[[col] + add_cols].explode(col) for col in explode_cols], axis=1)
    graph_df = graph_df.loc[:, ~graph_df.columns.duplicated()]

    # Turn into GHz
    if x == "frequencyspectrum":
        graph_df["frequencyspectrum"] = graph_df["frequencyspectrum"] * 1e-9

    fig = px.scatter(
        graph_df,
        x=x,
        y=y_spectrum,
        labels={"variable": "Polarization", "value": "Temperature", **GRAPH_LABELS},
        render_mode="webgl",
        template="plotly_dark",
        hover_data={col: True for col in add_cols},
    )

    # Make it transparent & drawings via the drawing tool in cyan
    fig.update_layout(
        transparent_layout,
        newshape=dict(line=dict(color="cyan", width=5)),
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="White")
    fig.update_yaxes(showgrid=True, rangemode="tozero", gridwidth=1, gridcolor="White")

    return fig


# Prevent from being called when the app is loaded via prevent_initial_call
@app.callback(
    Output("download", "data"),
    [Input("btn", "n_clicks")],
    [
        State("dropdown-select-uid", "value"),
        State("antenna-select", "value"),
        State("baseband-select", "value"),
        State("scan-select", "value"),
    ],
    prevent_initial_call=True,
)
def generate_csv(
    n_nlicks,
    uid,
    antennas,
    basebands,
    scans,
):
    out_df = df.loc[
        (df.uid == uid)
        & (df.antennaname.isin(antennas))
        & (df.basebandname.isin(basebands))
        & (df.caldataid.isin(scans))
    ]
    return dcc.send_data_frame(out_df.to_csv, filename="qa0_{}.csv".format(uid.strip("uid://")))


if __name__ == "__main__":
    app.run_server(debug=True)
