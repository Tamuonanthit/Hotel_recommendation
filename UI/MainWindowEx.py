import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QComboBox
from PyQt6.QtSql import QSqlDatabase

from UI import MainWindow
from UI.MainWindow import Ui_MainWindow
from UI.SearchResultsEx import SearchResultsEx
from Filter_based import FilterRecommender


class MainWindowEx(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        super().setupUi(self)
        # Connect buttons to their event handlers
        self.pushButtonSubmit.clicked.connect(self.openSearchResults)
        self.pushButtonClose.clicked.connect(self.close)
        for combo_box in self.findChildren(QComboBox):
            combo_box.activated.connect(self.updateSelectedValues)

    def updateSelectedValues(self):
        sender_combobox = self.sender()
        if sender_combobox.objectName() == "cbxCity":
            self.selected_city = sender_combobox.currentText()
        elif sender_combobox.objectName() == "cbxRoomtype":
            self.selected_roomtype = sender_combobox.currentText()
        elif sender_combobox.objectName() == "cbxAmenities":
            self.selected_amenities = sender_combobox.currentText()
    def openSearchResults(self):
        print(f"Opening search results for city: {self.selected_city}")
        city=self.selected_city
        roomtype=self.selected_roomtype
        amenities=self.selected_amenities
        print(city)
        print(roomtype)
        print(amenities)

        ct = FilterRecommender("airbnb_data.db")
        result = ct.city_based(self.selected_city)
        print(f"FilterRecommender result: {result}")

        window = QMainWindow()
        self.chartUI = SearchResultsEx()
        self.chartUI.setupUi(window)
        window.show()
