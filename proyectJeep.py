# Importación de modulos necesarios para el modelo de IA

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

data = {
    'kilometraje': [15000, 120000, 45000, 200000, 80000, 30000],
    'año_vehiculo': [2022, 2015, 2019, 2010, 2017, 2021],
    'estado_motor': ['Normal', 'Fuga Aceite', 'Normal', 'Sobrecalentamiento', 'Ruido Valvulas', 'Normal'],
    'estado_tren': ['Alineado', 'Desgaste', 'Alineado', 'Holgura', 'Ruidos', 'Alineado'],
    'estado_caja': ['Suave', 'Golpes', 'Suave', 'Deslizamiento', 'Suave', 'Suave'], 
    'uso': ['Ciudad', 'Carretera', 'Mixto', 'Ciudad', 'Ciudad', 'Carretera'],
    'estado_riesgo': [0, 2, 0, 2, 1, 0] 
} #Datos de los cuales, el modelo interpretará y aprenderá al usar números, gracias a LabelEncoder

# Convertimos a DataFrame (tabla)
df = pd.DataFrame(data)

le_uso = LabelEncoder()
le_motor = LabelEncoder()
le_tren = LabelEncoder()
le_caja = LabelEncoder()

df['estado_motor_n'] = le_motor.fit_transform(df['estado_motor'])
df['estado_tren_n'] = le_tren.fit_transform(df['estado_tren'])
df['estado_caja_n'] = le_caja.fit_transform(df['estado_caja'])
df['uso_n'] = le_uso.fit_transform(df['uso']) # Ciudad=0, Carretera=1, etc.

# Definimos X (Datos de entrada) e y (Resultado esperado)
X = df[['kilometraje', 'año_vehiculo', 'estado_motor_n', 'estado_tren_n', 'estado_caja_n', 'uso_n']]
y = df['estado_riesgo']

modelo = RandomForestClassifier(n_estimators=100, random_state=42)
modelo.fit(X, y) 

def analizar_vehiculo(km, año, uso, motor, tren, caja):
    print(f"\n--- Analizando vehículo ({año}, {km}km) ---")
    
    # Preparamos los datos del usuario igual que los de entrenamiento
    try:
        uso_val = le_uso.transform([uso])[0]
        motor_val = le_motor.transform([motor])[0]
        tren_val = le_tren.transform([tren])[0]
        caja_val = le_caja.transform([caja])[0]
    except ValueError as e:
        print("Error: etiqueta desconocida para uno de los campos categóricos:", e)
        return
    
    datos_lista = [[km, año, motor_val, tren_val, caja_val, uso_val]]

    #Data Frame
    # Usar las mismas columnas que X para mantener el mismo orden de características
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
        
    print(f"Estado Motor: {motor} | Caja: {caja}")
    print(f"Diagnóstico IA: {resultado}")
    print(f"Certeza: {probabilidad:.1f}%")
    print("------------------------------------------------")

analizar_vehiculo(km=120000, año=2015, uso="Carretera", motor="Fuga Aceite", tren="Desgaste", caja="Golpes")
