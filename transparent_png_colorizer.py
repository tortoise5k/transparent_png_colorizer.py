import argparse
import shutil
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


def check_dataset(image_files: list[Path], image_captions: list[Path]) -> None:
    len_img = len(image_files)
    len_txt = len(image_captions)
    if len_img == 0 or len_txt == 0:
        raise ValueError("画像ファイルとキャプションファイルのペアが見つかりません。")
    if len_img != len_txt:
        raise ValueError("画像ファイルとキャプションファイルの数が一致しません。")

    img_txt_pairs = [
        (img, txt)
        for img, txt in zip(image_files, image_captions)
        if img.stem == txt.stem
    ]
    if len_img != len(img_txt_pairs):
        raise ValueError("画像ファイルとキャプションファイルの名前が一致しません。")

    return None


def copy_input_files(
    copy_input_dir: Path, copy_output_dir: Path, num_colors: int, digits: int
) -> None:
    """
    入力ディレクトリの画像ファイル、キャプションファイルを出力ディレクトリにコピーする
    """
    # 出力ディレクトリを作成
    copy_output_dir.mkdir(parents=True, exist_ok=True)

    # 画像ファイルの拡張子リスト
    image_exts = [".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff", ".webp"]

    # input dirのすべてのファイルを画像ファイルか判定してリスト化、ソート (0001..000N)
    image_files = sorted(
        [f for f in copy_input_dir.glob("*") if f.suffix.lower() in image_exts]
    )
    # キャプションファイルの拡張子リスト
    image_captions = sorted(copy_input_dir.glob("*.txt"))

    check_dataset(image_files, image_captions)

    img_txt_pairs = [
        (img, txt)
        for img, txt in zip(image_files, image_captions)
        if img.stem == txt.stem
    ]

    # 画像ファイルを出力ディレクトリにコピー(num_colors分循環してコピー)
    for i in range(num_colors):
        # 画像ファイルのインデックス（循環させる）
        pair_index = i % len(img_txt_pairs)
        img_path, txt_path = img_txt_pairs[pair_index]

        # 出力ファイル名の形式を設定
        img_output_path = copy_output_dir / f"{str(i + 1).zfill(digits)}.png"
        txt_output_path = copy_output_dir / f"{str(i + 1).zfill(digits)}.txt"

        # ファイルをコピー
        shutil.copy(img_path, img_output_path)
        shutil.copy(txt_path, txt_output_path)


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
    parser.add_argument(
        "--copy_input_dir",
        help="入力ファイルを出力ディレクトリにコピーする場合に指定",
    )
    parser.add_argument(
        "--copy_output_dir",
        help="入力ファイルを出力ディレクトリにコピーする場合に指定",
    )
    args = parser.parse_args()
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    # 出力ディレクトリが存在しない場合は作成
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    # 透過PNGファイルのリストを取得
    png_files = [f.name for f in input_dir.iterdir() if f.suffix.lower() == ".png"]

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

    # 入力ディレクトリの画像ファイル、キャプションファイルを出力ディレクトリにコピー、足りない場合はindex循環してコピー
    if args.copy_input_dir:
        copy_input_files(
            Path(args.copy_input_dir),
            Path(args.copy_output_dir),
            args.num_colors,
            args.digits,
        )


if __name__ == "__main__":
    main()
