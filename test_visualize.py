import matplotlib

from color_cube import (
    DISTURB_L_MAX,
    DISTURB_L_MIN,
    DISTURB_S_MAX,
    DISTURB_S_MIN,
    DIVISIONS,
    L_MAX,
    L_MIN,
    S_MAX,
    S_MIN,
    add_disturbance,
    create_hsl_space,
    hsl_to_rgb,
    rgb_to_hsl,
)

matplotlib.use("TkAgg")

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap


def visualize_color_space():
    """
    HSL色空間とその揺らぎを可視化する関数
    """
    # HSL色空間を作成
    hsl_cube, rgb_cube = create_hsl_space()

    # 揺らぎを加える
    disturbed_hsl_cube, disturbed_rgb_cube = add_disturbance(hsl_cube, rgb_cube)

    # サブプロットを作成
    fig = plt.figure(figsize=(16, 10))
    gs = gridspec.GridSpec(2, 3, width_ratios=[1, 1, 0.05], height_ratios=[1, 1])

    # サブプロット1: HSL空間の3D表示（オリジナル）
    ax1 = fig.add_subplot(gs[0, 0], projection="3d")
    ax1.set_title("HSL色空間（オリジナル）")

    # HSL空間の点をプロット
    for i in range(DIVISIONS):
        for j in range(DIVISIONS):
            for k in range(DIVISIONS):
                h, s, l = hsl_cube[i, j, k]
                r, g, b = rgb_cube[i, j, k]
                ax1.scatter(h, s, l, color=(r, g, b), s=50)

    ax1.set_xlabel("H (色相)")
    ax1.set_ylabel("S (彩度)")
    ax1.set_zlabel("L (明度)")
    ax1.set_xlim(0, 1)
    ax1.set_ylim(S_MIN, S_MAX)
    ax1.set_zlim(L_MIN, L_MAX)

    # サブプロット2: HSL空間の3D表示（揺らぎあり）
    ax2 = fig.add_subplot(gs[0, 1], projection="3d")
    ax2.set_title("HSL色空間（揺らぎあり）")

    # 揺らぎを加えたHSL空間の点をプロット
    for i in range(DIVISIONS):
        for j in range(DIVISIONS):
            for k in range(DIVISIONS):
                h, s, l = disturbed_hsl_cube[i, j, k]
                r, g, b = disturbed_rgb_cube[i, j, k]
                ax2.scatter(h, s, l, color=(r, g, b), s=50)

    ax2.set_xlabel("H (色相)")
    ax2.set_ylabel("S (彩度)")
    ax2.set_zlabel("L (明度)")
    ax2.set_xlim(0, 1)
    ax2.set_ylim(DISTURB_S_MIN, DISTURB_S_MAX)
    ax2.set_zlim(DISTURB_L_MIN, DISTURB_L_MAX)

    # サブプロット3: 色相別の色表示（オリジナル）
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.set_title("色相別カラーマップ（オリジナル）")

    # 色相に対応する色を表示するためのデータを準備
    h_samples = np.linspace(0, 1, 256, endpoint=False)
    color_samples = np.array([hsl_to_rgb(h, 0.8, 0.5) for h in h_samples])

    # 色相に対応する色を表示
    h_img = np.zeros((50, 256, 3))
    for i in range(256):
        h_img[:, i, :] = color_samples[i]

    ax3.imshow(h_img, extent=[0, 1, 0, 1])
    ax3.set_xlabel("H (色相)")
    ax3.set_yticks([])

    # サブプロット4: 色相別の色表示（揺らぎあり）
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.set_title("ランダムサンプル（揺らぎあり）")

    # ランダムに色をサンプリング
    np.random.seed(42)  # 再現性のために乱数シードを固定
    random_samples = np.zeros((10, 10, 3))
    for i in range(10):
        for j in range(10):
            # ランダムにインデックスを選択
            idx_h = np.random.randint(0, DIVISIONS)
            idx_s = np.random.randint(0, DIVISIONS)
            idx_l = np.random.randint(0, DIVISIONS)
            # 対応するRGB値を取得
            random_samples[i, j] = disturbed_rgb_cube[idx_h, idx_s, idx_l]

    ax4.imshow(random_samples)
    ax4.set_xticks([])
    ax4.set_yticks([])

    # カラーバー
    cax = fig.add_subplot(gs[:, 2])
    cmap = ListedColormap(color_samples)
    cb = plt.colorbar(plt.cm.ScalarMappable(cmap=cmap), cax=cax)
    cb.set_label("色相 (H)")

    plt.tight_layout()
    plt.show()


def visualize_hsl_slices():
    """
    HSL色空間の2Dスライスを表示する関数
    """
    # HSL色空間を作成
    hsl_cube, rgb_cube = create_hsl_space()

    # 揺らぎを加える
    disturbed_hsl_cube, disturbed_rgb_cube = add_disturbance(hsl_cube, rgb_cube)

    # いくつかの固定値でスライスを表示
    h_fixed = 0  # 色相を固定（赤系）
    s_fixed = DIVISIONS // 2  # 彩度を中間に固定
    l_fixed = DIVISIONS // 2  # 明度を中間に固定

    fig, axes = plt.subplots(2, 3, figsize=(18, 12))

    # オリジナルのHSL空間のスライス
    # 色相固定（H固定）- SL平面
    sl_slice = rgb_cube[h_fixed, :, :, :]
    axes[0, 0].imshow(sl_slice)
    axes[0, 0].set_title(f"H固定 ({h_fixed / DIVISIONS:.2f})：SL平面（オリジナル）")
    axes[0, 0].set_xlabel("L (明度)")
    axes[0, 0].set_ylabel("S (彩度)")

    # 彩度固定（S固定）- HL平面
    hl_slice = rgb_cube[:, s_fixed, :, :]
    axes[0, 1].imshow(hl_slice)
    axes[0, 1].set_title(
        f"S固定 ({(s_fixed / DIVISIONS) * (S_MAX - S_MIN) + S_MIN:.2f})：HL平面（オリジナル）"
    )
    axes[0, 1].set_xlabel("L (明度)")
    axes[0, 1].set_ylabel("H (色相)")

    # 明度固定（L固定）- HS平面
    hs_slice = rgb_cube[:, :, l_fixed, :]
    axes[0, 2].imshow(hs_slice)
    axes[0, 2].set_title(
        f"L固定 ({(l_fixed / DIVISIONS) * (L_MAX - L_MIN) + L_MIN:.2f})：HS平面（オリジナル）"
    )
    axes[0, 2].set_xlabel("S (彩度)")
    axes[0, 2].set_ylabel("H (色相)")

    # 揺らぎを加えたHSL空間のスライス
    # 色相固定（H固定）- SL平面
    sl_slice_disturbed = disturbed_rgb_cube[h_fixed, :, :, :]
    axes[1, 0].imshow(sl_slice_disturbed)
    axes[1, 0].set_title(f"H固定 ({h_fixed / DIVISIONS:.2f})：SL平面（揺らぎあり）")
    axes[1, 0].set_xlabel("L (明度)")
    axes[1, 0].set_ylabel("S (彩度)")

    # 彩度固定（S固定）- HL平面
    hl_slice_disturbed = disturbed_rgb_cube[:, s_fixed, :, :]
    axes[1, 1].imshow(hl_slice_disturbed)
    axes[1, 1].set_title(
        f"S固定 ({(s_fixed / DIVISIONS) * (S_MAX - S_MIN) + S_MIN:.2f})：HL平面（揺らぎあり）"
    )
    axes[1, 1].set_xlabel("L (明度)")
    axes[1, 1].set_ylabel("H (色相)")

    # 明度固定（L固定）- HS平面
    hs_slice_disturbed = disturbed_rgb_cube[:, :, l_fixed, :]
    axes[1, 2].imshow(hs_slice_disturbed)
    axes[1, 2].set_title(
        f"L固定 ({(l_fixed / DIVISIONS) * (L_MAX - L_MIN) + L_MIN:.2f})：HS平面（揺らぎあり）"
    )
    axes[1, 2].set_xlabel("S (彩度)")
    axes[1, 2].set_ylabel("H (色相)")

    plt.tight_layout()
    plt.show()


def compare_color_sets():
    """
    揺らぎを加えた前後の色の比較を表示する関数
    """
    # HSL色空間を作成
    hsl_cube, rgb_cube = create_hsl_space()

    # 揺らぎを加える
    disturbed_hsl_cube, disturbed_rgb_cube = add_disturbance(hsl_cube, rgb_cube)

    # 全ての色をフラット化
    original_colors = rgb_cube.reshape(-1, 3)
    disturbed_colors = disturbed_rgb_cube.reshape(-1, 3)

    # 比較用の図を作成
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))

    # オリジナルの色セット
    n_colors = len(original_colors)
    grid_size = int(np.ceil(np.sqrt(n_colors)))

    original_grid = np.zeros((grid_size, grid_size, 3))
    disturbed_grid = np.zeros((grid_size, grid_size, 3))

    for i in range(n_colors):
        row = i // grid_size
        col = i % grid_size
        if row < grid_size and col < grid_size:
            original_grid[row, col] = original_colors[i]
            disturbed_grid[row, col] = disturbed_colors[i]

    axes[0].imshow(original_grid)
    axes[0].set_title("オリジナル色セット")
    axes[0].set_xticks([])
    axes[0].set_yticks([])

    axes[1].imshow(disturbed_grid)
    axes[1].set_title("揺らぎを加えた色セット")
    axes[1].set_xticks([])
    axes[1].set_yticks([])

    plt.tight_layout()
    plt.show()


def test_functions():
    """
    関数をテストして結果を表示
    """
    print("HSL→RGB変換テスト:")
    test_hsl = [(0, 1, 0.5), (1 / 3, 1, 0.5), (2 / 3, 1, 0.5)]
    for h, s, l in test_hsl:
        r, g, b = hsl_to_rgb(h, s, l)
        print(f"  HSL({h:.2f}, {s:.2f}, {l:.2f}) → RGB({r:.2f}, {g:.2f}, {b:.2f})")

    print("\nRGB→HSL変換テスト:")
    test_rgb = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
    for r, g, b in test_rgb:
        h, s, l = rgb_to_hsl(r, g, b)
        print(f"  RGB({r:.2f}, {g:.2f}, {b:.2f}) → HSL({h:.2f}, {s:.2f}, {l:.2f})")

    print("\nHSL空間作成テスト:")
    hsl_cube, rgb_cube = create_hsl_space()
    print(f"  HSL空間サイズ: {hsl_cube.shape}")
    print(f"  RGB空間サイズ: {rgb_cube.shape}")

    print("\n揺らぎ追加テスト:")
    disturbed_hsl_cube, disturbed_rgb_cube = add_disturbance(hsl_cube, rgb_cube)
    print(f"  揺らぎ後HSL空間サイズ: {disturbed_hsl_cube.shape}")
    print(f"  揺らぎ後RGB空間サイズ: {disturbed_rgb_cube.shape}")

    # 元の色と揺らぎを加えた色の差を計算
    original_flat = rgb_cube.reshape(-1, 3)
    disturbed_flat = disturbed_rgb_cube.reshape(-1, 3)

    # ユークリッド距離で色の違いを測定
    diff = np.sqrt(np.sum((original_flat - disturbed_flat) ** 2, axis=1))

    print("  揺らぎによる色の変化（ユークリッド距離）:")
    print(f"    最小: {np.min(diff):.4f}")
    print(f"    最大: {np.max(diff):.4f}")
    print(f"    平均: {np.mean(diff):.4f}")
    print(f"    標準偏差: {np.std(diff):.4f}")


if __name__ == "__main__":
    # 関数のテスト実行
    test_functions()

    # HSL色空間の可視化
    visualize_color_space()

    # HSL色空間の2Dスライスを表示
    visualize_hsl_slices()

    # 色セットの比較
    compare_color_sets()
