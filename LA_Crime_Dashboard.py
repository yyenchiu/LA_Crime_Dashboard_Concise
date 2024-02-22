import numpy as np
import pandas as pd
import json

pd.set_option('display.max_columns', None)

import plotly.graph_objects as go
import plotly.express as px
from wordcloud import WordCloud as wc

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

external_stylesheets = {
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'}

app = dash.Dash(__name__)
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

arrest_clean = pd.read_csv("arrest_present_clean.csv")
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

    html.Div([html.H1("Criminal Activity in LA City 2016-Present", style={"text-align": "center"}),
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
              dcc.RangeSlider(2016, 2023, 1, count=1,
                              marks={2016: "2016",
                                     2017: "2017",
                                     2018: "2018",
                                     2019: "2019",
                                     2020: "2020",
                                     2021: "2021",
                                     2022: "2022",
                                     2023: "2023"},
                              value=[2016, 2023], id="select_year"),

              html.Div(id="title_one", children=[],
                       style={"text-align": "center"}),
              ]),
    html.Div([
        html.Div([
            dcc.Graph(id="bar_total", figure={},
                      style={"height": 600})
        ], className="three columns"),
        html.Div([
            dcc.Graph(id="my_map", figure={},
                      style={"height": 600})
        ], className="six columns"),
        # "six columns" explained at https://community.plotly.com/t/not-really-getting-the-six-columns-thing/38751
        html.Div([
            dcc.Graph(id="bar_pct", figure={},
                      style={"height": 600})
        ], className="three columns"),
    ], className="row"),

    html.Div(id="title_two", children=[],
             style={"text-align": "center"}),
    html.Div([
        html.Div([
            dcc.Graph(id="g1", figure={}, style={"height": 600})
            ], className="four columns"),
        html.Div([
            dcc.Graph(id="g2", figure={}, style={"height": 600})
        ], className="four columns"),
        html.Div([
            dcc.Graph(id="g3", figure={}, style={"height": 600})
        ], className="four columns")], className="row"),

    html.Div([
        dcc.Graph(id="g4", figure={}, style={"height": 600})
    ]),
    html.Div([
        html.Div([
            dcc.Graph(id="g5", figure={}, style={"height": 600})
        ], className="eight columns"),
        html.Div([
            dcc.Graph(id="g6", figure={}, style={"height": 600})
        ], className="four columns")], className="row")

])


# ---------------------------------------------------------------------------------------
# Connect Plotly graphs with Dash Components
@app.callback(
    [Output(component_id="title_one", component_property="children"),
     Output(component_id="my_map", component_property="figure")],
    Input(component_id="select_cat", component_property="value"),
    Input(component_id="select_year", component_property="value"),
    Input(component_id="select_group", component_property="value"),
    Input(component_id="my_map", component_property="clickData")
)
def generate_graph(cat_selected, year_selected, group_selected, clickData):

    container = f"Data: {cat_selected} in LA from {year_selected[0]} to {year_selected[1]}"

    cur_group = map_info[(map_info["YEAR"] >= year_selected[0]) &
                         (map_info["YEAR"] <= year_selected[1]) &
                         (map_info["CRIME_GROUP"].isin(group_selected))].groupby(
        ["AREA_NAME", "id", "SqMile", "Population"]).aggregate(
        {"Arrests": "sum", "Reports": "sum", "Arrests_Per_SqMile": "sum", "Arrests_Per_10k_Pop": "sum",
         "Reports_Per_SqMile": "sum", "Reports_Per_10k_Pop": "sum"}).reset_index()

    hover = ["Population", "SqMile"]
    hover.append(cat_selected)

    fig = px.choropleth_mapbox(cur_group,
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
                               zoom=8.3,
                               opacity=0.7,
                               color_continuous_scale="thermal"
                               )
    fig.update_layout(title_x=0.5, title_xanchor="center")
    return container, fig


@app.callback(
    Output(component_id="bar_total", component_property="figure"),
    Output(component_id="bar_pct", component_property="figure"),
    Input(component_id="select_cat", component_property="value"),
    Input(component_id="select_year", component_property="value"),
    Input(component_id="select_group", component_property="value")
)
def generate_bar_pct_change(cat_selected, year_selected, group_selected):
    cat = cat_selected
    start = year_selected[0]
    end = year_selected[1]

    filtered = map_info[(map_info["YEAR"] >= start) & (map_info["YEAR"] <= end)
                        & (map_info["CRIME_GROUP"].isin(group_selected))]
    bar_total = pd.DataFrame(filtered.groupby("AREA_NAME")[cat].sum()).reset_index()

    fig1 = px.bar(bar_total,
                 x=cat,
                 y="AREA_NAME",
                 title=f"Total {cat}")

    fig1.update_layout(title_x=0.5, title_xanchor="center")

    grp_start = map_info[(map_info["YEAR"] == start) &
                         (map_info["CRIME_GROUP"].isin(group_selected))].groupby(
        ["AREA_NAME"]).agg({cat: "sum"})

    grp_end = map_info[(map_info["YEAR"] == end) &
                       (map_info["CRIME_GROUP"].isin(group_selected))].groupby(
        ["AREA_NAME"]).agg({cat: "sum"})

    change = pd.DataFrame(round((grp_end[cat] - grp_start[cat]) / grp_start[cat] * 100, 2)).reset_index()
    change["colors"] = ""
    for i in range(len(change)):
        if change.loc[i, cat] > 0:
            change.loc[i, "colors"] = "Red"
        else:
            change.loc[i, "colors"] = "Blue"

    # print(change)

    fig2 = go.Figure(data=(go.Bar(
        x=change[cat],
        y=change["AREA_NAME"],
        marker_color=change["colors"],
        orientation="h",
        hoverinfo="text+x")),
        layout=(go.Layout(
            title=f"% Change in Annual {cat}",
            xaxis={"title": "% Decrease/Increase"},
            yaxis={"title": "Area Name"}
        )))

    fig2.update_layout(title_x=0.5, title_xanchor="center")

    return fig1, fig2


@app.callback(
    Output(component_id="title_two", component_property="children"),
    Input(component_id="select_cat", component_property="value"),
    Input(component_id="select_year", component_property="value"),
    Input(component_id="my_map", component_property="clickData")
)
def generate_title_two(cat_selected, year_selected, clickData):
    if clickData is None:
        area = "TOPANGA"
    else:
        area = json.loads(json.dumps(clickData))["points"][0]["hovertext"]

    cat = cat_selected

    container = f"Data: {cat} in {area} from {year_selected[0]} to {year_selected[1]}"

    return container


@app.callback(
    Output(component_id="g1", component_property="figure"),
    Output(component_id="g2", component_property="figure"),
    Output(component_id="g3", component_property="figure"),
    Output(component_id="g4", component_property="figure"),
    Output(component_id="g5", component_property="figure"),
    Output(component_id="g6", component_property="figure"),
    Input(component_id="select_cat", component_property="value"),
    Input(component_id="select_year", component_property="value"),
    Input(component_id="my_map", component_property="clickData"),
    Input(component_id="select_group", component_property="value")
)
def generate_graphs(cat_selected, year_selected, clickData, group_selected):

    # Create filter params
    if clickData is None:
        area = "TOPANGA"
    else:
        area = json.loads(json.dumps(clickData))["points"][0]["hovertext"]

    df = arrest_clean

    # Fiilter data
    df_filtered = pd.DataFrame(df[(df["AREA_NAME"] == area) & (df["YEAR"] >= year_selected[0]) &
                                 (df["YEAR"] <= year_selected[1]) & (df["CRIME_GROUP"].isin(group_selected))])


    # Histogram showing age and sex
    fig1 = px.histogram(df_filtered,
                       x="AGE",
                       color="SEX",
                       pattern_shape="AGE_GROUP",
                       color_discrete_map={"M": "blue", "F": "red"},
                       barmode="overlay",
                       opacity=0.75,
                       title="Age Distribution by Sex",
                       )

    fig1.update_layout(title_x=0.5, title_xanchor="center",
                       legend={"yanchor": "top", "xanchor": "right"})


    # Histogram showing time of day
    fig2 = px.histogram(df_filtered,
                       x="TIME",
                       color="DAY_NIGHT",
                       color_discrete_sequence=["blue", "red"],
                       nbins=72,
                       title="Time Distribution",
                       )

    fig2.update_layout(title_x=0.5, title_xanchor="center",
                       legend={"yanchor": "top", "xanchor": "right"})


    # Histogram showing day of week
    df_bar_weekday = pd.DataFrame(df_filtered.groupby("WEEKDAY")["ID"].count()).rename(columns={"ID": "COUNT"}).sort_values("COUNT").reset_index()
    fig3 = px.bar(df_bar_weekday,
                 x="WEEKDAY",
                 y="COUNT",
                 title="Weekdays Distribution")

    fig3.update_layout(title_x=0.5, title_xanchor="center")

    fig3.update_xaxes(tickmode="array",
                     tickvals=np.arange(1, 8),
                     ticktext=["Mon", "Tues", "Wed", "Thurs", "Fri", "Sat", "Sun"])


    # Line chart for change in months

    df_filtered["DATE"] = pd.to_datetime(df_filtered["DATE"])
    df_month = pd.DataFrame(df_filtered.groupby("DATE")["ID"].count())
    df_month = pd.DataFrame(df_month["ID"].resample("M").sum()).reset_index().rename(columns={"ID": "COUNT"})
    fig4 = px.line(df_month,
                  x="DATE",
                  y="COUNT",
                  title="Monthly Total")

    fig4.update_layout(title_x=0.5, title_xanchor="center")

    # Bar graph of crime groups
    df_bar = pd.DataFrame(df_filtered.groupby("CRIME_GROUP")["ID"].count()).rename(columns={"DATE": "MONTH", "ID": "COUNT"}).sort_values(
        "COUNT").reset_index()
    total = df_bar["COUNT"].sum()
    df_bar["PERCENTAGE"] = ""
    df_bar.PERCENTAGE = round(df_bar.COUNT / total * 100, 2)

    fig5 = px.bar(df_bar,
                 x="COUNT",
                 y="CRIME_GROUP",
                 title="Crime Group Distribution",
                 hover_name="CRIME_GROUP",
                 hover_data={"CRIME_GROUP": True,
                             "COUNT": True,
                             "PERCENTAGE": True
                             }
                 )
    fig5.update_layout(title_x=0.5, title_xanchor="center")


    # Word cloud of specific crimes

    f = df_filtered["CHARGE_DESCRIPTION"].value_counts()
    wordcloud = wc(width = 2000, height = 1000, colormap="GnBu").generate_from_frequencies(f[f > 200])

    fig6 = px.imshow(wordcloud, title="Most Common Incident Descriptions")
    fig6.update_traces(hovertemplate=None,
                      hoverinfo="skip")
    fig6.update_xaxes(visible=False)
    fig6.update_yaxes(visible=False)

    return fig1, fig2, fig3, fig4, fig5, fig6


if __name__ == "__main__":
    app.run_server(debug=False)
