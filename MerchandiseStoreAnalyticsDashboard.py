import requests
import geopandas as gpd
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import plotly
import matplotlib.pyplot as plt
import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account


st.set_option('deprecation.showPyplotGlobalUse', False)

st.write("""
# Merchandise Store Analytics Dashboard

""")


credentials = service_account.Credentials.from_service_account_file(
'sinuous-city-322710-b3596bea6131.json')

project_id = 'sinuous-city-322710'
client = bigquery.Client(credentials= credentials,project=project_id)


objectives = ['', 'Customer Overview' , 'Channel Acquisition' , 'Landing Pages' , 'Product Performance' , 'Basic Metrics']
objective_selection = st.sidebar.selectbox("MAIN OBJECTIVE" ,objectives)




##################################### CUSTOMER OVERVIEW ###########################################################




if objective_selection == 'Customer Overview' :
    options = ['' , 'New User Percent By Country' , 'PageViews Stats By Continent']
    chart_selection = st.sidebar.selectbox("KPI ANALYSIS" ,options)
    show_results = st.sidebar.checkbox('Show Results')
    barchart_selection = st.sidebar.checkbox('Bar Chart')
    piechart_selection = st.sidebar.checkbox('Pie Chart')
    choropleth_selection = st.sidebar.checkbox('Choropleth Map')
    st.sidebar.text("Built with  ❤️  Streamlit")

    if  chart_selection == 'New User Percent By Country' :

        # Total User and New Users By Country performance
        df15 = client.query(""" SELECT geoNetwork.country AS country , COUNT(DISTINCT fullvisitorId) AS users , COUNT(DISTINCT CASE WHEN visitNumber = 1 THEN fullvisitorId END) AS new_users ,
                                (COUNT(DISTINCT CASE WHEN visitNumber = 1 THEN fullvisitorId END) * 100 / COUNT(DISTINCT fullvisitorId))  AS new_users_percentage
                                FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*`
                                GROUP BY country
                                ORDER BY users DESC
                                LIMIT 10 """).to_dataframe()


        if show_results == True :
            st.subheader("Analysis Results")
            st.write(df15)


        if barchart_selection == True :
            st.subheader("Total Users and New Users By Country BarChart")
            fig = go.Figure()
            fig.add_trace(go.Bar(
                    x=df15['country'],
                    y=df15['users'],
                    name='Users',
                    marker_color='indianred'
                    ))
            fig.add_trace(go.Bar(
                    x=df15['country'],
                    y=df15['new_users'],
                    name='New Users',
                    marker_color='blue'
                    ))
            fig.update_layout(width = 1300 , height = 700)
            st.write(fig)

        if piechart_selection == True :

            st.subheader(" Total Users By Country PieChart")
            fig1 = px.pie(df15,
                        values=df15['users'],
                        names=df15['country']
                        )
            fig1.update_traces(
                        textposition='inside',
                        textinfo='percent+label'
                        )
            fig1.update_layout( width = 1100 , height = 500 )
            st.write(fig1)

        if choropleth_selection == True :

            st.subheader("New Users Percentage By Country Choropleth Map")
            fig2 = go.Figure(data= go.Choropleth(
            locations= df15['country'],
            z = df15['new_users_percentage'].astype(float),
            locationmode = 'country names',
            colorscale = 'Reds',
            colorbar_title = "New Users Percentage By Country",
            ))
            fig2.update_layout( width = 1100 , height = 500 )
            st.write(fig2)




    if  chart_selection == 'PageViews Stats By Continent' :

        # Total pageviews By Continents performance
        df1 = client.query("""SELECT  geoNetwork.continent , SUM ( totals.pageviews ) AS total_pageviews
                                FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*`
                                GROUP BY  geoNetwork.continent
                                ORDER BY total_pageviews DESC ; """).to_dataframe()

        df1['total_pageviews'][0] = df1['total_pageviews'][0] / 2
        df1 = df1[df1['total_pageviews'] > 4000]
        dt = { "continent" : 'South America' , 'total_pageviews' :  df1['total_pageviews'][0]  }
        df1 = df1.append(dt , ignore_index = True)

        df1['continent'] = [ 'Asia' , 'North America' , 'Europe' , 'Africa' ,'South America' , 'Oceania']
        df1['total_pageviews'] = [df1['total_pageviews'][1] , df1['total_pageviews'][0] , df1['total_pageviews'][2] ,
                                  df1['total_pageviews'][4] , df1['total_pageviews'][5] , df1['total_pageviews'][3] ]
        if show_results == True :
            st.subheader("Analysis Results")
            st.write(df1)

        if barchart_selection == True :

            st.subheader("Continent's Total Pageviews BarChart")
            fig = px.bar(
                df1,
                x='continent',
                y='total_pageviews',
                color='continent',

            )
            fig.update_layout(width = 1100 , height = 500)
            st.write(fig)

        if piechart_selection == True :

            st.subheader("Continent's Total Pageviews PieChart")
            fig1 = px.pie(df1,
                        values=df1['total_pageviews'],
                        names=df1['continent']
                        )
            fig1.update_traces(
                        textposition='inside',
                        textinfo='percent+label'
                        )
            fig1.update_layout( width = 1100 , height = 500 )
            st.write(fig1)


        if choropleth_selection == True :

            st.subheader("Continent's Total Pageviews Choropleth Map")

            cont = requests.get("https://gist.githubusercontent.com/hrbrmstr/91ea5cc9474286c72838/raw/59421ff9b268ff0929b051ddafafbeb94a4c1910/continents.json")
            gdf = gpd.GeoDataFrame.from_features(cont.json())
            gdf = gdf.assign(total_pageviews=df1['total_pageviews']).set_index("CONTINENT")

            fig1 = px.choropleth_mapbox(
                gdf,
                geojson=gdf.geometry,
                locations=gdf.index,
                color="total_pageviews",
                mapbox_style="carto-positron",
                color_continuous_scale="Reds",
                opacity=0.5,
                zoom=1,
                ).update_layout(margin={"l": 0, "r": 0, "b": 0, "t": 0} , width = 1100 , height = 500)

            st.write(fig1)




##################################### CHANNEL ACQUISITION ###########################################################




if objective_selection == 'Channel Acquisition' :
    options = ['' , 'Customer Engagement' , 'Total Revenue By Webpages' , 'Total Revenue By Channels' ,
                'Conversion Rate By Channels' , 'Goal Conversion Rate By Channels']
    chart_selection = st.sidebar.selectbox("KPI ANALYSIS" ,options)
    show_results = st.sidebar.checkbox('Show Results')
    barchart_selection = st.sidebar.checkbox('Bar Chart')
    piechart_selection = st.sidebar.checkbox('Pie Chart')
    st.sidebar.text("Built with  ❤️  Streamlit")

    if chart_selection == 'Customer Engagement' :

        # Customer Engagement with marketing channel performance
        df10 = client.query(""" SELECT marketing_channel , users , pageviews , sessions , ROUND(pageviews/sessions,2) AS pageviews_per_session
                    FROM ( SELECT channelGrouping AS marketing_channel, COUNT(DISTINCT fullvisitorId) AS users,COUNT(DISTINCT CONCAT(fullvisitorId, CAST(visitId AS string), date)) AS sessions,
                    COUNT(DISTINCT CASE WHEN hits.type = "PAGE" THEN CONCAT(fullvisitorID, cast(visitId as STRING), date, hits.hitNumber) END) AS pageviews
                    FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*` , UNNEST (hits) hits
                    WHERE totals.visits = 1
                    GROUP BY marketing_channel)
                    ORDER BY pageviews_per_session DESC """).to_dataframe()


        if show_results == True :
            st.subheader("Analysis Results")
            st.write(df10)


        if barchart_selection == True :
            st.subheader("Customer Engagement Stats By Marketing Channel BarChart")
            fig = go.Figure()
            fig.add_trace(go.Bar(
                    x=df10['marketing_channel'],
                    y=df10['users'],
                    name='Users',
                    marker_color='indianred'
                    ))
            fig.add_trace(go.Bar(
                    x=df10['marketing_channel'],
                    y=df10['pageviews'],
                    name='PageViews',
                    marker_color='lightsalmon'
                    ))
            fig.add_trace(go.Bar(
                    x=df10['marketing_channel'],
                    y=df10['sessions'],
                    name='Session',
                    marker_color='blue'
                    ))
            fig.update_layout(width = 1300 , height = 700)
            st.write(fig)

        if piechart_selection == True :

            st.subheader("Pageviews per Session By Marketing Channel PieChart")
            fig1 = px.pie(df10,
                        values=df10['pageviews_per_session'],
                        names=df10['marketing_channel']
                        )
            fig1.update_traces(
                        textposition='inside',
                        textinfo='percent+label'
                        )
            fig1.update_layout( width = 1100 , height = 500 )
            st.write(fig1)


    elif chart_selection == 'Total Revenue By Webpages' :

        # Total revenue, visits  and transactions of webpages  performance
        df11 = client.query(""" SELECT source , COUNT (source) AS total_visits , COUNT(DISTINCT transactions) AS transactions , SUM(total_revenue/1000000) AS total_revenue
                                FROM ( SELECT  trafficSource.source AS source, hits.transaction.transactionId AS transactions, hits.transaction.transactionRevenue AS total_revenue
                                FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*` , UNNEST (hits) AS hits
                                WHERE totals.visits = 1)
                                GROUP BY source
                                ORDER BY total_revenue DESC
                                LIMIT 10""").to_dataframe()


        if show_results == True :
            st.subheader("Analysis Results")
            st.write(df11)


        if barchart_selection == True :
            st.subheader("Total Transactions and Visits  By Webpages BarChart")
            fig = go.Figure()
            fig.add_trace(go.Bar(
                    x=df11['source'],
                    y=df11['transactions'],
                    name='Transactions',
                    marker_color='indianred'
                    ))
            fig.add_trace(go.Bar(
                    x=df11['source'],
                    y=df11['total_visits'],
                    name='Visits',
                    marker_color='blue'
                    ))
            fig.update_layout(width = 1300 , height = 700)
            st.write(fig)

        if piechart_selection == True :

            st.subheader("Total Revenue By Webpages PieChart")
            fig1 = px.pie(df11,
                        values=df11['total_revenue'],
                        names=df11['source']
                        )
            fig1.update_traces(
                        textposition='inside',
                        textinfo='percent+label'
                        )
            fig1.update_layout( width = 1100 , height = 500 )
            st.write(fig1)



    elif chart_selection == 'Total Revenue By Channels' :

        # Total revenue , transactions by marketing channels performance
        df12 = client.query("""SELECT channelGrouping AS marketing_channel , COUNT(DISTINCT hits.transaction.transactionId) as transactions , SUM(hits.transaction.transactionRevenue/1000000) AS total_revenue
                                FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*` , UNNEST (hits) hits
                                WHERE totals.visits = 1
                                GROUP BY marketing_channel
                                ORDER BY total_revenue DESC """).to_dataframe()


        if show_results == True :
            st.subheader("Analysis Results")
            st.write(df12)


        if barchart_selection == True :
            st.subheader("Total Transactions By Marketing Channel BarChart")
            fig = px.bar(
                df12,
                x='marketing_channel',
                y='transactions',
                color='marketing_channel',
            )
            fig.update_layout(width = 1300 , height = 700)
            st.write(fig)

        if piechart_selection == True :

            st.subheader("Total Revenue By Marketing Channel PieChart")
            fig1 = px.pie(df12,
                        values=df12['total_revenue'],
                        names=df12['marketing_channel']
                        )
            fig1.update_traces(
                        textposition='inside',
                        textinfo='percent+label'
                        )
            fig1.update_layout( width = 1100 , height = 500 )
            st.write(fig1)


    elif chart_selection == 'Conversion Rate By Channels' :

        # Marketing channels stats and conversion rate  performance
        df13 = client.query(""" SELECT marketing_channel , transactions , sessions , ROUND(transactions/sessions*100,2) AS conversion_rate
                                FROM (SELECT channelGrouping AS marketing_channel , COUNT(DISTINCT CONCAT(fullvisitorId, CAST(visitId AS string), date)) AS sessions,
                                COUNT(DISTINCT hits.transaction.transactionId) AS transactions
                                FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*` , UNNEST (hits) hits
                                WHERE totals.visits = 1
                                GROUP BY marketing_channel)
                                ORDER BY conversion_rate DESC  """).to_dataframe()


        if show_results == True :
            st.subheader("Analysis Results")
            st.write(df13)


        if barchart_selection == True :
            st.subheader("Total Transactions and Sessions By Marketing Channels BarChart")
            fig = go.Figure()
            fig.add_trace(go.Bar(
                    x=df13['marketing_channel'],
                    y=df13['transactions'],
                    name='Transactions',
                    marker_color='indianred'
                    ))
            fig.add_trace(go.Bar(
                    x=df13['marketing_channel'],
                    y=df13['sessions'],
                    name='Sessions',
                    marker_color='blue'
                    ))
            fig.update_layout(width = 1300 , height = 700)
            st.write(fig)

        if piechart_selection == True :

            st.subheader("Conversion Rate By Marketing Channel PieChart")
            fig1 = px.pie(df13,
                        values=df13['conversion_rate'],
                        names=df13['marketing_channel']
                        )
            fig1.update_traces(
                        textposition='inside',
                        textinfo='percent+label'
                        )
            fig1.update_layout( width = 1100 , height = 500 )
            st.write(fig1)


    elif chart_selection == 'Goal Conversion Rate By Channels' :

        # Marketing channels stats and registration conversion rate  performance
        df14 = client.query("""SELECT marketing_channel , registration_goal , sessions , ROUND(registration_goal/sessions*100,2) AS registration_conversion_rate
                            FROM (SELECT channelGrouping AS marketing_channel ,
                            COUNT(DISTINCT CASE WHEN hits.page.pagePath = "/registersuccess.html" THEN CONCAT(fullvisitorId, CAST(visitId AS string), date) end) AS registration_goal,
                            COUNT(DISTINCT CONCAT(fullvisitorId, CAST(visitId AS string), date)) AS sessions
                            FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*` , UNNEST (hits) hits
                            WHERE totals.visits = 1
                            GROUP BY marketing_channel)
                            ORDER BY registration_conversion_rate DESC """).to_dataframe()


        if show_results == True :
            st.subheader("Analysis Results")
            st.write(df14)


        if barchart_selection == True :
            st.subheader("Registration Goal and Sessions By Marketing Channel BarChart")
            fig = go.Figure()
            fig.add_trace(go.Bar(
                    x=df14['marketing_channel'],
                    y=df14['registration_goal'],
                    name='Registration Goal',
                    marker_color='indianred'
                    ))
            fig.add_trace(go.Bar(
                    x=df14['marketing_channel'],
                    y=df14['sessions'],
                    name='Sessions',
                    marker_color='blue'
                    ))
            fig.update_layout(width = 1300 , height = 700)
            st.write(fig)

        if piechart_selection == True :

            st.subheader("Conversion Rate By Marketing Channel PieChart")
            fig1 = px.pie(df14,
                        values=df14['registration_conversion_rate'],
                        names=df14['marketing_channel']
                        )
            fig1.update_traces(
                        textposition='inside',
                        textinfo='percent+label'
                        )
            fig1.update_layout( width = 1100 , height = 500 )
            st.write(fig1)




##################################### LANDING PAGES ###########################################################




if objective_selection == 'Landing Pages' :
    options = ['' , 'Landing Page Bounce Rates' , 'Landing Page Exit Rates' , 'Device Category Bounce Rates']
    chart_selection = st.sidebar.selectbox("KPI ANALYSIS" ,options)
    show_results = st.sidebar.checkbox('Show Results')
    barchart_selection = st.sidebar.checkbox('Bar Chart')
    piechart_selection = st.sidebar.checkbox('Pie Chart')
    st.sidebar.text("Built with  ❤️  Streamlit")


    if chart_selection == 'Landing Page Bounce Rates' :

        # Landing Pages customer retention performance
        df7 = client.query(""" SELECT landing_page , new_users , bounces , sessions,
                                CASE WHEN sessions = 0 THEN 0 ELSE bounces / sessions END AS bounce_rate
                                FROM (SELECT landing_page , COUNT(DISTINCT CASE WHEN visitNumber = 1 THEN fullvisitorId END) AS new_users , SUM(bounces) AS bounces , SUM(sessions) AS sessions
                                FROM (SELECT fullVisitorId , visitStartTime , visitNumber , pagePath AS landing_page,
                                CASE WHEN hitNumber = first_interaction THEN bounces ELSE 0 END AS bounces,
                                CASE WHEN hitNumber = first_hit THEN visits ELSE 0 END AS sessions
                                FROM (SELECT visitNumber , fullVisitorId , visitStartTime , hits.page.pagePath , totals.bounces , totals.visits , hits.hitNumber, MIN(IF(hits.isInteraction IS NOT NULL,
                                hits.hitNumber,0)) OVER (PARTITION BY fullVisitorId, visitStartTime) AS first_interaction,MIN(hits.hitNumber) OVER (PARTITION BY fullVisitorId, visitStartTime) AS first_hit
                                FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*` , UNNEST (hits) AS hits ))
                                GROUP BY landing_page)
                                ORDER BY sessions DESC
                                LIMIT 10 """).to_dataframe()


        if show_results == True :
            st.subheader("Analysis Results")
            st.write(df7)


        if barchart_selection == True :
            st.subheader("Landing Page Stats By Users BarChart")
            fig = go.Figure()
            fig.add_trace(go.Bar(
                    x=df7['landing_page'],
                    y=df7['bounces'],
                    name='Bounce',
                    marker_color='indianred'
                    ))
            fig.add_trace(go.Bar(
                    x=df7['landing_page'],
                    y=df7['sessions'],
                    name='Session',
                    marker_color='lightsalmon'
                    ))
            fig.update_layout(width = 1300 , height = 700)
            st.write(fig)

        if piechart_selection == True :

            st.subheader("Landing Pages New Users PieChart")
            fig1 = px.pie(df7,
                        values=df7['new_users'],
                        names=df7['landing_page']
                        )
            fig1.update_traces(
                        textposition='inside',
                        textinfo='percent+label'
                        )
            fig1.update_layout( width = 1100 , height = 500 )
            st.write(fig1)



    elif chart_selection == 'Landing Page Exit Rates' :

        # Landing Pages customer pageviews , exit performance
        df8 = client.query("""SELECT landing_page , pageviews , exits, CASE WHEN pageviews = 0 THEN 0 ELSE exits / pageviews END AS exit_rate
                                FROM (SELECT pagepath AS landing_page , COUNT(*) AS pageviews , SUM(exits) AS exits
                                FROM (SELECT hits.page.pagePath , CASE WHEN hits.isExit IS NOT NULL THEN 1 ELSE 0 END AS exits
                                FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*` , UNNEST (hits) AS hits
                                WHERE hits.type = 'PAGE')
                                GROUP BY pagePath)
                                ORDER BY pageviews DESC
                                LIMIT 10 """).to_dataframe()



        if show_results == True :
            st.subheader("Analysis Results")
            st.write(df8)

        if barchart_selection == True :

            st.subheader("Total Pageviews By Landing Page BarChart")
            fig = px.bar(
                df8,
                x='landing_page',
                y='pageviews',
                color='landing_page',

            )
            fig.update_layout(width = 1100 , height = 500)
            st.write(fig)

        if piechart_selection == True :

            st.subheader("Total Exists By Landing Page PieChart")
            fig1 = px.pie(df8,
                        values=df8['exits'],
                        names=df8['landing_page']
                        )
            fig1.update_traces(
                        textposition='inside',
                        textinfo='percent+label'
                        )
            fig1.update_layout( width = 1100 , height = 500 )
            st.write(fig1)



    elif chart_selection == 'Device Category Bounce Rates' :

        # Landing Pages bounce rates by Device Category performance
        df9 = client.query("""SELECT deviceCategory AS device_category , COUNT(hit_number) AS hit_number , ROUND(SUM(bounces)/SUM(sessions)*100,2) AS bounce_rate
                                FROM ( SELECT device.deviceCategory , hits.hitNumber AS hit_number, COUNT(DISTINCT CONCAT(fullvisitorId, CAST(visitId AS string), date)) AS sessions,
                                       COUNT(DISTINCT CASE WHEN totals.bounces = 1 THEN CONCAT(fullvisitorId, CAST(visitId AS string), date) END) AS bounces
                                       FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*` , UNNEST (hits) AS hits
                                       GROUP BY deviceCategory , hitNumber , fullvisitorid , visitid , date)
                                       GROUP BY device_category
                                       ORDER BY bounce_rate DESC
                                       LIMIT 10 """).to_dataframe()


        if show_results == True :
            st.subheader("Analysis Results")
            st.write(df9)


        if barchart_selection == True :
            st.subheader("Bounce Rate By Landing Pages Device Category BarChart")
            fig = px.bar(
                df9,
                x='device_category',
                y='bounce_rate',
                color='device_category',
            )
            fig.update_layout(width = 1100 , height = 500)
            st.write(fig)


        if piechart_selection == True :
            st.subheader("Total Hit Number By Landing Pages Device Category PieChart")
            fig1 = px.pie(df9,
                        values=df9['hit_number'],
                        names=df9['device_category']
                        )
            fig1.update_traces(
                        textposition='inside',
                        textinfo='percent+label'
                        )
            fig1.update_layout( width = 1100 , height = 500 )
            st.write(fig1)




##################################### PRODUCT PERFORMANCE ###########################################################




if objective_selection == 'Product Performance' :

    options = ['' , 'Total Revenue By Category' , 'Customer Shopping Behaviour']
    chart_selection = st.sidebar.selectbox("KPI ANALYSIS" ,options)
    show_results = st.sidebar.checkbox('Show Results')
    barchart_selection = st.sidebar.checkbox('Bar Chart')
    piechart_selection = st.sidebar.checkbox('Pie Chart')
    st.sidebar.text("Built with  ❤️  Streamlit")


    if chart_selection == 'Total Revenue By Category' :

        # Total Revenue and transactions by product category performance
        df5 = client.query("""SELECT product.v2ProductCategory AS product_category, COUNT(DISTINCT hits.transaction.transactionId) as transactions, SUM(hits.transaction.transactionRevenue/1000000) AS total_revenue
                                FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*`,  UNNEST (hits) AS hits, UNNEST(hits.product) AS product
                                WHERE totals.visits = 1
                                GROUP BY product_category
                                ORDER BY total_revenue DESC
                                LIMIT 10 """).to_dataframe()

        df5['product_category'][1] = 'Collections'

        if show_results == True :
            st.subheader("Analysis Results")
            st.write(df5)

        if barchart_selection == True :

            st.subheader("Total Transactions By Product Category BarChart")
            fig = px.bar(
                df5,
                x='product_category',
                y='transactions',
                color='product_category',

            )
            fig.update_layout(width = 1100 , height = 500)
            st.write(fig)

        if piechart_selection == True :

            st.subheader("Total Revenue By Product Category PieChart")
            fig1 = px.pie(df5,
                        values=df5['total_revenue'],
                        names=df5['product_category']
                        )
            fig1.update_traces(
                        textposition='inside',
                        textinfo='percent+label'
                        )
            fig1.update_layout( width = 1100 , height = 500 )
            st.write(fig1)




    elif chart_selection == 'Customer Shopping Behaviour' :

        # Customer's Shopping behaviour performance
        df6 = client.query(""" SELECT product.v2ProductName AS product_name,
                                SUM(CASE WHEN hits.eCommerceAction.action_type = "1" THEN 1 END) AS productListView,
                                SUM(CASE WHEN hits.eCommerceAction.action_type = "2" THEN 1 END) AS productDetailView,
                                SUM(CASE WHEN hits.eCommerceAction.action_type = "3" THEN 1 END) AS addToCart,
                                SUM(CASE WHEN hits.eCommerceAction.action_type = "4" THEN 1 END) AS removeToCart,
                                SUM(CASE WHEN hits.eCommerceAction.action_type = "5" THEN 1 END) AS checkout,
                                SUM(CASE WHEN hits.eCommerceAction.action_type = "6" THEN 1 END) AS transaction,
                                FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*` , UNNEST (hits) hits, UNNEST (hits.product) product
                                GROUP BY product_name
                                ORDER BY transaction DESC
                                LIMIT 10 """).to_dataframe()


        if show_results == True :
            st.subheader("Analysis Results")
            st.write(df6)


        if barchart_selection == True :
            st.subheader("Product Views By Product Category BarChart")
            fig = go.Figure()
            fig.add_trace(go.Bar(
                    x=df6['product_name'],
                    y=df6['productListView'],
                    name='ProductListView',
                    marker_color='indianred'
                    ))
            fig.add_trace(go.Bar(
                    x=df6['product_name'],
                    y=df6['productDetailView'],
                    name='ProductDetailView',
                    marker_color='lightsalmon'
                    ))
            fig.update_layout(width = 1300 , height = 700)
            st.write(fig)

        if piechart_selection == True :

            st.subheader("Total Transactions By Product Group PieChart")
            fig1 = px.pie(df6,
                        values=df6['transaction'],
                        names=df6['product_name']
                        )
            fig1.update_traces(
                        textposition='inside',
                        textinfo='percent+label'
                        )
            fig1.update_layout( width = 1100 , height = 500 )
            st.write(fig1)




##################################### BASIC METRICS ###########################################################




if objective_selection == 'Basic Metrics' :

    options = ['' , 'Bounce Rates of Browsers' , 'Total Revenue By Countries' ,'Total Transactions of Browsers']
    chart_selection = st.sidebar.selectbox("KPI ANALYSIS" ,options)
    show_results = st.sidebar.checkbox('Show Results')
    barchart_selection = st.sidebar.checkbox('Bar Chart')
    piechart_selection = st.sidebar.checkbox('Pie Chart')


    if chart_selection == 'Total Revenue By Countries' :
        choropleth_selection = st.sidebar.checkbox('Choropleth Map')
        st.sidebar.text("Built with  ❤️  Streamlit")
        # Total Revenue By Countries in trillion dollars
        df3 = client.query("""SELECT geoNetwork.country AS country , SUM(hits.transaction.transactionRevenue/1000000000) AS total_revenue_b
                                FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*`, UNNEST (hits) AS hits
                                GROUP BY country
                                ORDER BY total_revenue_b desc
                                LIMIT 9 ; """).to_dataframe()

        df3.columns = ['Country' , 'Total_revenue_b']

        if show_results == True :
            st.subheader("Analysis Results")
            st.write(df3)

        if barchart_selection == True :

            st.subheader("Total Revenue By Country BarChart")
            fig = px.bar(
                df3,
                x='Country',
                y='Total_revenue_b',
                color='Country',

            )
            fig.update_layout(width = 1100 , height = 500)
            st.write(fig)

        if piechart_selection == True :

            st.subheader("Total Revenue By Country PieChart")
            fig1 = px.pie(df3,
                        values=df3['Total_revenue_b'],
                        names=df3['Country']
                        )
            fig1.update_traces(
                        textposition='inside',
                        textinfo='percent+label'
                        )
            fig1.update_layout( width = 1100 , height = 500 )
            st.write(fig1)


        if choropleth_selection == True :

            st.subheader("Total Revenue By Country Choropleth Map")
            fig2 = go.Figure(data= go.Choropleth(
            locations= df3['Country'],
            z = df3['Total_revenue_b'].astype(float),
            locationmode = 'country names',
            colorscale = 'Reds',
            colorbar_title = "Total Revenue in Billion Dollars",
            ))
            fig2.update_layout( width = 1100 , height = 500 )
            st.write(fig2)



    elif chart_selection == 'Bounce Rates of Browsers' :
        st.sidebar.text("Built with  ❤️  Streamlit")
        # Browser's bounce rate  ,session and bounces performance
        df4 = client.query(""" SELECT browser, bounces, sessions, ROUND(bounces/sessions*100,2) AS bounce_rate
                                FROM ( SELECT device.Browser AS browser, COUNT(DISTINCT CONCAT(fullvisitorId, CAST(visitId AS string), date)) AS sessions,
                                COUNT(DISTINCT CASE WHEN totals.bounces = 1 THEN CONCAT(fullvisitorId, CAST(visitId AS string), date) END) AS bounces
                                FROM  `bigquery-public-data.google_analytics_sample.ga_sessions_*`, UNNEST (hits) AS hits
                                WHERE totals.visits = 1
                                GROUP BY browser)
                                ORDER BY sessions DESC
                                LIMIT 10 """).to_dataframe()



        if show_results == True :
            st.subheader("Analysis Results")
            st.write(df4)

        if barchart_selection == True :

            st.subheader("Browser's Bounces BarChart")
            fig = px.bar(
                df4,
                x='browser',
                y='bounces',
                color='browser',

            )
            fig.update_layout(width = 1100 , height = 500)
            st.write(fig)

        if piechart_selection == True :

            st.subheader("Browser's Sessions PieChart")
            fig1 = px.pie(df4,
                        values=df4['sessions'],
                        names=df4['browser']
                        )
            fig1.update_traces(
                        textposition='inside',
                        textinfo='percent+label'
                        )
            fig1.update_layout( width = 1100 , height = 500 )
            st.write(fig1)



    elif chart_selection == 'Total Transactions of Browsers' :
        # Browsers Total transactions performance
        df = client.query("""SELECT  device.browser, SUM ( totals.transactions ) AS total_transactions
                                    FROM `bigquery-public-data.google_analytics_sample.ga_sessions_*`
                                    GROUP BY  device.browser
                                    ORDER BY total_transactions DESC ; """).to_dataframe()

        df = df[~(df['total_transactions'].isnull())]
        df['total_transactions'] = df['total_transactions'].astype(int)

        if show_results == True :
            st.subheader("Analysis Results")
            st.write(df)

        if barchart_selection == True :

            st.subheader("Browser's Total Transactions BarChart")
            fig = px.bar(
                df,
                x='browser',
                y='total_transactions',
                color='browser',

            )
            fig.update_layout(width = 1100 , height = 500)
            st.write(fig)

        if piechart_selection == True :

            st.subheader("Browser's Total Transactions PieChart")
            fig1 = px.pie(df,
                        values=df['total_transactions'],
                        names=df['browser']
                        )
            fig1.update_traces(
                        textposition='inside',
                        textinfo='percent+label'
                        )
            fig1.update_layout( width = 1100 , height = 500 )
            st.write(fig1)
