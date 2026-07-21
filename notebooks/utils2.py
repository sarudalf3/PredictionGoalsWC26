# utils.py
import requests
import pandas as pd
import numpy as np
import re
from datetime import datetime

def crear_diccionario_estadios(data):
    stadium_dict = {}
    
    for s in data['stadiums']:
        # Concatenación: Nombre, Ciudad, País
        info_completa = f"{s['name_en']}, {s['city_en']}, {s['country_en']}"
        
        # Asignar al diccionario usando el ID como llave
        stadium_dict[s['id']] = info_completa
        
    return stadium_dict

def preparar_calendario(lista_partidos):
    rows = []
    for partido in lista_partidos:
        # Registro 1: Perspectiva del Local
        rows.append({
            'Game_id': partido['id'],
            'Team_id': partido['home_team_id'],
            'Opponent_id': partido['away_team_id'],
            'Date': partido['local_date'],
            'home_score' : partido['home_score'],
            'away_score' : partido['away_score'],
            'stadium_id' : partido['stadium_id'],
            'type': partido['type']
        })
        # Registro 2: Perspectiva del Visitante
        rows.append({
            'Game_id': partido['id'],            
            'Team_id': partido['away_team_id'],
            'Opponent_id': partido['home_team_id'],
            'Date': partido['local_date'],
            'home_score' : partido['away_score'],
            'away_score' : partido['home_score'],
            'stadium_id' : partido['stadium_id'],
            'type': partido['type']            
        })
    
    return pd.DataFrame(rows)

mapa_nombres = {
    'United States': 'USA',
    'South Korea': 'KOR',
    'DR Congo': 'COD',
    'Ivory Coast': 'CIV',
    'Turkey': 'TUR',
    'China': 'CHN',
    'Iran': 'IRN',
    'North Korea': 'PRK',
    'Kyrgyzstan': 'KGZ',
    'Czech Republic': 'CZE',
    'Cape Verde': 'CPV',
    'Gambia': 'GAM',
    'Saint Kitts and Nevis':'SKN',
    'Saint Lucia':'LCA',
    'Democratic Republic of the Congo':'COD',
    'Mautitania': 'MTN'
}

def reclass_torneos(game_type):
    nombre = str(game_type).lower()
    # Orden de prioridad: de lo más específico a lo más general
    if nombre == 'fifa wc26':
        return 'World Cup'
    if any(x in nombre for x in ['copa américa', 'copa america']):
        return 'Federation Cup'
    if any(x in nombre for x in ['afc asian cup', 'asian cup', '20cup gs']):
        return 'Federation Cup'
    if any(x in nombre for x in ['afcon', 'africa cup']):
        return 'Federation Cup'
    if any(x in nombre for x in ['ofc']):
        return 'Federation Cup'    
    if any(x in nombre for x in ['euro', 'european championship']):
        return 'Federation Cup'
    if any(x in nombre for x in ['gold cup', 'concacaf gold']):
        return 'Federation Cup'
    if any(x in nombre for x in ['nations league','–league', 'uefa nl', 'cafa nations cup']):
        return 'Nations League'
    if any(x in nombre for x in ['fifa arab','arab cup']):
        return 'Federation Cup'
    if any(x in nombre for x in ['friendly', 'blue dream match', 'heritage match', 'world cup warm-up']):
        return 'Friendly'
    if any(x in nombre for x in ['world cup qualification', 'wcq', 'fifa world cup q', 'world cup qualifiers', 
            '2026 world cup q', 'world cup q', 'fifa world cup (qualification)','2026 fwc q','fifa wc qualifier',
            'fifa wc qualification', '2026 wc qualif']):
        return 'WC Qualifiers'
    return 'Other'


def calcular_decaimiento_exponencial(df, alpha=0.005):
    """
    Asigna un peso a cada partido basado en qué tan reciente es.
    alpha: tasa de decaimiento (ajustar según qué tan rápido pierden relevancia los datos viejos).
    """
    df['Date'] = pd.to_datetime(df['Date'])
    fecha_final = datetime(2026, 7, 20) #Dia posterior a final FIFA WC26
    df['Final_days'] = (fecha_final - df['Date']).dt.days
    df['Date_decay'] = np.exp(-alpha * df['Final_days'])
    df.drop(columns=['Final_days'], inplace=True)
    return df

def calcular_estadisticas_moviles(df, ventana=3):
    """
    Calcula el promedio de goles a favor y en contra de los últimos 3 partidos.
    """
    df = df.sort_values(['Team', 'Date'])
    
    # Agrupamos por equipo para calcular la media móvil
    df['goals_team_avg'] = df.groupby('Team')['Goals_team'].transform(
        lambda x: x.shift(1).rolling(window=ventana, min_periods=1).mean()
    )
    
    df['goals_avg'] = df.groupby('Team') \
        .apply(lambda x: (x['Goals_team'] + x['Goals_opponent']).shift(1).
            rolling(window=ventana, min_periods=1).mean()) \
        .reset_index(0, drop=True)
    
    df['goals_avg'] = df['goals_avg'].fillna(df['goals_avg'].mean())
    df['goals_team_avg'] = df['goals_team_avg'].fillna(df['goals_team_avg'].mean())
        
    return df

def crear_ventana_fatiga(df, ventana=1):
    """
    Crea una variable que indica si el equipo jugó un partido con alargue/penales
    en su último encuentro.
    """
    df = df.sort_values(['Team', 'Date'])
    # Si en el partido anterior (shift 1) hubo esfuerzo extra, el equipo llega fatigado
    df['AET_LastGame'] = df.groupby('Team')['AET'].transform(lambda x: x.shift(1))
    
    # Rellenamos los NaN (primeros partidos) con 0
    df['AET_LastGame'] = df['AET_LastGame'].fillna(0).astype(int)
    
    return df

def asignar_peso(tipo):
    if tipo == 'Friendly':
        return 0.4  # Menos peso para amistosos
    elif tipo == 'WC Qualifiers':
        return 0.6  # Peso completo para partidos oficiales
    elif tipo == 'Federation Cup':
        return 0.6  # Peso completo para partidos oficiales
    elif tipo == 'Nations League':
        return 0.5  # Peso completo para partidos oficiales
    elif tipo == 'World Cup':
        return 0.8  # Peso completo para partidos oficiales    
    else:
        return 0.4  # Un peso intermedio para otros