import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import flask
import plotly.graph_objs as go

from dash.dependencies import Input, Output


import json

data_path = '/app/data/data.jsonl'

def dump_jsonl(data, output_path, append=False):
    """
    Write list of objects to a JSON lines file.
    """
    mode = 'a+' if append else 'w'
    with open(output_path, mode, encoding='utf-8') as f:
        for line in data:
            json_record = json.dumps(line, ensure_ascii=False)
            f.write(json_record + '\n')
    print('Wrote {} records to {}'.format(len(data), output_path))

def load_jsonl(input_path) -> list:
    """
    Read list of objects from a JSON lines file.
    """
    data = []
    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line.rstrip('\n|\r')))
    print('Loaded {} records from {}'.format(len(data), input_path))
    return data

def load_measurements():
    ll = load_jsonl(data_path)
    data = []
    download = {}
    download['x'] = []
    download['y'] = []
    download['name'] = 'download'
    download['type'] = 'line'

    upload = {}
    upload['x'] = []
    upload['y'] = []
    upload['name'] = 'upload'
    upload['type'] = 'line'

    for item in ll:
        download['x'].append(item['timestamp'])
        download['y'].append(item['download']['bandwidth']/100000)

        upload['x'].append(item['timestamp'])
        upload['y'].append(item['upload']['bandwidth']/100000)
    data.append(download)
    data.append(upload)

    return data

data = load_measurements()

server = flask.Flask(__name__)
app = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP
    ]
)
app.config.suppress_callback_exceptions = True


app.layout = html.Div(children=[
    html.H1(children='Ookla speed test'),

    html.Div(children='''
        Using Dash - a web application framework for Python.
    '''),
    html.Button('Measure speed', id='my-button'),
    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                go.Scatter(
                    x=data[0]['x'],
                    y=data[0]['y'],
                    mode='lines+markers',
                    line = dict(color='royalblue', width=3),
                    marker = dict(size=10),
                    name=data[0]['name']
                ) 
            ],
            'layout': {
                'title': 'Download speed in Mbps'
            }
        }
    ),
     dcc.Graph(
        id='example-graph2',
        figure={
            'data': [
                go.Scatter(
                    x=data[1]['x'],
                    y=data[1]['y'],
                    mode='lines+markers',
                    line = dict(color='firebrick', width=3),
                    marker = dict(size=10),
                    name=data[1]['name']
                ) 
            ],
            'layout': {
                'title': 'Upload speed in Mbps'
            }
        }
    ),
    dcc.Interval(
            id='interval-component',
            interval=600000, # in milliseconds
            n_intervals=0
        )
])


            
@app.callback([
              Output('example-graph', 'figure'),
              Output('example-graph2', 'figure')],
              [Input('interval-component', 'n_intervals'),
              Input('my-button', 'n_clicks')
              ])
def update_graph_live(intervals,clicks):

    #bashCommand = "docker run 9dd3bd576e52"
    #CMD ["speedtest", "-p", "no", "-f", "json-pretty", "--accept-license", "--accept-gdpr"
    bashCommand = "speedtest -p no -f json-pretty --accept-license --accept-gdpr"
    import subprocess
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    item = json.loads(output)

    for dato in data:
        if dato['name'] == 'download':
            dato['x'].append(item['timestamp'])
            dato['y'].append(item['download']['bandwidth']/100000)
        if dato['name'] == 'upload':
            dato['x'].append(item['timestamp'])
            dato['y'].append(item['upload']['bandwidth']/100000)
    dump_jsonl([item],data_path,append=True)

    figure={
            'data': [
                go.Scatter(
                    x=data[0]['x'],
                    y=data[0]['y'],
                    mode='lines+markers',
                    line = dict(color='royalblue', width=3),
                    marker = dict(size=10),
                    
                    
                    name=data[0]['name']
                ) 
            ],
            'layout': {
                'title': 'Download speed in Mbps'
            }
        }
    figure2={
            'data': [
                go.Scatter(
                    x=data[1]['x'],
                    y=data[1]['y'],
                    mode='lines+markers',
                    line = dict(color='firebrick', width=3),
                    marker = dict(size=10),
                    
                    
                    name=data[1]['name']
                ) 
            ],
            'layout': {
                'title': 'Upload speed in Mbps'
            }
        }
    return figure,figure2


if __name__ == '__main__':

    import os

    #debug = False if os.environ['DASH_DEBUG_MODE'] == 'False' else True
    debug = True
    app.run_server(
        host='0.0.0.0',
        port=8050,
        debug=debug
    )
