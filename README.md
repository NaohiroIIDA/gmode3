# Robot Center of Mass Visualization Tool

This is a Python application that visualizes a robot's configuration and calculates its center of mass. The application provides a graphical interface to manipulate the robot's joint angles and visualize the results in real-time.

## Features

- Robot visualization with adjustable joint angles
- Center of mass calculation
- Ground reaction force calculation
- Ground slope adjustment (-45° to +45°)
- Stability analysis on slopes
- Zoom in/out functionality
- JSON configuration reload capability
- Link name labels on the visualization

## Requirements

- Python 3.8 or higher
- Dependencies listed in `requirements.txt`

## Installation

1. Clone this repository
2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python main.py
```

2. The application window will open with:
   - Robot visualization on the left
   - Control panel on the right including:
     - Reset button to restore initial angles
     - Ground slope adjustment slider (-45° to +45°)
     - Joint angle controls
     - Stability indicator
     - Ground reaction forces display
     - Zoom controls
     - Configuration reload button
     - Weight information display

3. The robot configuration can be modified by editing the `robot_config.json` file.

## Configuration

The robot's configuration is defined in `robot_config.json`. Each link has the following properties:

- `name`: Link identifier
- `length`: Length of the link in meters
- `mass`: Mass of the link in kg
- `initial_angle`: Initial angle in degrees
- `fixed_angle`: Boolean indicating if the angle is fixed
- `base_position`: Base position [x, y] for root links
- `parent_link`: Parent link name for connected links
- `connection_point`: Connection point [x, y] relative to parent link

## License

MIT License

---

# ロボット重心可視化ツール

このPythonアプリケーションは、ロボットの構成を可視化し、重心を計算するツールです。グラフィカルインターフェースを通じて、ロボットの関節角度をリアルタイムで操作・視覚化することができます。

## 機能

- ロボットのリンクと関節のリアルタイム可視化
- スライダーによる対話的な角度調整
- 重心の計算と可視化
- 地面反力の計算
- ズームイン/アウト機能
- JSON設定ファイルの再読み込み機能
- 可視化画面上のリンク名表示

## 必要条件

- Python 3.8以上
- `requirements.txt`に記載された依存パッケージ

## インストール方法

1. このリポジトリをクローン
2. 必要なパッケージをインストール：
```bash
pip install -r requirements.txt
```

## 使用方法

1. アプリケーションの実行：
```bash
python main.py
```

2. アプリケーションウィンドウが開き、以下が表示されます：
   - 左側にロボットの可視化
   - 右側に制御パネル：
     - 各関節の角度調整スライダー
     - ズーム制御
     - 設定再読み込みボタン
     - 重量情報の表示

3. `robot_config.json`ファイルを編集することで、ロボットの構成を変更できます。

## 設定

ロボットの構成は`robot_config.json`で定義されます。各リンクには以下のプロパティがあります：

- `name`: リンクの識別子
- `length`: リンクの長さ（メートル単位）
- `mass`: リンクの質量（kg単位）
- `initial_angle`: 初期角度（度単位）
- `fixed_angle`: 角度が固定かどうかのブール値
- `base_position`: ルートリンクの基準位置[x, y]
- `parent_link`: 接続先の親リンク名
- `connection_point`: 親リンクに対する接続点の位置[x, y]
