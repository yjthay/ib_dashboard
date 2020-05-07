import dash
import copy
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import pandas as pd
from datetime import datetime as dt, date
import dash_table.FormatTemplate as FormatTemplate
from dash_table.Format import Format, Scheme, Sign, Symbol
import calendar
import os


def date_to_int(input_date):
    ''' Convert datetime to ordinal timestamp '''
    return input_date.toordinal()


def check_month_end(input_date):
    ''' Check if input date is the last day of month '''
    if calendar.monthrange(input_date.year, input_date.month)[1] == input_date.day:
        return True
    else:
        return False


def getMarks(start_date, end_date, spacing=30):
    ''' Returns the marks for labeling.
        Every Nth value will be used.
    '''
    result = {}
    for i in range(date_to_int(start_date), date_to_int(end_date) + 1):
        date_i = date.fromordinal(i)
        if i == date_to_int(start_date) or i == date_to_int(end_date):
            result[i] = {'label': date_i.strftime('%d %b %y'),
                         'style': {'text-align': 'center',
                                   'margin': 'auto'}}
        if date_to_int(start_date) + 14 <= i <= date_to_int(end_date) - 14:
            if check_month_end(date_i):
                result[i] = {'label': date_i.strftime('%d %b %y'),
                             'style': {'text-align': 'center',
                                       'margin': 'auto'}}
    return result


csv_file_path = os.path.join('data/spx_test.csv')
api_data = pd.read_csv(csv_file_path)
api_data = api_data[(api_data.plot_type != 'spot') & (api_data.plot_type != 't')]
api_data['date'] = api_data['date'].apply(lambda x: dt.strptime(x, "%Y-%m-%d").date())
api_data['value'] = pd.to_numeric(api_data['value'])
plot_type = api_data['plot_type'].unique()

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Satellite Overview"
)

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
app = dash.Dash(__name__, assets_folder='assets')
server = app.server
app.config.suppress_callback_exceptions = True

app.layout = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("dash-logo.png"),
                            id="plotly-image",
                            style={
                                "height": "60px",
                                "width": "auto",
                                "margin-bottom": "25px",
                            },
                        ),
                    ],
                    className="one-third column",
                ),
                html.Div(
                    [
                        html.H1(
                            'Performance Plot',
                        ),
                    ],
                    id='title',
                    className="one-half column",
                ),
                html.Div(
                    [
                        html.A(
                            html.Button("Learn More", id="learn-more-button"),
                            href="https://github.com/yjthay/ib_dashboard",
                        )
                    ],
                    className="one-third column",
                    id="button",
                ),
            ],
            id="header",
            className="row header",
            style={"margin-bottom": "25px"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            "Risk Type to Plot on Graph",
                            className="control_label",
                        ),
                        html.Div(
                            [
                                html.P('Granularity of Spot'),
                                dcc.Dropdown(
                                    id="input_gap",
                                    options=[{'value': i, 'label': i} for i in
                                             range(1, 11)],
                                    value=10
                                ),
                            ],
                        ),
                    ],
                    id="info-container_2",
                    className="pretty_container four columns",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                dcc.RadioItems(
                                    id='radio_y_axis',
                                    options=[{'value': c, 'label': c} for c in plot_type],
                                    value='value',
                                    className="mini_container radiobutton-group",
                                ),
                                # html.Div(
                                #     [html.H6(id="delta_text"), html.P("Delta")],
                                #     id="delta",
                                #     className="mini_container",
                                # ),
                                # html.Div(
                                #     [html.H6(id="gamma_text"), html.P("Gamma")],
                                #     id="gamma",
                                #     className="mini_container",
                                # ),
                                # html.Div(
                                #     [html.H6(id="theta_text"), html.P("Theta")],
                                #     id="theta",
                                #     className="mini_container",
                                # ),
                                # html.Div(
                                #     [html.H6(id="vega_text"), html.P("Vega")],
                                #     id="vega",
                                #     className="mini_container",
                                # ),
                                # html.Div(
                                #     [html.H6(id="pnl_text"), html.P("P&L")],
                                #     id="pnl",
                                #     className="mini_container",
                                # ),
                            ],
                            id="info-container",
                            className="row container-display",
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        # html.P('Date reference'),
                                        dcc.RangeSlider(
                                            id='date_slider',
                                            min=date_to_int(min_date),
                                            max=date_to_int(max_date),
                                            value=[date_to_int(min_date),
                                                   date_to_int(max_date)],
                                            marks=getMarks(min_date, max_date),
                                            included=True,
                                            allowCross=False,
                                            updatemode='drag',
                                        )
                                    ], className='date-slider'
                                ),
                                dcc.Graph(
                                    id='graph_dynamic',
                                    animate=True,
                                ),
                                html.Div(id='output-container-range-slider',
                                         style={'text-align': 'left'}),
                            ],
                            id="graph_dynamicContainer",
                            className="pretty_container"
                        ),
                    ],
                    id="right-column",
                    className="eight columns",
                ),
            ],
            className="row flex-display",
        ),

        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            id='output_date_picker'
                        ),
                        dash_table.DataTable(
                            id='performance_table',
                            filter_action="native",
                            style_header=colors,
                            style_as_list_view=True,
                            style_table={'overflowX': 'scroll'}
                        ),
                    ],
                    className="eight columns",
                ),
            ],
            id='lower-dash_table',
            className="row flex-display",
        ),

    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)


# @app.callback(
#     [
#         Output("delta_text", "children"),
#         Output("gamma_text", "children"),
#         Output("theta_text", "children"),
#         Output("vega_text", "children"),
#         Output("pnl_text", "children"),
#     ],
#     [
#         Input('y_axis', 'value'),
#         Input('date_slider', 'value')
#     ],
# )
# def update_mini_containers(y_axis, date_slider):
#     start_date = date.fromordinal(min(date_slider))
#     end_date = date.fromordinal(max(date_slider))
#     df = api_data.loc[(api_data['date'] == start_date) & (api_data['plot_type'] == y_axis)]
#     ref_df = api_data.loc[(api_data['date'] == end_date) & (api_data['plot_type'] == y_axis)]
#     join_df = ref_df.merge(right=df, how='left', on=['spot', 'plot_type'], suffixes=['_end', '_start'])
#
#     return data[0] + " mcf", data[1] + " bbl", data[2] + " bbl"

@app.callback(Output('output-container-range-slider', 'children'),

              [Input('date_slider', 'value')])
def update_output(date_slider):
    start_date = date.fromordinal(min(date_slider))
    end_date = date.fromordinal(max(date_slider))
    return 'Examining data from {} to {}'.format(dt.strftime(start_date, '%d-%b-%y'),
                                                 dt.strftime(end_date, '%d-%b-%y'))


@app.callback(Output('graph_dynamic', 'figure'),
              [Input('radio_y_axis', 'value'),
               Input('date_slider', 'value')])
def graph_against_spot(y_axis, date_slider):
    layout_main_graph = copy.deepcopy(layout)

    start_date = date.fromordinal(min(date_slider))
    end_date = date.fromordinal(max(date_slider))
    df = api_data.loc[(api_data['date'] == start_date) & (api_data['plot_type'] == y_axis)]
    ref_df = api_data.loc[(api_data['date'] == end_date) & (api_data['plot_type'] == y_axis)]
    join_df = ref_df.merge(right=df, how='left', on=['spot', 'plot_type'], suffixes=['_end', '_start'])

    colors = []
    for i in range(min(join_df.spot), max(join_df.spot) + 1):
        colors.append("rgb(123, 199, 255)")

    data = [
        dict(
            type='bar',
            x=join_df['spot'],
            y=(join_df.value_start - join_df.value_end).astype(int),
            name='Start-End',
            marker=dict(color=colors),
        ),
        dict(
            x=df['spot'],
            y=df['value'],
            mode='lines',
            name='Start',
        ),
        dict(
            x=ref_df['spot'],
            y=ref_df['value'],
            mode='lines',
            name='End',
        ),
    ]
    layout_main_graph['title'] = 'Graph vs spot'
    layout_main_graph["showlegend"] = True
    layout_main_graph["autosize"] = True
    layout_main_graph["hovermode"] = 'compare'
    figure = dict(data=data, layout=layout_main_graph)
    return figure


@app.callback([Output('performance_table', 'columns'), Output('performance_table', 'data'),
               Output('performance_table', 'style_data_conditional')],
              [Input('input_gap', 'value'), Input('date_slider', 'value')])
def simple_dash_table(input_gap, date_slider):
    # input_date = dt.strptime(re.split('T| ', input_date)[0], '%Y-%m-%d').date()
    start_date = date.fromordinal(min(date_slider))
    end_date = date.fromordinal(max(date_slider))
    df = api_data[(api_data['date'] == start_date) | (api_data['date'] == end_date)]
    pt = df.pivot_table(columns=['spot'], values='value', index=['date', 'plot_type'],
                        aggfunc=sum).reset_index()
    # pt = pt[(pt.plot_type != 'spot') & (pt.plot_type != 't')]
    for i in pt.columns:
        if isinstance(i, int):
            pt[i] = pd.to_numeric(pt[i])
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
               for i in pt.columns if isinstance(i, int) and i % int(input_gap) == 0]
    data = pt[[i for i in pt.columns if isinstance(i, str) or i % int(input_gap) == 0]].to_dict('records')
    style_data_conditional = [{'if': {'row_index': 'odd'}, 'backgroundColor': '#e2f2f6'}] + \
                             [{'if': {'column_id': col['id'], 'filter_query': '{}<0.0'.format("{" + col['id'] + "}")},
                               'color': 'red'}
                              for col in columns if col['type'] == 'numeric']
    return columns, data, style_data_conditional


if __name__ == '__main__':
    # app.run_server(host='0.0.0.0', port=8080, debug=True, use_reloader=False)
    app.run_server(debug=True)
