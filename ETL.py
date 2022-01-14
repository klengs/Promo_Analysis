import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.signal import argrelextrema
from datetime import datetime

def load_df():
    df = pd.read_csv('Output.csv', encoding='windows-1251', sep=',')
    return df


def load_district_distr_info():
    df = load_df()
    event_count_by_dist = df.groupby(['FederalDistrict_Name', 'Event_Name']).sum().reset_index()
    graph_activasion = event_count_by_dist[event_count_by_dist.Event_Name == '"Активация кода"']
    graph_registration = event_count_by_dist[event_count_by_dist.Event_Name == '"Регистрация пользователя"']

    pie1 = px.pie(graph_activasion,
                 names='FederalDistrict_Name',
                 values='Event_Count',
                 color_discrete_sequence=px.colors.qualitative.Safe[::4])
    pie1.update_layout(showlegend=False)
    pie1.update_traces(marker=dict(line=dict(color='white', width=0)),
                      opacity=0.7,
                      textposition='outside',
                      textinfo='percent+label+value')

    pie2 = px.pie(graph_registration,
                 names='FederalDistrict_Name',
                 values='Event_Count',
                 color_discrete_sequence=px.colors.qualitative.Safe[::4])
    pie2.update_layout(showlegend=False)
    pie2.update_traces(marker=dict(line=dict(color='white', width=0)),
                      opacity=0.7,
                      textposition='outside',
                      textinfo='percent+label+value')
    loc_dict = {'Central': [55.75222, 37.61556],
                'Far Eastern': [43.1332, 131.9113],
                'North Caucasian': [44.0499, 43.0396],
                'Northwestern': [59.9311, 30.3609],
                'Siberian': [54.9833, 82.8964],
                'Southern': [47.2357, 39.7015],
                'Ural': [56.8431, 60.6454],
                'Volga': [56.3269, 44.0059]}
    map_activasion = graph_activasion[graph_activasion.FederalDistrict_Name != 'Undefined']
    map_activasion['lat'] = map_activasion.FederalDistrict_Name.apply(lambda name: loc_dict[name][0])
    map_activasion['lon'] = map_activasion.FederalDistrict_Name.apply(lambda name: loc_dict[name][1])

    map = px.scatter_geo(map_activasion,
                         lon = 'lon',
                         lat = 'lat',
                         size='Event_Count',
                         color='FederalDistrict_Name',
                         size_max=40,
                         color_discrete_sequence=px.colors.qualitative.Safe[5:])
    map.update_layout(legend_title_text='Districts',
                      showlegend=False)
    map.update_geos(projection_type='orthographic',
                    showcountries=True,
                    countrycolor="black")

    pop_dict = {'Central': 39250960,
                'Volga': 29070827,
                'Northwestern': 13941959,
                'Ural': 12329500,
                'Southern': 16482488,
                'Siberian': 17003927,
                'North Caucasian': 9967301,
                'Far Eastern': 8124053
                }

    map_activasion['population'] = map_activasion.FederalDistrict_Name.apply(lambda x: pop_dict[x])
    map_activasion['act_per_person'] = (map_activasion.Event_Count / map_activasion.population) * 100
    bar = px.bar(map_activasion,
           x='FederalDistrict_Name',
           y='act_per_person',
           color='population',
           labels={
                     "act_per_person": "Активаций на 100 человек в округе",
                     "population": "Численность населения",
                     "FederalDistrict_Name": "Название "
                 },
           color_continuous_scale=px.colors.sequential.Brwnyl)

    return event_count_by_dist, pie1, pie2, map, bar

def load_daily_info():
    df = load_df()
    data_per_day = df.groupby(['Date', 'Event_Name']).sum().reset_index()
    activasions = data_per_day[data_per_day.Event_Name == '"Активация кода"'][['Date', 'Event_Count']]
    activasions.rename(columns={'Event_Count': 'n_activasions'}, inplace=True)
    registrations = data_per_day[data_per_day.Event_Name == '"Регистрация пользователя"'][['Date', 'Event_Count']]
    registrations.rename(columns={'Event_Count': 'n_registrations'}, inplace=True)
    dif_df = pd.merge(activasions, registrations, on='Date')
    dif_df['n_regestered_users'] = dif_df.n_activasions - dif_df.n_registrations
    d_fig = px.line(data_per_day,
                  x='Date',
                  y='Event_Count',
                  color='Event_Name',

                  color_discrete_sequence=px.colors.qualitative.Safe[4::4],
                  labels={
                        "Event_Count": "Кол-во активаций/регистраций",
                        "Date": "Дата",
                        "Event_Name": "Явление"
                    })
    d_fig.add_trace(go.Bar(x=dif_df.Date,
                     y=dif_df.n_regestered_users,
                     name='Зарегистрированные пользователи'))
    d_fig.update_traces(marker_color=px.colors.qualitative.Safe[5])
    d_fig.update_xaxes(showgrid=False)
    d_fig.update_yaxes(showgrid=False)

    N = data_per_day[data_per_day.Event_Name == '"Регистрация пользователя"'].Event_Count.to_numpy()
    maximas = argrelextrema(N, np.greater)
    Dates = data_per_day[data_per_day.Event_Name == '"Регистрация пользователя"'].Date.to_numpy()
    dates_formated = []
    for date in Dates[maximas]:
        dates_formated.append(datetime.strptime(date, '%Y-%m-%d %H:%M:%S'))
    x = []
    for i in range(len(dates_formated)-1):
        x.append((dates_formated[i+1] - dates_formated[i]).total_seconds()/60/60/24)

    avg_time_between_spikes = np.mean(x)
    std = np.std(x)

    return data_per_day, d_fig, avg_time_between_spikes, std

def load_daily_district_data():
    df = load_df()
    daily_data_for_each_district = df[df.Event_Name == '"Активация кода"'].groupby(['Date', 'FederalDistrict_Name']).sum().Event_Count.reset_index()
    return daily_data_for_each_district

