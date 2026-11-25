import dash
import plotly.graph_objects as go
from dash import callback, dcc, html
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots

from emwrp.database import get_db

dash.register_page(__name__)

layout = html.Div(
    [
        dcc.Graph(id="live-update-graph", config={"displaylogo": False}),
        dcc.Interval(
            id="live-interval",
            interval=30 * 1000,  # 30 seconds
            n_intervals=0,
        ),
    ]
)


@callback(
    Output("live-update-graph", "figure"),
    Input("live-interval", "n_intervals"),
)
def update_graph_live(_n):
    measurements = get_db().get_last_n_measurements(24 * 60)
    measurements.reverse()  # chronological order (oldest -> newest)

    times = [m["datetime"] for m in measurements]
    temps = [m["temp"] for m in measurements]
    hums = [m["hum"] for m in measurements]
    pressures = [m["pressure"] for m in measurements]

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

    fig.add_trace(go.Scatter(x=times, y=temps, mode="lines", name="Temperature"), row=1, col=1)
    fig.add_trace(go.Scatter(x=times, y=hums, mode="lines", name="Humidity"), row=2, col=1)
    fig.add_trace(go.Scatter(x=times, y=pressures, mode="lines", name="Pressure"), row=3, col=1)

    fig.update_layout(
        height=900,
        showlegend=False,
        margin={"l": 40, "r": 20, "b": 30, "t": 40},
    )
    return fig
