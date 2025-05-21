# transparent_png_colorizer.py

透過PNGに背景色を適用するプログラムです。
framepack 1frame学習で使うために作りました。

## usage

`transparent_png_colorizer.py [-h]  --num_colors NUM_COLORS [--digits DIGITS] [--add_disturbance] [--copy_input_dir COPY_INPUT_DIR] [--copy_output_dir COPY_OUTPUT_DIR] input_dir output_dir`

## positional arguments

- `input_dir`: 透過PNGファイルのディレクトリ
- `output_dir`: 出力ディレクトリ

## options

- `-h,  --help`: ヘルプ
- `--num_colors NUM_COLORS`: 生成する色の数
- `--digits DIGITS`: ファイル名の連番の桁数（デフォルト: 4）
- `--add_disturbance`: 揺らぎを加える場合に指定
- `--copy_input_dir COPY_INPUT_DIR`: 入力ファイルを出力ディレクトリにコピーする場合に指定
- `--copy_output_dir COPY_OUTPUT_DIR`: 入力ファイルを出力ディレクトリにコピーする場合に指定
