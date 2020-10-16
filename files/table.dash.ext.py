# -*- coding: utf-8 -*-
import sys, requests, plotly.express as px, pandas as pd
from datetime import datetime as dt
import dash, dash_core_components as dcc, dash_html_components as html

# An utility function to use for date converting into a python dtetime object
def convert_date(dts):
	dto = dt.strptime(dts, '%d.%m.%y  %H:%M')
	return dto.strftime('%Y-%m-%d %H:%M')

# An utility function to use for date converting into a python dtetime object
def generate_table(dataframe, columns, column_names):
	return html.Table([		
	  html.Thead(		
		[html.Tr([html.Th(col) for col in column_names ])]
	  ),
	  html.Tbody([
		html.Tr([
			html.Td(dataframe.iloc[i][col]) for col in columns
		]) for i in range(len(dataframe))
	  ])
	])


url = 'http://localhost:8080'	# Spider Project's API Server 
filename = "1km_road_api.001.sprj"    # Please prepend with the full path

r = requests.post( url, json={'command':'openFile', 'fileName':filename, 'sessId':''} )
print('Project opened.') if r.status_code == 200 else sys.exit(0)
docHandle = r.json()['docHandle'] 

# **************************************************************************************************************************
# Retrieving gantt table data and building diagrams
r = requests.post( url, json={ 'command':'getTableHandle', 'docHandle':str(docHandle), 'table':'GanttAct', 'sessId':'' } )
print('Gantt table handle obtained.') if r.status_code == 200 else sys.exit(0)
tableHandle = r.json()['tableHandle'] 

r = requests.post( url, json={ 'command':'getTable', 'tableHandle':str(tableHandle), 'sessId':'' } )
print('Gantt table content obtained.') if r.status_code == 200 else sys.exit(0)
r = r.json()

df = pd.DataFrame( r['array'] )
df['Level'] = df['Level'].fillna(0)
df['Start'] = df['Start'].apply(convert_date)
df['Fin'] = df['Fin'].apply(convert_date)
fig_gantt = px.timeline(df, x_start="Start", x_end="Fin", y='Name', color="Name", height=680, title='Диаграмма Гантта')

dfp2 = df.loc[ (df['Level'] == '2') & (pd.notnull(df['c_sum_кс'])) ]
dfp2 = dfp2.reset_index()
dfp2['c_sum_кс'] = dfp2['c_sum_кс'].astype(float).round(0)
dfp2['pie_names'] = dfp2['Name'] + ": " + dfp2['c_sum_кс'].astype(str) + " р."
fig_pie2 = px.pie( dfp2, values='c_sum_кс', names='pie_names', title='Уровень 2' ) 

dfp3 = df.loc[ (df['Level'] == 0) & (pd.notnull(df['c_sum_кс'])) ]
dfp3 = dfp3.reset_index()
dfp3['c_sum_кс'] = dfp3['c_sum_кс'].astype(float).round(0)
dfp3['pie_names'] = dfp3['Name'] + ": " + dfp3['c_sum_кс'].astype(str) + " р."
fig_pie3 = px.pie( dfp3, values='c_sum_кс', names='pie_names', title='Уровень 3' ) 

# **************************************************************************************************************************
# Retrieving resource table data and building diagrams and table
rr = requests.post( url, json={ 'command':'getTableHandle', 'docHandle':str(docHandle), 'table':'Resource', 'sessId':'' } )
print('Resource table handle obtained.') if rr.status_code == 200 else sys.exit(0)
tableHandle = rr.json()['tableHandle'] 

rr = requests.post( url, json={ 'command':'getTable', 'tableHandle':str(tableHandle), 'sessId':'' } )
print('Resource table content obtained.') if rr.status_code == 200 else sys.exit(0)
rr = rr.json()

dfr = pd.DataFrame( rr['array'] )
dfr = dfr.dropna(subset=['Start','Fin', 'CostTotal'])
dfr['Start'] = dfr['Start'].apply(convert_date)
dfr['Fin'] = dfr['Fin'].apply(convert_date)
dfr['CostTotal'] = dfr['CostTotal'].apply( lambda x: round(float(x)) )
fig_gantt_r = px.timeline(dfr, x_start="Start", x_end="Fin", y='Name', color="Name", height=680, title='Использование ресурсов')

dfr['pie_names'] = dfr['Name'] + ": " + dfr['CostTotal'].astype(str) + " р."
fig_pie_r = px.pie( dfr, values='CostTotal', names='pie_names', title='Стоимости ресурсов' ) 

app = dash.Dash(__name__)
	
app.layout = html.Div(
	style = {'backgroundColor': '#efefef'}, 
	children = [
		html.H1(children = r['array'][0]['Name'],
			style = { 'textAlign': 'center', 'color': '#7f7f7f' }
		),
		dcc.Graph(figure = fig_pie2),
		dcc.Graph(figure = fig_pie3),
		dcc.Graph(figure = fig_gantt),
		html.H4(children='Таблица операций'),
		generate_table(df, [ 'Name', 'Start', 'Fin', 'c_sum_кс' ], [ 'Название', 'Начало', 'Окончание', 'Стоимость' ]),
		html.H4(children='Ресуры'),
		dcc.Graph(figure = fig_gantt_r),
		dcc.Graph(figure = fig_pie_r),
		generate_table(dfr, [ 'Name', 'Start', 'Fin', 'CostTotal' ], [ 'Название', 'Начало', 'Окончание', 'Стоимость' ])
	])

if __name__ == '__main__':
   app.run_server(debug=True)