import numpy as np
import pandas as pd
import plotly.express as px
import dash
import dash_core_components as dcc 
import dash_html_components as html
from dash.dependencies import Input,Output

#------------------------------------------------------------------

#the data
df=pd.read_csv("FAO.csv",encoding="ISO-8859-1")
df=df.loc[df["Element"]=="Food"]
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
df=df.melt(id_vars=["Country","Item","latitude","longitude"],var_name="Year",value_name="Amount")

#------------------------------------------------------------------

#the app
app=dash.Dash()
server=app.server

app.layout=html.Div([
    html.H1("How much food?",
            style={"font-family":"Verdana","text-align":"center","height":"50px","padding-top":"40px"}),

    html.Div("As the global population rises and food security becomes more pressing due to climate change, are we producing enough food to sustain us?",
             style={"font-family":"Verdana","text-align":"center","width":"85%","margin-left":"auto","margin-right":"auto"}),

    html.Div("Select a year or a range of years to view food production during that period",
             style={"font-family":"Verdana","font-size":"13px","font-style":"italic","text-align":"center","margin-top":"20px"}),   

    html.Div([dcc.RangeSlider(id="year_slider",min=1961,max=2013,step=1,marks={1961:"1961",1974:"1974",1987:"1987",2000:"2000",2013:"2013"},value=[1985,2005])],
             style={"width":"70%","margin-left":"auto","margin-right":"auto","margin-top":"10px"}),

    html.Div(id="year_output",
             style={"font-family":"Verdana","font-size":"15px","text-align":"center","margin-top":"10px"}),

    html.Div([dcc.Graph(id="map_figure",figure={})],
             style={"margin-top":"15px","margin-left":"30px","margin-right":"30px"}),

    html.Div("Click a country on the map and select a food item from each dropdown",
             style={"font-family":"Verdana","font-size":"13px","font-style":"italic","text-align":"center","margin-top":"20px"}),

    html.Div(id="country_output",
             style={"font-family":"Verdana","font-size":"15px","text-align":"center","margin-top":"10px","height":"20px"}),

    html.Div([dcc.Dropdown(id="first_item_dropdown",options=[{"label":i,"value":i} for i in df["Item"].unique()],value="Eggs"),
              dcc.Graph(id="item1_figure",figure={})],
             style={"display":"inline-block","width":"30%","margin-left":"60px","margin-top":"10px","margin-bottom":"50px"}),

    html.Div([dcc.Dropdown(id="second_item_dropdown",options=[{"label":i,"value":i} for i in df["Item"].unique()],value="Poultry Meat"),
              dcc.Graph(id="item2_figure",figure={})],
             style={"display":"inline-block","width":"30%","margin-top":"10px","margin-bottom":"50px"}),

    html.Div([dcc.Dropdown(id="third_item_dropdown",options=[{"label":i,"value":i} for i in df["Item"].unique()],value="Wine"),
              dcc.Graph(id="item3_figure",figure={})],
             style={"display":"inline-block","width":"30%","margin-top":"10px","margin-bottom":"50px"})

],style={"background-color":"lavenderblush"})


@app.callback(
    Output(component_id="year_output",component_property="children"),
    [Input(component_id="year_slider",component_property="value")])
def update_year_output(selected_years):
    container="You have chosen {year1} to {year2}".format(year1=selected_years[0],year2=selected_years[1])
    return container


@app.callback(
    Output(component_id="map_figure",component_property="figure"),
    [Input(component_id="year_slider",component_property="value")])
def update_map_figure(selected_years):
    if selected_years==[1985,2005]:
        df_allitems=df.groupby(["Country","latitude","longitude","Year"],as_index=False)["Amount"].sum()
        df_allitems["Year"]=df_allitems["Year"].astype("int")
        df_allitems=df_allitems[(df_allitems["Year"]>=1985)&(df_allitems["Year"]<=2005)]
        df_allitems=df_allitems.groupby(["Country","latitude","longitude"],as_index=False)["Amount"].sum()
        figure_map=px.scatter_geo(data_frame=df_allitems,scope="world",lat="latitude",lon="longitude",size="Amount",color="Amount",color_continuous_scale="pinkyl",size_max=40,hover_name="Country",labels={"Amount":"Amount Produced (1000 tonnes)"},hover_data={"latitude":False,"longitude":False})
        figure_map.update_layout(margin={"t":0,"r":0,"b":0,"l":0})
        figure_map.update_layout({"plot_bgcolor":"rgba(0,0,0,0)","paper_bgcolor":"rgba(0,0,0,0)"})  
        return figure_map
    else:
        df_allitems=df.groupby(["Country","latitude","longitude","Year"],as_index=False)["Amount"].sum()
        df_allitems["Year"]=df_allitems["Year"].astype("int")
        df_allitems=df_allitems[(df_allitems["Year"]>=selected_years[0])&(df_allitems["Year"]<=selected_years[1])]
        df_allitems=df_allitems.groupby(["Country","latitude","longitude"],as_index=False)["Amount"].sum()
        figure_map=px.scatter_geo(data_frame=df_allitems,scope="world",lat="latitude",lon="longitude",size="Amount",color="Amount",color_continuous_scale="pinkyl",size_max=40,hover_name="Country",labels={"Amount":"Amount Produced (1000 tonnes)"},hover_data={"latitude":False,"longitude":False})
        figure_map.update_layout(margin={"t":0,"r":0,"b":0,"l":0})
        figure_map.update_layout({"plot_bgcolor":"rgba(0,0,0,0)","paper_bgcolor":"rgba(0,0,0,0)"})
        return figure_map


@app.callback(
    Output(component_id="country_output",component_property="children"),
    [Input(component_id="map_figure",component_property="clickData")])
def update_country_output(clickData):
    if clickData is None:
        container="You have not chosen a country so the below graphs are displaying worldwide production"
        return container
    else:
        container="You have chosen {country}".format(country=clickData["points"][0]["hovertext"])
        return container


@app.callback(
    Output(component_id="item1_figure",component_property="figure"),
    [Input(component_id="year_slider",component_property="value"),
     Input(component_id="first_item_dropdown",component_property="value"),
     Input(component_id="map_figure",component_property="clickData")])
def update_item1_figure(selected_years,selected_item,clickData):
    if clickData is None:
        df_items=df.groupby(["Country","Item","latitude","longitude","Year"],as_index=False)["Amount"].sum()
        df_items["Year"]=df_items["Year"].astype("int")
        df_items=df_items[(df_items["Year"]>=selected_years[0])&(df_items["Year"]<=selected_years[1])]
        df_items=df_items[df_items["Item"]==selected_item]
        df_items.groupby(["Year"],as_index=False)["Amount"].sum()
        figure_item1=px.bar(data_frame=df_items,x="Year",y="Amount",color_discrete_sequence=["lightskyblue"],labels={"Amount":"Amount Produced (1000 tonnes)"})
        figure_item1.update_xaxes(tick0=1961,dtick=1)
        figure_item1.update_layout(margin={"t":25,"r":30,"b":60,"l":60})
        figure_item1.update_layout({"plot_bgcolor":"rgba(0,0,0,0)","paper_bgcolor":"rgba(0,0,0,0)"})
        return figure_item1      
    else:
        df_items=df.groupby(["Country","Item","latitude","longitude","Year"],as_index=False)["Amount"].sum()
        df_items["Year"]=df_items["Year"].astype("int")
        df_items=df_items[(df_items["Year"]>=selected_years[0])&(df_items["Year"]<=selected_years[1])]
        df_items=df_items[df_items["Item"]==selected_item]
        country_name=clickData["points"][0]["hovertext"]
        df_items=df_items[df_items["Country"]==country_name]
        figure_item1=px.bar(data_frame=df_items,x="Year",y="Amount",color_discrete_sequence=["lightskyblue"],labels={"Amount":"Amount Produced (1000 tonnes)"})
        figure_item1.update_xaxes(tick0=1961,dtick=1)
        figure_item1.update_layout(margin={"t":25,"r":30,"b":60,"l":60})
        figure_item1.update_layout({"plot_bgcolor":"rgba(0,0,0,0)","paper_bgcolor":"rgba(0,0,0,0)"})
        return figure_item1


@app.callback(
    Output(component_id="item2_figure",component_property="figure"),
    [Input(component_id="year_slider",component_property="value"),
     Input(component_id="second_item_dropdown",component_property="value"),
     Input(component_id="map_figure",component_property="clickData")])
def update_item2_figure(selected_years,selected_item,clickData):
    if clickData is None:
        df_items=df.groupby(["Country","Item","latitude","longitude","Year"],as_index=False)["Amount"].sum()
        df_items["Year"]=df_items["Year"].astype("int")
        df_items=df_items[(df_items["Year"]>=selected_years[0])&(df_items["Year"]<=selected_years[1])]
        df_items=df_items[df_items["Item"]==selected_item]
        df_items.groupby(["Year"],as_index=False)["Amount"].sum()
        figure_item2=px.bar(data_frame=df_items,x="Year",y="Amount",color_discrete_sequence=["turquoise"],labels={"Amount":"Amount Produced (1000 tonnes)"})
        figure_item2.update_xaxes(tick0=1961,dtick=1)
        figure_item2.update_layout(margin={"t":25,"r":30,"b":60,"l":60})
        figure_item2.update_layout({"plot_bgcolor":"rgba(0,0,0,0)","paper_bgcolor":"rgba(0,0,0,0)"})
        return figure_item2 
    else:
        df_items=df.groupby(["Country","Item","latitude","longitude","Year"],as_index=False)["Amount"].sum()
        df_items["Year"]=df_items["Year"].astype("int")
        df_items=df_items[(df_items["Year"]>=selected_years[0])&(df_items["Year"]<=selected_years[1])]
        df_items=df_items[df_items["Item"]==selected_item]
        country_name=clickData["points"][0]["hovertext"]
        df_items=df_items[df_items["Country"]==country_name]
        figure_item2=px.bar(data_frame=df_items,x="Year",y="Amount",color_discrete_sequence=["turquoise"],labels={"Amount":"Amount Produced (1000 tonnes)"})
        figure_item2.update_xaxes(tick0=1961,dtick=1)
        figure_item2.update_layout(margin={"t":25,"r":30,"b":60,"l":60})
        figure_item2.update_layout({"plot_bgcolor":"rgba(0,0,0,0)","paper_bgcolor":"rgba(0,0,0,0)"})
        return figure_item2


@app.callback(
    Output(component_id="item3_figure",component_property="figure"),
    [Input(component_id="year_slider",component_property="value"),
     Input(component_id="third_item_dropdown",component_property="value"),
     Input(component_id="map_figure",component_property="clickData")])
def update_item3_figure(selected_years,selected_item,clickData):
    if clickData is None:
        df_items=df.groupby(["Country","Item","latitude","longitude","Year"],as_index=False)["Amount"].sum()
        df_items["Year"]=df_items["Year"].astype("int")
        df_items=df_items[(df_items["Year"]>=selected_years[0])&(df_items["Year"]<=selected_years[1])]
        df_items=df_items[df_items["Item"]==selected_item]
        df_items.groupby(["Year"],as_index=False)["Amount"].sum()
        figure_item3=px.bar(data_frame=df_items,x="Year",y="Amount",color_discrete_sequence=["aquamarine"],labels={"Amount":"Amount Produced (1000 tonnes)"})
        figure_item3.update_xaxes(tick0=1961,dtick=1)
        figure_item3.update_layout(margin={"t":25,"r":30,"b":60,"l":60})
        figure_item3.update_layout({"plot_bgcolor":"rgba(0,0,0,0)","paper_bgcolor":"rgba(0,0,0,0)"})
        return figure_item3
    else:
        df_items=df.groupby(["Country","Item","latitude","longitude","Year"],as_index=False)["Amount"].sum()
        df_items["Year"]=df_items["Year"].astype("int")
        df_items=df_items[(df_items["Year"]>=selected_years[0])&(df_items["Year"]<=selected_years[1])]
        df_items=df_items[df_items["Item"]==selected_item]
        country_name=clickData["points"][0]["hovertext"]
        df_items=df_items[df_items["Country"]==country_name]
        figure_item3=px.bar(data_frame=df_items,x="Year",y="Amount",color_discrete_sequence=["aquamarine"],labels={"Amount":"Amount Produced (1000 tonnes)"})
        figure_item3.update_xaxes(tick0=1961,dtick=1)
        figure_item3.update_layout(margin={"t":25,"r":30,"b":60,"l":60})
        figure_item3.update_layout({"plot_bgcolor":"rgba(0,0,0,0)","paper_bgcolor":"rgba(0,0,0,0)"})
        return figure_item3


if __name__=="__main__":
    app.run_server(debug=True)
