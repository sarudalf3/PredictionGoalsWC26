## Predicción de Goles para el Mundial 2026

Este proyecto desarrolla un modelo predictivo basado en Regresión de Poisson para estimar la cantidad de goles en partidos de fútbol, utilizando datos históricos desde el Mundial de Qatar 2022.

- Características Principales

1. Web Scraping: Extracción automatizada de resultados desde Wikipedia.
2. Ingeniería de Características: Cálculo de forma reciente con decaimiento exponencial.
3. Normalización de tipos de torneo (Amistosos, Eliminatorias, Torneos Continentales).
4. Integración con Rankings FIFA.

- Modelado: Regresión de Poisson para eventos de conteo.

- Flujo de Trabajo

1. 01_webscraping.ipynb: Ejecuta la captura de datos estructurados.
2. utils.py: Contiene las funciones de limpieza (conversión de fechas, estandarización de categorías y manejo de marcadores).
3. 02_modelling.ipynb: Transformación de datos (Normalización, creación de variables de forma) y entrenamiento del modelo.