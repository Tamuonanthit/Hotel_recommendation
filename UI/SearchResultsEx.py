from PyQt6.QtWidgets import QMainWindow, QTableWidgetItem
from PyQt6.QtSql import QSqlQuery
from SearchResults import Ui_MainWindow

from Filter_based import FilterRecommender
from Content_based import ContentRecommender

class SearchResultsEx(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButtonBack.clicked.connect(self.close)

        # self.db = db
        # self.city = city
        # self.room_type = room_type
        # self.amenities = amenities
        # self.price_from = price_from
        # self.price_to = price_to
        # self.populateResults()

    def showDataIntoTableWidget(self, df):
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(len(df.columns))
        for i in range(len(df.columns)):
            columnHeader = df.columns[i]
            self.tableWidget.setHorizontalHeaderItem(i, QTableWidgetItem(columnHeader))
        row = 0
        for item in df.iloc:
            arr = item.values.tolist()
            self.tableWidget.insertRow(row)
            j = 0
            for data in arr:
                self.tableWidget.setItem(row, j, QTableWidgetItem(str(data)))
                j = j + 1
            row = row + 1



