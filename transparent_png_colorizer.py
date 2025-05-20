import argparse
from pathlib import Path

import numpy as np
from PIL import Image

from color_cube import add_disturbance, create_hsl_space


def generate_unique_colors(num_colors, use_disturbance=True):
    """
    指定された数のユニークな色を生成する

    Args:
        num_colors (int): 生成する色の数
        use_disturbance (bool): 揺らぎを加えるかどうか

    Returns:
        list: (r, g, b)形式のRGB値のリスト（各0-255）
    """
    # HSL色空間を作成
    hsl_cube, rgb_cube = create_hsl_space()

    if use_disturbance:
        # 揺らぎを加える
        _, disturbed_rgb_cube = add_disturbance(hsl_cube, rgb_cube)
        # 使用する色空間を揺らぎを加えたものに設定
        color_cube = disturbed_rgb_cube
    else:
        # 元の色空間をそのまま使用
        color_cube = rgb_cube

    # 3次元配列を1次元に変換
    all_colors = color_cube.reshape(-1, 3)

    # 色をシャッフル
    np.random.shuffle(all_colors)

    # 必要な数の色を選択
    selected_colors = all_colors[:num_colors]

    # 0-1の範囲から0-255の範囲に変換
    selected_colors_255 = (selected_colors * 255).astype(np.uint8)

    # タプルのリストに変換
    return [tuple(color) for color in selected_colors_255]


def apply_color_to_transparent_png(png_path, color, output_path):
    """
    透過PNGに背景色を適用する

    Args:
        png_path (str): 透過PNGファイルのパス
        color (tuple): 適用する色 (r, g, b)
        output_path (str): 出力ファイルのパス
    """
    # 画像を開く
    img = Image.open(png_path).convert("RGBA")

    # 画像の幅と高さを取得
    width, height = img.size

    # 画像データをNumPy配列に変換
    img_data = np.array(img)

    # 背景色の画像を作成
    background = np.zeros((height, width, 4), dtype=np.uint8)
    background[:, :, 0] = color[0]  # R
    background[:, :, 1] = color[1]  # G
    background[:, :, 2] = color[2]  # B
    background[:, :, 3] = 255  # アルファ（完全不透明）

    # アルファ値に基づいて元の画像と背景を合成
    alpha = img_data[:, :, 3:4] / 255.0
    img_data[:, :, :3] = img_data[:, :, :3] * alpha + background[:, :, :3] * (1 - alpha)
    img_data[:, :, 3] = 255  # 完全不透明に設定

    # NumPy配列を画像に変換
    result_img = Image.fromarray(img_data)

    # 結果を保存
    result_img.save(output_path)


def main():
    parser = argparse.ArgumentParser(description="透過PNGに背景色を適用するプログラム")
    parser.add_argument("input_dir", help="透過PNGファイルのディレクトリ")
    parser.add_argument("output_dir", help="出力ディレクトリ")
    parser.add_argument("--num_colors", type=int, required=True, help="生成する色の数")
    parser.add_argument(
        "--digits", type=int, default=4, help="ファイル名の連番の桁数（デフォルト: 4）"
    )
    parser.add_argument(
        "--add_disturbance", action="store_true", help="揺らぎを加える場合に指定"
    )
    args = parser.parse_args()
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    # 出力ディレクトリが存在しない場合は作成
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    # 透過PNGファイルのリストを取得
    png_files = [f for f in input_dir.iterdir() if f.lower().endswith(".png")]

    # 透過PNGの数
    num_pngs = len(png_files)

    if num_pngs == 0:
        print("透過PNGファイルが見つかりません。")
        return

    # ユニークな色を生成（揺らぎオプションを渡す）
    use_disturbance = args.add_disturbance
    colors = generate_unique_colors(args.num_colors, use_disturbance)

    print(f"揺らぎ: {'有効' if args.add_disturbance else '無効'}")

    # 生成する総数
    total_outputs = args.num_colors

    # 各色に対して処理
    for i in range(total_outputs):
        # 透過PNGのインデックス（循環させる）
        png_index = i % num_pngs
        png_path = input_dir / png_files[png_index]

        # 色のインデックス
        color_index = i
        color = colors[color_index]

        # 出力ファイル名の形式を設定
        output_filename = f"{str(i + 1).zfill(args.digits)}.png"
        output_path = output_dir / output_filename

        # 背景色を適用
        apply_color_to_transparent_png(png_path, color, output_path)

        print(
            f"処理完了: {output_filename} - PNG: {png_files[png_index]}, 色: RGB{color}"
        )


if __name__ == "__main__":
    main()
