import dash
from dash import Dash, html
from flask import Flask

EXTERNAL_STYLESHEETS = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]


def create_dash_application(flask_app: Flask) -> Dash:
    dash_app = Dash(
        __name__,
        external_stylesheets=EXTERNAL_STYLESHEETS,
        use_pages=True,
        server=flask_app,
        url_base_pathname="/",
    )

    dash_app.layout = html.Div(
        [
            html.Div(
                [
                    html.Img(src="/assets/favicon.ico", height="45"),
                    html.A("EMWRP", href="/", className="logo"),
                    html.Div(
                        [
                            html.A("Home", className="active", href="/"),
                            html.A("Live", href="/live"),
                            html.A("Analysis", href="/analysis"),
                        ],
                        className="header-right",
                    ),
                ],
                className="header",
            ),
            html.Div(dash.page_container),
        ]
    )

    return dash_app
