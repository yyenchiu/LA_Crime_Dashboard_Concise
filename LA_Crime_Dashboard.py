import numpy as np
import pandas as pd
import json

pd.set_option('display.max_columns', None)

import plotly.graph_objects as go
import plotly.express as px
from wordcloud import WordCloud as wc

import dash
from dash import dcc
import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Input, Output

import time

external_stylesheets = {
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'}

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# bootstrap themes: bootswatch.com

# ---------------------------------------------------------------------------------------
# Import cleaned data

arrest_clean_a = pd.read_csv("arrest_clean_a.csv", index_col=0)
arrest_clean_b = pd.read_csv("arrest_clean_b.csv", index_col=0)
arrest_clean_c = pd.read_csv("arrest_clean_c.csv", index_col=0)
arrest_clean_d = pd.read_csv("arrest_clean_d.csv", index_col=0)
arrest_clean_e = pd.read_csv("arrest_clean_e.csv", index_col=0)
arrest_clean_f = pd.read_csv("arrest_clean_f.csv", index_col=0)
arrest_clean_g = pd.read_csv("arrest_clean_g.csv", index_col=0)
arrest_clean_h = pd.read_csv("arrest_clean_h.csv", index_col=0)

map_info = pd.read_csv("map_info_more_detailed_present.csv")
map_gj = json.load(open("LAPD_Divisions.geojson", "r"))

arrest_clean = pd.concat([arrest_clean_a, arrest_clean_b, arrest_clean_c, arrest_clean_d,
                         arrest_clean_e, arrest_clean_f, arrest_clean_g, arrest_clean_h], axis=1)

arrest_clean["AREA_NAME"] = arrest_clean.AREA_NAME.apply(lambda x: x.upper())
arrest_clean.replace({"WEST LA": "WEST LOS ANGELES", "N HOLLYWOOD": "NORTH HOLLYWOOD"}, inplace=True)

area_id_map = {}
for feature in map_gj["features"]:
    feature["id"] = feature["properties"]["PREC"]
    area_id_map[feature["properties"]["APREC"]] = feature["id"]

map_info["id"] = map_info["AREA_NAME"].apply(lambda x: area_id_map[x])

# ---------------------------------------------------------------------------------------
# App layout
app.layout = html.Div([

    html.Div([html.H1("Criminal Activity in LA City 2018-2023", style={"text-align": "center"}),
              dcc.Dropdown(id="select_cat",
                           options=[
                               {"label": "Arrests", "value": "Arrests"},
                               {"label": "Arrests_Per_10k_Pop", "value": "Arrests_Per_10k_Pop"},
                               {"label": "Arrests_Per_SqMile", "value": "Arrests_Per_SqMile"}],
                           multi=False,
                           value="Arrests",
                           style={"width": "40%"}
                           ),
              dcc.Dropdown(id="select_group",
                           options=[
                               {"label": "Against Family/Child", "value": "Against Family/Child"},
                               {"label": "Aggravated Assault", "value": "Aggravated Assault"},
                               {"label": "Burglary", "value": "Burglary"},
                               {"label": "Disorderly Conduct", "value": "Disorderly Conduct"},
                               {"label": "Disturbing the Peace", "value": "Disturbing the Peace"},
                               {"label": "Driving Under Influence", "value": "Driving Under Influence"},
                               {"label": "Drunkeness", "value": "Drunkeness"},
                               {"label": "Federal Offenses", "value": "Federal Offenses"},
                               {"label": "Forgery/Counterfeit", "value": "Forgery/Counterfeit"},
                               {"label": "Fraud/Embezzlement", "value": "Fraud/Embezzlement"},
                               {"label": "Gambling", "value": "Gambling"},
                               {"label": "Homicide", "value": "Homicide"},
                               {"label": "Larceny", "value": "Larceny"},
                               {"label": "Liquor Laws", "value": "Liquor Laws"},
                               {"label": "Miscellaneous Other Violations", "value": "Miscellaneous Other Violations"},
                               {"label": "Moving Traffic Violations", "value": "Moving Traffic Violations"},
                               {"label": "Narcotic Drug Laws", "value": "Narcotic Drug Laws"},
                               {"label": "Non-Criminal Detention", "value": "Non-Criminal Detention"},
                               {"label": "Other Assaults", "value": "Other Assaults"},
                               {"label": "Pre-Delinquency", "value": "Pre-Delinquency"},
                               {"label": "Prostitution/Allied", "value": "Prostitution/Allied"},
                               {"label": "Rape", "value": "Rape"},
                               {"label": "Receive Stolen Property", "value": "Receive Stolen Property"},
                               {"label": "Robbery", "value": "Robbery"},
                               {"label": "Sex (except rape/prst)", "value": "Sex (except rape/prst)"},
                               {"label": "Unknown", "value": "Unknown"},
                               {"label": "Vehicle Theft", "value": "Vehicle Theft"},
                               {"label": "Weapon (carry/poss)", "value": "Weapon (carry/poss)"}],
                           multi=True,
                           value=map_info["CRIME_GROUP"].unique()
                           ),
              html.Br(),
              dcc.RangeSlider(2018, 2023, 1, count=1,
                              marks={2018: "2018",
                                     2019: "2019",
                                     2020: "2020",
                                     2021: "2021",
                                     2022: "2022",
                                     2023: "2023"},
                              value=[2018, 2023], id="select_year"),

              html.Div(id="title_one", children=[],
                       style={"text-align": "center"}),
              ]),
    html.Div(
        [
           dbc.Row(
               dbc.Stack(
                   [
                       dcc.Graph(id="bar_total", figure={}, style={"width": "30%"}),
                       dcc.Graph(id="my_map", figure={}, style={"width": "40%"}),
                       dcc.Graph(id="bar_pct", figure={}, style={"width": "30%"})
                   ],
                   direction="horizontal"
               ),
               align="start"
           ),
            dbc.Row(html.Div(id="title_two", children=[],
                     style={"text-align": "center"})
                   ),
            dbc.Row(
                dbc.Stack(
                    [
                        dcc.Graph(id="g1", figure={}, style={"width": "33%"}),
                        dcc.Graph(id="g2", figure={}, style={"width": "33%"}),
                        dcc.Graph(id="g3", figure={}, style={"width": "33%"})
                    ],
                    direction="horizontal"
                ),
                align="start"
           ),
            dbc.Row(html.Div(dcc.Graph(id="g4", figure={}))),
            dbc.Row(
                dbc.Stack(
                    [
                        dcc.Graph(id="g5", figure={}, style={"width": "60%"}),
                        dcc.Graph(id="g6", figure={}, style={"width": "40%"})
                    ],
                    direction="horizontal"
                ),
                align="start"
           ),
        ]
    )
])


# ---------------------------------------------------------------------------------------
# Connect Plotly graphs with Dash Components
@app.callback(
    [Output(component_id="title_one", component_property="children"),
     Output(component_id="my_map", component_property="figure"),
     Output(component_id="bar_total", component_property="figure"),
     Output(component_id="bar_pct", component_property="figure"),
     Output(component_id="title_two", component_property="children"),
     Output(component_id="g1", component_property="figure"),
     Output(component_id="g2", component_property="figure"),
     Output(component_id="g3", component_property="figure"),
     Output(component_id="g4", component_property="figure"),
     Output(component_id="g5", component_property="figure"),
     Output(component_id="g6", component_property="figure")],
    Input(component_id="select_cat", component_property="value"),
    Input(component_id="select_year", component_property="value"),
    Input(component_id="select_group", component_property="value"),
    Input(component_id="my_map", component_property="clickData")
)
def generate_graph(cat_selected, year_selected, group_selected, clickData):

    container1 = f"Data: {cat_selected} in LA from {year_selected[0]} to {year_selected[1]}"
    
    if clickData is None:
        area = "TOPANGA"
    else:
        area = json.loads(json.dumps(clickData))["points"][0]["hovertext"]

    container2 = f"Data: {cat_selected} in {area} from {year_selected[0]} to {year_selected[1]}"

    filtered = map_info[(map_info["YEAR"] >= year_selected[0]) & (map_info["YEAR"] <= year_selected[1])
                & (map_info["CRIME_GROUP"].isin(group_selected))]
    cur_group = filtered.groupby(["AREA_NAME", "id", "SqMile", "Population"]).aggregate(
        {"Arrests": "sum", "Reports": "sum", "Arrests_Per_SqMile": "sum", "Arrests_Per_10k_Pop": "sum",
         "Reports_Per_SqMile": "sum", "Reports_Per_10k_Pop": "sum"}).reset_index()

    hover = ["Population", "SqMile"]
    hover.append(cat_selected)

    bar_total = pd.DataFrame(filtered.groupby("AREA_NAME")[cat_selected].sum()).reset_index()

    fig1 = px.choropleth_mapbox(cur_group,
                               locations="id",
                               geojson=map_gj,
                               color=cat_selected,
                               hover_name="AREA_NAME",
                               hover_data={"id": False,
                                           "Population": True,
                                           "SqMile": True,
                                           cat_selected: ":.2f"
                                           },
                               title="Regional Data",
                               mapbox_style="open-street-map",
                               center={"lat": 34, "lon": -118.5},
                               zoom=8,
                               opacity=0.7,
                               color_continuous_scale="thermal"
                               )
    fig1.update_layout(title_x=0.5, title_xanchor="center")
    
    fig2 = px.bar(bar_total,
                 x=cat_selected,
                 y="AREA_NAME",
                 title=f"Total {cat_selected}")

    fig2.update_layout(title_x=0.5, title_xanchor="center")

    grp_start = map_info[(map_info["YEAR"] == year_selected[0]) &
                         (map_info["CRIME_GROUP"].isin(group_selected))].groupby(
        ["AREA_NAME"]).agg({cat_selected: "sum"})

    grp_end = map_info[(map_info["YEAR"] == year_selected[1]) &
                       (map_info["CRIME_GROUP"].isin(group_selected))].groupby(
        ["AREA_NAME"]).agg({cat_selected: "sum"})

    change = pd.DataFrame(round((grp_end[cat_selected] - grp_start[cat_selected]) / 
                                grp_start[cat_selected] * 100, 2)).reset_index()
    change["colors"] = ""
    for i in range(len(change)):
        if change.loc[i, cat_selected] > 0:
            change.loc[i, "colors"] = "Red"
        else:
            change.loc[i, "colors"] = "Blue"

    fig3 = go.Figure(data=(go.Bar(
        x=change[cat_selected],
        y=change["AREA_NAME"],
        marker_color=change["colors"],
        orientation="h",
        hoverinfo="text+x")),
        layout=(go.Layout(
            title=f"% Change in Annual {cat_selected}",
            xaxis={"title": "% Decrease/Increase"},
            yaxis={"title": "Area Name"}
        )))

    fig3.update_layout(title_x=0.5, title_xanchor="center")
    
    df = arrest_clean

    # Fiilter data
    df_filtered = pd.DataFrame(df[(df["AREA_NAME"] == area) & (df["YEAR"] >= year_selected[0]) &
                                 (df["YEAR"] <= year_selected[1]) & (df["CRIME_GROUP"].isin(group_selected))])


    # Histogram showing age and sex
    fig4 = px.histogram(df_filtered,
                       x="AGE",
                       color="SEX",
                       pattern_shape="AGE_GROUP",
                       color_discrete_map={"M": "blue", "F": "red"},
                       barmode="overlay",
                       opacity=0.75,
                       title="Age Distribution by Sex",
                       )

    fig4.update_layout(title_x=0.5, title_xanchor="center",
                       legend={"yanchor": "top", "xanchor": "right"})


    # Histogram showing time of day
    fig5 = px.histogram(df_filtered,
                       x="TIME",
                       color="DAY_NIGHT",
                       color_discrete_sequence=["blue", "red"],
                       nbins=72,
                       title="Time Distribution",
                       )

    fig5.update_layout(title_x=0.5, title_xanchor="center",
                       legend={"yanchor": "top", "xanchor": "right"})


    # Histogram showing day of week
    df_bar_weekday = pd.DataFrame(df_filtered.groupby("WEEKDAY")["ID"].count()).rename(columns={"ID": "COUNT"}).sort_values("COUNT").reset_index()
    fig6 = px.bar(df_bar_weekday,
                 x="WEEKDAY",
                 y="COUNT",
                 title="Weekdays Distribution")

    fig6.update_layout(title_x=0.5, title_xanchor="center")

    fig6.update_xaxes(tickmode="array",
                     tickvals=np.arange(1, 8),
                     ticktext=["Mon", "Tues", "Wed", "Thurs", "Fri", "Sat", "Sun"])


    # Line chart for change in months

    df_filtered["DATE"] = pd.to_datetime(df_filtered["DATE"])
    df_month = pd.DataFrame(df_filtered.groupby("DATE")["ID"].count())
    df_month = pd.DataFrame(df_month["ID"].resample("M").sum()).reset_index().rename(columns={"ID": "COUNT"})
    fig7 = px.line(df_month,
                  x="DATE",
                  y="COUNT",
                  title="Monthly Total")

    fig7.update_layout(title_x=0.5, title_xanchor="center")

    # Bar graph of crime groups
    df_bar = pd.DataFrame(df_filtered.groupby("CRIME_GROUP")["ID"].count()).rename(columns={"DATE": "MONTH", "ID": "COUNT"}).sort_values(
        "COUNT").reset_index()
    total = df_bar["COUNT"].sum()
    df_bar["PERCENTAGE"] = ""
    df_bar.PERCENTAGE = round(df_bar.COUNT / total * 100, 2)

    fig8 = px.bar(df_bar,
                 x="COUNT",
                 y="CRIME_GROUP",
                 title="Crime Group Distribution",
                 hover_name="CRIME_GROUP",
                 hover_data={"CRIME_GROUP": True,
                             "COUNT": True,
                             "PERCENTAGE": True
                             }
                 )
    fig8.update_layout(title_x=0.5, title_xanchor="center")


    # Word cloud of specific crimes

    f = df_filtered["CHARGE_DESCRIPTION"].value_counts()
    wordcloud = wc(width = 2000, height = 1000, colormap="GnBu").generate_from_frequencies(f[f > 200])

    fig9 = px.imshow(wordcloud, title="Most Common Incident Descriptions")
    fig9.update_traces(hovertemplate=None,
                      hoverinfo="skip")
    fig9.update_xaxes(visible=False)
    fig9.update_yaxes(visible=False)
    
    return container1, fig1, fig2, fig3, container2, fig4, fig5, fig6, fig7, fig8, fig9

if __name__ == "__main__":
    app.run_server(debug=False)
