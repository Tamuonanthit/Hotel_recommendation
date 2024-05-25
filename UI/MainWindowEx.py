import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QComboBox
from PyQt6.QtSql import QSqlDatabase

from UI import MainWindow
from UI.MainWindow import Ui_MainWindow
from UI.SearchResultsEx import SearchResultsEx



class MainWindowEx(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # Connect buttons to their event handlers
        self.pushButtonSubmit.clicked.connect(self.openSearchResults)
        self.pushButtonClose.clicked.connect(self.close)

        self.selected_city = None
        self.selected_roomtype = None
        self.selected_amenities = None

        for combo_box in self.findChildren(QComboBox):
            combo_box.activated.connect(self.updateSelectedCombo)

        self.lineEditDays.textChanged.connect(self.updateSelectedLine)
        self.lineEditFrom.textChanged.connect(self.updateSelectedLine)
        self.lineEditTo.textChanged.connect(self.updateSelectedLine)

    def updateSelectedLine(self):
        sender = self.sender()
        if sender.objectName() == "lineEditDays":
            self.selected_days = sender.text()
        elif sender.objectName() == "lineEditFrom":
            self.selected_minprice = sender.text()
        elif sender.objectName() == "lineEditTo":
            self.selected_maxprice = sender.text()

    def updateSelectedCombo(self):
        sender = self.sender()
        if sender.objectName() == "cbxCity":
            self.selected_city = sender.currentText()
        elif sender.objectName() == "cbxRoomtype":
            self.selected_roomtype = sender.currentText()
        elif sender.objectName() == "cbxAmenities":
            self.selected_amenities = sender.currentText()


    def openSearchResults(self):
        city = self.selected_city
        room_type = self.selected_roomtype
        amenities = self.selected_amenities
        days = int(self.selected_days)
        price_from = int(self.selected_minprice)
        price_to = int(self.selected_maxprice)

        self.chartUI = SearchResultsEx()
        self.chartUI.show()




