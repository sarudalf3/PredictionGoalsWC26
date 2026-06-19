# utils.py
import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
from datetime import datetime

###Function to get the fifa ranking
def obtener_ranking_fifa_oficial(url_api):
    print("Conectando y procesando el JSON de la FIFA...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json'
    }
    
    try:
        # Asegúrate de pasar la URL exacta que usaste para obtener ese JSON
        respuesta = requests.get(url_api, headers=headers, timeout=15)
        
        if respuesta.status_code == 200:
            datos_json = respuesta.json()
            
            # 1. Ahora buscamos bajo la llave 'Results' según tu output
            resultados_lista = datos_json.get('Results', [])
            
            datos_limpios = []
            for item in resultados_lista:
                # 2. Extraemos el Ranking y Puntos Totales
                ranking_actual = item.get('Rank')
                puntos_totales = item.get('TotalPoints')
                siglas_pais = item.get('IdCountry')
                
                # 3. El nombre viene en una lista: TeamName -> [0] -> Description
                nombre_pais = None
                nombres_lista = item.get('TeamName', [])
                if nombres_lista and len(nombres_lista) > 0:
                    nombre_pais = nombres_lista[0].get('Description')
                
                if nombre_pais:
                    datos_limpios.append({
                        "Ranking_Actual": ranking_actual,
                        "Seleccion": nombre_pais,
                        "Puntos_FIFA": puntos_totales,
                        "Codigo_Pais": siglas_pais
                    })
            
            df_ranking = pd.DataFrame(datos_limpios)
            print(f"¡Éxito! Se importaron {len(df_ranking)} selecciones desde el Ranking FIFA.")
            return df_ranking
            
        else:
            print(f"[!] La API respondió con código de error: {respuesta.status_code}")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"[!] Error al procesar la API: {e}")
        return pd.DataFrame()


#Alias Paises renames
alias_paises = {
    'Bosnia and Herzegovina': 'BIH',
    'Czech Republic': 'CZE',
    'Curacao': 'CUW',
    'South Korea': 'KOR',
    'United States': 'USA',
    'Ivory Coast': 'CIV',
    'DR Congo': 'COD',
    'Cape Verde': 'CPV',
    'Iran': 'IRN',
    'Turkey': 'TUR'
}


#Find the country code name
def obtener_codigo_pais(nombre_wiki, df_fifa):
    # A) Buscar si está en nuestros alias definidos manualmente
    if nombre_wiki in alias_paises:
        return alias_paises[nombre_wiki]
    
    # B) Buscar directamente por nombre en el DataFrame de la FIFA
    match = df_fifa[df_fifa['Seleccion'].str.contains(nombre_wiki, case=False, na=False)]
    if not match.empty:
        return match.iloc[0]['Codigo_Pais']
    
    return "N/A"


#Wikipedia websites by team
records_teams = {
 'ARG':'https://en.wikipedia.org/wiki/Argentina_national_football_team_results_(2020%E2%80%93present)',
 'ESP':'https://en.wikipedia.org/wiki/Spain_national_football_team_results_(2020%E2%80%93present)',
 'FRA':'https://en.wikipedia.org/wiki/France_national_football_team_results_(2020%E2%80%93present)',
 'ENG':'https://en.wikipedia.org/wiki/England_national_football_team_results_(2020%E2%80%93present)',
 'POR':'https://en.wikipedia.org/wiki/Portugal_national_football_team_results_(2020%E2%80%93present)',
 'BRA': 'https://en.wikipedia.org/wiki/Brazil_national_football_team_results_(2020%E2%80%93present)',
 'MAR': 'https://en.wikipedia.org/wiki/Morocco_national_football_team_results_(2020%E2%80%93present)',
 'NED': 'https://en.wikipedia.org/wiki/Netherlands_national_football_team_results_(2020%E2%80%93present)',
 'BEL': 'https://en.wikipedia.org/wiki/Belgium_national_football_team_results_(2020%E2%80%93present)',
 'GER': 'https://en.wikipedia.org/wiki/Germany_national_football_team_results_(2020%E2%80%93present)',
 'CRO': 'https://en.wikipedia.org/wiki/Croatia_national_football_team_results_(2020%E2%80%93present)',
 'MEX': 'https://en.wikipedia.org/wiki/Mexico_national_football_team_results_(2020%E2%80%93present)',
 'COL': 'https://en.wikipedia.org/wiki/Colombia_national_football_team_results_(2020%E2%80%93present)',
 'SEN': 'https://en.wikipedia.org/wiki/Senegal_national_football_team_results_(2020%E2%80%93present)',
 'URU': 'https://en.wikipedia.org/wiki/Uruguay_national_football_team_results_(2020%E2%80%93present)',
 'JPN': 'https://en.wikipedia.org/wiki/Japan_national_football_team_results_(2020%E2%80%93present)',
 'SUI': 'https://en.wikipedia.org/wiki/Switzerland_national_football_team_results_(2020%E2%80%93present)',
 'IRN': 'https://en.wikipedia.org/wiki/Iran_national_football_team_results_(2020%E2%80%93present)',
 'KOR': 'https://en.wikipedia.org/wiki/South_Korea_national_football_team_results_(2020%E2%80%93present)',
 'TUR': 'https://en.wikipedia.org/wiki/Turkey_national_football_team_results_(2020%E2%80%93present)',
 'ECU': 'https://en.wikipedia.org/wiki/Ecuador_national_football_team_results_(2020%E2%80%93present)',
 'AUT': 'https://en.wikipedia.org/wiki/Austria_national_football_team_results_(2020%E2%80%93present)',
 'ALG': 'https://en.wikipedia.org/wiki/Algeria_national_football_team_results_(2020%E2%80%93present)',
 'EGY': 'https://en.wikipedia.org/wiki/Egypt_national_football_team_results_(2020%E2%80%93present)',
 'NOR': 'https://en.wikipedia.org/wiki/Norway_national_football_team_results_(2020%E2%80%93present)',
 'CAN': 'https://en.wikipedia.org/wiki/Canada_men%27s_national_soccer_team_results_(2020%E2%80%93present)',
 'CIV': 'https://en.wikipedia.org/wiki/Ivory_Coast_national_football_team_results_(2020%E2%80%93present)',
 'PAN': 'https://en.wikipedia.org/wiki/Panama_national_football_team_results_(2020%E2%80%93present)',
 'SWE': 'https://en.wikipedia.org/wiki/Sweden_men%27s_national_football_team_results_(2020%E2%80%93present)',
 'SCO': 'https://en.wikipedia.org/wiki/Scotland_national_football_team_results_(2020%E2%80%93present)',
 'SRB': 'https://en.wikipedia.org/wiki/Serbia_national_football_team_results_(2020%E2%80%93present)',
 'PAR': 'https://en.wikipedia.org/wiki/Paraguay_national_football_team_results_(2020%E2%80%93present)',
 'TUN': 'https://en.wikipedia.org/wiki/Tunisia_national_football_team_results_(2020%E2%80%93present)',
 'COD': 'https://en.wikipedia.org/wiki/DR_Congo_national_football_team_results_(2020%E2%80%93present)',
 'UZB': 'https://en.wikipedia.org/wiki/Uzbekistan_national_football_team_results_(2020%E2%80%93present)',
 'QAT': 'https://en.wikipedia.org/wiki/Qatar_national_football_team_results_(2020%E2%80%93present)',
 'IRQ': 'https://en.wikipedia.org/wiki/Iraq_national_football_team_results_(2020%E2%80%93present)',
 'KSA': 'https://en.wikipedia.org/wiki/Saudi_Arabia_national_football_team_results_(2020%E2%80%93present)',
 'RSA': 'https://en.wikipedia.org/wiki/South_Africa_national_football_team_results_(2020%E2%80%93present)',
 'BIH': 'https://en.wikipedia.org/wiki/Bosnia_and_Herzegovina_national_football_team_results_(2020%E2%80%93present)',
 'JOR': 'https://en.wikipedia.org/wiki/Jordan_national_football_team_results_(2020%E2%80%93present)',
 'CPV': 'https://en.wikipedia.org/wiki/Cape_Verde_national_football_team_results_(2020%E2%80%93present)',
 'GHA': 'https://en.wikipedia.org/wiki/Ghana_national_football_team_results_(2020%E2%80%93present)',
 'CUW': 'https://en.wikipedia.org/wiki/Cura%C3%A7ao_national_football_team_results_(2020%E2%80%93present)',
 'HAI': 'https://en.wikipedia.org/wiki/Haiti_national_football_team_results_(2010%E2%80%93present)',
 'NZL': 'https://en.wikipedia.org/wiki/New_Zealand_men%27s_national_football_team_results_(2020%E2%80%93present)',
 'AUS': 'https://en.wikipedia.org/wiki/Australia_men%27s_national_soccer_team_results_(2020%E2%80%93present)',
 'USA': 'https://en.wikipedia.org/wiki/United_States_men%27s_national_soccer_team_results_(2020%E2%80%93present)',
 'CZE': 'https://en.wikipedia.org/wiki/Czech_Republic_national_football_team_results_(2020%E2%80%93present)'
} 


#Extract wikipedia type01
def games_type01(url, codigo_pais):
    print(f"Iniciando extracción de datos para: {codigo_pais}...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extraer tablas y encontrar la que contiene los resultados
    tablas = pd.read_html(str(soup), flavor='bs4')
    df = next((t for t in tablas if 'Opponents' in t.columns or 'Opponent' in t.columns), None)
    
    if df is None:
        print(f"No se pudo encontrar la tabla de partidos para {codigo_pais}")
        return pd.DataFrame()

    partidos = []
    fecha_corte = datetime(2022, 12, 18) # Fin del Mundial de Qatar

    for _, fila in df.iterrows():
        try:
            # 1. Limpieza y formato de Fecha
            fecha_raw = str(fila.get('Date', ''))
            fecha_limpia = re.sub(r'\[.*?\]', '', fecha_raw).strip()
            fecha_dt = pd.to_datetime(fecha_limpia, errors='coerce')
            
            # Filtro: Solo partidos posteriores a Qatar 2022
            if pd.isna(fecha_dt) or fecha_dt <= fecha_corte:
                continue
            
            # 2. Extracción de campos
            marcador_original = re.sub(r'\[.*?\]', '', str(fila.get('Score', ''))).strip()
            venue_crudo = str(fila.get('Venue', ''))
            goles = re.findall(r'\d+', marcador_original)

            # 1. Regex para el Marcador (identificador clave de que es una fila de partido)
            #game_raw = re.search(r'^\d{1,2}\s+[A-Za-z]+.*?(\d+)\s*[–-]\s*(\d+)', marcador_original)
            #if not game_raw:
            #    continue
            
            # 3. Lógica avanzada
            partidos.append({
                "Seleccion": codigo_pais,
                "Fecha": fecha_dt.strftime("%Y-%m-%d"),
                "Tipo_Partido": str(fila.get('Competition', '')),
                "Venue": venue_crudo,
                "Condicion": 'L' if '(H)' in venue_crudo else ('V' if '(A)' in venue_crudo else 'N'),
                "Oponente": str(fila.get('Opponents', '')),
                "Goles_Equipo": int(goles[0]) if len(goles) > 0 else None,
                "Goles_Rival": int(goles[1]) if len(goles) > 1 else None,
                "Resultado_Original": marcador_original,
                "Es_Penales": "p)" in marcador_original,
                "Es_Tiempo_Extra": "(a.e.t.)" in marcador_original
            })
        except Exception:
            continue
            
    return pd.DataFrame(partidos)


#Extract wikipedia type02
def games_type02(url, codigo_pais, df_ranking_fifa):
    print(f"Iniciando extracción robusta para: {codigo_pais}...")
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        respuesta = requests.get(url, headers=headers)
        soup = BeautifulSoup(respuesta.text, 'html.parser')
    except Exception as e:
        print(f"Error al conectar con la página: {e}")
        return pd.DataFrame()

    partidos = []
    fecha_limite = pd.to_datetime("2022-12-18")
    
    año_actual = "2022" # Valor por defecto

    # Buscamos h2, h3 o filas de tabla en el orden en que aparecen
    for elemento in soup.find_all(['h2', 'h3', 'tr']):
        
        # 1. Si es un título, intentamos detectar el año
        if elemento.name in ['h2', 'h3']:
            texto_titulo = elemento.get_text()
            match_año = re.search(r'(20\d{2})', texto_titulo)
            if match_año:
                año_actual = match_año.group(1)
            continue
        
        # 2. Si es una fila, procesamos el partido
        if elemento.name == 'tr':
            celdas = elemento.find_all('td')
            if len(celdas) < 4: continue
            
            texto_fila = elemento.get_text(" ", strip=True)
            
            # Buscamos día y mes (ej: "31 March")
            match_dia_mes = re.search(r'(\d{1,2})\s+([A-Za-z]+)', texto_fila)
            if not match_dia_mes: continue
            
            # Construimos la fecha completa usando el año del encabezado
            fecha_str = f"{match_dia_mes.group(1)} {match_dia_mes.group(2)} {año_actual}"
            try:
                fecha_dt = pd.to_datetime(fecha_str)
            except: continue
                
            if fecha_dt <= fecha_limite:
                continue    
    
            # 1. Regex para el Marcador (identificador clave de que es una fila de partido)
            game_raw = re.search(r'^\d{1,2}\s+[A-Za-z]+.*?(\d+)\s*[–-]\s*(\d+)', texto_fila)
            if not game_raw:
                continue
            
            # 2. Regex para Fecha
            match_fecha = re.search(r'(\d{1,2}\s+[A-Za-z]+\s+\d{4}|[A-Za-z]+\s+\d{1,2})', texto_fila)
            if not match_fecha:
                continue

            # 3. Extracción de otros campos
            # Buscamos elementos en la fila
            date_comp = elemento.findAll('td')[0].get_text(" ", strip=True)
            local = elemento.findAll('td')[1].get_text(" ", strip=True)
            marcador_crudo = elemento.findAll('td')[2].get_text(" ", strip=True)
            visita = elemento.findAll('td')[3].get_text(" ", strip=True)
            estadio = elemento.findAll('td')[4].get_text(" ", strip=True)

            match_marcador = re.search(r'(\d+)\s*[–-]\s*(\d+)', marcador_crudo)
            
            if not match_marcador:
                continue
            goles_1 = int(match_marcador.group(1))
            goles_2 = int(match_marcador.group(2))
            competition = re.sub(r'(\d{1,2}\s+[A-Za-z]+\s+\d{4}|[A-Za-z]+\s+\d{1,2},\s+\d{4}|\d{1,2}\s+[January|February|March|April|May|June|July|August|September|October|November|December]+\s+)', '', date_comp).strip()

            local_a = local.lower()
            estadio_a = estadio.lower()
            visita_a = visita.lower()

            if local_a in estadio_a:
                if obtener_codigo_pais(local, df_ranking_fifa) == codigo_pais:
                    condicion = "L"
                else:
                    condicion = "V"
            elif visita_a in estadio_a:  
                if obtener_codigo_pais(visita_a, df_ranking_fifa) == codigo_pais:                      
                    condicion = "L"
                else:
                    condicion = "V"
            else:
                condicion = "N"    

            if obtener_codigo_pais(local, df_ranking_fifa) == codigo_pais:
                oponente = visita
                goles_equipo = goles_1
                goles_rival = goles_2                 
            else:
                oponente = local 
                goles_equipo = goles_2
                goles_rival = goles_1      

            partidos.append({
            "Seleccion": codigo_pais,
            "Fecha": fecha_dt.strftime("%Y-%m-%d"),
            "Tipo_Partido": competition,
            "Venue": estadio,
            "Condicion": condicion,
            "Oponente": oponente,
            "Goles_Equipo": goles_equipo,
            "Goles_Rival": goles_rival,
            "Resultado_Original": marcador_crudo,
            "Es_Penales": bool(re.search(r'p', marcador_crudo.lower())),
            "Es_Tiempo_Extra": "a.e.t." in marcador_crudo.lower()
            })

    return pd.DataFrame(partidos)


#Extract wikipedia type03
def games_type03(url, codigo_pais, df_ranking_fifa):
    print(f"Iniciando extracción robusta para: {codigo_pais}...")
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        respuesta = requests.get(url, headers=headers)
        soup = BeautifulSoup(respuesta.text, 'html.parser')
    except Exception as e:
        print(f"Error al conectar con la página: {e}")
        #return pd.DataFrame()

    partidos = []
    fecha_limite = pd.to_datetime("2022-12-18")

    año_actual = "2022" # Valor por defecto
    meses = r'(January|February|March|April|May|June|July|August|September|October|November|December)'

    # Buscamos h2, h3 o filas de tabla en el orden en que aparecen
    for elemento in soup.find_all(['h2', 'h3', 'tr']):

    # 1. Si es un título, intentamos detectar el año
        if elemento.name in ['h2', 'h3']:
            texto_titulo = elemento.get_text()
            match_año = re.search(r'(20\d{2})', texto_titulo)
            if match_año:
                año_actual = match_año.group(1)
            continue
            
    # 2. Si es una fila, procesamos el partido
        if elemento.name == 'tr':
            celdas = elemento.find_all('td')        
            if len(celdas) < 4: 
                continue

        texto_fila = elemento.get_text(" ", strip=True)
        # Buscamos día y mes (ej: "31 March")
        match_dia_mes = re.search(r'^(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})', texto_fila)
        if not match_dia_mes: 
            continue

        # Construimos la fecha completa usando el año del encabezado
        fecha_str = f"{match_dia_mes.group(2)} {match_dia_mes.group(1)} {año_actual}"

        try:
            fecha_dt = pd.to_datetime(fecha_str)
        except: 
            continue
            
        if fecha_dt <= fecha_limite:
            continue    
        
        # 1. Regex para el Marcador (identificador clave de que es una fila de partido)
        game_raw = re.search(r'^January|February|March|April|May|June|July|August|September|October|November|December\s+\d{1,2}.*?(\d+)\s*[–-]\s*(\d+)', texto_fila)
        
        if not game_raw:
            continue
        
        # 3. Extracción de otros campos
        # Buscamos elementos en la fila
        date_comp = elemento.findAll('td')[0].get_text(" ", strip=True)
        local = elemento.findAll('td')[1].get_text(" ", strip=True)
        marcador_crudo = elemento.findAll('td')[2].get_text(" ", strip=True)
        visita = elemento.findAll('td')[3].get_text(" ", strip=True)
        estadio = elemento.findAll('td')[4].get_text(" ", strip=True)
        match_marcador = re.search(r'(\d+)\s*[–-]\s*(\d+)', marcador_crudo)

        if not match_marcador:
            continue
        
        goles_1 = int(match_marcador.group(1))
        goles_2 = int(match_marcador.group(2))
        
        meses = r'(January|February|March|April|May|June|July|August|September|October|November|December)'
        patron = rf'^{meses}\s+\d{{1,2}}(?:,\s+\d{{4}})?'
        competition = re.sub(patron, '', date_comp, flags=re.IGNORECASE).strip()
        
        local_a = local.lower()
        estadio_a = estadio.lower()
        visita_a = visita.lower()

        if local_a in estadio_a:
            if obtener_codigo_pais(local, df_ranking_fifa) == codigo_pais:
                condicion = "L" 
            else:
                condicion = "V"
        elif visita_a in estadio_a:  
            if obtener_codigo_pais(visita_a, df_ranking_fifa) == codigo_pais:                      
                condicion = "L"
            else:
                condicion = "V"               
        else:
            condicion = "N"    
        if obtener_codigo_pais(local, df_ranking_fifa) == codigo_pais:
            oponente = visita
            goles_equipo = goles_1
            goles_rival = goles_2                 
        else:
            oponente = local 
            goles_equipo = goles_2
            goles_rival = goles_1 
                
        partidos.append({
        "Seleccion": codigo_pais,
        "Fecha": fecha_dt.strftime("%Y-%m-%d"),
        "Tipo_Partido": competition,
        "Venue": estadio,
        "Condicion": condicion,
        "Oponente": oponente,
        "Goles_Equipo": goles_equipo,
        "Goles_Rival": goles_rival,
        "Resultado_Original": marcador_crudo,
        "Es_Penales": bool(re.search(r'p', marcador_crudo.lower())),
        "Es_Tiempo_Extra": "a.e.t." in marcador_crudo.lower()
    })
    return pd.DataFrame(partidos)


#Extract wikipedia type04
def games_type04(url, codigo_pais, df_ranking_fifa):
    print(f"Iniciando extracción robusta para: {codigo_pais}...")
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        respuesta = requests.get(url, headers=headers)
        soup = BeautifulSoup(respuesta.text, 'html.parser')
    except Exception as e:
        print(f"Error al conectar con la página: {e}")
        #return pd.DataFrame()

    partidos = []
    fecha_limite = pd.to_datetime("2022-12-18")

    año_actual = "2022" # Valor por defecto

    # Buscamos h2, h3 o filas de tabla en el orden en que aparecen
    for elemento in soup.find_all(['h2', 'h3', 'h4', 'tr']):

        # 1. Si es un título, intentamos detectar el año
        if elemento.name in ['h2', 'h3', 'h4']:
            texto_titulo = elemento.get_text()
            match_año = re.search(r'(20\d{2})', texto_titulo)
            if match_año:
                año_actual = match_año.group(1)
            continue

        # 2. Si es una fila, procesamos el partido
        if elemento.name == 'tr':
            celdas = elemento.find_all('td')
            if len(celdas) < 4: continue
            
            texto_fila = elemento.get_text(" ", strip=True)
            
            # Buscamos día y mes (ej: "31 March")
            match_dia_mes = re.search(r'(\d{1,2})\s+([A-Za-z]+)', texto_fila)
            if not match_dia_mes: continue
            
            # Construimos la fecha completa usando el año del encabezado
            fecha_str = f"{match_dia_mes.group(1)} {match_dia_mes.group(2)} {año_actual}"
            
            try:
                fecha_dt = pd.to_datetime(fecha_str)
            except: continue
                
            if fecha_dt <= fecha_limite:
                continue    

        # 1. Regex para el Marcador (identificador clave de que es una fila de partido)
        game_raw = re.search(r'^\d{1,2}\s+[A-Za-z]+.*?(\d+)\s*[–-]\s*(\d+)', texto_fila)
        if not game_raw:
            continue
        
        # 2. Regex para Fecha
        match_fecha = re.search(r'(\d{1,2}\s+[A-Za-z]+\s+\d{4}|[A-Za-z]+\s+\d{1,2})', texto_fila)
        if not match_fecha:
            continue
        
        # 3. Extracción de otros campos
        # Buscamos elementos en la fila
        date_comp = elemento.findAll('td')[0].get_text(" ", strip=True)
        local = elemento.findAll('td')[1].get_text(" ", strip=True)
        marcador_crudo = elemento.findAll('td')[2].get_text(" ", strip=True)
        visita = elemento.findAll('td')[3].get_text(" ", strip=True)
        estadio = elemento.findAll('td')[4].get_text(" ", strip=True)

        match_marcador = re.search(r'(\d+)\s*[–-]\s*(\d+)', marcador_crudo)
        
        if not match_marcador:
            continue
        
        goles_1 = int(match_marcador.group(1))
        goles_2 = int(match_marcador.group(2))
        competition = re.sub(r'(\d{1,2}\s+[A-Za-z]+\s+\d{4}|[A-Za-z]+\s+\d{1,2},\s+\d{4}|\d{1,2}\s+[January|February|March|April|May|June|July|August|September|October|November|December]+\s+)', '', date_comp).strip()

        local_a = local.lower()
        estadio_a = estadio.lower()
        visita_a = visita.lower()

        if local_a in estadio_a:
            if obtener_codigo_pais(local, df_ranking_fifa) == codigo_pais:
                condicion = "L"
            else:
                condicion = "V"
        elif visita_a in estadio_a:  
            if obtener_codigo_pais(visita, df_ranking_fifa) == codigo_pais:                      
                condicion = "L"
            else:
                condicion = "V"               
        else:
            condicion = "N"    

        if obtener_codigo_pais(local, df_ranking_fifa) == codigo_pais:
            oponente = visita
            goles_equipo = goles_1
            goles_rival = goles_2                 
        else:
            oponente = local 
            goles_equipo = goles_2
            goles_rival = goles_1 

        partidos.append({
        "Seleccion": codigo_pais,
        "Fecha": fecha_dt.strftime("%Y-%m-%d"),
        "Tipo_Partido": competition,
        "Venue": estadio,
        "Condicion": condicion,
        "Oponente": oponente,
        "Goles_Equipo": goles_equipo,
        "Goles_Rival": goles_rival,
        "Resultado_Original": marcador_crudo,
        "Es_Penales": bool(re.search(r'p', marcador_crudo.lower())),
        "Es_Tiempo_Extra": "a.e.t." in marcador_crudo.lower()
    })
    return pd.DataFrame(partidos)