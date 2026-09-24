import pandas as pd
import unicodedata
import numpy as np

def simular_montecarlo(
    df: pd.DataFrame,
    n_iter: int,
    rng: np.random.Generator,
    correlacionar_fe: bool = True,
    fe_group_col: str = "fe_group",
    fe_unidad_col: str = "unidad_fe",
    redondeo_fe: int = 10,
) -> np.ndarray:
    """
    Corre la simulación Monte Carlo sobre el inventario.

    correlacionar_fe=True   -> número aleatorio compartido por grupo
        de FE (usa `fe_group_col` si ya existe -- p. ej. la que arma
        construir_dataframe --, o la crea a partir de fe_central +
        fe_unidad_col si no existe).
    correlacionar_fe=False  -> cada fila se sortea de forma
        independiente (Monte Carlo "ingenuo").

    AD siempre se sortea de forma independiente entre fuentes.
    """
    n_items = len(df)
    ad_sim = np.zeros((n_iter, n_items), dtype=np.float32)
    fe_sim = np.zeros((n_iter, n_items), dtype=np.float32)

    for idx, row in df.iterrows():
        dist_ad, params_ad = fit_distribution(row.cantidad, row.unc_ad, row.dist_ad)
        ad_sim[:, idx] = sample_distribution(dist_ad, params_ad, n_iter, rng)

    if correlacionar_fe:
        if fe_group_col not in df.columns:
            if fe_unidad_col not in df.columns:
                raise ValueError(
                    f"Para construir '{fe_group_col}' automáticamente hace "
                    f"falta la columna '{fe_unidad_col}' con la unidad del FE."
                )
            df[fe_group_col] = (
                df["fe_central"].round(redondeo_fe).astype(str)
                + "_" + df[fe_unidad_col].astype(str).str.strip()
            )

        chequeo = df.groupby(fe_group_col)[["fe_central", "unc_fe", "dist_fe"]].nunique()
        if (chequeo > 1).any(axis=None):
            raise ValueError(
                f"Hay grupos en '{fe_group_col}' con parámetros de FE "
                "inconsistentes entre filas -- revisar la agrupación."
            )

        for fe_key, pos in df.groupby(fe_group_col).indices.items():
            fila_ref = df.iloc[pos[0]]
            dist_fe, params_fe = fit_distribution(
                fila_ref.fe_central, fila_ref.unc_fe, fila_ref.dist_fe
            )
            fe_muestra = sample_distribution(dist_fe, params_fe, n_iter, rng)
            for idx in pos:
                fe_sim[:, idx] = fe_muestra
    else:
        for idx, row in df.iterrows():
            dist_fe, params_fe = fit_distribution(row.fe_central, row.unc_fe, row.dist_fe)
            fe_sim[:, idx] = sample_distribution(dist_fe, params_fe, n_iter, rng)

    return (fe_sim * ad_sim).astype(np.float32)