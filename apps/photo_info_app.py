import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog
from PyQt5.QtGui import QPixmap
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

class PhotoInfoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Photo Info Viewer")
        self.setGeometry(100, 100, 600, 600)

        # Layout principal
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Bouton pour ouvrir une image
        self.open_button = QPushButton("Ouvrir une image", self)
        self.open_button.clicked.connect(self.open_image)
        self.layout.addWidget(self.open_button)

        # Label pour afficher l'image
        self.image_label = QLabel(self)
        self.image_label.setFixedSize(400, 400)
        self.layout.addWidget(self.image_label)

        # Labels pour les informations
        self.date_label = QLabel("Date: Non disponible", self)
        self.time_label = QLabel("Heure: Non disponible", self)
        self.lat_label = QLabel("Latitude: Non disponible", self)
        self.lon_label = QLabel("Longitude: Non disponible", self)
        self.layout.addWidget(self.date_label)
        self.layout.addWidget(self.time_label)
        self.layout.addWidget(self.lat_label)
        self.layout.addWidget(self.lon_label)

    def open_image(self):
        # Ouvrir un dialogue pour sélectionner une image
        file_name, _ = QFileDialog.getOpenFileName(self, "Ouvrir une image", "", "Images (*.jpg *.jpeg *.png)")
        if file_name:
            # Afficher l'image
            pixmap = QPixmap(file_name).scaled(400, 400, aspectRatioMode=1)
            self.image_label.setPixmap(pixmap)

            # Extraire les métadonnées EXIF
            try:
                image = Image.open(file_name)
                exif_data = image._getexif()
                if not exif_data:
                    self.date_label.setText("Date: Non disponible")
                    self.time_label.setText("Heure: Non disponible")
                    self.lat_label.setText("Latitude: Non disponible")
                    self.lon_label.setText("Longitude: Non disponible")
                    return

                # Extraire la date et l'heure
                date_time = None
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag == "DateTime":
                        date_time = value
                        break

                if date_time:
                    date, time = date_time.split(" ")
                    date = date.replace(":", "-")
                    self.date_label.setText(f"Date: {date}")
                    self.time_label.setText(f"Heure: {time}")
                else:
                    self.date_label.setText("Date: Non disponible")
                    self.time_label.setText("Heure: Non disponible")

                # Extraire les coordonnées GPS
                gps_info = None
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag == "GPSInfo":
                        gps_info = value
                        break

                if gps_info:
                    lat = self.get_decimal_coordinates(gps_info.get(2), gps_info.get(1))
                    lon = self.get_decimal_coordinates(gps_info.get(4), gps_info.get(3))
                    formatted_coords = self.format_coordinates(lat, lon, gps_info.get(1), gps_info.get(3))
                    self.lat_label.setText(f"Latitude: {formatted_coords['latitude']}")
                    self.lon_label.setText(f"Longitude: {formatted_coords['longitude']}")
                else:
                    self.lat_label.setText("Latitude: Non disponible")
                    self.lon_label.setText("Longitude: Non disponible")

            except Exception as e:
                print(f"Erreur lors de la lecture des métadonnées: {e}")
                self.date_label.setText("Date: Erreur")
                self.time_label.setText("Heure: Erreur")
                self.lat_label.setText("Latitude: Erreur")
                self.lon_label.setText("Longitude: Erreur")

    def get_decimal_coordinates(self, coords, ref):
        if not coords:
            return None
        degrees, minutes, seconds = coords
        decimal = degrees + minutes / 60.0 + seconds / 3600.0
        if ref in ["S", "W"]:
            decimal = -decimal
        return decimal

    def format_coordinates(self, latitude, longitude, lat_ref, lon_ref):
        if latitude is None or longitude is None:
            return {"latitude": "Non disponible", "longitude": "Non disponible"}
        
        def format_degrees(value):
            degrees = int(abs(value))
            minutes = (abs(value) - degrees) * 60
            formatted_minutes = f"{minutes:.2f}".zfill(5)
            return f"{degrees}°{formatted_minutes}"

        return {
            "latitude": format_degrees(latitude) + ("N" if latitude >= 0 else "S"),
            "longitude": format_degrees(longitude) + ("E" if longitude >= 0 else "W")
        }

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PhotoInfoApp()
    ex.show()
    sys.exit(app.exec_())