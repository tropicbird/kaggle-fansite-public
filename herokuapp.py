from dash import Dash, dcc, html, Input, Output, dash_table
import plotly.express as px
from functions import add_latest_rank_in_country
import pandas as pd
import dash_bootstrap_components as dbc
import config

app = Dash(__name__, external_stylesheets=[dbc.themes.MATERIA], suppress_callback_exceptions=True)
app.title = "Kaggle Ranking Fansite"

#Setup google analytics
app.index_string = """<!DOCTYPE html>
<html>
    <head>
        <!-- Google tag (gtag.js) -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-L93YK59KDZ"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());

          gtag('config', 'G-L93YK59KDZ');
        </script>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>"""
server = app.server

#Set date of the latest ranking datasets
latest_YM=config.latest_YM

# Load selectable countries
options_asia = config.searchable_countries['options_asia']
options_europe = config.searchable_countries['options_europe']
options_africa = config.searchable_countries['options_africa']
options_americas = config.searchable_countries['options_americas']
options_oceania = config.searchable_countries['options_oceania']

# Load ranking datasets
df_cmp_all = pd.read_csv(f'./datasets/merged_ranking/competitions/df_cmp_all.csv')
df_datasets_all = pd.read_csv(f'./datasets/merged_ranking/datasets/df_datasets_all.csv')
df_notebooks_all = pd.read_csv(f'./datasets/merged_ranking/notebooks/df_notebooks_all.csv')
df_discussion_all = pd.read_csv(f'./datasets/merged_ranking/discussion/df_discussion_all.csv')

df_all={'competitions':df_cmp_all,
        'datasets':df_datasets_all,
        'notebooks':df_notebooks_all,
        'discussion':df_discussion_all
        }

# Make unique users list
usernames=[]
usernames.extend(df_cmp_all['url'].unique().tolist())
usernames.extend(df_datasets_all['url'].unique().tolist())
usernames.extend(df_notebooks_all['url'].unique().tolist())
usernames.extend(df_discussion_all['url'].unique().tolist())
usernames=list(set(usernames))
usernames.sort(key=str.lower)
usernames=[username_tmp.replace("https://www.kaggle.com/", '') for username_tmp in usernames]

# Make unique Year-Month list
YM_list=df_cmp_all.YM.unique().tolist()
YM_list.sort()

# HTML style
continents_font={'margin-bottom': '0px', 'font-weight': 'bold'}

# HTML layout
app.layout = html.Div([
    html.Div([
        html.H1('🌈Kaggle Ranking Fansite',style={'text-align': 'center','color':'rgb(0, 192, 251)'}),
        html.H4('What is this website?'),
        html.Div(
            [dcc.Markdown('''
            Welcome! This is the fansite of [Kaggle](https://www.kaggle.com/), especially for the ranking. All ranking categories (*Competitions, Datasets, Notebooks, and Discussion*) are covered. On this website, you can search for...
             
            * **Domestic Ranking**: Ranking within your selected countries.
            * **Users History**: Ranking history of your selected users.
            
            I hope you will find it interesting and get some insights. Any feedbacks are welcome😊! ([Contact](https://www.kaggle.com/hdsk38))
            
            **NOTE (Datasets):** 
            Top-1000 ranking data has been stored on the 15th of every month since October 2021 ([datasets](https://www.kaggle.com/datasets/hdsk38/comp-top-1000-data)). For that reason, the searchable countries and usernames are limited to the dataset. This website will also be updated every month. Looking for general analysis of the ranking data? Take a look at [this notebook](https://www.kaggle.com/code/hdsk38/eda-top-1000-kaggle-ranking-in-2022).     
            ''')
            ]
        ),
        html.Hr(),
        html.H4('1. Ranking Category'),
        dcc.Dropdown(
            ['competitions','datasets','notebooks','discussion'],
            id='ranking_type',
            value='competitions'
        ),
        html.P('',style={'margin-bottom': '36px'}),
    ]),
    html.Div([
            html.H4('2. Search for...'),
            dcc.Tabs(id="tabs-search-for", mobile_breakpoint=0,
                children=[
                    dcc.Tab(label="Domestic Ranking", value='tab-domestic-ranking',
                            style={'height': '44px', 'padding': '6px', 'fontWeight': 'bold'},
                            selected_style={'height': '24px', 'padding': '6px'}),
                    dcc.Tab(label="Users History", value='tab-ranking-history',
                            style={'height': '44px', 'padding': '6px', 'fontWeight': 'bold'},
                            selected_style={'height': '24px', 'padding': '6px'}),
                ]
            ),

        html.Div(id='tabs-content-example-graph'),
    ]),
    html.Hr(),
    html.H4('⬇️⬇️️📈️Generated Output📈️⬇️️⬇️',style={"text-align": "center"}),
    dcc.Loading(
        id="loading-1",
        type="default",
        children=html.Div([
        dcc.Graph(id="graph", style={
            'margin-top': '0px'},
                  )])
    ),
    html.Div([html.Label(f"Ranking as of {str(latest_YM)}-15",style={'font-weight': 'bold'}),
            dash_table.DataTable(
            id='datable-paging',
            columns=[
                dict(name='Rank within the group', id='crank', type='text'),
                dict(name='World Rank', id='latest_rank', type='text'),
                dict(name='User', id='name_url', type='text', presentation='markdown'),
            ],
            page_size=5,
            row_selectable="multi",
            selected_rows = [0,1,2],
            cell_selectable=False,
            style_cell={
                'text-align': 'center',
                'marginLeft': 'auto',
                'marginRight': 'auto'
            }
        )
    ],style={
    'textAlign': 'center',
    "margin-left":"20px",
    "margin-right":"20px"
}),
    ],
    style = {'margin-top': '12px',
             'margin-left': 'auto',
             'margin-right': 'auto',
             'padding':'12px',
             'max-width': '900px',}
)


@app.callback(Output('tabs-content-example-graph', 'children'),
              Input('tabs-search-for', 'value'))
def render_content(tab):
    if tab == 'tab-domestic-ranking':
        return html.Div([
        html.Div([
            dcc.ConfirmDialogProvider(
                children=html.Button('ℹ️ Additional Info.️',
                                     ),
                id='information-provider',
                message=f'''
***HOW TO USE***
-Select countries, then you will see the ranking limited to the countries. Malaysia is selected as example. 
***NOTE***
-"WR1000+ or moved" means the user was not within the top-1000 World Ranking on {str(latest_YM)}-15 or moved to another country. So, they were not considered for the domestic ranking.
''',
            ),
            html.Div(id='output-provider')
        ]),
        html.P(''),
        html.Div([html.P('Asia',
                         style=continents_font),
        dcc.Dropdown(
                        id="options_asia",
                        options=options_asia,
                        multi=True,
                        value=['Malaysia'],
                        placeholder="Select countries...",
                        ),]),

        html.Div([html.P('Europe',
                         style=continents_font),
        dcc.Dropdown(
            id="options_europe",
            options=options_europe,
            multi=True,
            value=[],
            placeholder="Select countries..."
        ),]),

        html.Div([html.P('Africa',
                         style=continents_font),
        dcc.Dropdown(
            id="options_africa",
            options=options_africa,
            multi=True,
            value=[],
            placeholder="Select countries..."
        ),]),

        html.Div([html.P('America',
                         style=continents_font),
        dcc.Dropdown(
            id="options_americas",
            options=options_americas,
            multi=True,
            value=[],
            placeholder="Select countries..."
        ),]),
        html.Div([html.P('Oceania',
                         style=continents_font),
        dcc.Dropdown(
            id="options_oceania",
            options=options_oceania,
            multi=True,
            value=[],
            placeholder="Select countries..."
        ),]),
        html.Div([html.P('Other (*ALL* shows simply Top 1000 Wold Rank)',
                        style=continents_font),
        dcc.Dropdown(
            id="options_all",
            options=['ALL','UNKOWN'],
            multi=True,
            value=[],
            placeholder="Select countries..."
        ),]),
        html.Div(id='username'),
        ])
    elif tab == 'tab-ranking-history':
        return html.Div([
            html.Div([
                dcc.ConfirmDialogProvider(
                    children=html.Button('ℹ️ Additional Info.️',
                                         ),
                    id='information-provider',
                    message=f'''
***HOW TO USE***
-Select or type usernames. Usernames are different from display names. Usernames are located at the end of the URL of a Kaggle profile page.
***NOTE***
-The searchable users are those who have been at the Top-1000 at least once since October 2021.
-"WR1000+ or moved" means the user was not within the top-1000 World Ranking on {str(latest_YM)}-15 or moved to another country. So, they were not considered for the domestic ranking.  
''',
                ),
                html.Div(id='output-provider')
            ],                                         style={
                                                'display':'flex',
                                                'justify-content':'flex-end'
                                                }),
        html.P(''),

            html.Div([html.P('User Name (👉https://www.kaggle.com/<USER NAME>)',
                         style={'margin-bottom': '0px',
                                'font-weight': 'bold'}),
                dcc.Dropdown(
                    usernames,
                    id='username',
                    multi=True,
                    value='',
                    placeholder="Select or Type username..."
                ),
                html.Div(id='options_oceania'),
                html.Div(id='options_americas'),
                html.Div(id='options_africa'),
                html.Div(id='options_europe'),
                html.Div(id='options_asia'),
                html.Div(id='options_all'),
                html.Div()
            ])
        ])
    else:
        return html.Div([
            html.Div(id='options_oceania'),
            html.Div(id='options_americas'),
            html.Div(id='options_africa'),
            html.Div(id='options_europe'),
            html.Div(id='options_asia'),
            html.Div(id='options_all'),
            html.Div(id='username'),
        ])

@app.callback(
    Output("datable-paging", "selected_rows"),
    Input("options_oceania", "value"),
    Input("options_americas", "value"),
    Input("options_africa", "value"),
    Input("options_europe", "value"),
    Input("options_asia", "value"),
    Input("options_all", "value"),
    Input("ranking_type", "value"),
    Input(component_id='username', component_property='value'),
)
def reset_selected_rows(a,b,c,d,e,f,g,h):
    return [0,1,2]

@app.callback(
    Output("graph", "figure"),
    Output("datable-paging","data"),
    Input("options_oceania", "value"),
    Input("options_americas", "value"),
    Input("options_africa", "value"),
    Input("options_europe", "value"),
    Input("options_asia", "value"),
    Input("options_all", "value"),
    Input("ranking_type", "value"),
    Input(component_id='username', component_property='value'),
    Input('datable-paging', 'selected_rows')
)
def update_line_chart(options_oceania,
                      options_americas,
                      options_africa,
                      options_europe,
                      options_asia,
                      options_all,
                      ranking_type,username,
                      selected_rows):
    df = df_all[ranking_type]
    if username is None:
        if options_all==None:
            df = df[df['url']=='aaa']
            countries='aaa'
        elif 'ALL' in options_all:
            countries='ALL'
        else:
            countries=[]
            countries.extend(options_asia)
            countries.extend(options_europe)
            countries.extend(options_africa)
            countries.extend(options_americas)
            countries.extend(options_oceania)
            countries.extend(options_all)
            mask = df.country.isin(countries)
            df = df[mask]
    else:
        user_name=("https://www.kaggle.com/" + un for un in username)
        df = df[df['url'].isin(user_name)]

    if len(df)==0:
        df['crank']=None
        fig = px.line(df, x="YM", y="rank", color='name_id', markers=True)
    else:
        df = add_latest_rank_in_country(df)

        #ADD None to not collected YM
        crank_name_id_ls=df.crank_name_id.unique().tolist()
        for crank_name_id in crank_name_id_ls:
            user_YM_list=df[df['crank_name_id']==crank_name_id].YM.unique().tolist()
            user_YM_list.sort()
            indx=YM_list.index(user_YM_list[0])
            if YM_list[indx:]==user_YM_list.sort():
                continue
            else:
                rank_name_id = set(df[df['crank_name_id'] == crank_name_id].rank_name_id.values)
                rank_name_id = list(rank_name_id)
                name_id= set(df[df['crank_name_id'] == crank_name_id].name_id.values)
                name_id=list(name_id)
                latest_rank= set(df[df['crank_name_id'] == crank_name_id].latest_rank.values)
                latest_rank=list(latest_rank)
                if latest_rank==[1001]:
                    latest_rank=["WR1000+ or moved"]
                crank= set(df[df['crank_name_id'] == crank_name_id].crank.values)
                crank=list(crank)
                url= set(df[df['crank_name_id'] == crank_name_id].url.values)
                url = list(url)
                for YM in YM_list[indx:]:
                    if YM not in user_YM_list:
                        df2 = {'crank_name_id': [crank_name_id], 'YM': [YM], 'rank': [None],'rank_name_id':rank_name_id,'name_id':name_id,
                               'latest_rank':latest_rank, 'crank':crank,'url':url}
                        df2 = pd.DataFrame(df2)
                        df= pd.concat([df,df2])

        df_top_1000 = df[df['YM'] == latest_YM].copy()
        df_below_1000 = df[df['YM'] != latest_YM].copy()
        df_top_1000.sort_values(by='rank', ascending=True, inplace=True)
        df_below_1000.sort_values(by='YM', ascending=False, inplace=True)
        df=pd.concat([df_top_1000,df_below_1000])
        df['YM'] = df['YM'].astype(str)

        if username is None:
            fig = px.line(df,
                x="YM", y="rank", color='crank_name_id',markers=True)
        else:
            fig = px.line(df,
                x="YM", y="rank", color='rank_name_id',markers=True)

    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(range=['2021-9',latest_YM+'-20'])
    fig.update_traces(connectgaps=False)

    if username is None and countries != "ALL":
        fig.update_layout(showlegend=True,
                          yaxis_title="World Rank",
                          legend_title=f"<b>Domestic Ranking in [{', '.join(countries)}] as of '{latest_YM[2:]}-15</b>",
                          )
        fig.update_layout(legend=dict(x=0,
                                      y=1.1,
                                      xanchor='left',
                                      yanchor='bottom',
                                      borderwidth=1,
                                      itemclick=False,
                                      itemdoubleclick=False,
                                      ))
    elif username is None and countries == "ALL":
        fig.update_layout(showlegend=True,
                          yaxis_title="World Rank",
                          legend_title=f"<b>World Rank as of '{latest_YM[2:]}-15</b>",
                          )
        fig.update_layout(legend=dict(x=0,
                                      y=1.1,
                                      xanchor='left',
                                      yanchor='bottom',
                                      borderwidth=1
                                      ))
    else:
        fig.update_layout(showlegend=True,
                          yaxis_title="World Rank",
                          legend_title=f"<b>As of '{latest_YM[2:]}-15</b>",
                          )
        fig.update_layout(legend=dict(x=0,
                                      y=1.1,
                                      xanchor='left',
                                      yanchor='bottom',
                                      borderwidth=1,
                                      itemclick=False,
                                      itemdoubleclick=False,
                                      ))
    display_num = len(df.name_id.unique())

    if display_num<len(selected_rows):
        fig.update_traces(visible=True)
    else:
        fig.update_traces(visible="legendonly")
        for selected_row in selected_rows:
            fig.data[selected_row].visible = True

    df_table=df[df['YM']==latest_YM][['crank','latest_rank','name_id','url']]
    df_table['name_url']='['+df_table['name_id']+']'+'('+df_table['url']+')'
    return fig, df_table.to_dict("records")

if __name__ == '__main__':
    app.run_server(debug=False)