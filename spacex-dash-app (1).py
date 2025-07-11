# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

launch_sites = spacex_df['Launch Site'].unique()
# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                    options=[{'label':'All Sites','value':'ALL'}] + \
                                    [{'label':launch_site,'value':launch_site} for launch_site in launch_sites],
                                    placeholder ='Select a Launch Site here',
                                    searchable=True
                                    ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0,max=10000,step=2500,
                                    marks={
                                        0:'0',
                                        2500:'2,500',
                                        5000:'5,000',
                                        7500:'7,500',
                                        10000:'10,000'},
                                    value=[min_payload,max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart',component_property='figure'),
                Input(component_id='site-dropdown',component_property='value'))
def get_pie_chart(launch_site_input):
    filtered_df = spacex_df[['Launch Site','class']]
    if launch_site_input == 'ALL':
        fig = px.pie(filtered_df, values='class', 
        names='Launch Site', 
        title='All Launch Sites')
        return fig
    else:
        selected_ls = filtered_df.loc[filtered_df['Launch Site']==launch_site_input,'class'].value_counts().reset_index()
        selected_ls.columns = ['class','count']
        selected_ls['labels'] = selected_ls['class'].map({0:'Failed',1:'Success'})
        fig = px.pie(selected_ls, values='count', 
        names='labels',
        color='labels',
        color_discrete_map={'Success':'green','Failed':'red'},
        title=launch_site_input)
        return fig
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
            Input(component_id='site-dropdown', component_property='value'), Input(component_id="payload-slider", component_property="value"))
def get_scatter_chart(launch_site, payload_value):
    filtered_df = spacex_df[['Launch Site','Payload Mass (kg)','Booster Version Category','class']]
    ch_title = 'All sites'
    if launch_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site']==launch_site]
        ch_title = launch_site
    payload_df = filtered_df[(filtered_df['Payload Mass (kg)'] >= payload_value[0]) & (filtered_df['Payload Mass (kg)'] <= payload_value[1])]
    fig = px.scatter(payload_df,x='Payload Mass (kg)',y='class',
                        color='Booster Version Category',
                        title=f'Correlation between Payload and Success for {ch_title}')
    return fig
# Run the app
if __name__ == '__main__':
    app.run()
    
