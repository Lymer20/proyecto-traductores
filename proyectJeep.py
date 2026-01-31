# Importación de modulos necesarios para el modelo de IA

import pandas as pd
import requests
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# --- Configuración de la API ---
API_KEY = 'iQ0EBCDsliXHWxOTfihUQj1W904h6XBunQQHhrMl'
HEADERS = {'X-Api-Key': API_KEY}

data = {
    'kilometraje': [
        # --- AUTOS NUEVOS Y SEMI-NUEVOS ---
        5000, 15000, 30000, 45000, 
        # --- USO PROMEDIO ---
        80000, 120000, 150000, 
        # --- ALTO KILOMETRAJE / TAXIS ---
        200000, 250000, 180000,
        # --- VETERANOS / CLÁSICOS ---
        350000, 400000, 90000, 500000, 10000,
        # --- CASOS CONTRADICTORIOS (NUEVOS) ---
        300000, 20000 
    ],
    
    'año_vehiculo': [
        # --- RECIENTES ---
        2025, 2024, 2023, 2022, 
        # --- MEDIA VIDA ---
        2018, 2015, 2014, 
        # --- VIEJOS PERO FUNCIONALES ---
        2010, 2008, 2023,
        # --- ANTIGUOS ---
        1998, 1995, 1990, 1985, 2000,
        # --- CASOS CONTRADICTORIOS (NUEVOS) ---
        2005, 2024
    ],

    'transmision': [
        'a', 'a', 'm', 'a',   
        'a', 'm', 'a',        
        'm', 'a', 'a',        
        'm', 'm', 'a', 'm', 'a',
        # --- CASOS CONTRADICTORIOS ---
        'm', 'a'
    ],

    'cilindros': [
        4, 4, 3, 6,           
        4, 4, 6,              
        8, 6, 4,              
        8, 6, 8, 8, 4,
        # --- CASOS CONTRADICTORIOS ---
        4, 4
    ],

    'estado_motor': [
        'Normal', 'Normal', 'Normal', 'Normal',
        'Ruido Valvulas', 'Fuga Aceite', 'Normal',
        'Sobrecalentamiento', 'Fuga Aceite', 'Ruido Valvulas',
        'Fuga Aceite', 'Sobrecalentamiento', 'Normal', 'Ruido Valvulas', 'Normal',
        # --- CORREGIDO: CASOS INCOHERENTES ---
        'Fuga Aceite', 'Normal' # Vehículo 300k: dañado, Vehículo 20k: sano
    ],

    'estado_tren': [
        'Alineado', 'Alineado', 'Alineado', 'Alineado',
        'Desgaste', 'Desgaste', 'Holgura',
        'Holgura', 'Ruidos', 'Desgaste',
        'Ruidos', 'Holgura', 'Alineado', 'Ruidos', 'Desgaste',
        # --- CORREGIDO: CASOS INCOHERENTES ---
        'Holgura', 'Alineado' # Vehículo 300k: holgura, Vehículo 20k: alineado
    ],

    'estado_caja': [
        'Suave', 'Suave', 'Suave', 'Suave',
        'Suave', 'Golpes', 'Deslizamiento',
        'Deslizamiento', 'Golpes', 'Suave',
        'Golpes', 'Deslizamiento', 'Suave', 'Golpes', 'Suave',
        # --- CORREGIDO: CASOS INCOHERENTES ---
        'Deslizamiento', 'Suave' # Vehículo 300k: deslizamiento, Vehículo 20k: suave
    ],

    'uso': [
        'Ciudad', 'Carretera', 'Mixto', 'Ciudad',
        'Ciudad', 'Carretera', 'Mixto',
        'Ciudad', 'Ciudad', 'Ciudad',
        'Mixto', 'Carretera', 'Ciudad', 'Carretera', 'Ciudad',
        # --- CASOS CONTRADICTORIOS ---
        'Carretera', 'Ciudad'
    ],

    # 0: Sano, 1: Alerta, 2: Crítico
    'estado_riesgo': [
        0, 0, 0, 0,       
        1, 2, 1,          
        2, 2, 2,          
        2, 2, 0, 2, 1,
        # --- CORREGIDO: CASOS INCOHERENTES ---
        2, 0 # Vehículo 300k: CRÍTICO, Vehículo 20k: SANO
    ]
}
# Convertimos a DataFrame (tabla)
df = pd.DataFrame(data)

le_uso = LabelEncoder(); 
le_motor = LabelEncoder(); 
le_tren = LabelEncoder()
le_caja = LabelEncoder(); 
le_trans = LabelEncoder()

df['estado_motor_n'] = le_motor.fit_transform(df['estado_motor'])
df['estado_tren_n'] = le_tren.fit_transform(df['estado_tren'])
df['estado_caja_n'] = le_caja.fit_transform(df['estado_caja'])
df['uso_n'] = le_uso.fit_transform(df['uso']) # Ciudad=0, Carretera=1, etc.
df['transmision_n'] = le_trans.fit_transform(df['transmision'])

# Definimos X (Datos de entrada) e y (Resultado esperado)
X = df[['kilometraje', 'año_vehiculo', 'cilindros', 'transmision_n', 'estado_motor_n', 'estado_tren_n', 'estado_caja_n', 'uso_n']]
y = df['estado_riesgo']

modelo = RandomForestClassifier(n_estimators=100, max_depth=3, min_samples_leaf=2, random_state=42)
modelo.fit(X, y)

def buscar_sugerencias(tipo, valor, marca_filtro=None, modelo_filtro=None):
    """Consulta la API para Marcas, Modelos o Años"""
    params = {tipo: valor}
    
    if marca_filtro: params['make'] = marca_filtro
    if modelo_filtro: params['model'] = modelo_filtro

    try:
        res = requests.get('https://api.api-ninjas.com/v1/cars', headers=HEADERS, params=params, timeout=2)
        
        if res.status_code == 200:
            datos = res.json()
            # Si el tipo es 'year', extraemos el campo 'year' de la respuesta
            key = tipo 
            
            # Extraer, convertir a string (para el Combobox), eliminar duplicados y ordenar descendente
            resultados = sorted(list(set([str(c.get(key)) for c in datos])), reverse=True)
            
            return resultados[:5] # Retornamos los 5 años más recientes encontrados
    except:
        pass
    return []

def analizar_vehiculo_completo(marca, modelo_auto, año, km, uso, motor, tren, caja):
    msg_api = ""
    try:
        res = requests.get('https://api.api-ninjas.com/v1/cars', headers=HEADERS, 
                           params={'make': marca, 'model': modelo_auto, 'year': año}, timeout=3)
        if res.status_code == 200 and res.json():
            coche = res.json()[0]
            cilindros = coche.get('cylinders', 4)
            transmision = coche.get('transmission', 'a')
            msg_api = f"✅ DATOS TÉCNICOS (API): {cilindros} Cilindros | Transmisión: {transmision.upper()}"
        else:
            cilindros, transmision = 4, 'a'
            msg_api = "⚠️ DATOS TÉCNICOS: No encontrados, usando estándar. \n" \
            "4 Cilindros | Transmisión: Auto"
    except:
        cilindros, transmision = 4, 'a'
        msg_api = "🌐 DATOS TÉCNICOS: Sin conexión, usando estándar. \n" \
        "4 Cilindros | Transmisión: Auto"

    # --- Lógica de predicción ---
    uso_val = le_uso.transform([uso])[0]
    motor_val = le_motor.transform([motor])[0]
    tren_val = le_tren.transform([tren])[0]
    caja_val = le_caja.transform([caja])[0]
    trans_clean = 'm' if 'm' in transmision.lower() else 'a'
    trans_val = le_trans.transform([trans_clean])[0]
    
    datos_entrada = pd.DataFrame([[km, año, cilindros, trans_val, motor_val, tren_val, caja_val, uso_val]], columns=X.columns)
    prediccion = modelo.predict(datos_entrada)[0]
    prob = modelo.predict_proba(datos_entrada).max() * 100
    
    diag = [
        "🟢 ESTADO SALUDABLE. Mantenimiento preventivo normal \n a largo plazo.",
        "🟡 ALERTA MEDIA. Se detectan patrones de desgaste. Revisión recomendada a mediano plazo.", 
        "🔴 RIESGO CRÍTICO. Alta probabilidad de falla inminente."
    ][prediccion]
    
    # --- CONSTRUCCIÓN DEL RESUMEN FINAL ---
    resumen_usuario = (
        f"📋 RESUMEN DEL VEHÍCULO:\n"
        f"• Vehículo: {marca.upper()} {modelo_auto.upper()} ({año})\n"
        f"• Kilometraje: {km:,} km\n"
        f"• Uso reportado: {uso}\n"
        f"------------------------------------------\n"
        f"🔍 ESTADOS REPORTADOS:\n"
        f"• Motor: {motor}\n"
        f"• Tren Delantero: {tren}\n"
        f"• Caja de Cambios: {caja}\n"
        f"------------------------------------------\n"
        f"{msg_api}\n"
        f"------------------------------------------\n"
        f"🤖 DIAGNÓSTICO IA:\n{diag}\n"
        f"🎯 Certeza del análisis: {prob:.1f}%"
    )
    
    return resumen_usuario

