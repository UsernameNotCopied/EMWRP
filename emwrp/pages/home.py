import dash
from dash import callback, dcc, html
from dash.dependencies import Input, Output

from emwrp.database import get_db

dash.register_page(__name__, path="/")

layout = html.Div(
    [
        html.Div(id="home-live-text", style={"marginTop": "10px"}),
        dcc.Interval(
            id="home-interval",
            interval=30 * 1000,  # 30 seconds
            n_intervals=0,
        ),
    ]
)


@callback(
    Output("home-live-text", "children"),
    Input("home-interval", "n_intervals"),
)
def update_metrics(_n):
    latest = get_db().get_latest_measurement()
    style = {"padding": "5px", "fontSize": "20px"}

    if latest is None:
        return [html.P("No sensor data available yet.", style=style)]

    return [
        html.P(f"Temperature: {latest['temp']:.1f}°C", style=style),
        html.P(f"Relative Humidity: {latest['hum']:.1f}%", style=style),
        html.P(f"Atmospheric Pressure: {latest['pressure']:.1f} hPa", style=style),
    ]
