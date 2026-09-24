import pandas as pd
import unicodedata
import numpy as np

def fit_distribution(central: float, cv_pct: float, dist: str):
    """
    Ajusta los parámetros de una distribución a partir de:
        - valor central (media)
        - incertidumbre relativa (%)
        - tipo de distribución
    La incertidumbre porcentual se interpreta como un coeficiente de
    variación (CV = σ / μ), siguiendo el enfoque recomendado por el
    IPCC para propagación de incertidumbre.
    """
    if pd.isna(central):
        return ("Constante", {"value": np.nan})
    if dist in (None, "", "N/A"):
        return ("Constante", {"value": central})
    if cv_pct is None or pd.isna(cv_pct):
        return ("Constante", {"value": central})

    cv = cv_pct / 100.0

    if dist == "Normal":
        std = abs(central) * cv
        return ("Normal", {"mean": central, "std": std})

    elif dist == "Lognormal":
        if central <= 0:
            raise ValueError(
                f"La distribución Lognormal requiere valores positivos. Valor recibido: {central}"
            )
        sigma = np.sqrt(np.log(1 + cv**2))
        mu = np.log(central) - sigma**2 / 2
        return ("Lognormal", {"mu": mu, "sigma": sigma})

    elif dist == "Triangular":
        k = cv * np.sqrt(6)
        left = max(0, central * (1 - k))
        right = central * (1 + k)
        return ("Triangular", {"left": left, "mode": central, "right": right})

    else:
        raise ValueError(f"Distribución no soportada: {dist}")


def sample_distribution(dist: str, params: dict, n: int, rng: np.random.Generator):
    """Genera n simulaciones con los parámetros de fit_distribution()."""
    if dist == "Constante":
        return np.full(n, params["value"])

    elif dist == "Normal":
        muestras = rng.normal(loc=params["mean"], scale=params["std"], size=n)
        return np.maximum(muestras, 0)  # evitar consumos negativos

    elif dist == "Lognormal":
        return rng.lognormal(mean=params["mu"], sigma=params["sigma"], size=n)

    elif dist == "Triangular":
        return rng.triangular(
            left=params["left"], mode=params["mode"], right=params["right"], size=n
        )

    else:
        raise ValueError(f"Distribución no soportada: {dist}")
