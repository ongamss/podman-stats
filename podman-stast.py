import json
import subprocess
import pandas as pd
import dash
from dash import dash_table, dcc, html
from dash.dependencies import Input, Output
from collections import OrderedDict


app = dash.Dash()

app.layout = html.Div(children=[
    html.H1(
        children='Pods Statistics',
    ),
    dash_table.DataTable(
        id='table',
        columns=[],
        style_data_conditional=[
            {
                'if': {
                    'column_id': 'mem_percent',
                    'filter_query': '{mem_percent} > 0.6'},
                'backgroundColor': 'red',
                'color': 'white'
            }
        ]
    ),
    dcc.Interval(id='interval-component', interval=3000, n_intervals=0)
])

@app.callback(Output('table', 'data'),
              [Input('interval-component', 'n_intervals')])
def update_table(n):
    proc = subprocess.Popen(["podman", "stats", "--no-stream", "--format=json"], stdout=subprocess.PIPE)
    output = proc.stdout.read().decode()
    json_data = json.loads(output,object_pairs_hook=OrderedDict)
    df = pd.DataFrame(json_data)
    # df.rename(columns={'mem %': 'mem_percent'}, inplace=True)
    df['mem_percent'] = df['mem_percent'].apply(lambda x: x.strip("%"))
    df['mem_percent'] = pd.to_numeric(df['mem_percent'])
    df['mem_percent'] = df['mem_percent'].apply(lambda x: x/100)
    return df.to_dict("rows")

@app.callback(Output('table', 'columns'),
              [Input('table', 'data')])
def update_columns(data):
    columns = [{'name': i, 'id': i} for i in data[0]]
    return columns

if __name__ == '__main__':
    app.run_server(debug=True)
