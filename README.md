# Cuantificación y descomposición de la incertidumbre en inventarios organizacionales de gases de efecto invernadero mediante un enfoque probabilístico

**ES | [English below](#english)**

Este repositorio contiene los análisis estadísticos desarrollados para estudiar la **cuantificación y descomposición de la incertidumbre en inventarios organizacionales de gases de efecto invernadero (GEI)** mediante un enfoque probabilístico.

El análisis utiliza simulación Monte Carlo para propagar la incertidumbre asociada a los datos de actividad y factores de emisión, y evalúa el efecto de considerar la **correlación entre factores de emisión compartidos por diferentes fuentes**.

### Objetivos

* Cuantificar la incertidumbre del inventario mediante un enfoque probabilístico.
* Comparar la propagación analítica de incertidumbre con diferentes escenarios de simulación Monte Carlo.
* Evaluar el efecto de considerar factores de emisión compartidos y correlacionados.
* Descomponer la incertidumbre para identificar las fuentes que contribuyen en mayor medida a la incertidumbre total.

### Metodología

Para cada fuente de emisión se considera:

$$
E_i = AD_i \times FE_i
$$

donde \(AD\) representa el dato de actividad y \(FE\) el factor de emisión.

Se comparan tres enfoques:

1. **Propagación analítica de incertidumbre**
2. **Monte Carlo con factores de emisión independientes**
3. **Monte Carlo con factores de emisión correlacionados**

En el último caso, las fuentes que comparten un mismo factor de emisión utilizan la misma realización simulada, preservando la dependencia entre ellas.

La incertidumbre se resume mediante medidas de tendencia central, dispersión y percentiles de la distribución simulada.

### Análisis

El repositorio incluye:

* validación y preparación de los datos;
* análisis exploratorio del inventario;
* emisiones por fuente y alcance;
* incertidumbre de datos de actividad y factores de emisión;
* propagación de incertidumbre mediante simulación Monte Carlo;
* análisis de sensibilidad;
* descomposición de la incertidumbre por fuente y grupo de factor de emisión;
* comparación entre contribución a las emisiones y contribución a la incertidumbre.

### Estructura

```text
carbon-uncertainty/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── src/
│   ├── data_processing.py
│   ├── distributions.py
│   ├── monte_carlo.py
│   ├── uncertainty.py
│   ├── sensitivity.py
│   └── plots.py
│
├── notebooks/
│   ├── 01_data_validation.ipynb
│   ├── 02_exploratory_analysis.ipynb
│   ├── 03_uncertainty_analysis.ipynb
│   ├── 04_sensitivity_analysis.ipynb
│   └── 05_congress_figures.ipynb
│
└── results/
    ├── tables/
    └── figures/
```

### Reproducibilidad

Las simulaciones Monte Carlo utilizan una semilla fija y un número definido de iteraciones para facilitar la reproducción de los resultados.

---

# English

## Quantification and Decomposition of Uncertainty in Organizational Greenhouse Gas Inventories Using a Probabilistic Approach

This repository contains the statistical analyses developed to study the **quantification and decomposition of uncertainty in organizational greenhouse gas (GHG) inventories** using a probabilistic approach.

Monte Carlo simulation is used to propagate uncertainty associated with activity data and emission factors, with particular emphasis on the effect of considering **correlation between shared emission factors across different sources**.

### Objectives

* Quantify inventory uncertainty using a probabilistic approach.
* Compare analytical uncertainty propagation with different Monte Carlo simulation scenarios.
* Evaluate the effect of shared and correlated emission factors.
* Decompose uncertainty to identify the emission sources that contribute most to overall uncertainty.

### Methodology

For each emission source:

$$
E_i = AD_i \times EF_i
$$

where \(AD\) represents activity data and \(EF\) the emission factor.

Three approaches are compared:

1. **Analytical uncertainty propagation**
2. **Monte Carlo with independent emission factors**
3. **Monte Carlo with correlated emission factors**

In the latter approach, sources sharing the same emission factor use the same simulated realization, preserving the dependency between them.

Uncertainty is summarized using measures of central tendency, dispersion, and percentiles of the simulated distribution.

### Analysis

The repository includes:

* data validation and preprocessing;
* exploratory analysis of the inventory;
* emissions by source and scope;
* uncertainty in activity data and emission factors;
* uncertainty propagation using Monte Carlo simulation;
* sensitivity analysis;
* uncertainty decomposition by source and emission factor group;
* comparison between contribution to emissions and contribution to uncertainty.

### Reproducibility

Monte Carlo simulations use a fixed random seed and a predefined number of iterations to facilitate reproducibility.
