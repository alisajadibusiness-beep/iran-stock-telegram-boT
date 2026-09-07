import pandas as pd
import numpy as np


def calculate_sma(series, period):

    return series.rolling(
        period
    ).mean()


def calculate_ema(series, period):

    return series.ewm(
        span=period,
        adjust=False
    ).mean()


def calculate_rsi(
    series,
    period=14
):

    delta = series.diff()

    gain = delta.clip(
        lower=0
    )

    loss = -delta.clip(
        upper=0
    )

    average_gain = gain.rolling(
        period
    ).mean()

    average_loss = loss.rolling(
        period
    ).mean()

    rs = (
        average_gain /
        average_loss.replace(
            0,
            np.nan
        )
    )

    rsi = 100 - (
        100 / (1 + rs)
    )

    return rsi.fillna(50)


def calculate_macd(
    series
):

    ema12 = calculate_ema(
        series,
        12
    )

    ema26 = calculate_ema(
        series,
        26
    )

    macd = ema12 - ema26

    signal = calculate_ema(
        macd,
        9
    )

    histogram = macd - signal

    return macd, signal, histogram


def calculate_atr(
    data,
    period=14
):

    high = data["high"]

    low = data["low"]

    close = data["close"]

    previous_close = close.shift(1)

    tr1 = high - low

    tr2 = (
        high -
        previous_close
    ).abs()

    tr3 = (
        low -
        previous_close
    ).abs()

    true_range = pd.concat(
        [tr1, tr2, tr3],
        axis=1
    ).max(axis=1)

    atr = true_range.rolling(
        period
    ).mean()

    return atr


def calculate_bollinger(
    series,
    period=20,
    deviation=2
):

    middle = series.rolling(
        period
    ).mean()

    std = series.rolling(
        period
    ).std()

    upper = middle + (
        deviation * std
    )

    lower = middle - (
        deviation * std
    )

    return middle, upper, lower


def analyze_stock(
    symbol,
    data
):

    if len(data) < 50:
        raise ValueError(
            "داده کافی برای تحلیل وجود ندارد."
        )

    close = data["close"]

    current_price = float(
        close.iloc[-1]
    )

    sma20 = calculate_sma(
        close,
        20
    )

    sma50 = calculate_sma(
        close,
        50
    )

    ema20 = calculate_ema(
        close,
        20
    )

    rsi = calculate_rsi(
        close
    )

    macd, macd_signal, histogram = calculate_macd(
        close
    )

    atr = calculate_atr(
        data
    )

    bb_middle, bb_upper, bb_lower = calculate_bollinger(
        close
    )

    volume_average = data[
        "volume"
    ].rolling(
        20
    ).mean()

    current_volume = float(
        data["volume"].iloc[-1]
    )

    average_volume = float(
        volume_average.iloc[-1]
    )

    score = 50

    reasons = []

    if current_price > float(
        sma20.iloc[-1]
    ):
        score += 8
        reasons.append(
            "قیمت بالاتر از SMA20"
        )
    else:
        score -= 6

    if current_price > float(
        sma50.iloc[-1]
    ):
        score += 10
        reasons.append(
            "قیمت بالاتر از SMA50"
        )
    else:
        score -= 8

    if float(
        ema20.iloc[-1]
    ) > float(
        sma50.iloc[-1]
    ):
        score += 5
        reasons.append(
            "روند میان‌مدت مثبت"
        )

    current_rsi = float(
        rsi.iloc[-1]
    )

    if 45 <= current_rsi <= 65:

        score += 8

        reasons.append(
            "RSI در محدوده مناسب"
        )

    elif current_rsi < 30:

        score += 4

        reasons.append(
            "RSI اشباع فروش"
        )

    elif current_rsi > 75:

        score -= 12

        reasons.append(
            "RSI اشباع خرید"
        )

    current_macd = float(
        macd.iloc[-1]
    )

    current_macd_signal = float(
        macd_signal.iloc[-1]
    )

    if current_macd > current_macd_signal:

        score += 8

        reasons.append(
            "MACD مثبت"
        )

    else:

        score -= 6

    if (
        average_volume > 0
        and current_volume >
        average_volume * 1.5
    ):

        score += 8

        reasons.append(
            "حجم معاملات بالاتر از میانگین"
        )

    current_atr = float(
        atr.iloc[-1]
    )

    if np.isnan(current_atr):
        current_atr = current_price * 0.03

    stop_loss = max(
        current_price - (
            current_atr * 1.5
        ),
        current_price * 0.90
    )

    target1 = current_price + (
        current_atr * 1.5
    )

    target2 = current_price + (
        current_atr * 2.5
    )

    target3 = current_price + (
        current_atr * 4
    )

    score = max(
        0,
        min(
            100,
            score
        )
    )

    if score >= 75:

        signal = "BUY"

    elif score >= 60:

        signal = "WATCH"

    elif score <= 35:

        signal = "SELL"

    else:

        signal = "HOLD"

    return {
        "symbol": symbol,
        "price": current_price,
        "score": round(score, 1),
        "signal": signal,
        "rsi": round(current_rsi, 2),
        "macd": round(
            current_macd,
            4
        ),
        "atr": round(
            current_atr,
            2
        ),
        "stop_loss": round(
            stop_loss,
            2
        ),
        "target1": round(
            target1,
            2
        ),
        "target2": round(
            target2,
            2
        ),
        "target3": round(
            target3,
            2
        ),
        "reasons": reasons
    }


def calculate_profit(
    buy_price,
    current_price,
    quantity
):

    investment = (
        buy_price *
        quantity
    )

    current_value = (
        current_price *
        quantity
    )

    profit = (
        current_value -
        investment
    )

    if investment == 0:

        percentage = 0

    else:

        percentage = (
            profit /
            investment
        ) * 100

    return {
        "investment": investment,
        "current_value": current_value,
        "profit": profit,
        "percentage": percentage
    }
