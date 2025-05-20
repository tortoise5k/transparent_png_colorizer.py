import matplotlib

matplotlib.use("TkAgg")
import colorsys

import numpy as np

# 定数
DIVISIONS = 8  # HSL空間の分割数
S_MIN = 0  # 彩度の最小値
S_MAX = 1  # 彩度の最大値
L_MIN = 0  # 明度の最小値
L_MAX = 1  # 明度の最大値

# 揺らぎのパラメータ
DISTURB_S_MIN = 0  # 揺らぎ後の彩度の最小値
DISTURB_S_MAX = 1  # 揺らぎ後の彩度の最大値
DISTURB_L_MIN = 0  # 揺らぎ後の明度の最小値
DISTURB_L_MAX = 1  # 揺らぎ後の明度の最大値


def hsl_to_rgb(h, s, l):
    """
    HSL値をRGB値(0-1)に変換

    Args:
        h (float): 色相 (0-1)
        s (float): 彩度 (0-1)
        l (float): 明度 (0-1)

    Returns:
        tuple: RGB値のタプル (r, g, b)（各0-1）
    """
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return r, g, b


def rgb_to_hsl(r, g, b):
    """
    RGB値(0-1)をHSL値に変換

    Args:
        r (float): 赤 (0-1)
        g (float): 緑 (0-1)
        b (float): 青 (0-1)

    Returns:
        tuple: HSL値のタプル (h, s, l)（各0-1）
    """
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h, s, l


def create_hsl_space():
    """
    HSL色空間のグリッドを作成

    Returns:
        tuple: (hsl_cube, rgb_cube) - HSL値とそれに対応するRGB値の3次元配列
    """
    # HSL空間を分割する値を生成
    h_values = np.linspace(0, 1, DIVISIONS, endpoint=False)
    s_values = np.linspace(
        S_MIN, S_MAX, DIVISIONS
    )  # 彩度は低すぎると色の区別がしにくい
    l_values = np.linspace(
        L_MIN, L_MAX, DIVISIONS
    )  # 明度は暗すぎたり明るすぎたりすると色の区別がしにくい

    # HSL色空間の3次元配列を作成
    hsl_cube = np.zeros((DIVISIONS, DIVISIONS, DIVISIONS, 3))
    rgb_cube = np.zeros((DIVISIONS, DIVISIONS, DIVISIONS, 3))

    # オリジナルのHSL色立方体を作成
    for i, h in enumerate(h_values):
        for j, s in enumerate(s_values):
            for k, l in enumerate(l_values):
                hsl_cube[i, j, k] = [h, s, l]
                rgb_cube[i, j, k] = hsl_to_rgb(h, s, l)

    return hsl_cube, rgb_cube


def add_disturbance(hsl_cube, rgb_cube):
    """
    HSL色空間にランダムな揺らぎを加える

    Args:
        hsl_cube (ndarray): オリジナルのHSL値の3次元配列
        rgb_cube (ndarray): オリジナルのRGB値の3次元配列

    Returns:
        tuple: (disturbed_hsl_cube, disturbed_rgb_cube) - 揺らぎを加えたHSLとRGB値の3次元配列
    """
    disturbed_hsl_cube = np.copy(hsl_cube)
    disturbed_rgb_cube = np.copy(rgb_cube)

    # 隣接するセル間の距離の半分を揺らぎの最大値とする
    h_step = 1.0 / DIVISIONS / 2
    s_step = (S_MAX - S_MIN) / DIVISIONS / 2
    l_step = (L_MAX - L_MIN) / DIVISIONS / 2

    for i in range(DIVISIONS):
        for j in range(DIVISIONS):
            for k in range(DIVISIONS):
                # HSLの各成分にランダムな揺らぎを加える
                dh = np.random.uniform(-h_step, h_step)
                ds = np.random.uniform(-s_step, s_step)
                dl = np.random.uniform(-l_step, l_step)

                # 新しい値を計算して制限内に収める
                new_h = (
                    hsl_cube[i, j, k, 0] + dh
                ) % 1.0  # 色相は循環するので0-1の範囲にモジュロ演算
                new_s = np.clip(hsl_cube[i, j, k, 1] + ds, DISTURB_S_MIN, DISTURB_S_MAX)
                new_l = np.clip(hsl_cube[i, j, k, 2] + dl, DISTURB_L_MIN, DISTURB_L_MAX)

                # 値を更新
                disturbed_hsl_cube[i, j, k] = [new_h, new_s, new_l]
                disturbed_rgb_cube[i, j, k] = hsl_to_rgb(new_h, new_s, new_l)

    return disturbed_hsl_cube, disturbed_rgb_cube
