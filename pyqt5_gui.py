import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QComboBox, QLineEdit, QPushButton, QVBoxLayout, QGridLayout, QMessageBox, QDateEdit, QTimeEdit, QCheckBox, QHBoxLayout, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt, QThread, QDate, QTime, pyqtSignal, QDateTime
import webdriver
import filter

from PyQt5.QtGui import QColor, QPixmap, QIcon
# import debugpy
# import pdb
class Worker(QThread):
    def __init__(self, departure, arrival, date, passengers, start_time, end_time, all_time, anahat_trains_checkbox, aktarma_checkbox, business_checkbox, disabled_checkbox):
        super().__init__()
        self.departure = departure
        self.arrival = arrival
        self.date = date
        self.passengers = passengers
        self.start_time = start_time
        self.end_time = end_time
        self.all_time = all_time
        self.anahat_trains_checkbox = anahat_trains_checkbox
        self.aktarma_checkbox = aktarma_checkbox
        self.business_checkbox = business_checkbox
        self.disabled_checkbox = disabled_checkbox
        self.search_active = True
    result_signal = pyqtSignal(dict)
    status_signal = pyqtSignal(str)  # Status string to show the current state of the search

    def run(self):
        # debugpy.debug_this_thread()
        # pdb.set_trace()  # Set a breakpoint here
        while self.search_active:
            self.status_signal.emit("Searching for trains...")
            # current_time = QTime.currentTime()
            # print("Departure:", self.departure)
            # print("Arrival:", self.arrival)
            # print("Date:", self.date)
            # print("Passengers:", self.passengers)
            # print("Start Time:", self.start_time.toString("HH:mm"))
            # print("End Time:", self.end_time.toString("HH:mm"))
            # print("all_time:", self.all_time)
            # print("anahat_trains_checkbox", self.anahat_trains_checkbox)
            # print("aktarma_checkbox", self.aktarma_checkbox)
            # print("business_checkbox", self.business_checkbox)
            # print("disabled_checkbox", self.disabled_checkbox)
            trains_info = webdriver.webdriverrun(self.departure, self.arrival, self.date, self.passengers)
            if "Growl message" in trains_info:
                self.result_signal.emit(trains_info)
                self.status_signal.emit("Search stopped")
                self.search_active = False


            if not trains_info:
                self.result_signal.emit({'fail':"could not connect the site trying again"})

            # print(trains_info)
            if trains_info and "Growl message" not in trains_info:
                filtered_trains = filter.filter_trains(trains_info, self.start_time, self.end_time, int(self.passengers), self.all_time, self.anahat_trains_checkbox, self.anahat_trains_checkbox, self.business_checkbox, self.disabled_checkbox)
                if not filtered_trains:
                    filtered_trains = {'fail':"no available trains"}
                    self.result_signal.emit(filtered_trains)
                else:
                    self.result_signal.emit(filtered_trains)
                    self.status_signal.emit("Search stopped")
                    self.search_active = False
                    break

            # time.sleep(5)  # Hardcoded interval if necessary


    def stop(self):
        self.status_signal.emit("Search stopped")
        self.search_active = False

class TrainAlertApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.worker = None

    def update_result(self, result):
        if "Growl message" in result:
            QMessageBox.information(self, "Search Result", result["Growl message"])
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.stop_search()
        elif "fail" in result:
            current_time = QDateTime.currentDateTime().toString("hh:mm:ss")
            pixmap = QPixmap(20, 20)  # Create a 20x20 square
            pixmap.fill(QColor('red'))  
            message = result["fail"]
            item_text = f"{current_time} - {message}"
            item = QListWidgetItem(item_text)
            icon = QIcon(pixmap)
            item.setIcon(icon)
            self.search_display.insertItem(0, item)

        elif result:
            train_count = len(result)
            # current_time = QDateTime.currentDateTime().toString("hh:mm:ss")
            pixmap = QPixmap(20, 20)  # Create a 20x20 square
            pixmap.fill(QColor('green')) 
            for count, train in enumerate(result, 1):
                message = result[train]['Departure Date'][:10] + " - "+ result[train]['Departure Date'][-5:] +  " - " + str(result[train]['Wagon Types'])
                item_text = f"Train {count} - {message}"
                item = QListWidgetItem(item_text)
                icon = QIcon(pixmap)
                item.setIcon(icon)
                self.search_display.insertItem(0, item)
            QMessageBox.information(self, "Search Result", f"{train_count} train(s) found.")
            self.stop_search()


    def initUI(self):
        # things to consider max 11 passenger number, date cannot be older, 
        self.setWindowTitle('TCDD - High-speed Train Place Finder')
        self.setGeometry(100, 50, 400, 300)

        self.search_active = False
        self.places =['Adana','Adana (Kiremithane)','Adapazarı','Adnanmenderes Havaalanı','Afyon A.Çetinkaya','Ahmetler','Ahmetli','Akdağmadeni YHT','Akgedik','Akhisar','Aksakal','Akçadağ','Akçamağara','Akşehir','Alayunt','Alayunt Müselles','Alaşehir','Alifuatpaşa','Aliköy','Alp','Alpu','Alpullu','Alöve','Amasya','Ankara Gar','Araplı','Argıthan','Arifiye','Artova','Arıkören','Asmakaya','Atça','Avşar','Aydın','Ayran','Ayrancı','Ayvacık','Aşkale','Bahçe','Bahçeli (Km.755+290 S)','Bahçeşehir','Bahçıvanova','Bakır','Balıkesir','Balıkesir (Gökköy)','Balıköy','Balışıh','Banaz','Bandırma Şehir','Baraklı','Baskil','Batman','Battalgazi','Bağıştaş','Bedirli','Belemedik','Bereket','Beyhan','Beylikköprü','Beylikova','Beyoğlu','Beşiri','Bilecik','Bilecik YHT','Bismil','Biçer','Bor','Bostankaya','Bozkanat','Bozkurt','Bozüyük','Bozüyük YHT','Boğazköprü','Boğazköprü Müselles','Boğazköy','Buharkent','Burdur','Böğecik','Büyükderbent YHT','Büyükçobanlar','Caferli','Ceyhan','Cürek','Dazkırı','Demirdağ','Demiriz','Demirkapı','Demirli','Demiryurt','Demirözü','Denizli','Derince YHT','Değirmenözü','Değirmisaz','Diliskelesi YHT','Dinar','Divriği','Diyarbakır','Doğançay','Doğanşehir','Dumlupınar','Durak','Dursunbey','Döğer','ERYAMAN YHT','Edirne','Ekerek','Ekinova','Elazığ','Elmadağ','Emiralem','Emirler','Erbaş','Ereğli','Ergani','Eriç','Erzincan','Erzurum','Eskişehir','Evciler','Eşme','Fevzipaşa','Fırat','Gazellidere','Gaziantep','Gaziemir','Gazlıgöl','Gebze','Genç','Germencik','Germiyan','Gezin','Goncalı','Goncalı Müselles','Gökçedağ','Gökçekısık','Gölbaşı','Gölcük','Gömeç','Göçentaşı','Güllübağ','Gümüş','Gümüşgün','Gündoğan','Güneyköy','Güneş','Güzelbeyli','Güzelyurt','Hacıbayram','Hacıkırı','Hacırahmanlı','Hanlı','Hasankale','Havza','Hekimhan','Hereke YHT','Himmetdede','Horasan','Horozköy','Horozluhan','Horsunlu','Huzurkent','Hüyük','Ildızım','Ilgın','Ilıca','Irmak','Isparta','Ispartakule','Kabakça','Kadılı','Kadınhan','Kaklık','Kalecik','Kalkancık','Kalın','Kandilli','Kangal','Kanlıca','Kapaklı','Kapıdere İstasyonu','Kapıkule','Karaali','Karaali','Karaağaçlı','Karabük','Karaisalıbucağı','Karakuyu','Karaköy','Karalar','Karaman','Karaosman','Karasenir','Karasu','Karaurgan','Karaözü','Kars','Kavak','Kavaklıdere','Kayabaşı','Kayabeyli','Kayaş','Kayseri','Kayseri (İncesu)','Kayışlar','Kaşınhan','Kelebek','Kemah','Kemaliye Çaltı','Kemerhisar','Keykubat','Keçiborlu','Kireç','Km. 30+500','Km. 37+362','Km.102+600','Km.139+500','Km.156 Durak','Km.171+000','Km.176+000','Km.186+000','Km.282+200','Km.286+500','Konaklar','Konya','Konya (Selçuklu YHT)','Kozdere','Kumlu Sayding','Kunduz','Kurbağalı','Kurfallı','Kurt','Kurtalan','Kuyucak','Kuşcenneti','Kuşsarayı','Köprüağzı','Köprüköy','Köprüören','Köşk','Kürk','Kütahya','Kılıçlar','Kırkağaç','Kırıkkale','Kırıkkale YHT','Kızoğlu','Kızılca','Kızılinler','Ladik','Lalahan','Leylek','Lüleburgaz','Maden','Malatya','Mamure','Manisa','Mazlumlar','Menderes','Menemen','Mercan','Meydan','Mezitler','Meşelidüz','Mithatpaşa','Muradiye','Muratlı','Mustafayavuz','Muş','Narlı','Nazilli','Nizip','Niğde','Nohutova','Nurdağ','Nusrat','Ortaklar','Osmancık','Osmaneli','Osmaniye','Oturak','Ovasaray','Oymapınar','Palandöken','Palu','Pamukören','Pancar','Pazarcık','Paşalı','Pehlivanköy','Piribeyler','Polatlı','Polatlı YHT','Porsuk','Pozantı','Pınarbaşı','Pınarlı','Rahova','Sabuncupınar','Salat','Salihli','Sallar','Samsun','Sandal','Sandıklı','Sapanca','Sarayköy','Sarayönü','Saruhanlı','Sarıdemir','Sarıkamış','Sarıkent','Sarımsaklı','Sarıoğlan','Savaştepe','Sağlık','Sekili','Selçuk','Sevindik','Seyitler','Sincan','Sindirler','Sinekli','Sivas','Sivas(Adatepe)','Sivrice','Soma','Sorgun YHT','Soğucak','Subaşı','Sudurağı','Sultandağı','Sultanhisar','Suluova','Susurluk','Suveren','Suçatı','Söke','Söğütlü Durak','Süngütaşı','Sünnetçiler','Sütlaç','Sıcaksu','Tanyeri','Tatvan Gar','Tavşanlı','Tayyakadın','Taşkent','Tecer','Tepeköy','Tokat(Yeşilyurt)','Topaç','Topdağı','Topulyurdu','Torbalı','Turgutlu','Turhal','Tuzhisar','Tüney','Türkoğlu','Tınaztepe','Ulam','Uluköy','Ulukışla','Uluova','Umurlu','Urganlı','Uyanık','Uzunköprü','Uşak','Velimeşe','Vezirhan','Yahşihan','Yahşiler','Yakapınar','Yarbaşı','Yarımca YHT','Yayla','Yaylıca','Yazlak','Yazıhan','Yağdonduran','Yeni Karasar','Yenice','Yenice D','Yenifakılı','Yenikangal','Yeniköy','Yeniçubuk','Yerköy','Yeşilhisar','Yolçatı','Yozgat YHT','Yunusemre','Yurt','Yıldırımkemal','Yıldızeli','Zile','Çadırkaya','Çakmak','Çalıköy','Çamlık','Çankırı','Çardak','Çatalca','Çavundur','Çavuşcugöl','Çay','Çağlar','Çerikli','Çerkezköy','Çerkeş','Çetinkaya','Çiftehan','Çizözü','Çiğli','Çobanhasan','Çorlu','Çukurbük','Çukurhüseyin','Çumra','Çöltepe','Çöğürler','İhsaniye','İliç','İnay','İncirlik','İncirliova','İsabeyli','İshakçelebi','İsmetpaşa','İstanbul(Bakırköy)','İstanbul(Bostancı)','İstanbul(Halkalı)','İstanbul(Pendik)','İstanbul(Söğütlüçeşme)','İzmir (Basmane)','İzmit YHT','Şakirpaşa','Şarkışla','Şefaatli','Şefkat','Şehitlik','Şerbettar']
        layout = QGridLayout()
        self.setLayout(layout)

        # Place
        departure_layout = QHBoxLayout()
        self.departure_label = QLabel('Departure:')
        departure_layout.addWidget(self.departure_label)
        self.departure_dropdown = QComboBox()
        self.departure_dropdown.addItems(self.places)
        departure_layout.addWidget(self.departure_dropdown, alignment=Qt.AlignmentFlag.AlignLeft)
        self.departure_dropdown.setEditable(True)
        departure_layout.setStretch(1, 3)  

        layout.addLayout(departure_layout, 0, 0)  # Spanning across columns 0 and 1
        
        arrival_layout = QHBoxLayout()

        self.arrival_label = QLabel('Arrival:')
        arrival_layout.addWidget(self.arrival_label)
        self.arrival_dropdown = QComboBox()
        self.arrival_dropdown.addItems(self.places)
        arrival_layout.addWidget(self.arrival_dropdown, alignment=Qt.AlignmentFlag.AlignLeft)
        self.arrival_dropdown.setEditable(True)
        arrival_layout.setStretch(1, 3)  
        arrival_layout.setSpacing(23)

        layout.addLayout(arrival_layout, 1, 0)  # Spanning across columns 0 and 1


        # Date
        date_layout = QHBoxLayout()
        
        self.date_label = QLabel('Date:')
        date_layout.addWidget(self.date_label)
        self.date_entry = QDateEdit(calendarPopup=True)
        
        self.date_entry.setDisplayFormat("dd.MM.yyyy")
        self.date_entry.setDate(QDate.currentDate())  # Default to current date
        self.date_entry.setFixedWidth(80)
        date_layout.addWidget(self.date_entry, alignment=Qt.AlignmentFlag.AlignLeft)
        date_layout.setStretch(1, 3)
        date_layout.setSpacing(30)

        layout.addLayout(date_layout, 2, 0)  # Spanning across columns 0 and 1

        # Number of Passengers
        passengers_layout = QHBoxLayout()
        self.passengers_label = QLabel('Passenger:')
        passengers_layout.addWidget(self.passengers_label)

        self.passengers_entry = QLineEdit()
        self.passengers_entry.setMaxLength(2)
        self.passengers_entry.setText("1")  # Default to 1 passenger

        passengers_layout.addWidget(self.passengers_entry, alignment=Qt.AlignmentFlag.AlignLeft)
        self.passengers_entry.setFixedWidth(30)
        passengers_layout.setStretch(1, 3)
        # self.passengers_entry.setStyleSheet("margin-left: -50px;")  # Adjust the value to your needs
        # Set the spacing to 0 between widgets
        # passengers_layout.setSpacing(0)

        # Add the horizontal layout to the grid layout
        layout.addLayout(passengers_layout, 3, 0)  # Spanning across columns 0 and 1


        # All Time Checkbox - Using QHBoxLayout to place label before checkbox
        all_time_layout = QHBoxLayout()
        self.all_time_label = QLabel('I dont have any specific time interval')
        all_time_layout.addWidget(self.all_time_label)
        self.all_time_checkbox = QCheckBox()
        self.all_time_checkbox.stateChanged.connect(self.toggle_time_entries)
        all_time_layout.addWidget(self.all_time_checkbox, alignment=Qt.AlignmentFlag.AlignLeft)
        self.start_time_label = QLabel('Start Time:')
        all_time_layout.addWidget(self.start_time_label)
        self.start_time_entry = QTimeEdit()
        self.start_time_entry.setDisplayFormat("HH:mm")
        self.start_time_entry.setTime(QTime.currentTime())  # Default to current time
        all_time_layout.addWidget(self.start_time_entry)
        self.end_time_label = QLabel('End Time:')
        all_time_layout.addWidget(self.end_time_label, alignment=Qt.AlignmentFlag.AlignLeft)
        self.end_time_entry = QTimeEdit()
        self.end_time_entry.setDisplayFormat("HH:mm")
        self.end_time_entry.setTime(QTime.currentTime().addSecs(3600))  # Default to 1 hour later
        all_time_layout.addWidget(self.end_time_entry, alignment=Qt.AlignmentFlag.AlignLeft)

        
        layout.addLayout(all_time_layout, 4, 0)

        # Check boxes for anahat trains, aktarma, business class, disabled seats
        # All Time Checkbox - Using QHBoxLayout to place label before checkbox
        preferences_layout = QHBoxLayout()
        self.preferences_layout = QLabel('Include the followings?')
        preferences_layout.addWidget(self.preferences_layout)
        layout.addLayout(preferences_layout, 5,0)

        anahat_layout = QHBoxLayout()
        self.anahat_layout = QLabel('Include mainline(anahat) trains? e.g Ankara Ekspresi')
        anahat_layout.addWidget(self.anahat_layout)
        self.anahat_trains_checkbox = QCheckBox()
        anahat_layout.addWidget(self.anahat_trains_checkbox)
        layout.addLayout(anahat_layout, 6,0)

        aktarma_layout = QHBoxLayout()
        self.aktarma_layout = QLabel('Include transfer(aktarma) trains?')
        aktarma_layout.addWidget(self.aktarma_layout)
        self.aktarma_checkbox = QCheckBox()
        aktarma_layout.addWidget(self.aktarma_checkbox, alignment=Qt.AlignmentFlag.AlignLeft)
        aktarma_layout.setStretch(1, 3)
        layout.addLayout(aktarma_layout, 7,0)

        business_layout = QHBoxLayout()
        self.business_layout = QLabel('Inlude business class seats?')
        business_layout.addWidget(self.business_layout)
        self.business_checkbox = QCheckBox()
        business_layout.addWidget(self.business_checkbox, alignment=Qt.AlignmentFlag.AlignLeft)
        business_layout.setStretch(1, 3)

        layout.addLayout(business_layout, 8,0)

        disabled_layout = QHBoxLayout()
        self.disabled_layout = QLabel('Include disabled seats?')
        disabled_layout.addWidget(self.disabled_layout)
        self.disabled_checkbox = QCheckBox()
        disabled_layout.addWidget(self.disabled_checkbox , alignment=Qt.AlignmentFlag.AlignLeft)
        disabled_layout.setStretch(1, 3)

        layout.addLayout(disabled_layout, 9,0)

        button_layout = QHBoxLayout()
        self.start_button = QPushButton('Start')
        self.start_button.clicked.connect(self.start_search)
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton('Stop')
        self.stop_button.clicked.connect(self.stop_search)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)

        self.clear_button = QPushButton('Clear Display')
        self.clear_button.clicked.connect(self.clear_display)
        button_layout.addWidget(self.clear_button)

        layout.addLayout(button_layout, 10, 0)

        status_layout = QHBoxLayout()
        self.status_label = QLabel('Status: Waiting for search to start...')
        status_layout.addWidget(self.status_label)
        layout.addLayout(status_layout, 11, 0)

        # Train Search Info Display (QListWidget)
        self.search_display = QListWidget()  # Create QListWidget to display train search results
        layout.addWidget(self.search_display, 12, 0)  # Add it directly to the layout

    def toggle_time_entries(self, state):
        is_checked = (state == Qt.Checked)
        self.start_time_entry.setEnabled(not is_checked)
        self.end_time_entry.setEnabled(not is_checked)
        self.start_time_entry.setStyleSheet("background-color: lightgray;" if is_checked else "background-color: white;")
        self.end_time_entry.setStyleSheet("background-color: lightgray;" if is_checked else "background-color: white;")

    def update_status(self, status):
        """Update the status label to show the current state."""
        self.status_label.setText(f"Status: {status}")
        

    def start_search(self):
        departure = self.departure_dropdown.currentText()
        arrival = self.arrival_dropdown.currentText()
        date = self.date_entry.date().toString("dd.MM.yyyy")
        passengers = self.passengers_entry.text()
        start_time = self.start_time_entry.time().toString()
        end_time = self.end_time_entry.time().toString()
        all_time = self.all_time_checkbox.isChecked()
        anahat_trains_checkbox = self.anahat_trains_checkbox.isChecked()
        aktarma_checkbox = self.aktarma_checkbox.isChecked()
        business_checkbox = self.business_checkbox.isChecked()
        disabled_checkbox = self.disabled_checkbox.isChecked()
        self.start_button.setEnabled(False)  # Disable start button
        self.stop_button.setEnabled(True)

        if not passengers.isdigit():
            QMessageBox.critical(self, "Error", "Passengers must be numeric.")
            return

        if not all_time and start_time >= end_time:
            QMessageBox.critical(self, "Error", "Start time must be before end time.")
            return
        
        if self.worker is not None:  # Prevent multiple threads
            QMessageBox.warning(self, "Warning", "Search is already running.")
            return
        
        self.search_active = True
        self.worker = Worker(departure, arrival, date, passengers, start_time, end_time, all_time, anahat_trains_checkbox, aktarma_checkbox, business_checkbox, disabled_checkbox)
        self.worker.result_signal.connect(self.update_result)
        self.worker.status_signal.connect(self.update_status)  # Connect the worker signal to update the status label

        self.worker.start()

    def stop_search(self):
        if self.worker is not None:
            self.worker.stop()
            self.worker.wait()  # Ensure thread finishes execution
            self.worker = None
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def clear_display(self):
        self.search_display.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TrainAlertApp()
    ex.show()
    sys.exit(app.exec_())



#        self.places =['Adana','Adana (Kiremithane)','Adapazarı','Adnanmenderes Havaalanı','Afyon A.Çetinkaya','Ahmetler','Ahmetli','Akdağmadeni YHT','Akgedik','Akhisar','Aksakal','Akçadağ','Akçamağara','Akşehir','Alayunt','Alayunt Müselles','Alaşehir','Alifuatpaşa','Aliköy','Alp','Alpu','Alpullu','Alöve','Amasya','Ankara Gar','Araplı','Argıthan','Arifiye','Artova','Arıkören','Asmakaya','Atça','Avşar','Aydın','Ayran','Ayrancı','Ayvacık','Aşkale','Bahçe','Bahçeli (Km.755+290 S)','Bahçeşehir','Bahçıvanova','Bakır','Balıkesir','Balıkesir (Gökköy)','Balıköy','Balışıh','Banaz','Bandırma Şehir','Baraklı','Baskil','Batman','Battalgazi','Bağıştaş','Bedirli','Belemedik','Bereket','Beyhan','Beylikköprü','Beylikova','Beyoğlu','Beşiri','Bilecik','Bilecik YHT','Bismil','Biçer','Bor','Bostankaya','Bozkanat','Bozkurt','Bozüyük','Bozüyük YHT','Boğazköprü','Boğazköprü Müselles','Boğazköy','Buharkent','Burdur','Böğecik','Büyükderbent YHT','Büyükçobanlar','Caferli','Ceyhan','Cürek','Dazkırı','Demirdağ','Demiriz','Demirkapı','Demirli','Demiryurt','Demirözü','Denizli','Derince YHT','Değirmenözü','Değirmisaz','Diliskelesi YHT','Dinar','Divriği','Diyarbakır','Doğançay','Doğanşehir','Dumlupınar','Durak','Dursunbey','Döğer','ERYAMAN YHT','Edirne','Ekerek','Ekinova','Elazığ','Elmadağ','Emiralem','Emirler','Erbaş','Ereğli','Ergani','Eriç','Erzincan','Erzurum','Eskişehir','Evciler','Eşme','Fevzipaşa','Fırat','Gazellidere','Gaziantep','Gaziemir','Gazlıgöl','Gebze','Genç','Germencik','Germiyan','Gezin','Goncalı','Goncalı Müselles','Gökçedağ','Gökçekısık','Gölbaşı','Gölcük','Gömeç','Göçentaşı','Güllübağ','Gümüş','Gümüşgün','Gündoğan','Güneyköy','Güneş','Güzelbeyli','Güzelyurt','Hacıbayram','Hacıkırı','Hacırahmanlı','Hanlı','Hasankale','Havza','Hekimhan','Hereke YHT','Himmetdede','Horasan','Horozköy','Horozluhan','Horsunlu','Huzurkent','Hüyük','Ildızım','Ilgın','Ilıca','Irmak','Isparta','Ispartakule','Kabakça','Kadılı','Kadınhan','Kaklık','Kalecik','Kalkancık','Kalın','Kandilli','Kangal','Kanlıca','Kapaklı','Kapıdere İstasyonu','Kapıkule','Karaali','Karaali','Karaağaçlı','Karabük','Karaisalıbucağı','Karakuyu','Karaköy','Karalar','Karaman','Karaosman','Karasenir','Karasu','Karaurgan','Karaözü','Kars','Kavak','Kavaklıdere','Kayabaşı','Kayabeyli','Kayaş','Kayseri','Kayseri (İncesu)','Kayışlar','Kaşınhan','Kelebek','Kemah','Kemaliye Çaltı','Kemerhisar','Keykubat','Keçiborlu','Kireç','Km. 30+500','Km. 37+362','Km.102+600','Km.139+500','Km.156 Durak','Km.171+000','Km.176+000','Km.186+000','Km.282+200','Km.286+500','Konaklar','Konya','Konya (Selçuklu YHT)','Kozdere','Kumlu Sayding','Kunduz','Kurbağalı','Kurfallı','Kurt','Kurtalan','Kuyucak','Kuşcenneti','Kuşsarayı','Köprüağzı','Köprüköy','Köprüören','Köşk','Kürk','Kütahya','Kılıçlar','Kırkağaç','Kırıkkale','Kırıkkale YHT','Kızoğlu','Kızılca','Kızılinler','Ladik','Lalahan','Leylek','Lüleburgaz','Maden','Malatya','Mamure','Manisa','Mazlumlar','Menderes','Menemen','Mercan','Meydan','Mezitler','Meşelidüz','Mithatpaşa','Muradiye','Muratlı','Mustafayavuz','Muş','Narlı','Nazilli','Nizip','Niğde','Nohutova','Nurdağ','Nusrat','Ortaklar','Osmancık','Osmaneli','Osmaniye','Oturak','Ovasaray','Oymapınar','Palandöken','Palu','Pamukören','Pancar','Pazarcık','Paşalı','Pehlivanköy','Piribeyler','Polatlı','Polatlı YHT','Porsuk','Pozantı','Pınarbaşı','Pınarlı','Rahova','Sabuncupınar','Salat','Salihli','Sallar','Samsun','Sandal','Sandıklı','Sapanca','Sarayköy','Sarayönü','Saruhanlı','Sarıdemir','Sarıkamış','Sarıkent','Sarımsaklı','Sarıoğlan','Savaştepe','Sağlık','Sekili','Selçuk','Sevindik','Seyitler','Sincan','Sindirler','Sinekli','Sivas','Sivas(Adatepe)','Sivrice','Soma','Sorgun YHT','Soğucak','Subaşı','Sudurağı','Sultandağı','Sultanhisar','Suluova','Susurluk','Suveren','Suçatı','Söke','Söğütlü Durak','Süngütaşı','Sünnetçiler','Sütlaç','Sıcaksu','Tanyeri','Tatvan Gar','Tavşanlı','Tayyakadın','Taşkent','Tecer','Tepeköy','Tokat(Yeşilyurt)','Topaç','Topdağı','Topulyurdu','Torbalı','Turgutlu','Turhal','Tuzhisar','Tüney','Türkoğlu','Tınaztepe','Ulam','Uluköy','Ulukışla','Uluova','Umurlu','Urganlı','Uyanık','Uzunköprü','Uşak','Velimeşe','Vezirhan','Yahşihan','Yahşiler','Yakapınar','Yarbaşı','Yarımca YHT','Yayla','Yaylıca','Yazlak','Yazıhan','Yağdonduran','Yeni Karasar','Yenice','Yenice D','Yenifakılı','Yenikangal','Yeniköy','Yeniçubuk','Yerköy','Yeşilhisar','Yolçatı','Yozgat YHT','Yunusemre','Yurt','Yıldırımkemal','Yıldızeli','Zile','Çadırkaya','Çakmak','Çalıköy','Çamlık','Çankırı','Çardak','Çatalca','Çavundur','Çavuşcugöl','Çay','Çağlar','Çerikli','Çerkezköy','Çerkeş','Çetinkaya','Çiftehan','Çizözü','Çiğli','Çobanhasan','Çorlu','Çukurbük','Çukurhüseyin','Çumra','Çöltepe','Çöğürler','İhsaniye','İliç','İnay','İncirlik','İncirliova','İsabeyli','İshakçelebi','İsmetpaşa','İstanbul(Bakırköy)','İstanbul(Bostancı)','İstanbul(Halkalı)','İstanbul(Pendik)','İstanbul(Söğütlüçeşme)','İzmir (Basmane)','İzmit YHT','Şakirpaşa','Şarkışla','Şefaatli','Şefkat','Şehitlik','Şerbettar']
