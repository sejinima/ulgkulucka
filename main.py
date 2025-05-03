import sys
import os
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QGridLayout, QGroupBox
)
from PyQt5.QtCore import QTimer, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
import pyqtgraph as pg
import folium


class GroundStation(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Yer İstasyonu Arayüzü")
        self.resize(1200, 900)

        self.data = pd.read_csv("telemetry_data.csv")
        self.current_index = 0

        self.init_ui()
        self.init_timer()

    def init_ui(self):
        self.layout = QVBoxLayout()

        self.info_label = QLabel("TEAM_ID: - | MODE: - | STATE: -")
        self.layout.addWidget(self.info_label)

        graph_group = QGroupBox("Gerçek Zamanlı Telemetri Verileri")
        graph_layout = QGridLayout()

        self.temp_plot = self.create_plot("Temperature (°C)", "red")
        self.alt_plot = self.create_plot("Altitude (m)", "blue")
        self.press_plot = self.create_plot("Pressure (Pa)", "green")
        self.volt_plot = self.create_plot("Voltage (V)", "orange")

        graph_layout.addWidget(self.temp_plot, 0, 0)
        graph_layout.addWidget(self.alt_plot, 0, 1)
        graph_layout.addWidget(self.press_plot, 1, 0)
        graph_layout.addWidget(self.volt_plot, 1, 1)

        graph_group.setLayout(graph_layout)
        self.layout.addWidget(graph_group)

        self.map_view = QWebEngineView()
        self.layout.addWidget(self.map_view)

        self.setLayout(self.layout)

        self.x = []
        self.temp_data = []
        self.alt_data = []
        self.press_data = []
        self.volt_data = []

        self.update_map_widget(39.92077, 32.85411)


    def create_plot(self, title, color):
        plot_widget = pg.PlotWidget(title=title)
        plot_widget.setBackground("w")
        plot_widget.showGrid(x=True, y=True)
        plot_widget.getPlotItem().getAxis("left").setPen(pg.mkPen(color))
        plot_widget.getPlotItem().getAxis("bottom").setPen(pg.mkPen("black"))
        curve = plot_widget.plot(pen=pg.mkPen(color, width=2))
        setattr(self, f"{title.split()[0].lower()}_curve", curve)
        return plot_widget

    def init_timer(self):
        self.timer = QTimer()
        self.timer.setInterval(1000) 
        self.timer.timeout.connect(self.update_data)
        self.timer.start()

    def update_data(self):
        if self.current_index >= len(self.data):
            self.timer.stop()
            return

        row = self.data.iloc[self.current_index]

        self.info_label.setText(
            f"TEAM_ID: {row['TEAM_ID']} | MODE: {row['MODE']} | STATE: {row['STATE']}"
        )

        self.x.append(self.current_index)
        self.temp_data.append(float(row["TEMPERATURE"]))
        self.alt_data.append(float(row["ALTITUDE"]))
        self.press_data.append(float(row["PRESSURE"]))
        self.volt_data.append(float(row["VOLTAGE"]))

        self.temperature_curve.setData(self.x, self.temp_data)
        self.altitude_curve.setData(self.x, self.alt_data)
        self.pressure_curve.setData(self.x, self.press_data)
        self.voltage_curve.setData(self.x, self.volt_data)

        try:
            lat = float(row["LATITUDE"])
            lon = float(row["LONGITUDE"])
            self.update_map_widget(lat, lon)
        except Exception as e:
            print("GPS verisi yüklenemedi:", e)

        self.current_index += 1

    def create_map(self, lat, lon):
        m = folium.Map(location=[lat, lon], zoom_start=16)
        folium.Marker([lat, lon], popup="Konum").add_to(m)
        m.save("map.html")

    def update_map_widget(self, lat, lon):
        self.create_map(lat, lon)
        map_path = os.path.abspath("map.html")
        self.map_view.load(QUrl.fromLocalFile(map_path))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    station = GroundStation()
    station.show()
    sys.exit(app.exec_())
