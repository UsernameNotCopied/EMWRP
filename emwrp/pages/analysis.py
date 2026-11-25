from datetime import date, timedelta

import dash
import plotly.graph_objects as go
from dash import callback, dcc, html
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots

from emwrp.database import get_db

dash.register_page(__name__)


def layout():
    today = date.today()
    first = get_db().get_first_measurement()
    if first is not None and first["datetime"] is not None:
        min_date = first["datetime"].date()
    else:
        min_date = today - timedelta(days=1)

    return html.Div(
        [
            dcc.DatePickerRange(
                id="analysis-date-picker",
                min_date_allowed=min_date,
                max_date_allowed=today,
                initial_visible_month=today,
                start_date=max(min_date, today - timedelta(days=1)),
                end_date=today,
                display_format="DD/MM/YYYY",
            ),
            dcc.Graph(id="analysis-graph", config={"displaylogo": False}),
        ],
        style={"marginTop": "10px"},
    )


@callback(
    Output("analysis-graph", "figure"),
    Input("analysis-date-picker", "start_date"),
    Input("analysis-date-picker", "end_date"),
)
def update_analysis_graph(start_date, end_date):
    fig = make_subplots(
        rows=3,
        cols=1,
        vertical_spacing=0.1,
        subplot_titles=(
            "Temperature (°C)",
            "Relative Humidity (%)",
            "Atmospheric Pressure (hPa)",
        ),
    )

    if start_date and end_date:
        measurements = get_db().get_measurements_for_date_range(start_date, end_date)
        times = [m["datetime"] for m in measurements]
        temps = [m["temp"] for m in measurements]
        hums = [m["hum"] for m in measurements]
        pressures = [m["pressure"] for m in measurements]

        fig.add_trace(go.Scatter(x=times, y=temps, mode="lines", name="Temperature"), row=1, col=1)
        fig.add_trace(go.Scatter(x=times, y=hums, mode="lines", name="Humidity"), row=2, col=1)
        fig.add_trace(go.Scatter(x=times, y=pressures, mode="lines", name="Pressure"), row=3, col=1)

    fig.update_layout(
        height=900,
        showlegend=False,
        margin={"l": 40, "r": 20, "b": 30, "t": 40},
    )
    return fig
