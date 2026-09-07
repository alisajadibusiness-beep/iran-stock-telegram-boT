import random
import math

import pandas as pd
import numpy as np


DEFAULT_SYMBOLS = [
    "فولاد",
    "فملی",
    "شپنا",
    "شبندر",
    "خودرو",
    "خساپا",
    "شتران",
    "ذوب",
]


def generate_demo_data(
    symbol,
    rows=180
):

    seed = sum(
        ord(char)
        for char in symbol
    )

    random.seed(seed)

    base_price = random.randint(
        1000,
        15000
    )

    prices = []

    current = float(base_price)

    for index in range(rows):

        trend = math.sin(index / 18) * 0.01

        noise = random.uniform(
            -0.025,
            0.025
        )

        change = trend + noise

        current *= (1 + change)

        current = max(
            100,
            current
        )

        prices.append(current)

    closes = np.array(prices)

    highs = closes * np.array([
        1 + random.uniform(
            0.002,
            0.025
        )
        for _ in range(rows)
    ])

    lows = closes * np.array([
        1 - random.uniform(
            0.002,
            0.025
        )
        for _ in range(rows)
    ])

    opens = closes * np.array([
        1 + random.uniform(
            -0.015,
            0.015
        )
        for _ in range(rows)
    ])

    volumes = np.array([
        random.randint(
            100000,
            5000000
        )
        for _ in range(rows)
    ])

    data = pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes
    })

    return data


def get_market_data(symbol):

    symbol = symbol.strip()

    if not symbol:
        raise ValueError(
            "نماد وارد نشده است."
        )

    return generate_demo_data(
        symbol
    )


def get_market_symbols():

    return DEFAULT_SYMBOLS.copy()
