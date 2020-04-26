import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import pandas as pd
from datetime import datetime as dt
import datetime
import dash_table.FormatTemplate as FormatTemplate
from dash_table.Format import Format, Scheme, Sign, Symbol
import re

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
api_data = pd.read_csv("spx_test.csv")
api_data['date'] = api_data['date'].apply(lambda x: dt.strptime(x, "%Y-%m-%d").date())
plot_type = api_data['plot_type'].unique()
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


def date_to_int(input_date):
    ''' Convert datetime to ordinal timestamp '''
    return input_date.toordinal()


def getMarks(start_date, end_date, spacing=30):
    ''' Returns the marks for labeling.
        Every Nth value will be used.
    '''
    result = {}
    for i, date_i in enumerate(range(date_to_int(start_date), date_to_int(end_date) + 1)):
        if i % spacing == 0:
            result[date_i] = datetime.date.fromordinal(date_i)
    result[date_to_int(end_date)] = end_date
    return result


# lower = datetime.date(2020, 5, 30)
# upper = datetime.date(2020, 6, 8)
min_date = min(api_data['date'])
max_date = max(api_data['date'])

colors = {
    'background': 'rgb(230, 230, 230)',
    'text': '#7FDBFF',
    'text-align': 'center',
    'fontWeight': 'bold',
    'font-family': 'Arial',
    'font-size': '15'
}
app.layout = html.Div(children=[html.H1(['Performance Plot'],
                                        style={'text-align': 'center'}),
                                html.Div([dcc.Dropdown(id='y_axis',
                                                       options=[{'value': c, 'label': c} for c in plot_type],
                                                       value='value', )
                                          ],
                                         style={"display": "grid", "grid-template-columns": "20% 20% 60%"}
                                         ),
                                dcc.RangeSlider(id='date_slider',
                                                min=date_to_int(min_date),
                                                max=date_to_int(max_date),
                                                value=[date_to_int(min_date),
                                                       date_to_int(max_date)],
                                                marks=getMarks(min_date, max_date),
                                                allowCross=False, updatemode='drag'),
                                html.Div(id='output-container-range-slider'),
                                dcc.Graph(id='graph_dynamic', animate=True),
                                html.Div(children=[dcc.DatePickerSingle(id='input_date',
                                                                        min_date_allowed=min_date,
                                                                        max_date_allowed=max_date,
                                                                        date=max_date),
                                                   dcc.Dropdown(id="input_gap",
                                                                options=[{'value': i, 'label': i} for i in
                                                                         range(1, 11)],
                                                                value=10)]
                                         ,
                                         style={"display": "grid", "grid-template-columns": "20% 20% 60%"}
                                         ),
                                dash_table.DataTable(id='performance_table',
                                                     style_cell={'text-align': 'center'},
                                                     filter_action="native",
                                                     style_header=colors,
                                                     style_as_list_view=True,
                                                     style_table={'overflowX': 'scroll'}),
                                html.Div(id='output_date_picker'),
                                ])


@app.callback(Output('output-container-range-slider', 'children'),
              [Input('date_slider', 'value')])
def update_output(date_slider):
    return 'Examining data from {} to {}'.format(datetime.date.fromordinal(min(date_slider)),
                                                 datetime.date.fromordinal(max(date_slider)))


@app.callback(Output('graph_dynamic', 'figure'),
              [Input('y_axis', 'value'),
               Input('date_slider', 'value')])
def graph_over_time(y_axis, date_slider):
    start_date = datetime.date.fromordinal(min(date_slider))
    end_date = datetime.date.fromordinal(max(date_slider))
    df = api_data.loc[(api_data['date'] == start_date) & (api_data['plot_type'] == y_axis)]
    ref_df = api_data.loc[(api_data['date'] == end_date) & (api_data['plot_type'] == y_axis)]
    figure = {
        'data': [
            {'x': df['spot'],
             'y': df['value'],
             'mode': 'lines',
             'name': start_date,
             },
            {'x': ref_df['spot'],
             'y': ref_df['value'],
             'mode': 'lines',
             'name': end_date,
             },
        ],
        'layout': {
            'margin': {'t': 0, 'b': 180}
        }
    }
    return figure


@app.callback(Output('output_date_picker', 'children'),
              [Input('input_date', 'date')])
def update_output(input_date):
    input_date = dt.strptime(re.split('T| ', input_date)[0], '%Y-%m-%d').date()
    return 'Examining data from {}'.format(input_date)


@app.callback([Output('performance_table', 'columns'), Output('performance_table', 'data'),
               Output('performance_table', 'style_data_conditional')],
              [Input('input_gap', 'value'), Input('input_date', 'date')])
def simple_dash_table(input_gap, input_date):
    input_date = dt.strptime(re.split('T| ', input_date)[0], '%Y-%m-%d').date()
    df = api_data[api_data['date'] == input_date]
    pt = df.pivot_table(columns=['spot'], values='value', index=['date', 'plot_type'],
                        aggfunc=sum).reset_index()
    pt = pt[(pt.plot_type != 'spot') & (pt.plot_type != 't')]
    for i in pt.columns:
        if isinstance(i, int):
            pt[i] = pd.to_numeric(pt[i])
    temp = pt.loc[pt['date'] == input_date]
    columns = [{'id': 'date', 'name': 'date', 'type': 'text'}] + \
              [{'id': 'plot_type', 'name': 'plot_type', 'type': 'text'}] + \
              [{'id': str(i),
                'name': str(i),
                'type': 'numeric',
                'format': Format(
                    nully='N/A',
                    precision=2,
                    scheme=Scheme.fixed,
                    sign=Sign.parantheses
                )}
               for i in temp.columns if isinstance(i, int) and i % int(input_gap) == 0]
    data = temp[[i for i in temp.columns if isinstance(i, str) or i % int(input_gap) == 0]].to_dict('records')
    style_data_conditional = [{'if': {'row_index': 'odd'}, 'backgroundColor': '#e2f2f6'}] + \
                             [{'if': {'column_id': col['id'], 'filter_query': '{}<0.0'.format("{" + col['id'] + "}")},
                               'color': 'red'}
                              for col in columns if col['type'] == 'numeric']
    return columns, data, style_data_conditional


if __name__ == '__main__':
    app.run_server(debug=True)
