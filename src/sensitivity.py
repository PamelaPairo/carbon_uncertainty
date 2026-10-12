import pandas as pd
import unicodedata
import numpy as np

def sensibilidad(df: pd.DataFrame, emis_matrix: np.ndarray) -> pd.DataFrame:
    """
    Descompone la varianza del total simulado en la contribución EXACTA
    de cada fuente, usando la identidad que vale para cualquier modelo
    aditivo (Total = suma de fuentes):

        sum_j  Cov(E_j, Total)  =  Var(Total)
        =>     contribucion_j   =  Cov(E_j, Total) / Var(Total)

    Esas contribuciones suman exactamente 100%. A diferencia de una
    correlación al cuadrado (que solo aproxima), esto es exacto para
    un inventario de GEI porque el total es literalmente una suma.
    (Para modelos no aditivos/no lineales haría falta un análisis
    tipo Sobol; acá no hace falta.)

    Se calcula sobre la corrida CORRELACIONADA -- hacerlo sobre la
    ingenua subestima la contribución de los grupos con FE compartido,
    igual que subestima la incertidumbre del total.
    """
    total = emis_matrix.sum(axis=1)
    n = emis_matrix.shape[0]
    emis_c = emis_matrix - emis_matrix.mean(axis=0, keepdims=True)
    total_c = total - total.mean()

    cov_j_total = (emis_c * total_c[:, None]).sum(axis=0) / (n - 1)
    var_total = (total_c @ total_c) / (n - 1)

    resultado = df[["alcance", "fuente", "actividad", "fe_group"]].copy()
    resultado["emision_media_tn"] = emis_matrix.mean(axis=0) / 1000
    resultado["emision_media_pct_total"] = (
        resultado["emision_media_tn"] / (total.mean() / 1000) * 100
    )
    resultado["contribucion_incertidumbre_pct"] = cov_j_total / var_total * 100
    # >1 = aporta más incertidumbre de lo que "pesa" en la emisión media
    # (candidato prioritario para mejorar calidad de dato);
    # <1 = pesa en la emisión pero está bien caracterizado.
    resultado["indice_riesgo"] = (
        resultado["contribucion_incertidumbre_pct"] / resultado["emision_media_pct_total"]
    )
    return resultado.sort_values("contribucion_incertidumbre_pct", ascending=False)


def sensibilidad_por_grupo(
    df: pd.DataFrame, emis_matrix: np.ndarray, group_col: str = "fe_group"
) -> pd.DataFrame:
    """Igual que sensibilidad(), pero agregada por grupo de FE -- útil
    porque un grupo con muchas actividades correlacionadas puede
    dominar la incertidumbre aunque cada actividad individual se vea
    chica. También suma exactamente 100%."""
    total = emis_matrix.sum(axis=1)
    n = emis_matrix.shape[0]
    total_c = total - total.mean()
    var_total = (total_c @ total_c) / (n - 1)

    filas = []
    for grupo, pos in df.groupby(group_col).indices.items():
        emis_grupo = emis_matrix[:, pos].sum(axis=1)
        cov = ((emis_grupo - emis_grupo.mean()) * total_c).sum() / (n - 1)
        filas.append(dict(
            fe_group=grupo,
            n_actividades=len(pos),
            actividades=", ".join(df.iloc[pos]["actividad"].astype(str).unique()),
            emision_media_tn=emis_grupo.mean() / 1000,
            contribucion_incertidumbre_pct=cov / var_total * 100,
        ))
    return pd.DataFrame(filas).sort_values("contribucion_incertidumbre_pct", ascending=False)

