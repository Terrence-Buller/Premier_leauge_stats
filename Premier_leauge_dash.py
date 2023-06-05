import pandas as pd
import mysql.connector
import dash
import plotly.graph_objs as go
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output

STAT_COLOR = {
    'Manchester City': '#6CABDD', 'Liverpool': '#C8102E', 'Chelsea': '#034694', 'Manchester United': '#DA291C',
    'Tottenham Hotspur': '#132257', 'Arsenal': '#EF0107', 'Leicester City': '#003090', 'Everton': '#003399',
    'Wolverhampton Wanderers': '#FDB913', 'West Ham United': '#7A263A', 'Leeds United': '#FFCD00',
    'Southampton': '#D71920', 'Brentford': '#cd3529', 'Stoke City': '#E03A3E', 'Crystal Palace': '#1B458F',
    'Swansea City': '#ffffff', 'Newcastle United': '#FFFFFF', 'Bournemouth': '#DA291C', 'Burnley': '#6C1D45',
    'Brighton & Hove Albion': '#0057B8', 'West Bromwich Albion': '#122F67', 'Watford': '#FBEE23',
    'Sheffield United': '#EE2737', 'Aston Villa': '#95BFE5', 'Wigan Athletic': '#1d59af', 'Sunderland': '#ff0000',
    'Hull City': '#f5971d', 'Fulham': '#ffffff', 'Cardiff City': '#0070B5', 'Norwich City': '#FFF200',
    'Middlesbrough': '#e11b22', 'Reading': '#004494', 'Queens Park Rangers': '#1D5BA4',
    'Huddersfield Town': '#0E63AD', 'Ipswich Town': '#3a64a3', 'Derby County': '#ffffff',
    'Blackburn Rovers': '#009ee0', 'Bolton Wanderers': '#263c7e', 'Birmingham City': '#202959',
    'Portsmouth': '#001489', 'Charlton Athletic': '#d4021d', 'Blackpool': '#F68712', 'Coventry City': '#ffffff',
    'Bradford City': '#7A263A', 'Nottingham Forest': '#DD0000'
}

app = dash.Dash(__name__, suppress_callback_exceptions=True)

mydb = mysql.connector.connect(
    host="***",
    user="***",
    password="***",
    database="***"
)

query = "SELECT * FROM 2000_now ORDER BY Year ASC"
df = pd.read_sql(query, mydb)
df['Team'] = df['Team'].str.replace('\(C\)$|\(R\)$', '', regex=True).str.strip()

query2 = "SELECT * FROM topscorer ORDER BY Year ASC"
df2 = pd.read_sql(query2, mydb)

selected_year = df.Year.unique()
available_stats = ['Pos', 'Wins', 'Draw', 'Loss', 'Goals_for', 'Goals_against', 'Goal_differential', 'Points']
team_options = [{'label': team, 'value': team} for team in sorted(df.Team.unique())]

start_layout = html.Div(
    [
        html.Img(
            src='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTOJh8vsVmfAqtADNZycxbT0RjmKIr4nhX_XQ&usqp=CAU',
            alt='Premier League Logo',
            style={'width': '200px', 'margin': '0 auto', 'display': 'block'}
        ),
        html.H1(
            'Premier League Stats',
            style={'textAlign': 'center', 'backgroundColor': '#3F1052', 'color': 'white', 'padding': '20px'}
        ),
        html.Div(
            [
                dcc.Link(
                    'All-time',
                    href='/All-time',
                    style={'margin': '100px', 'color': 'white', 'backgroundColor': '#3F1052',
                           'textDecoration': 'underline', 'padding': '15px'}
                ),
                dcc.Link(
                    'Season Stats',
                    href='/Season-stats',
                    style={'margin': '100px', 'color': 'white', 'backgroundColor': '#3F1052',
                           'textDecoration': 'underline',
                           'padding': '15px'}
                ),
                dcc.Link(
                    'Averages',
                    href='/Averages',
                    style={'margin': '100px', 'color': 'white', 'backgroundColor': '#3F1052',
                           'textDecoration': 'underline', 'padding': '15px'}
                ),
                dcc.Link(
                    'Scorers',
                    href='/Scorers',
                    style={'margin': '100px', 'color': 'white', 'backgroundColor': '#3F1052',
                           'textDecoration': 'underline', 'padding': '15px'}
                ),

            ],
            style={'textAlign': 'center'}
        )

    ],
    style={'backgroundImage': 'linear-gradient(to bottom, #0070B5, #DBFCFF)', 'padding': '300px'}
)

# Callback to handle page navigation
@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/All-time':
        return All_time_layout
    elif pathname == '/Season-stats':
        return season_stats_layout
    elif pathname == '/Averages':
        return averages_layout
    elif pathname == '/Scorers':
        return Scorers
    else:
        return start_layout


###All_time###
All_time_layout = html.Div(
    style={'backgroundColor': '#3F1052'},
    children=[
        html.H1('All-time', style={'textAlign': 'center', 'color': 'white', 'padding': '20px'}),
        html.Div([
            dcc.Dropdown(options=team_options, id='team-selection', multi=True),
            dcc.Dropdown(options=[{'label': stat, 'value': stat} for stat in available_stats], id='stat-selection', multi=True),
        ], style={'textAlign': 'center', 'padding': '20px'}),
        dcc.Graph(id='all-time-graph-content')
    ]
)

@app.callback(
    Output('all-time-graph-content', 'figure'),
    Input('team-selection', 'value'),
    Input('stat-selection', 'value')
)

def update_graph(teams, selected_stats):
    if selected_stats is None or teams is None:
        return {}

    if not isinstance(teams, list):
        teams = [teams]

    data = []

    for team in teams:
        dff = df[df['Team'] == team]
        for stat in selected_stats:
            trace = go.Scatter(
                x=dff['Year'],
                y=dff[stat],
                mode='lines+markers',
                name=f'{team}',
                line=dict(color=STAT_COLOR.get(team, 'grey'))

            )
            data.append(trace)

    layout = go.Layout(
        title='Team Performance',
        titlefont=dict(color='purple'),
        plot_bgcolor='#d8d8d8',
        paper_bgcolor='#a5a5a5',
        xaxis=dict(title='Year', titlefont=dict(color='purple'), tickfont=dict(color='purple'), showgrid=False),
        yaxis=dict(title='Statistic', titlefont=dict(color='purple'), tickfont=dict(color='purple')),
        legend=dict(font=dict(color='purple'), bgcolor='#f1f1f1')
    )
    fig = go.Figure(data=data, layout=layout)
    return fig


###season_stats####
season_stats_layout = html.Div(
    style={'backgroundColor': '#3F1052'},
    children=[
        html.H2(children='Stats per season:', style={'textAlign': 'center', 'color': 'white', 'padding': '5px'}),
        dcc.Dropdown(options=[{'label': year, 'value': year} for year in selected_year], id='Season-selection', style={'textAlign': 'center'}),
        dcc.Dropdown(options=[{'label': stat, 'value': stat} for stat in available_stats], id='Season-stat-selection', style={'textAlign': 'center'}),
        html.Div(id='table-content'),
        dcc.Graph(id='Season-graph-content')
    ]
)

@app.callback(
    Output('table-content', 'children'),
    Input('Season-selection', 'value'),
)
def update_table(years):
    if years is None:
        return dash_table.DataTable()
    if not isinstance(years, list):
        years = [years]

    dft = df[df['Year'].isin(years)]
    dft = dft.sort_values('Pos')

    columns = [{'name': col, 'id': col} for col in dft.columns if col != 'Year']
    table = dash_table.DataTable(
        data=dft.to_dict('records'),
        columns=columns,
        style_cell={'textAlign': 'center'},
        style_header={'fontWeight': 'bold'},
        style_data_conditional=[
            {'if': {'column_id': c}, 'backgroundColor': '#3F1052', 'color': 'white'} for c in dft.columns if c != 'Year'
        ],
        style_table={'margin': '1px'}
    )


    return table


@app.callback(
    Output('Season-graph-content', 'figure'),
    Input('Season-selection', 'value'),
    Input('Season-stat-selection', 'value')
)
def update_graph_season(years, selected_stat):
    if selected_stat is None or years is None:
        return {}

    if not isinstance(years, list):
        years = [years]

    data = []

    for year in years:
        dfs = df[df['Year'] == year]
        dfs_sorted = dfs.sort_values(by=selected_stat, ascending=(selected_stat in ['Pos', 'Goals_against', 'Loss']))
        stat_values = dfs_sorted[selected_stat].values
        team_names = dfs_sorted['Team'].values

        trace = go.Bar(
            x=team_names,
            y=stat_values,
            name=f'{year} - {selected_stat}',
            marker=dict(color=[STAT_COLOR.get(team, 'black') for team in team_names])
         )
        data.append(trace)

    layout = go.Layout(
        title='Team Performance',
        template='plotly',
        plot_bgcolor='#3F1052',
        paper_bgcolor='#3F1052',
        titlefont=dict(color='white'),
        xaxis=dict(title='Year', titlefont=dict(color='white'), tickfont=dict(color='white')),
        yaxis=dict(title='Statistic', titlefont=dict(color='white'), tickfont=dict(color='white'))
    )
    fig = go.Figure(data=data, layout=layout)
    return fig


###Averages_layout###
averages_layout = html.Div(
    style={'backgroundColor': '#3F1052'},
    children=[
    html.H2('Averages', style={'textAlign': 'center', 'color': 'white', 'padding': '5px'}),
    dcc.Dropdown(options=team_options, id='team-selection-avg', multi=True, style={'textAlign': 'center'}),
    dcc.Dropdown(options=[{'label': stat, 'value': stat} for stat in available_stats], id='stat-selection-avg', multi=True, style={'textAlign': 'center'}),
    dcc.Graph(id='graph-content-avg')
])

# Callback to update the graph based on team and stat selection for averages
@app.callback(
    Output('graph-content-avg', 'figure'),
    Input('team-selection-avg', 'value'),
    Input('stat-selection-avg', 'value')
)
def update_graph_avg(teams, selected_stats):
    if selected_stats is None or teams is None:
        return {}

    if not isinstance(teams, list):
        teams = [teams]

    data = []
    for team in teams:
        team_avg = df[df['Team'] == team].mean(numeric_only=True)
        for stat in selected_stats:
            trace = go.Bar(
                x=[team],
                y=[team_avg[stat]],
                name=f'{team} - {stat}',
                marker=dict(color=STAT_COLOR.get(team, 'black'))
            )
            data.append(trace)
    data.sort(key=lambda trace: trace.y[0], reverse=True)
    layout = go.Layout(title='Team Averages',
                       template='plotly',
                       plot_bgcolor='#3F1052',
                       paper_bgcolor='#3F1052',
                       titlefont=dict(color='white'),
                       xaxis=dict(title='Team', titlefont=dict(color='white'), tickfont=dict(color='white')),
                       yaxis=dict(title='Statistic', titlefont=dict(color='white'), tickfont=dict(color='white'))
                       )
    fig = go.Figure(data=data, layout=layout)
    return fig




###top_scorers###
Scorers = html.Div(
    style={'backgroundColor': '#3F1052'},
    children=[
        html.H2(children='Topscorers:', style={'textAlign': 'center', 'color': 'white', 'padding': '5px'}),
        dcc.Dropdown(options=[{'label': year, 'value': year} for year in selected_year], id='Year-selection', style={'textAlign': 'center'}),
        dcc.Graph(id='graph-content-scorers')
])

@app.callback(
    Output('graph-content-scorers', 'figure'),
    Input('Year-selection', 'value')
)
def update_graph(years):
    if years is None:
        return {}

    if not isinstance(years, list):
        years = [years]

    data = []

    for year in years:
        dff1 = df2[df2['Year'] == year]
        dff1 = dff1.sort_values('Goals', ascending=False)
        clubs = dff1['Club'].tolist()
        colors = [STAT_COLOR.get(club, 'grey') for club in clubs]



        trace = go.Bar(
            x=dff1['Player'],
            y=dff1['Goals'],
            marker=dict(color=colors),
            hovertemplate = '<b>Player:</b> %{x}<br><b>Goals:</b> %{y}<br><b>Club:</b> ' + dff1['Club'] + '<extra></extra>'

        )
        data.append(trace)

    layout = go.Layout(title='Topscorers',
                       template='plotly',
                       plot_bgcolor='#3F1052',
                       paper_bgcolor='#3F1052',
                       titlefont=dict(color='white'),
                       xaxis=dict(title='Player', titlefont=dict(color='white'), tickfont=dict(color='white')),
                       yaxis=dict(title='Goals', titlefont=dict(color='white'), tickfont=dict(color='white'))
                       )
    fig = go.Figure(data=data, layout=layout)
    return fig

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

if __name__ == '__main__':
    app.run_server(debug=True)
