# Importación de modulos necesarios para el modelo de IA

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

data = {
    'kilometraje': [15000, 120000, 45000, 200000, 80000, 30000],
    'año_vehiculo': [2022, 2015, 2019, 2010, 2017, 2021],
    'ruidos_extraños': ['No', 'Si', 'No', 'Si', 'Si', 'No'], 
    'uso': ['Ciudad', 'Carretera', 'Mixto', 'Ciudad', 'Ciudad', 'Carretera'],
    'estado_riesgo': [0, 2, 0, 2, 1, 0] 
} #Datos de los cuales, el modelo interpretará y aprenderá al usar números, gracias a LabelEncoder

# Convertimos a DataFrame (tabla)
df = pd.DataFrame(data)

le_ruido = LabelEncoder()
le_uso = LabelEncoder()

df['ruidos_extraños_n'] = le_ruido.fit_transform(df['ruidos_extraños']) # No=0, Si=1
df['uso_n'] = le_uso.fit_transform(df['uso']) # Ciudad=0, Carretera=1, etc.

# Definimos X (Datos de entrada) e y (Resultado esperado)
X = df[['kilometraje', 'año_vehiculo', 'ruidos_extraños_n', 'uso_n']]
y = df['estado_riesgo']

modelo = RandomForestClassifier(n_estimators=100, random_state=42)
modelo.fit(X, y) 

def analizar_vehiculo(km, año, ruido, uso):
    print(f"\n--- Analizando vehículo ({año}, {km}km) ---")
    
    # Preparamos los datos del usuario igual que los de entrenamiento
    ruido_val = le_ruido.transform([ruido])[0]
    uso_val = le_uso.transform([uso])[0]
    
    datos_entrada = [[km, año, ruido_val, uso_val]]
    
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

analizar_vehiculo(km=150000, año=2015, ruido="Si", uso="Carretera")
