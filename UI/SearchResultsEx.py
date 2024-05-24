from PyQt6.QtWidgets import QMainWindow, QTableWidgetItem
from PyQt6.QtSql import QSqlQuery
from SearchResults import Ui_MainWindow


class SearchResultsEx(QMainWindow, Ui_MainWindow):
    def __init__(self):

    # def __init__(self, db, city, room_type, amenities, price_from, price_to):

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

    # def populateResults(self):
    #     query_str = """
    #     SELECT name, listing_url, price, review_scores_rating
    #     FROM airbnb_data
    #     WHERE city = ?
    #     AND room_type = ?
    #     AND amenities LIKE ?
    #     AND price BETWEEN ? AND ?
    #     AND julianday('now') < julianday(available_date) + (maximum_nights - minimum_nights)
    #     """
    #     query = QSqlQuery(self.db)
    #     query.prepare(query_str)
    #     query.addBindValue(self.city)
    #     query.addBindValue(self.room_type)
    #     query.addBindValue(f'%{self.amenities}%')
    #     query.addBindValue(self.price_from)
    #     query.addBindValue(self.price_to)
    #
    #     if not query.exec():
    #         print("Failed to execute query:", query.lastError().text())
    #         return
    #
    #     self.ui.tableWidget.setColumnCount(4)
    #     self.ui.tableWidget.setHorizontalHeaderLabels(['Name', 'Link URL', 'Price', 'Rate'])

    #     row = 0
    #     while query.next():
    #         self.ui.tableWidget.insertRow(row)
    #         self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(query.value(0)))
    #         self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(query.value(1)))
    #         self.ui.tableWidget.setItem(row, 2, QTableWidgetItem(query.value(2)))
    #         self.ui.tableWidget.setItem(row, 3, QTableWidgetItem(query.value(3)))
    #         row += 1

