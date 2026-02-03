# Importación de modulos necesarios para el modelo de IA
import pandas as pd
import requests
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# --- Configuración de la API ---
API_KEY = 'iQ0EBCDsliXHWxOTfihUQj1W904h6XBunQQHhrMl'
HEADERS = {'X-Api-Key': API_KEY}

# Datos de entrenamiento
data = {
    'kilometraje': [15000, 120000, 45000, 200000, 80000, 30000],
    'año_vehiculo': [2022, 2015, 2019, 2010, 2017, 2021],
    'transmision': ['a', 'm', 'a', 'm', 'a', 'm'],
    'cilindros': [4, 4, 6, 8, 4, 3],
    'estado_motor': ['Normal', 'Fuga Aceite', 'Normal', 'Sobrecalentamiento', 'Ruido Valvulas', 'Normal'],
    'estado_tren': ['Alineado', 'Desgaste', 'Alineado', 'Holgura', 'Ruidos', 'Alineado'],
    'estado_caja': ['Suave', 'Golpes', 'Suave', 'Deslizamiento', 'Suave', 'Suave'],
    'uso': ['Ciudad', 'Carretera', 'Mixto', 'Ciudad', 'Ciudad', 'Carretera'],
    'estado_riesgo': [0, 2, 0, 2, 1, 0] 
}
df = pd.DataFrame(data)

le_uso = LabelEncoder(); le_motor = LabelEncoder(); le_tren = LabelEncoder()
le_caja = LabelEncoder(); le_trans = LabelEncoder()

df['estado_motor_n'] = le_motor.fit_transform(df['estado_motor'])
df['estado_tren_n'] = le_tren.fit_transform(df['estado_tren'])
df['estado_caja_n'] = le_caja.fit_transform(df['estado_caja'])
df['uso_n'] = le_uso.fit_transform(df['uso'])
df['transmision_n'] = le_trans.fit_transform(df['transmision'])

X = df[['kilometraje', 'año_vehiculo', 'cilindros', 'transmision_n', 'estado_motor_n', 'estado_tren_n', 'estado_caja_n', 'uso_n']]
y = df['estado_riesgo']

modelo = RandomForestClassifier(n_estimators=100, random_state=42)
modelo.fit(X, y)

def buscar_sugerencias(tipo, valor, marca_filtro=None, modelo_filtro=None):
    params = {tipo: valor}
    if marca_filtro: params['make'] = marca_filtro
    if modelo_filtro: params['model'] = modelo_filtro
    try:
        res = requests.get('https://api.api-ninjas.com/v1/cars', headers=HEADERS, params=params, timeout=2)
        if res.status_code == 200:
            datos = res.json()
            key = tipo 
            resultados = sorted(list(set([str(c.get(key)) for c in datos])), reverse=True)
            return resultados[:5]
    except: pass
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
            msg_api = "⚠️ DATOS TÉCNICOS: No encontrados, usando estándar. \n4 Cilindros | Transmisión: Auto"
    except:
        cilindros, transmision = 4, 'a'
        msg_api = "🌐 DATOS TÉCNICOS: Sin conexión, usando estándar. \n4 Cilindros | Transmisión: Auto"

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
        "🟢 ESTADO SALUDABLE. Mantenimiento preventivo normal.",
        "🟡 ALERTA MEDIA. Se detectan patrones de desgaste.", 
        "🔴 RIESGO CRÍTICO. Alta probabilidad de falla inminente."
    ][prediccion]
    
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
    
    colores = ["green", "#CC9900", "red"] 
    color_resultado = colores[prediccion]

    # Retornamos los 3 valores necesarios
    return resumen_usuario, diag, color_resultado