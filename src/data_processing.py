import pandas as pd
import unicodedata
import numpy as np
import openpyxl

def normalizar(texto: str) -> str:
    if texto is None:
        return ""
    t = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    return " ".join(t.strip().lower().split())


def cargar_lookup_incertidumbre(path: str, sheet: str = "Hoja1") -> dict:
    """Lee el archivo de incertidumbre y arma un diccionario
    normalizar(actividad) -> parámetros."""
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb[sheet]
    lookup = {}
    for r in range(2, ws.max_row + 1):
        actividad = ws.cell(row=r, column=3).value
        if actividad is None:
            continue
        key = normalizar(actividad)
        lookup[key] = dict(
            fe_central=ws.cell(row=r, column=6).value,
            unidad_fe=ws.cell(row=r, column=7).value,
            fuente_factor=ws.cell(row=r, column=8).value,
            dist_fe=ws.cell(row=r, column=9).value,
            unc_fe=ws.cell(row=r, column=10).value,
            dist_ad=ws.cell(row=r, column=4).value,
            unc_ad=ws.cell(row=r, column=5).value,
        )
    return lookup


def buscar_actividad(actividad_raw: str, lookup: dict, keys: list):
    """Match exacto primero; si falla, match por prefijo
    (ej. 'Reciclables (papel)' -> 'Reciclables')."""
    key = normalizar(actividad_raw)
    if key in lookup:
        return lookup[key], key
    candidatos = [k for k in keys if key.startswith(k) or k.startswith(key)]
    if candidatos:
        mejor = max(candidatos, key=len)
        return lookup[mejor], mejor
    return None, None


def construir_dataframe(
    file_activity: str,
    file_uncertainty: str,
    sheet_activity: str = "Hoja2",
    sheet_uncertainty: str = "Hoja1",
):
    """
    Une el archivo de actividad con el de incertidumbre por nombre de
    actividad. Devuelve (df, sin_match, discrepancias).

    df incluye:
      - fe_group: la clave de incertidumbre efectivamente usada en el
        match para cada fila. Es la agrupación CORRECTA para
        correlacionar_fe en simular_montecarlo -- no hace falta
        reconstruirla a partir de fe_central, porque ya es la
        identidad real del factor aplicado.
      - match_exacto: False si la fila cayó en el fallback por
        prefijo, para poder auditar los matches más riesgosos (un
        prefijo corto puede unir actividades que en realidad no
        comparten factor).
    """
    unc_lookup = cargar_lookup_incertidumbre(file_uncertainty, sheet_uncertainty)
    unc_keys = list(unc_lookup.keys())

    wb_act = openpyxl.load_workbook(file_activity, data_only=True)
    ws_act = wb_act[sheet_activity]

    items, sin_match = [], []
    for r in range(2, ws_act.max_row + 1):
        actividad = ws_act.cell(row=r, column=3).value
        if actividad is None:
            continue
        alcance = ws_act.cell(row=r, column=1).value
        fuente = ws_act.cell(row=r, column=2).value
        cantidad = ws_act.cell(row=r, column=4).value
        unidad_act = ws_act.cell(row=r, column=5).value
        fe_reportado = ws_act.cell(row=r, column=6).value

        match, key = buscar_actividad(actividad, unc_lookup, unc_keys)
        if match is None:
            sin_match.append((r, fuente, actividad))
            continue

        items.append(dict(
            fila=r, alcance=alcance, fuente=fuente, actividad=actividad,
            etiqueta=f"{actividad} | {fuente}",
            cantidad=cantidad, unidad_actividad=unidad_act,
            fe_central=match["fe_central"], unidad_fe=match["unidad_fe"],
            dist_ad=match["dist_ad"], unc_ad=match["unc_ad"],
            dist_fe=match["dist_fe"], unc_fe=match["unc_fe"],
            fe_reportado_en_actividad=fe_reportado,
            fe_group=key,
            match_exacto=(key == normalizar(actividad)),
        ))

    df = pd.DataFrame(items).reset_index(drop=True)

    discrepancias = df[
        abs(df["fe_central"] - df["fe_reportado_en_actividad"])
        > 1e-6 * df["fe_central"].abs()
    ]

    return df, sin_match, discrepancias


def afinar_fe_group(
    df: pd.DataFrame,
    fe_group_col: str = "fe_group",
    fe_central_col: str = "fe_central",
    fe_unidad_col: str = "unidad_fe",
    redondeo_fe: int = 10,
) -> pd.DataFrame:
    """
    El fe_group que arma construir_dataframe agrupa bien los casos
    donde la MISMA actividad se reutiliza en varias filas (Diesel,
    Electricidad, Utilitario 3.5 tn...), porque esas filas matchean
    contra la misma fila del archivo de incertidumbre.

    Pero NO agrupa actividades con nombres distintos que casualmente
    comparten el mismo valor numérico de FE -- típico de factores
    basados en gasto (USD), donde varios ítems distintos (ej. "Ropa
    de trabajo" y "Guantes de trabajo") caen en la misma categoría de
    gasto y por lo tanto en el mismo FE, pero son filas separadas en
    el archivo de incertidumbre, cada una con su propia clave.

    Esta función detecta esos casos -- dos o más fe_group distintos
    que comparten (fe_central, unidad_fe) -- y los fusiona bajo una
    única clave, para que simular_montecarlo los trate como
    correlacionados. Imprime qué se fusionó, para poder auditarlo.
    """
    df = df.copy()
    valor_fe = (
        df[fe_central_col].round(redondeo_fe).astype(str)
        + "_" + df[fe_unidad_col].astype(str).str.strip()
    )

    mapping = {}
    fusiones = []
    for valor, sub in df.groupby(valor_fe):
        grupos_distintos = sorted(sub[fe_group_col].unique())
        if len(grupos_distintos) > 1:
            canon = grupos_distintos[0]  # el primero alfabéticamente -> determinístico
            for g in grupos_distintos:
                mapping[g] = canon
            fusiones.append((canon, grupos_distintos))

    if mapping:
        df[fe_group_col] = df[fe_group_col].map(lambda g: mapping.get(g, g))
        print(f"afinar_fe_group: se fusionaron {len(fusiones)} conjuntos de fe_group "
              "que compartían el mismo valor numérico de FE bajo nombres distintos:")
        for canon, grupos in fusiones:
            print(f"  -> '{canon}'  (fusiona: {grupos})")
    else:
        print("afinar_fe_group: no se encontraron grupos para fusionar (fe_group ya "
              "refleja bien los valores numéricos compartidos).")

    return df