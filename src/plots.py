import pandas as pd
import unicodedata
import numpy as np

def graficar_sensibilidad(
    tabla_sens: pd.DataFrame,
    top_n: int = 10,
    path: str = "C:/Users/Pame/Desktop/carbon_uncertainty/outs/sensibilidad_incertidumbre.png",
):
    """Barras horizontales con las actividades que más aportan a la
    incertidumbre del total. Guarda un PNG para usar en slides/póster."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    top = tabla_sens.head(top_n).iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 0.42 * top_n + 1.5))
    ax.barh(top["actividad"], top["contribucion_incertidumbre_pct"], color="#2a78d6")
    ax.set_xlabel("Contribución a la incertidumbre del total (%)")
    ax.set_title("Qué actividad aporta más incertidumbre al inventario\n(no necesariamente la que más emite)")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def graficar_comparacion_metodos(
    resumen_tier1: dict,
    resumen_mc_naive: dict,
    resumen_mc_corr: dict,
    path: str = "C:/Users/Pame/Desktop/carbon_uncertainty/outs/comparacion_metodos.png",
):
    """
    Compara la incertidumbre del TOTAL del inventario según tres
    formas de calcularla: Tier 1 analítico, MC ingenuo, MC con
    correlación explícita. Barra = media: línea = intervalo del 95%.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    metodos = ["Tier 1\n(analítico)", "MC\n(ingenuo)", "MC\n(correlacionado)"]
    resumenes = [resumen_tier1, resumen_mc_naive, resumen_mc_corr]
    medias = [r["media"] for r in resumenes]
    err_abajo = [r["media"] - r["p2_5"] for r in resumenes]
    err_arriba = [r["p97_5"] - r["media"] for r in resumenes]
    colores = ["#898781", "#2a78d6", "#eb6834"]

    fig, ax = plt.subplots(figsize=(6.5, 5))
    x = np.arange(len(metodos))
    ax.bar(x, medias, yerr=[err_abajo, err_arriba], capsize=6,
           color=colores, alpha=0.85, width=0.55)
    for xi, r in zip(x, resumenes):
        pct = (r["p97_5"] - r["p2_5"]) / 2 / r["media"] * 100
        ax.text(xi, r["p97_5"] + max(medias) * 0.02, f"±{pct:.1f}%",
                ha="center", va="bottom", fontsize=10)
    ax.set_ylabel("Emisiones totales (tnCO2e)")
    ax.set_title("Incertidumbre del inventario según método de propagación\n(barra = media, línea = intervalo 95%)")
    ax.set_xticks(x)
    ax.set_xticklabels(metodos)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path