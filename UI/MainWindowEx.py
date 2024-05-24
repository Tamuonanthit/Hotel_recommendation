import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtSql import QSqlDatabase, QSqlQuery
from UI.MainWindow import Ui_MainWindow
from UI.SearchResultsEx import SearchResultsEx


class MainWindowEx(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Kết nối nút Submit và Back với các hàm xử lý sự kiện
        self.pushButtonSubmit.clicked.connect(self.openSearchResults)
        self.pushButtonClose.clicked.connect(self.close)

        # Khởi tạo và kết nối cơ sở dữ liệu
        self.loadDatabase()

        # Tải dữ liệu cho các ComboBox
        self.loadCities()
        self.loadRoomTypes()
        self.loadAmenities()

    def loadDatabase(self):
        baseDir = os.path.dirname(__file__)
        databasePath = os.path.join(baseDir, "airbnb_data.db")
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(databasePath)
        if not self.db.open():
            QMessageBox.critical(
                self, "Error", "Failed to open database!", QMessageBox.StandardButton.Ok
            )
            return False
        return True

    def loadAmenities(self):
        amenities = ["Smoke alarm", "Kitchen", "Essentials", "Wifi", "Carbon monoxide alarm",
                     "Hot water", "Hangers", "Hair dryer", "Dishes and silverware", "Microwave"]
        self.cbxAmenities.addItems(amenities)

    def loadCities(self):
        city = ["New Jersey", "Washington DC", "Seattle",
                "Chicago", "Texas", "Boston", "San Diego", "Dallas"]
        self.cbxCity.addItems(city)

    def loadRoomTypes(self):
        roomtype = ["Private room", "Entire home/apt", "Hotel room", "Shared room"]
        self.cbxRoomtype.addItems(roomtype)

    def openSearchResults(self):
        city = self.cbxCity.currentText()
        room_type = self.cbxRoomtype.currentText()
        date = self.lineEditDate.text()
        amenities = self.cbxAmenities.currentText()
        price_from = self.lineEditFrom.text()
        price_to = self.lineEditTo.text()

        window = QMainWindow()
        self.chartUI = SearchResultsEx()
        # self.chartUI = SearchResultsEx(self.db, city, room_type, date, amenities, price_from, price_to)
        self.chartUI.setupUi(window)
        self.chartUI.show()





