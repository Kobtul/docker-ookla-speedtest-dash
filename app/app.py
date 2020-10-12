import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.graph_objs as go

import json
import flask

import os
from dash.dependencies import Input, Output


# server = flask.Flask(__name__)
app = dash.Dash(
    __name__,
    # server=server,
    # external_stylesheets=[
    #     dbc.themes.BOOTSTRAP
    # ]
)
app.config.suppress_callback_exceptions = True
UPDADE_INTERVAL = 3600



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

def conver_json_to_data(measurements):
    data = {}

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

    for item in measurements:
        if 'timestamp' in item:
            download['x'].append(item['timestamp'])
            download['y'].append(item['download']['bandwidth']/100000)

            upload['x'].append(item['timestamp'])
            upload['y'].append(item['upload']['bandwidth']/100000)

    data['download'] =download
    data['upload'] = upload
    return data

def make_layout():
    data = conver_json_to_data(load_jsonl('/app/data/data.jsonl'))
    chart_title = "data updates server-side every {} seconds".format(UPDADE_INTERVAL)

    return html.Div(children=[
    html.H1(children='Ookla speed test'),

    html.Div(children=chart_title),
    html.Div(id='hidden-div', style={'display':'none'}),
    html.Button('Measure speed', id='button-measure'),
    dcc.Graph(
            id='chart-download',
            figure={
            'data': [
                go.Scatter(
                    x=data['download']['x'],
                    y=data['download']['y'],
                    mode='lines+markers',
                    line = dict(color='royalblue', width=3),
                    marker = dict(size=10),
                    name=data['download']['name']
                ) 
            ],
            'layout': {
                'title': 'Download speed in Mbps'
            }
        }
        ),
        dcc.Graph(
        id='chart-upload',
        figure={
            'data': [
                go.Scatter(
                    x=data['upload']['x'],
                    y=data['upload']['y'],
                    mode='lines+markers',
                    line = dict(color='firebrick', width=3),
                    marker = dict(size=10),
                    name=data['upload']['name']
                ) 
            ],
            'layout': {
                'title': 'Upload speed in Mbps'
            }
        }
    )])

# we need to set layout to be a function so that for each new page load                                                                                                       
# the layout is re-created with the current data, otherwise they will see                                                                                                     
# data that was generated when the Dash app was first initialised                                                                                                             
app.layout = make_layout

@app.callback(
    Output(component_id='hidden-div', component_property='children'),
    [Input(component_id='button-measure', component_property='n_clicks')],
    prevent_initial_call=True
)
def get_new_data_button(n):
    get_new_data()
    return ""

def get_new_data():
    print('get_new_data')
    """Updates the global variable 'data' with new data"""
    #bashCommand = "docker run 9dd3bd576e52"
    bashCommand = "speedtest -p no -f json-pretty --accept-license --accept-gdpr"
    import subprocess
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    print('output is here')
    item = json.loads(output)
    dump_jsonl([item],'/app/data/data.jsonl',True)

def get_new_data_every(period=UPDADE_INTERVAL):
    print('get_new_data_every')
    """Update the data every 'period' seconds"""
    while True:
        print("Executing our Task on Process {}".format(os.getpid()))
        get_new_data()
        print("data updated")
        time.sleep(period)


# def start_multi():
#     executor = ProcessPoolExecutor()
#     executor.submit(get_new_data_every)
    # import threading

    # ookla_thread = threading.Thread(target=get_new_data_every, name="OOkla")
    # ookla_thread.start()
    # continue doing stuff

if __name__ == '__main__':


    with ProcessPoolExecutor(max_workers=1) as executor:
        task1 = executor.submit(get_new_data_every)
        app.run_server(
            host='0.0.0.0',
            port=8050,
            debug=False
        )

        