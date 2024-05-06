import numpy as np
import pandas as pd
import plotly.express as px
import dash
import dash_core_components as dcc 
import dash_html_components as html
from dash.dependencies import Input,Output


#------------------------------------------------------------------


df = pd.read_csv("FAO.csv",encoding="ISO-8859-1")
df = df.loc[df["Element"]=="Food"]
df.drop(["Area Abbreviation","Area Code","Item Code","Element Code","Element","Unit"],axis=1,inplace=True)
df.rename(columns={"Area":"Country"},inplace=True)
df.rename(columns=lambda x:x.split("Y")[-1] if x.startswith("Y") else x, inplace=True)
df["Item"].replace("Coconuts - Incl Copra","Coconuts (incl Copra)",inplace=True)
df["Item"].replace("Tea (including mate)","Tea (incl Mate)",inplace=True)
df["Item"].replace("Olives (including preserved)","Olives (incl Preserved)",inplace=True)
df["Item"].replace("Milk - Excluding Butter","Tea Milk (excl Butter)",inplace=True)
df["Item"].replace("Cereals - Excluding Beer","Cereals (excl Beer)",inplace=True)
df["Item"].replace("Fruits - Excluding Wine","Fruits (excl Wine)",inplace=True)
df.fillna(0,inplace=True)
df = df.melt(id_vars=["Country","Item","latitude","longitude"],var_name="Year",value_name="Amount")
df.sort_values(by="Item",inplace=True)


#------------------------------------------------------------------


def draw_map(selected_years):
    df_all = df.groupby(["Country","latitude","longitude","Year"],as_index=False)["Amount"].sum()
    df_all["Year"] = df_all["Year"].astype("int")
    df_all = df_all[(df_all["Year"]>=selected_years[0])&(df_all["Year"]<=selected_years[1])]
    df_all = df_all.groupby(["Country","latitude","longitude"],as_index=False)["Amount"].sum()
    figure = px.scatter_geo(data_frame=df_all,scope="world",lat="latitude",lon="longitude",size="Amount",color="Amount",color_continuous_scale="Blugrn",size_max=40,hover_name="Country",labels={"Amount":"Amount Produced (1000 tonnes)"},hover_data={"latitude":False,"longitude":False})
    figure.update_layout(margin={"t":0,"r":0,"b":0,"l":0})
    figure.update_layout({"plot_bgcolor":"rgba(0,0,0,0)","paper_bgcolor":"rgba(0,0,0,0)"})
    figure.update_layout(font_family="Geneva",font_color="black")
    figure.update_layout(coloraxis_colorbar=dict(xanchor="left",x=0.75))
    return figure


def draw_bar(selected_years,selected_item,clickData):
    df_selected = df.groupby(["Country","Item","latitude","longitude","Year"],as_index=False)["Amount"].sum()
    df_selected["Year"] = df_selected["Year"].astype("int")
    df_selected = df_selected[(df_selected["Year"]>=selected_years[0])&(df_selected["Year"]<=selected_years[1])]
    df_selected = df_selected[df_selected["Item"]==selected_item]
    if clickData is None:
        df_selected = df_selected.groupby(["Year"],as_index=False)["Amount"].sum()
    else:
        df_selected = df_selected[df_selected["Country"]==clickData["points"][0]["hovertext"]]
    figure = px.bar(data_frame=df_selected,x="Year",y="Amount",color="Amount",color_continuous_scale=px.colors.sequential.Blugrn,hover_data={"Year":False},labels={"Amount":"Amount Produced (1000 tonnes)"})
    figure.update_xaxes(tick0=1961,dtick=1)
    figure.update_layout(margin={"t":25,"r":30,"b":60,"l":60})
    figure.update_layout({"plot_bgcolor":"rgba(0,0,0,0)","paper_bgcolor":"rgba(0,0,0,0)"})
    figure.update_layout(font_family="Geneva",font_color="black")
    figure.update_layout(coloraxis_showscale=False)
    return figure


#------------------------------------------------------------------


app = dash.Dash()

app.layout=html.Div([

    html.H1("Ever wonder where your food comes from beyond the supermarket?",
            style={"font-family":"Geneva","font-size":"30px","font-style":"bold","text-align":"center","height":"60px","padding-top":"60px"}),

    html.Div("Select a year or a range of years to view the food production during that period",
             style={"font-family":"Geneva","font-size":"17px","font-style":"italic","text-align":"center","margin-top":"23px"}),

    html.Div([dcc.RangeSlider(id="year_slider",min=1961,max=2013,step=1,marks={1961:"1961",1974:"1974",1987:"1987",2000:"2000",2013:"2013"},value=[1985,2005])],
             style={"width":"70%","margin-left":"auto","margin-right":"auto","margin-top":"10px"}),

    html.Div(id="year_output",
             style={"font-family":"Geneva","font-size":"20px","text-align":"center","margin-top":"10px"}),

    html.Div([dcc.Graph(id="map_figure",figure={})],
             style={"margin-top":"32px","margin-left":"30px","margin-right":"30px"}),

    html.Div("Click a country on the map above and select a food item from each dropdown below",
             style={"font-family":"Geneva","font-size":"17px","font-style":"italic","text-align":"center","margin-top":"20px"}),

    html.Div(id="country_output",
             style={"font-family":"Geneva","font-size":"20px","text-align":"center","margin-top":"20px","margin-bottom":"30px","height":"20px"}),

    html.Div([dcc.Dropdown(id="item1_dropdown",options=[{"label":i,"value":i} for i in df["Item"].unique()],value="Rye and products"),
              dcc.Graph(id="item1_figure",figure={})],
             style={"display":"inline-block","width":"30%","margin-left":"60px","margin-top":"17px","margin-bottom":"50px","font-family":"Geneva"}),

    html.Div([dcc.Dropdown(id="item2_dropdown",options=[{"label":i,"value":i} for i in df["Item"].unique()],value="Cloves"),
              dcc.Graph(id="item2_figure",figure={})],
             style={"display":"inline-block","width":"30%","margin-left":"33px","margin-top":"17px","margin-bottom":"50px","margin-right":"33px","font-family":"Geneva"}),

    html.Div([dcc.Dropdown(id="item3_dropdown",options=[{"label":i,"value":i} for i in df["Item"].unique()],value="Soyabeans"),
              dcc.Graph(id="item3_figure",figure={})],
             style={"display":"inline-block","width":"30%","margin-top":"17px","margin-bottom":"50px","font-family":"Geneva"}),

    html.Div([html.A("view the code",href="https://github.com/gracecmy/FoodProduction-DASHboard/blob/main/fao.py",target="_blank")],
             style={"font-family":"Geneva","font-size":"15px","text-align":"right"})

],style={"background-color":"#f8f9fa"})


#------------------------------------------------------------------


@app.callback(
    Output(component_id="year_output",component_property="children"),
    [Input(component_id="year_slider",component_property="value")])
def update_year_output(selected_years):
    container = "You have chosen {year1} to {year2}".format(year1=selected_years[0],year2=selected_years[1])
    return container


@app.callback(
    Output(component_id="map_figure",component_property="figure"),
    [Input(component_id="year_slider",component_property="value")])
def update_map_figure(selected_years):
    figure_map = draw_map(selected_years)
    return figure_map


@app.callback(
    Output(component_id="country_output",component_property="children"),
    [Input(component_id="map_figure",component_property="clickData")])
def update_country_output(clickData):
    if clickData is None:
        container = "You have not chosen a country so the below graphs are displaying worldwide production"
        return container
    else:
        container = "You have chosen {country}".format(country=clickData["points"][0]["hovertext"])
        return container


@app.callback(
    Output(component_id="item1_figure",component_property="figure"),
    [Input(component_id="year_slider",component_property="value"),
     Input(component_id="item1_dropdown",component_property="value"),
     Input(component_id="map_figure",component_property="clickData")])
def update_item1_figure(selected_years,selected_item,clickData):
    figure_item1 = draw_bar(selected_years,selected_item,clickData)
    return figure_item1


@app.callback(
    Output(component_id="item2_figure",component_property="figure"),
    [Input(component_id="year_slider",component_property="value"),
     Input(component_id="item2_dropdown",component_property="value"),
     Input(component_id="map_figure",component_property="clickData")])
def update_item2_figure(selected_years,selected_item,clickData):
    figure_item2 = draw_bar(selected_years,selected_item,clickData)
    return figure_item2


@app.callback(
    Output(component_id="item3_figure",component_property="figure"),
    [Input(component_id="year_slider",component_property="value"),
     Input(component_id="item3_dropdown",component_property="value"),
     Input(component_id="map_figure",component_property="clickData")])
def update_item3_figure(selected_years,selected_item,clickData):
    figure_item3 = draw_bar(selected_years,selected_item,clickData)
    return figure_item3


if __name__ == "__main__":
    app.run_server(debug=True)
