import sys
import json
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QPushButton
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class RobotVisualizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('ロボット重心計算アプリ')
        self.setGeometry(100, 100, 1200, 800)

        # ロボット設定の読み込み
        with open('robot_config.json', 'r', encoding='utf-8') as f:
            self.robot_config = json.load(f)

        # メインウィジェットとレイアウトの設定
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # Matplotlibの図を作成
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # コントロールパネルの作成
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        layout.addWidget(control_panel)

        # 各リンクの角度スライダーを作成
        self.sliders = {}
        self.angle_labels = {}
        for link in self.robot_config['links']:
            link_name = link['name']
            
            # 固定角度のリンクはスキップ
            if link.get('fixed_angle', False):
                continue
            
            # ラベルの作成
            label = QLabel(f"{link_name}の角度: {link['initial_angle']}°")
            control_layout.addWidget(label)
            
            # スライダーの作成
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(-180)
            slider.setMaximum(180)
            slider.setValue(int(link['initial_angle']))
            slider.valueChanged.connect(lambda value, name=link_name: self.update_angle(name, value))
            control_layout.addWidget(slider)
            
            self.sliders[link_name] = slider
            self.angle_labels[link_name] = label
            
        # 固定角度のリンクのスライダーを作成（非表示）
        for link in self.robot_config['links']:
            if link.get('fixed_angle', False):
                slider = QSlider(Qt.Horizontal)
                slider.setValue(int(link['initial_angle']))
                slider.hide()
                self.sliders[link['name']] = slider

        # ズームコントロールの追加
        zoom_layout = QHBoxLayout()
        self.zoom_label = QLabel("ズーム: 100%")
        zoom_layout.addWidget(self.zoom_label)
        
        zoom_in_btn = QPushButton("+")
        zoom_in_btn.clicked.connect(self.zoom_in)
        zoom_layout.addWidget(zoom_in_btn)
        
        zoom_out_btn = QPushButton("-")
        zoom_out_btn.clicked.connect(self.zoom_out)
        zoom_layout.addWidget(zoom_out_btn)
        
        control_layout.addLayout(zoom_layout)
        
        # JSONの再読み込みボタン
        reload_btn = QPushButton("設定を再読み込み")
        reload_btn.clicked.connect(self.reload_config)
        control_layout.addWidget(reload_btn)
        
        # 重心情報表示用のラベル
        self.weight_info_label = QLabel("地面接点の重量: ")
        control_layout.addWidget(self.weight_info_label)
        
        # ズーム率の初期値
        self.zoom_level = 100

        # 初期描画
        self.update_robot_visualization()

    def zoom_in(self):
        self.zoom_level = min(200, self.zoom_level + 10)
        self.zoom_label.setText(f"ズーム: {self.zoom_level}%")
        self.update_robot_visualization()
    
    def zoom_out(self):
        self.zoom_level = max(50, self.zoom_level - 10)
        self.zoom_label.setText(f"ズーム: {self.zoom_level}%")
        self.update_robot_visualization()
    
    def reload_config(self):
        try:
            with open('robot_config.json', 'r', encoding='utf-8') as f:
                self.robot_config = json.load(f)
            
            # スライダーの値を更新
            for link in self.robot_config['links']:
                if link['name'] in self.sliders:
                    self.sliders[link['name']].setValue(int(link['initial_angle']))
                    if not link.get('fixed_angle', False):
                        self.angle_labels[link['name']].setText(f"{link['name']}の角度: {link['initial_angle']}°")
            
            self.update_robot_visualization()
        except Exception as e:
            print(f"設定ファイルの読み込みエラー: {e}")
    
    def update_angle(self, link_name, value):
        # 角度ラベルの更新
        self.angle_labels[link_name].setText(f"{link_name}の角度: {value}°")
        # ロボットの再描画
        self.update_robot_visualization()

    def get_link_by_name(self, name):
        """名前からリンクを取得"""
        for link in self.robot_config['links']:
            if link['name'] == name:
                return link
        return None

    def calculate_link_position(self, link):
        """リンクの位置を計算（親リンクの位置を考慮）"""
        angle_rad = np.radians(self.sliders[link['name']].value())
        length = link['length']

        if 'parent_link' in link and 'connection_point' in link:
            # 親リンクの位置を取得
            parent = self.get_link_by_name(link['parent_link'])
            parent_base, parent_end = self.calculate_link_position(parent)
            
            # 親リンクでの接続点の位置を計算
            parent_angle = np.radians(self.sliders[parent['name']].value())
            connection = np.array(link['connection_point'])
            dx = connection[0] * np.cos(parent_angle) - connection[1] * np.sin(parent_angle)
            dy = connection[0] * np.sin(parent_angle) + connection[1] * np.cos(parent_angle)
            
            # 基準位置を親リンクの位置から計算
            base_pos = parent_base + np.array([dx, dy])
        else:
            # 基準位置が直接指定されている場合
            base_pos = np.array(link.get('base_position', [0, 0]))

        # 終端位置を計算
        end_pos = base_pos + length * np.array([np.cos(angle_rad), np.sin(angle_rad)])
        return base_pos, end_pos

    def calculate_link_positions(self):
        positions = []
        total_mass = 0
        center_of_mass = np.array([0.0, 0.0])

        # 各リンクの位置を計算
        for link in self.robot_config['links']:
            base_pos, end_pos = self.calculate_link_position(link)
            positions.append((base_pos, end_pos))
            
            # リンクの重心位置を計算（リンクの中点）
            mass = link['mass']
            link_com = base_pos + (link['length']/2) * np.array([
                np.cos(np.radians(self.sliders[link['name']].value())),
                np.sin(np.radians(self.sliders[link['name']].value()))
            ])
            
            # 全体の重心計算に寄与
            center_of_mass += link_com * mass
            total_mass += mass

        center_of_mass /= total_mass
        return positions, center_of_mass, total_mass

    def update_robot_visualization(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # ロボットリンクの描画
        positions, com, total_mass = self.calculate_link_positions()
        
        # 地面の描画
        ax.axhline(y=0, color='k', linestyle='-')
        
        # 各リンクの描画
        for link, (start_pos, end_pos) in zip(self.robot_config['links'], positions):
            color = 'r' if link['name'] in ['left_leg', 'right_leg'] else 'b'
            ax.plot([start_pos[0], end_pos[0]], [start_pos[1], end_pos[1]], f'{color}-', linewidth=2)
            
            # リンクの中央位置を計算
            mid_x = (start_pos[0] + end_pos[0]) / 2
            mid_y = (start_pos[1] + end_pos[1]) / 2
            
            # リンク名を表示
            ax.text(mid_x, mid_y, link['name'], 
                    horizontalalignment='center',
                    verticalalignment='center',
                    bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
            
        # 重心の描画
        ax.plot(com[0], com[1], 'go', label='重心')
        
        # 重心から下ろした垂線の描画
        ax.plot([com[0], com[0]], [0, com[1]], 'g--')
        
        # 接地点の反力計算
        g = 9.81  # 重力加速度 [m/s^2]
        total_weight = total_mass * g
        left_pos = positions[0][0]  # 左足の接地点
        right_pos = positions[1][0]  # 右足の接地点
        
        # モーメントのつり合いから各接地点の反力を計算
        total_distance = right_pos[0] - left_pos[0]
        if total_distance != 0:
            right_ratio = (com[0] - left_pos[0]) / total_distance
            left_ratio = 1 - right_ratio
            
            left_force = total_weight * left_ratio
            right_force = total_weight * right_ratio
        else:
            left_force = right_force = total_weight / 2

        # 反力の表示
        self.weight_info_label.setText(
            f"総重量: {total_weight:.1f} N\n" +
            f"左足の反力: {left_force:.1f} N\n" +
            f"右足の反力: {right_force:.1f} N"
        )
        
        # グラフの設定
        ax.set_aspect('equal')
        ax.grid(True)
        ax.set_xlabel('X [m]')
        ax.set_ylabel('Y [m]')
        ax.legend()
        
        # 表示範囲の設定
        zoom_factor = self.zoom_level / 100.0
        ax.set_xlim(-1.5/zoom_factor, 1.5/zoom_factor)
        ax.set_ylim(-0.5/zoom_factor, 3/zoom_factor)
        
        self.canvas.draw()

def main():
    app = QApplication(sys.argv)
    window = RobotVisualizerApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
