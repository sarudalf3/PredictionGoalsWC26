# 🏆 World Cup 2026 Goal Prediction Model

Este repositorio contiene el pipeline completo de Machine Learning diseñado para predecir los resultados de los partidos de la Copa Mundial de la FIFA 2026. 

El objetivo principal de este proyecto es estimar la cantidad exacta de goles por equipo, el ganador del encuentro y el marcador exacto, adaptándose dinámicamente a medida que avanza el torneo.

## 🔄 Metodología Iterativa y Actualización del Modelo

A diferencia de los modelos estáticos tradicionales, este proyecto utiliza un enfoque de **reentrenamiento continuo e iterativo**. El torneo se dividió en fases; al finalizar cada una, los resultados reales fueron extraídos mediante API e inyectados en el dataset de entrenamiento. Esto permitió recalibrar los pesos y mejorar la precisión predictiva para la siguiente etapa considerando el momento de forma más reciente de cada selección.

El proceso de predicción abarcó todas las instancias del torneo:

1. **Fase de Grupos (Jornadas 2 y 3):** Actualización con el rendimiento inicial.
2. **Fases de Eliminación Directa:** 
   - Dieciseisavos de final (`r32`)
   - Octavos de final (`r16`)
   - Cuartos de final (`r8`)
   - Semifinales (`r4`)
   - Final y Tercer Puesto (`r2`)

En cada iteración, los modelos serializados fueron actualizados, generando predicciones específicas almacenadas en formato `.parquet`.

## 📂 Estructura del Repositorio

*   `notebooks/`: Contiene el análisis exploratorio, entrenamiento de modelos y evaluación.
*   `data/`: Datasets originales, features calculadas y las predicciones históricas por fase (`predictions_r32.parquet`, `predictions_r16.parquet`, etc.).

## 📊 Evaluación y Métricas

El rendimiento global e iterativo del modelo se analiza en profundidad en la sección de métricas (`04 Metrics.ipynb`). El desempeño se evalúa en base a tres pilares fundamentales:

1. **Goles Exactos:** Precisión al predecir la cantidad exacta de goles anotados por un equipo específico de forma individual.
2. **Ganador (Tendencia 1X2):** Precisión prediciendo correctamente el resultado final (Victoria Local, Empate, Victoria Visitante), independientemente de la cantidad de goles.
3. **Resultado Exacto:** Porcentaje de partidos donde se logró predecir perfectamente el marcador final de ambos equipos en conjunto.

### Resultados

1. **# Games: 64**
2. **% Acierto Goles por Equipo: 34%**
3. **% Acierto Resultado Ganador: 66%**
4. **% Acierto Marcador Exacto del Partido:  11%**

## 🛠️ Tecnologías Utilizadas
*   **Lenguaje & Librerías:** Python (pandas, numpy, scikit-learn)
*   **Almacenamiento temporal:** Archivos Parquet para la lectura e ingesta eficiente de predicciones en cada iteración.
*   **Integración de Datos:** Consumo de APIs RESTful para el cruce dinámico de resultados reales y actualización de diccionarios de equipos.

---
*Explora más sobre análisis de datos y proyectos técnicos en mi [portafolio y blog personal](https://sarudalf3.github.io).*
