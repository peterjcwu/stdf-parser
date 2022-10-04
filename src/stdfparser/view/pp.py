from dash import Dash, dcc, html, Input, Output
import plotly.express as px

app = Dash(__name__)


app.layout = html.Div([
    html.H4('Olympic medals won by countries'),
    dcc.Graph(id="graph"),
    html.P("Medals included:"),
    dcc.Checklist(
        id='medals',
        options=["gold", "silver", "bronze"],
        value=["gold", "silver"],
    ),
])



@app.callback(
    Output("graph", "figure"),
    Input("medals", "value"))
def filter_heatmap(cols):
    df = px.data.medals_wide(indexed=True) # replace with your own data source
    fig = px.imshow(df[cols])
    return fig


app.run_server(debug=True)