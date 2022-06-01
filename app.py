#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 19 12:45:08 2022

@author: rramirez
"""

import dash
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd 
from dash.dependencies import Input, Output
from dash import dcc, html
from flask import Flask

df = pd.read_csv('CANCER.csv')

colsVars = list(df.columns)
colsVars.remove('id')
colsVars.remove('diagnosis')
colsVars.remove('Unnamed: 32')

external_stylesheets = [
    {
        'href': 'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3',
        'crossorigin': 'anonymous'
    },
    ]

external_scripts = [
    {
        'src': 'https://code.jquery.com/jquery-3.6.0.min.js',
        'integrity': 'sha256-/xUj+3OJU5yExlq6GSYGSHk7tPXikynS7ogEvDej/m4=',
        'crossorigin': 'anonymous'
    },
    {
        'src': 'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js',
        'integrity': 'sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p',
        'crossorigin': 'anonymous'
    },
    ]

server = Flask(__name__)

if __name__ == ('__main__'):
    app = dash.Dash(__name__,
                    external_stylesheets=external_stylesheets,
                    external_scripts=external_scripts,
                    server=server,
                    title="Daschboard - Wisconsin de cáncer de mama"
                    ) 
else:
    app = dash.Dash(__name__,
                    external_stylesheets=external_stylesheets,
                    external_scripts=external_scripts,
                    server=server,
                    requests_pathname_prefix='/dashboard-cancer/',
                    title="Daschboard - Wisconsin de cáncer de mama"
                    ) 

app.layout = html.Div([
    html.Div([
        html.H1('Conjunto de datos de Wisconsin de cáncer de mama'),
        html.Div([
            html.Div([
                html.Label('Variable Principal: ', className="form-label", htmlFor="varPrincipal"),
                dcc.Dropdown(
                    options=[{'label':col, 'value':col} for col in colsVars],
                    id='varPrincipal', clearable=False, value=colsVars[0])
                ], className="col-sm-4"),
            html.Div([
                html.Label('Cantidad de Bins: ', className="form-label", htmlFor="cantBins"),
                dcc.Input(id='cantBins', type='number', value=10, min=1, max=100, className='form-control')
            ], className="col-sm-4"),
        ], className='row'),
        html.Div([
            html.Div([html.Div([dcc.Graph(id='gHistograma', figure={})]),], className='col-sm-4'),
            html.Div([html.Div([dcc.Graph(id='gHistogramaAcumulativo', figure={})]),], className='col-sm-4'),
            html.Div([html.Div([dcc.Graph(id='gCajaBigote', figure={})]),], className='col-sm-4'),
        ], className='row'),
        html.Div([
            html.Div([html.Div([dcc.Graph(id='gHistogramaBM', figure={})]),], className='col-sm-4'),
            html.Div([html.Div([dcc.Graph(id='gHistogramaAcumulativoBM', figure={})]),], className='col-sm-4'),
            html.Div([html.Div([dcc.Graph(id='gCajaBigoteBM', figure={})]),], className='col-sm-4'),
        ], className='row'),
        html.Div([
            html.Div([
                html.Label('Variable Comparar: ', className="form-label", htmlFor="varSecundaria"),
                dcc.Dropdown(
                    options=[{'label':col, 'value':col} for col in colsVars],
                    id='varSecundaria', clearable=False, value=colsVars[0])
                ], className="col-sm-4"),
            html.Div([html.Div([dcc.Graph(id='gDispersion', figure={})]),], className='col-sm-4'),
            html.Div([html.Div([dcc.Graph(id='gDispersionBM', figure={})]),], className='col-sm-4'),
        ], className='row'),
    ], className='container')
], id='page')

@app.callback(
    Output('gHistograma', component_property='figure'),
    [
        Input('varPrincipal', component_property='value'),
        Input('cantBins', component_property='value')])
def updateGraphHistograma(columna, nBins):
    return px.histogram(df, x=columna, nbins=nBins)

@app.callback(
    Output('gHistogramaAcumulativo', component_property='figure'),
    [
        Input('varPrincipal', component_property='value'),
        Input('cantBins', component_property='value')])
def updateGraphHistogramaAcumulativo(columna, nBins):
    data = generaDataHistogramaAcumulativo(df[columna], nBins)
    return px.line(data, x='valor', y='conteo')

@app.callback(
    Output('gHistogramaBM', component_property='figure'),
    [
        Input('varPrincipal', component_property='value'),
        Input('cantBins', component_property='value')])
def updateGraphHistogramaBM(columna, nBins):
    return px.histogram(df, x=columna, nbins=nBins, color='diagnosis')

@app.callback(
    Output('gHistogramaAcumulativoBM', component_property='figure'),
    [
        Input('varPrincipal', component_property='value'),
        Input('cantBins', component_property='value')])
def updateGraphHistogramaAcumulativoBM(columna, nBins):
    data = []
    for tipo in df['diagnosis'].unique():
        for bin in generaDataHistogramaAcumulativo(df[df['diagnosis']==tipo][columna], nBins):
            bin.update({'tipo': tipo})
            data.append(bin)
    return px.line(data, x='valor', y='conteo', color='tipo')

@app.callback(
    Output('gCajaBigote', component_property='figure'),
    [Input('varPrincipal', component_property='value'), ])
def updateGraphCajaBigote(columna):
    return px.box(df, x=columna)

@app.callback(
    Output('gCajaBigoteBM', component_property='figure'),
    [Input('varPrincipal', component_property='value'), ])
def updateGraphCajaBigoteBM(columna):
    return px.box(df, x=columna, color='diagnosis')

@app.callback(
    Output('gDispersion', component_property='figure'),
    [
        Input('varPrincipal', component_property='value'),
        Input('varSecundaria', component_property='value'),])
def updateGraphDispersion(principal, secundaria):
    return px.scatter(df, x=principal, y=secundaria)

@app.callback(
    Output('gDispersionBM', component_property='figure'),
    [
        Input('varPrincipal', component_property='value'),
        Input('varSecundaria', component_property='value'),])
def updateGraphDispersionBM(principal, secundaria):
    return px.scatter(df, x=principal, y=secundaria, color='diagnosis')

def generaDataHistogramaAcumulativo(datos, nBins):
    minimo = min(datos)
    maximo = max(datos)
    increm = (maximo - minimo) / nBins
    data = []
    acum = 0
    for x in range(nBins):
        ini = minimo + x * increm
        fin = minimo + (x + 1) * increm
        acum += len(datos[(ini <= datos)&(datos <= fin)])
        data.append({
            'valor': minimo + (x + 0.5) * increm,
            'conteo': acum,
            'inicio': ini,
            'fin': fin,
        })
    return data

if __name__ == ('__main__'):
    app.run_server(debug=True, port=8050)

