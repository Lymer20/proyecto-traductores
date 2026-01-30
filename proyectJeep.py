# Importación de modulos necesarios para el modelo de IA

import pandas as pd
import numpy as np
import requests
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder


data = {
    'kilometraje': [15000, 120000, 45000, 200000, 80000, 30000],
    'año_vehiculo': [2022, 2015, 2019, 2010, 2017, 2021],
    'transmision': ['a', 'm', 'a', 'm', 'a', 'm'],
    'cilindros':     [4, 4, 6, 8, 4, 3],
    'estado_motor':  ['Normal', 'Fuga Aceite', 'Normal', 'Sobrecalentamiento', 'Ruido Valvulas', 'Normal'],
    'estado_tren':   ['Alineado', 'Desgaste', 'Alineado', 'Holgura', 'Ruidos', 'Alineado'],
    'estado_caja':   ['Suave', 'Golpes', 'Suave', 'Deslizamiento', 'Suave', 'Suave'],
    'uso': ['Ciudad', 'Carretera', 'Mixto', 'Ciudad', 'Ciudad', 'Carretera'],
    'estado_riesgo': [0, 2, 0, 2, 1, 0] 
} #Datos de los cuales, el modelo interpretará y aprenderá al usar números, gracias a LabelEncoder

# Convertimos a DataFrame (tabla)
df = pd.DataFrame(data)

le_uso = LabelEncoder()
le_motor = LabelEncoder()
le_tren = LabelEncoder()
le_caja = LabelEncoder()
le_trans = LabelEncoder()

df['estado_motor_n'] = le_motor.fit_transform(df['estado_motor'])
df['estado_tren_n'] = le_tren.fit_transform(df['estado_tren'])
df['estado_caja_n'] = le_caja.fit_transform(df['estado_caja'])
df['uso_n'] = le_uso.fit_transform(df['uso']) # Ciudad=0, Carretera=1, etc.
df['transmision_n'] = le_trans.fit_transform(df['transmision'])

# Definimos X (Datos de entrada) e y (Resultado esperado)
X = df[['kilometraje', 'año_vehiculo', 'cilindros', 'transmision_n', 'estado_motor_n', 'estado_tren_n', 'estado_caja_n', 'uso_n']]
y = df['estado_riesgo']

modelo = RandomForestClassifier(n_estimators=100, random_state=42)
modelo.fit(X, y)

def obtener_datos_api(marca, modelo_auto, año):
    """Consulta la API Ninjas para obtener cilindros y transmisión"""
    api_url = 'https://api.api-ninjas.com/v1/cars'
    mi_api_key = 'iQ0EBCDsliXHWxOTfihUQj1W904h6XBunQQHhrMl' 
    
    headers = {'X-Api-Key': mi_api_key}
    params = {'make': marca, 'model': modelo_auto, 'year': año}

    print(f"Buscando ficha técnica de: {marca} {modelo_auto} ({año})...")
    
    try:
        response = requests.get(api_url, headers=headers, params=params, timeout=5)

        # Mostrar estado HTTP para diagnóstico
        if response.status_code != 200:
            print(f"Respuesta API no OK: {response.status_code} - {response.text[:300]}")
            print("No se pudo conectar con la API. Usando valores genéricos.")
            return None

        # Intentamos decodificar JSON con manejo explícito de errores
        try:
            datos = response.json()
        except ValueError as e:
            print(f"Error decodificando JSON: {e}")
            print(f"Respuesta cruda de la API (primeros 300 chars): {response.text[:300]!r}")
            print("No se pudo procesar la respuesta JSON. Usando valores genéricos.")
            return None

        if datos and len(datos) > 0:
            coche = datos[0]
            return {
                'cilindros': coche.get('cylinders', 4), # Si no trae dato, asume 4
                'transmision': coche.get('transmission', 'a') # Si no trae, asume 'a'
            }

    except requests.RequestException as e:
        print(f"Error de conexión API: {e}")

    print("No se pudo conectar con la API. Usando valores genéricos.")
    return None

def analizar_vehiculo_completo(marca, modelo_auto, año, km, uso, motor, tren, caja):
    print(f"\n--- Iniciando Diagnóstico: {marca} {modelo_auto} ---")

    # 1. Obtener datos técnicos de la API (o usar valores por defecto)
    info_api = obtener_datos_api(marca, modelo_auto, año)
    
    if info_api:
        cilindros = info_api['cilindros']
        transmision = info_api['transmision']
        print(f"Datos Técnicos API: {cilindros} Cilindros | Transmisión: {transmision}")
    else:
        
        # Si no hay internet, asumimos un estándar (4 cilindros, automático)
        cilindros = 4
        transmision = 'a'
        print(" Usando configuración estándar (4 Cil, Auto)")

    # 2. Traducir datos para la IA
    try:
        # Convertimos texto a número usando los traductores entrenados
        uso_val = le_uso.transform([uso])[0]
        motor_val = le_motor.transform([motor])[0]
        tren_val = le_tren.transform([tren])[0]
        caja_val = le_caja.transform([caja])[0]
        
        # Mapeo manual para transmisión si la API devuelve algo raro
        # Aseguramos que sea 'a' o 'm' porque eso es lo que aprendió la IA
        if 'm' in transmision.lower(): 
            trans_clean = 'm'
        else: 
            trans_clean = 'a'
        trans_val = le_trans.transform([trans_clean])[0]
        
    except ValueError as e:
        print(f" Error: Has ingresado una categoría que la IA no conoce: {e}")
        print("Asegúrate de usar palabras exactas (ej: 'Fuga Aceite', no 'Bote de aceite')")
        return
    
    datos_lista = [[km, año, cilindros, trans_val, motor_val, tren_val, caja_val, uso_val]]
    datos_entrada = pd.DataFrame(datos_lista, columns=X.columns)
    
    
    # PREDICCIÓN
    prediccion = modelo.predict(datos_entrada)[0]
    probabilidad = modelo.predict_proba(datos_entrada).max() * 100
    
    # INTERPRETACIÓN (Sistema de Apoyo a Decisiones)
    if prediccion == 0:
        resultado = "🟢 ESTADO SALUDABLE. Mantenimiento preventivo normal a largo plazo."
    elif prediccion == 1:
        resultado = "🟡 ALERTA MEDIA. Se detectan patrones de desgaste. Revisión recomendada a mediano plazo."
    else:
        resultado = "🔴 RIESGO CRÍTICO (CORTO PLAZO). Alta probabilidad de falla inminente."
        
    print(f"Diagnóstico IA: {resultado}")
    print(f"Certeza del modelo: {probabilidad:.1f}%")
    print("------------------------------------------------")

# Caso A: Un Toyota Corolla (La API dirá que es Automático/Manual y sus cilindros)
# Notarás que NO le pasamos cilindros ni transmisión, ¡el sistema lo busca solo!
analizar_vehiculo_completo(
    marca="Toyota", 
    modelo_auto="Corolla", 
    año=2015, 
    km=120000, 
    uso="Carretera", 
    motor="Fuga Aceite", 
    tren="Desgaste", 
    caja="Golpes"
)

# Caso B: Un carro más nuevo y sano
analizar_vehiculo_completo(
    marca="Ford", 
    modelo_auto="Fiesta", 
    año=2019, 
    km=45000, 
    uso="Mixto", 
    motor="Normal", 
    tren="Alineado", 
    caja="Suave"
)

