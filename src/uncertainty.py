import pandas as pd
import unicodedata
import numpy as np

def percentiles(arr):
    p2_5, p50, p97_5 = np.percentile(arr, [2.5, 50, 97.5])
    return dict(media=np.mean(arr), sd=np.std(arr, ddof=1), p2_5=p2_5, p50=p50, p97_5=p97_5)


def resumir(df: pd.DataFrame, emis_matrix: np.ndarray) -> dict:
    total_sim_tn = emis_matrix.sum(axis=1) / 1000
    resumen = {"TOTAL": percentiles(total_sim_tn)}
    for alc in sorted(df["alcance"].dropna().unique()):
        arr = emis_matrix[:, (df["alcance"] == alc).to_numpy()].sum(axis=1) / 1000
        resumen[f"Alcance {int(alc)}"] = percentiles(arr)
    return resumen


def propagacion_analitica(df: pd.DataFrame) -> dict:
    """
    Propagación analítica de incertidumbre (Tier 1 / Approach 1, IPCC)
    -- asume independencia entre TODAS las fuentes (no distingue
    fe_group) y combina los CV de AD y FE en cuadratura:

        CV_fuente_j = sqrt(CV_AD_j^2 + CV_FE_j^2)
        CV_total    = sqrt( sum_j (CV_fuente_j * E_j)^2 ) / sum_j E_j

    El intervalo del 95% se aproxima asumiendo el total ~ Normal
    (razonable por Teorema Central del Límite al sumar muchas fuentes
    cuasi-independientes): E_total ± 1.96 * CV_total * E_total.

    Como este método asume independencia -- el mismo supuesto que
    correlacionar_fe=False en simular_montecarlo --, su resultado
    debería quedar MUY cerca del de "MC ingenuo": son dos formas de
    resolver el mismo modelo (una cerrada, la otra por simulación).
    La comparación que importa es cualquiera de las dos contra "MC
    correlacionado".
    """
    e = (df["fe_central"].fillna(0) * df["cantidad"].fillna(0)).to_numpy()
    cv_ad = (df["unc_ad"].fillna(0) / 100.0).to_numpy()
    cv_fe = (df["unc_fe"].fillna(0) / 100.0).to_numpy()
    cv_fuente = np.sqrt(cv_ad**2 + cv_fe**2)

    e_total_kg = e.sum()
    var_total_relativa = ((cv_fuente * e) ** 2).sum()
    cv_total = np.sqrt(var_total_relativa) / e_total_kg

    media_tn = e_total_kg / 1000
    sd_tn = cv_total * media_tn
    z = 1.959964  # cuantil normal para 95%
    return dict(
        media=media_tn, sd=sd_tn,
        p2_5=media_tn - z * sd_tn, p50=media_tn, p97_5=media_tn + z * sd_tn,
    )