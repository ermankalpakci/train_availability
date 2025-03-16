import sys
import re
from PyQt5.QtWidgets import QApplication, QCompleter, QWidget, QFrame, QStatusBar, QLabel, QComboBox, QLineEdit, QPushButton, QGridLayout, QMessageBox, QDateEdit, QTimeEdit, QCheckBox, QHBoxLayout, QVBoxLayout, QScrollArea, QGroupBox
from PyQt5.QtCore import Qt, QThread, QDate, QTime, pyqtSignal, pyqtSlot
from send_email import EmailSender
from user import TrainSearch
from api_auth import SeleniumDriver, SeleniumDriverError
from searchobserver import TrainSearchObserver
from user import SearchResult
from db_train import TrainDatabase, DBConfig
from datetime import timedelta


class EmailWorker(QThread):
    email_sent_signal = pyqtSignal(bool, str)

    def __init__(self, email, password):
        super().__init__()
        self.email = email
        self.password = password

    def run(self):

        try:
            emailsender = EmailSender()
            emailsender.send_test_email(self.email, self.password)
            self.email_sent_signal.emit(True, "Test email sent successfully!")
        except Exception as e:
            self.email_sent_signal.emit(False, f"Failed to send email: {str(e)}")


class SeleniumWorker(QThread):
    auth_header_signal = pyqtSignal(bool, str)

    def __init__(self):
        super().__init__()
        self._result = None

    def run(self):
        try:
            with SeleniumDriver().managed_session() as selenium:
                selenium.navigate_to('https://ebilet.tcddtasimacilik.gov.tr')
                auth_header = selenium.find_authorization_header()
                self._result = (True, auth_header) if auth_header else (False, "No auth header found")
        except SeleniumDriverError as e:
            self._result = (False, f"Error: {str(e)}")
        finally:
            if self._result:
                self.auth_header_signal.emit(*self._result)

    def wait_for_result(self):
        """Block until thread completes and return result"""
        if self.isRunning():
            self.finished.connect(lambda: None)
            self.wait()
        return self._result


class TrainAlertApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.email_worker = None
        self.selenium_worker = None
        self.users = []
        self.selected_user = None
        self.auth_header = None  
        self.search_active = False 
        self.observer = None
        self.search_widget_map = {}


    def email_function(self):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@gmail\.com$', self.email_input.text()):
            QMessageBox.warning(self, "Error", "Check your email")
            self.email_test_button.setEnabled(True)
            return

        self.email_test_button.setText("Sending...")
        self.email_test_button.setEnabled(False)
        self.start_button.setEnabled(False)

        self.email_worker = EmailWorker(self.email_input.text(), self.password_input.text())
        self.email_worker.email_sent_signal.connect(self.handle_email_status)
        self.email_worker.finished.connect(lambda: self.email_worker.deleteLater())
        self.email_worker.start()

    def handle_email_status(self, success, message):
        QMessageBox.information(self, "Email Status", message)
        self.email_test_button.setText("Send Test Email")
        self.email_test_button.setEnabled(True)
        self.start_button.setEnabled(True)

    def create_labeled_input(self, label_text, input_widget):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0) 
        layout.setSpacing(8) 
        label = QLabel(label_text)
        layout.addWidget(label)
        layout.addWidget(input_widget, alignment=Qt.AlignmentFlag.AlignLeft)
        return layout
    
    def create_line(self):
        h_line = QFrame()
        h_line.setFrameShape(QFrame.HLine)  
        h_line.setFrameShadow(QFrame.Sunken)  
        h_line.setFixedHeight(2)  
        return h_line
    

    def initUI(self):
        self.setWindowTitle('TCDD - High-speed Train Place Finder')
        self.setGeometry(200, 100, 800, 600)

        self.places = ['ADAPAZARI', 'ALİFUATPAŞA', 'ARİFİYE', 'BİLECİK', 'BOZÜYÜK', 'GEBZE', 'MİTHATPAŞA', 'OSMANELİ', 'İSTANBUL(PENDİK)', 'KARAKÖY', 'VEZİRHAN', 'YAYLA', 'SAPANCA', 'AHATLI', 'BEYLİKKÖPRÜ', 'BİÇER', 'ESKİŞEHİR', 'ANKARA GAR', 'ARAPLI', 'BALIKISIK', 'BALIŞIH', 'YUNUSEMRE', 'BEYLİKOVA', 'BOR', 'CAFERLİ', 'CEBECİLER', 'SARIKENT', 'ÇANKIRI', 'ÇATALAĞZI', 'ÇERİKLİ', 'DERECİKÖREN', 'BEREKET', 'YENİFAKILI', 'FİLYOS', 'GÖBÜ', 'GÖKÇELER', 'HİMMETDEDE', 'ELMADAĞ', 'IRMAK', 'IŞIKVEREN', 'KALECİK', 'KALKANCIK', 'KANLICA', 'KAPUZ', 'KARABÜK', 'YAĞDONDURAN', 'KARAOSMAN', 'KARALAR', 'KARASENİR', 'KAYIKÇILAR', 'KAYADİBİ', 'HÜYÜK', 'İNAĞZI', 'KAYSERİ (İNCESU)', 'KİLİMLİ', 'KILIÇLAR', 'KIRIKKALE', 'SALTUKOVA', 'KURBAĞALI', 'LALAHAN', 'SAZPINARI', 'MALIKÖY', 'KAYSERİ', 'KAZKÖY', 'KEMERHİSAR', 'NİĞDE', 'PAŞALI', 'POLATLI', 'SİNCAN', 'ŞEFAATLİ', 'TEMELLİ', 'TÜNEY', 'TÜRKALİ', 'MUSLU', 'YAHŞİHAN', 'YERKÖY', 'ÜÇBURGU', 'YEŞİLHİSAR', 'ZONGULDAK', 'ÇAMLARALTI', 'BAKACAKKADI', 'AKYAMAÇ', 'SEFERCİK', 'YEŞİLYENİCE', 'KÖLEMEN', 'TÜRKOBASI', 'ZONGULDAK (KİREMİTHANE)', 'IBRICAK', 'POLATLI YHT', 'PINARLI DURAĞI', 'AKKEÇİLİ DURAĞI', 'GÜMÜŞÇAY DURAĞI', 'BAYINDIR MYO', 'AHMETLER', 'AKHİSAR', 'AKSAKAL', 'PİYADELER', 'ARIKBAŞI', 'ATÇA', 'AYDIN', 'AYVACIK', 'BANAZ', 'BANDIRMA ŞEHİR', 'CEBER KAMARA', 'BEYTİKÖY', 'ADNANMENDERES HAVAALANI', 'BUHARKENT', 'KUŞCENNETİ', 'MENDERES', 'ÇALIKÖY', 'ÇİĞLİ', 'ÇOBANHASAN', 'ÇOBANİSA', 'ÇUKURHÜSEYİN', 'DENİZLİ', 'DEREBAŞI', 'KAVAKLIDERE', 'İZMİR (BASMANE)', 'EŞME', 'FURUNLU', 'GAZİEMİR', 'PAMUKÖREN', 'GERMENCİK', 'GONCALI', 'GONCALI MÜSELLES', 'GÜMÜŞÇAYI', 'GÜRGÜR', 'HACIRAHMANLI', 'BAKIR', 'HOROZKÖY', 'HORSUNLU', 'DOYRANLI', 'ELİFLİ', 'EMİRALEM', 'İSHAKÇELEBİ', 'KABAZLI', 'KAPAKLI', 'KARAAĞAÇLI', 'KARAALİ', 'KARPUZLU', 'KAYIŞLAR', 'KIRKAĞAÇ', 'KONAKLAR', 'KÖSEALİ', 'KÖŞK', 'İLKKURŞUN', 'İNAY', 'İNCİRLİOVA', 'İSABEYLİ', 'MURADİYE', 'NAZİLLİ', 'NOHUTOVA', 'ORTAKLAR', 'OTURAK', 'PANCAR', 'SAĞLIK', 'SALİHLİ', 'KUYUCAK', 'MANİSA', 'MENEMEN', 'SAZLIKÖY', 'SELÇUK', 'SOĞUCAK', 'SÖKE', 'SUSURLUK', 'TAŞKESİK', 'TEPEKÖY', 'SARAYKÖY', 'SART', 'SARUHANLI', 'SAVAŞTEPE', 'TOKI DURAĞI', 'UMURLU', 'URGANLI', 'UŞAK', 'YAKAKÖY', 'YENİKÖY', 'YENİKÖY D', 'SÜNNETÇİLER', 'ARMUTLU DURAĞI', 'YARAŞLI', 'TİRE', 'TORBALI', 'ÇİZÖZÜ', 'KM.85+597', 'ULAŞŞEHİR', 'ÇELİKALAN', 'KM.1+164', 'KM.1+290', 'BAHÇELİ (KM.755+290 S)', 'AŞAĞI GÜNEŞ', 'YAHŞİLER', 'KM 649+760 (VARYANTBAŞI)', 'YENİKANGAL', 'KM 700+670 (VARYANTSONU)', 'AMASYA', 'ARTOVA', 'AŞKALE', 'AVŞAR', 'BAĞIŞTAŞ', 'BORSA', 'BOĞAZKÖY', 'BOSTANKAYA', 'GÖÇENTAŞI', 'CEBESOY', 'CÜREK', 'KEMALİYE ÇALTI', 'KÖMÜR İŞLETMELERİ', 'TOPAÇ', 'ÇETİNKAYA', 'BEDİRLİ', 'BOĞAZİÇİ', 'ERBAŞ', 'KM.45+492 MR', 'ERİÇ', 'ERZURUM', 'SANDAL', 'ATMA', 'YENİÇUBUK', 'GERMİYAN', 'ÇUKURBÜK', 'DAZLAK', 'DEMİRDAĞ', 'GÜLLÜBAĞ', 'GÜNEŞ', 'HACIBAYRAM', 'HANLI', 'HASANKALE', 'HAVZA', 'KALIN', 'KANDİLLİ', 'GÖMEÇ', 'KARASU', 'KARAURGAN', 'KARS', 'KAVAK', 'KAYABAŞI', 'KEMAH', 'KIZILCA', 'KIZOĞLU', 'ILICA', 'KARAÖZÜ', 'MEŞELİDÜZ', 'TOKAT(YEŞİLYURT)', 'ÖZEL İDARE', 'OVASARAY', 'PALANDÖKEN', 'DURAKLI', 'SİVAS(ADATEPE)', 'SAMSUN', 'SARIDEMİR', 'DEMİRKAPI', 'KÖPRÜKÖY', 'KUNDUZ', 'KURUDERE', 'LADİK', 'SİVAS', 'SÜNGÜTAŞI', 'SULUOVA', 'ŞAHNALAR', 'ŞARKIŞLA', 'TANYERİ', 'TECER', 'TUZHİSAR', 'SARIKAMIŞ', 'SARIMSAKLI', 'GÜZELBEYLİ', 'TOPDAĞI', 'YILDIZELİ', 'ZİLE', 'ULAŞ', 'YENİCE D', 'SALUCA', 'AYAZ', 'TABUR', 'DUTLUK', 'GEMİCİ', 'KM.102+600', 'AKÇAMAĞARA', 'AMBAR', 'BASKİL', 'BATMAN', 'UĞUR', 'KUŞSARAYI', 'BEŞİRİ', 'ÇİĞDEM', 'ÇÖLTEPE', 'ELAZIĞ', 'ERGANİ', 'BATTALGAZİ', 'FIRAT', 'GEZİN', 'BEYHAN', 'BİSMİL', 'ÇAĞLAR', 'HEKİMHAN', 'KURT', 'KURTALAN', 'MURATBAĞI', 'KÜRK', 'LEYLEK', 'MADEN', 'GÖLCÜK', 'BOZDEMİR', 'YAYLICA', 'MUŞ', 'PALU', 'PINARLI', 'SALAT', 'SALLAR', 'EKEREK', 'ARZUOĞLU', 'MALATYA', 'DEMİRLİKUYU', 'ULAM', 'ULUOVA', 'YOLÇATI', 'YURT', 'BAHÇETEPE', 'RAHOVA', 'TATVAN GAR', 'SİVRİCE', 'SUVEREN', 'ŞEFKAT', 'SEYİTHASAN', 'HODAN', 'ADANA (KİREMİTHANE)', 'KM.262+646', 'ADANA', 'KM 11+100', 'BELEMEDİK', 'BÖĞECİK', 'CEYHAN', 'ÇAKMAK', 'ÇUMRA', 'DÖRTYOL', 'DURAK', 'EREĞLİ', 'ERZİN', 'ARIKÖREN', 'AYRANCI', 'HACIKIRI', 'İNCİRLİK', 'İSKENDERUN', 'KARAİSALIBUCAĞI', 'KARAMAN', 'KAŞINHAN', 'BÜYÜKDERBENT YHT', 'KONYA', 'GÜMÜŞ', 'YAKAPINAR', 'MUSTAFAYAVUZ', 'NİZİP', 'PAYAS', 'POZANTI', 'SARISEKİ', 'SUDURAĞI', 'ŞAKİRPAŞA', 'DEMİRYURT', 'TAŞKENT', 'TOPRAKKALE', 'ULUKIŞLA', 'GÜNYAZI', 'ŞEHİTLİK', 'GAZİANTEP', 'OSMANCIK', 'HOROZLUHAN', 'PAYAS ŞEHİR D. KM.38+075', 'AFYON A.ÇETİNKAYA', 'ALÖVE', 'FEN LİSESİ DURAĞI', 'BARAKLI', 'BOZKURT', 'BURDUR', 'BÜYÜKÇOBANLAR', 'ÇARDAK', 'ÇAVUŞCUGÖL', 'AKŞEHİR', 'ALAYUNT', 'ALAYUNT MÜSELLES', 'DAZKIRI', 'DEĞİRMENÖZÜ', 'DEĞİRMİSAZ', 'DEMİRLİ', 'DÖĞER', 'DUMLUPINAR', 'DURSUNBEY', 'EKİNOVA', 'EMİRLER', 'GAZELLİDERE', 'GÖKÇEDAĞ', 'GÖKÇEKISIK', 'ÇAY', 'ÇÖĞÜRLER', 'GÜZELYURT', 'GAZLIGÖL', 'ISPARTA', 'ÇİFTLİK', 'İHSANİYE', 'KADINHAN', 'KAKLIK', 'KARAKUYU', 'GÜMÜŞGÜN', 'KÖPRÜÖREN', 'KÜTAHYA', 'ALİKÖY', 'DEMİRÖZÜ', 'MAZLUMLAR', 'MAHMUDİYE', 'MEZİTLER', 'NUSRAT', 'PINARBAŞI', 'KIZILİNLER', 'KİREÇ', 'SARAYÖNÜ', 'SİNDİRLER', 'SULTANDAĞI', 'SÜTLAÇ', 'TAVŞANLI', 'TINAZTEPE', 'ULUKÖY', 'YILDIRIMKEMAL', 'PORSUK', 'SABUNCUPINAR', 'ALPULLU', 'ÇERKEZKÖY', 'ÇORLU', 'İSTANBUL(HALKALI)', 'KABAKÇA', 'KAYABEYLİ', 'KURFALLI', 'EDİRNE', 'BAHÇIVANOVA', 'PEHLİVANKÖY', 'SEYİTLER', 'SİNEKLİ', 'UZUNKÖPRÜ', 'VELİMEŞE', 'MURATLI', 'TAYYAKADIN', 'KAPIKULE', 'ALPU', 'BOLKUŞ', 'BOĞAZKÖPRÜ', 'KEYKUBAT', 'POYRAZ', 'ALAŞEHİR', 'GÜNEYKÖY', 'KİLLİK', 'ÖDEMİŞ GAR', 'SULTANHİSAR', 'YEŞİLKAVAK', 'ALP', 'ÇAKŞUR', 'ÇADIRKAYA', 'TOPULYURDU', 'AKGEDİK', 'DEMİRİZ', 'SICAKSU', 'KM. 345+500', 'ÇİFTEHAN', 'YENİCE', 'DİNAR', 'MEYDAN', 'ÇATALCA', 'ISPARTAKULE', 'YENİ KARASAR', 'İSMAİLBEY', 'ÇAYCUMA', 'SEKİLİ', 'DİYARBAKIR', 'ARGITHAN', 'ILGIN', 'KÖSEKÖY', 'AHMETLİ', 'ÇAMLIK', 'SUBAŞI', 'GENÇ', 'YAZIHAN', 'BALIKÖY', 'EVCİLER', 'KEÇİBORLU', 'LÜLEBURGAZ', 'İLİÇ', 'MUALLİMKÖY HT', 'HEREKE YHT', 'YARIMCA YHT', 'DERİNCE YHT', 'İZMİT YHT', 'KM. 123+400 HT', 'KM. 146+338 HT', 'PAMUKOVA YHT', 'BİLECİK YHT', 'KM. 221+401 HT', 'KM. 222+399 HT', 'BOZÜYÜK YHT', 'AKYAKA', 'ÖDEMİŞ ŞEHİR', 'BAYINDIR', 'DİVRİĞİ', 'ERZİNCAN', 'HORASAN', 'MERCAN', 'ÇATAL', 'SARIOĞLAN', 'TURHAL', 'BALIKESİR', 'SANDIKLI', 'KAYAŞ', 'GÖKÇEBEY', 'TURGUTLU', 'SOMA', 'BALIKESİR (GÖKKÖY)', 'KOÇKALE', 'KM. 215+596 HT', 'KM. 224+482 HT', 'KARDEŞGEDİĞİ', 'DAVUTLAR KÖYÜ', 'YILDIRIM SAYDİNGİ', 'BALASTOCAĞI SAYDİNGİ (KM 347+765)', 'HAVALİMANI DURAĞI', 'PİRİBEYLER', 'KM. 251+485', 'BURMAHAN (KM.801+150)', 'ERYAMAN YHT', 'GÜNDOĞAN', 'ASMAKAYA', 'YAMANLAR', 'SAZLIK', 'SOĞUKSU', 'OYMAPINAR', 'GEBZE (YENİ)', 'ÇAYIROVA SAYDİNG', 'TUZLA SAYDİNG', 'TERSANE SAYDİNG', 'YUNUS SAYDİNG', 'ATALAR SAYDİNG', 'İSTANBUL(BOSTANCI)', 'ERENKÖY SAYDİNG', 'İSTANBUL(SÖĞÜTLÜÇEŞME)', 'AS04 KM.44+471 MAKAS', 'AS03 KM.44+558 MAKAS', 'İSTANBUL(BAKIRKÖY)', 'ZEYTİNBURNU S HAT3', 'YEŞİLKÖY S HAT3', 'ATAKÖY S HAT3', 'BOZKANAT', 'ULUKAYA', 'UYANIK', 'YENİDOĞAN DURAĞI', 'SELÇUKLU YHT (KONYA)', 'DİLİSKELESİ YHT', 'DENİZCİLER', 'YENİKÖŞK', 'KM  0+936/0+000', 'TAŞLICA', 'KM 331+985 ŞEFKAT BAŞ MAKAS', 'KIRIKKALE YHT', 'YOZGAT YHT', 'SORGUN YHT', 'AKDAĞMADENİ YHT', 'OSMANİYE', 'YILDIZELİ YHT', 'YERKÖY YHT', 'ELMADAĞ YHT', 'KIRKİKİEVLER HT', 'TOKAT', 'Kelebek']
        layout = QGridLayout()
        layout.setHorizontalSpacing(15) 
        layout.setVerticalSpacing(10)    
        self.setLayout(layout)

        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)


        self.departure_dropdown = QComboBox()
        self.departure_dropdown.addItems(self.places)
        self.departure_dropdown.setEditable(True)
        self.departure_dropdown.setMaxVisibleItems(10) 
        self.departure_dropdown.setInsertPolicy(QComboBox.NoInsert)
        self.departure_dropdown.completer().setFilterMode(Qt.MatchContains) 
        self.departure_dropdown.completer().setCompletionMode(QCompleter.PopupCompletion)
        departure_layout = self.create_labeled_input("Departure:", self.departure_dropdown)

        self.arrival_dropdown = QComboBox()
        self.arrival_dropdown.addItems(self.places)
        self.arrival_dropdown.setEditable(True)
        self.arrival_dropdown.setMaxVisibleItems(10) 
        self.arrival_dropdown.setInsertPolicy(QComboBox.NoInsert)
        self.arrival_dropdown.completer().setFilterMode(Qt.MatchContains) 
        self.arrival_dropdown.completer().setCompletionMode(QCompleter.PopupCompletion)  
        arrival_layout = self.create_labeled_input("Arrival:", self.arrival_dropdown)

        place_container = QHBoxLayout()
        place_container.setContentsMargins(0, 0, 0, 0) 
        place_container.setSpacing(20) 

        place_container.addLayout(departure_layout)
        place_container.addLayout(arrival_layout)
        place_container.addStretch(3)  
        layout.addLayout(place_container, 0, 0)

        self.date_entry = QDateEdit(calendarPopup=True)
        self.date_entry.setDisplayFormat("dd.MM.yyyy")
        self.date_entry.setDate(QDate.currentDate())
        date_layout = self.create_labeled_input("Date:", self.date_entry)
        date_layout.setSpacing(28)

        self.passengers_entry = QLineEdit()
        self.passengers_entry.setMaxLength(2)
        self.passengers_entry.setText("1")
        self.passengers_entry.setFixedWidth(30)
        passenger_layout = self.create_labeled_input("Passenger:", self.passengers_entry)
        passenger_layout.setStretch(1, 2)
        
        date_passenger_container = QHBoxLayout()
        date_passenger_container.setContentsMargins(0, 0, 0, 0) 
        date_passenger_container.setSpacing(36) 

        date_passenger_container.addLayout(date_layout)
        date_passenger_container.addLayout(passenger_layout)
        layout.addLayout(date_passenger_container, 1, 0)

        layout.addWidget(self.create_line(), 4, 0)

        self.all_time_checkbox = QCheckBox()
        self.all_time_checkbox.stateChanged.connect(self.toggle_time_entries)
        all_time_layout = self.create_labeled_input("If any time works for you, click, if not, choose below", self.all_time_checkbox)
        all_time_layout.setStretch(1, 2)
        layout.addLayout(all_time_layout, 5, 0)

        self.start_time_entry = QTimeEdit()
        self.start_time_entry.setDisplayFormat("HH:mm")
        self.start_time_entry.setTime(QTime.currentTime()) 
        start_time_layout = self.create_labeled_input("Start Time:", self.start_time_entry)


        self.end_time_entry = QTimeEdit()
        self.end_time_entry.setDisplayFormat("HH:mm")
        self.end_time_entry.setTime(QTime.currentTime().addSecs(3600)) 
        end_time_layout = self.create_labeled_input("End Time:", self.end_time_entry)



        time_container = QHBoxLayout()
        time_container.setContentsMargins(0, 0, 0, 0)  
        time_container.setSpacing(20) 

        time_container.addLayout(start_time_layout)
        time_container.addLayout(end_time_layout)
        time_container.addStretch(3) 
        layout.addLayout(time_container, 6, 0)

        
        layout.addWidget(self.create_line(), 7, 0)


        self.preferences_layout = QHBoxLayout()
        self.preferences_label = QLabel('Some options to choose:')
        self.preferences_layout.addWidget(self.preferences_label)
        layout.addLayout(self.preferences_layout, 8,0)

        self.only_yht_checkbox = QCheckBox()
        anahat_layout = self.create_labeled_input("1-Only fast(YHT) trains?", self.only_yht_checkbox)

        self.transfer_checkbox = QCheckBox()
        aktarma_layout = self.create_labeled_input("2-Include transfer(aktarma) trains?", self.transfer_checkbox)

        checkbox_container = QHBoxLayout()
        checkbox_container.setContentsMargins(0, 0, 0, 0)  
        checkbox_container.setSpacing(68) 

        checkbox_container.addLayout(anahat_layout)
        checkbox_container.addLayout(aktarma_layout)
        checkbox_container.addStretch(3)  
        layout.addLayout(checkbox_container, 9, 0)

        self.business_checkbox = QCheckBox()
        business_layout = self.create_labeled_input("3-Include business class seats?", self.business_checkbox)


        self.disabled_checkbox = QCheckBox()
        disabled_layout = self.create_labeled_input("4-Include disabled seats?", self.disabled_checkbox)


        checkbox_container_1 = QHBoxLayout()
        checkbox_container_1.setContentsMargins(0, 0, 0, 0)  
        checkbox_container_1.setSpacing(39)  

        checkbox_container_1.addLayout(business_layout)
        checkbox_container_1.addLayout(disabled_layout)
        checkbox_container_1.addStretch(3)  
        layout.addLayout(checkbox_container_1, 10, 0)


        self.compartment_checkbox = QCheckBox()
        compartment_layout = self.create_labeled_input("5-Include compartment(loca) seats?", self.compartment_checkbox)


        self.sleeper_checkbox = QCheckBox()
        sleeper_layout = self.create_labeled_input("6-Include sleeper(yatakli) seats?", self.sleeper_checkbox)

        checkbox_container_2 = QHBoxLayout()
        checkbox_container_2.setContentsMargins(0, 0, 0, 0)  
        checkbox_container_2.setSpacing(21)  
        checkbox_container_2.addLayout(compartment_layout)
        checkbox_container_2.addLayout(sleeper_layout)
        checkbox_container_2.addStretch(3) 

        layout.addLayout(checkbox_container_2, 11, 0)

        layout.addWidget(self.create_line(), 12, 0)


        self.email_question_layout = QHBoxLayout()
        self.email_question_label = QLabel('Receive email when found? (Optional) (Gmail+App password required)')
        self.email_question_layout.addWidget(self.email_question_label)
        self.info_icon = QLabel("ⓘ", self)
        self.info_icon.setToolTip("Not your Gmail pass, app password needs to be created")
        self.info_icon.setGeometry(0, 0, 20, 20)  
        self.info_icon.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.info_icon.setStyleSheet("""
            QLabel {
                color: gray;
                background-color: transparent;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        self.email_question_layout.addWidget(self.info_icon)
        self.email_question_layout.addStretch(0)

        layout.addLayout(self.email_question_layout, 14,0)


        mail_container = QHBoxLayout()

        self.email_input = QLineEdit()
        self.email_input.setText("ermankalpakci@gmail.com")
        email_layout = self.create_labeled_input("Email:", self.email_input)

        self.password_input = QLineEdit()
        self.password_input.setText("aqjjxqsxklfdpubt")
        password_layout = self.create_labeled_input("App password:", self.password_input)


        mail_container.setContentsMargins(0, 0, 0, 0) 
        mail_container.addLayout(email_layout)
        mail_container.addLayout(password_layout)
        mail_container.addStretch(1) 

        layout.addLayout(mail_container, 15, 0)



        email_test_button_layout = QHBoxLayout()
        self.email_test_button = QPushButton('Send Test Email')
        self.email_test_button.setFixedWidth(100)
        self.email_test_button.clicked.connect(self.email_function)
        email_test_button_layout.addWidget(self.email_test_button, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addLayout(email_test_button_layout, 16, 0)

        layout.addWidget(self.create_line(), 17, 0)

        button_layout = QHBoxLayout()

        self.start_button = QPushButton('Add to the list')
        self.start_button.setFixedWidth(100)
        self.start_button.clicked.connect(self.start_search)
        button_layout.addWidget(self.start_button, alignment=Qt.AlignmentFlag.AlignLeft)


        self.statusBar = QStatusBar()
        button_layout.addWidget(self.statusBar)

        layout.addLayout(button_layout, 18, 0)
        
        users_list_group = QGroupBox("Search List")
        users_list_layout = QVBoxLayout()

        self.scroll_area = QScrollArea()
        self.scroll_content = QWidget()
        self.users_layout = QVBoxLayout()
        self.scroll_content.setLayout(self.users_layout)
        self.scroll_area.setWidget(self.scroll_content)
        self.scroll_area.setWidgetResizable(True)

        users_list_layout.addWidget(self.scroll_area)
        users_list_group.setLayout(users_list_layout)
        layout.addWidget(users_list_group, 19, 0)






        

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
        date = self.date_entry.date().addDays(-1).toString("dd-MM-yyyy")
        passengers = self.passengers_entry.text().strip()
        start_time = self.start_time_entry.time().toString()
        end_time = self.end_time_entry.time().toString()
        all_time = self.all_time_checkbox.isChecked()
        only_yht_checkbox = self.only_yht_checkbox.isChecked()
        transfer_checkbox = self.transfer_checkbox.isChecked()
        business_checkbox = self.business_checkbox.isChecked()
        disabled_checkbox = self.disabled_checkbox.isChecked()
        sleeper_checkbox = self.sleeper_checkbox.isChecked()
        compartment_checkbox = self.compartment_checkbox.isChecked()
        email_input = self.email_input.text().strip()
        password_input = self.password_input.text().strip()

        if int(passengers) >= 12:
            QMessageBox.critical(self, "Error", "Passengers cannot be more than 11")
            self.start_button_enabled(True)
            return

        if departure not in self.places or arrival not in self.places:
            QMessageBox.critical(self, "Error", "Choose from the list.")
            self.start_button_enabled(True)
            return

        if not passengers.isdigit():
            QMessageBox.critical(self, "Error", "Passengers must be numeric.")
            self.start_button_enabled(True)
            return

        if not all_time and start_time >= end_time:
            QMessageBox.critical(self, "Error", "Start time must be before end time.")
            self.start_button_enabled(True)
            return
        
        if departure == arrival:
            QMessageBox.critical(self, "Error", "Departure and arrival cannot be the same.")
            self.start_button_enabled(True)
            return
        
        if not re.match(r'^[a-zA-Z0-9._%+-]+@gmail\.com$', self.email_input.text()):
            QMessageBox.critical(self, "Error", "Check your email")
            self.start_button_enabled(True)
            return

        selected_date = self.date_entry.date()
        today = QDate.currentDate()

        if selected_date < today:
            QMessageBox.critical(self, "Error", "Selected date must be today or earlier.")
            self.start_button_enabled(True)  # Adjust button state if needed
            return

        
        self.search_active = True
        self.start_button.setEnabled(False)
        QApplication.processEvents()

        if not (email_input and password_input):
            email_input = password_input = None

        self.stored_search_params = {
            'departure' : departure,
            "arrival" : arrival,
            "date" : date,
            "passengers" : passengers,
            "start_time" : start_time,
            "end_time" :end_time,
            "all_time" : all_time,
            "only_yht_checkbox" : only_yht_checkbox,
            "transfer_checkbox" : transfer_checkbox,
            "business_checkbox" : business_checkbox,
            "disabled_checkbox" : disabled_checkbox,
            "sleeper_checkbox" : sleeper_checkbox,
            "compartment_checkbox" : compartment_checkbox,
            "email_input" : email_input,
            "password_input" : password_input
            }


        if not self.auth_header:
            self.statusBar.showMessage("Authenticating...")
            self.selenium_worker = SeleniumWorker()
            self.selenium_worker.auth_header_signal.connect(self._handle_auth_result)
            # self.selenium_worker.finished.connect(self._on_selenium_finished)
            self.selenium_worker.start()
            # self.selenium_worker.wait_for_result()
            return
        
        self.statusBar.showMessage("Authentication: success")
        self._proceed_with_search()





    def _proceed_with_search(self):
        params = self.stored_search_params
        self.statusBar.showMessage("Authentication: success")

        options = [params["only_yht_checkbox"], params['transfer_checkbox'], params['business_checkbox'],
                   params["disabled_checkbox"], params['compartment_checkbox'], params["sleeper_checkbox"]]
        
        train_search = TrainSearch(
            params['departure'],
            params['arrival'],
            params['date'],
            int(params['passengers']),
            params['all_time'],
            params['start_time'],
            params['end_time'],
            options,
            params['email_input'],
            params['password_input']
        )

        user_widget = UserWidget(train_search)
        self.search_widget_map[train_search] = user_widget
        self.users_layout.addWidget(user_widget)

        config = DBConfig()
        db = TrainDatabase(config)

        departure_name = train_search.departure
        arrival_name = train_search.arrival

        train_search.departure_id = db.get_id_given_name(departure_name)
        train_search.arrival_id = db.get_id_given_name(arrival_name)

        if not self.observer:
            self.observer = TrainSearchObserver(self.auth_header)
        self.observer.add_search(train_search)
        user_widget.remove_requested.connect(self._remove_search)
        user_widget.run_requested.connect(self._handle_run_request)
        self.start_button.setEnabled(True)

    def _handle_auth_result(self, success, header):
        self.search_active = False
        self.start_button.setEnabled(True)

        if success:
            self.auth_header = header
            self.observer = TrainSearchObserver(auth_header=header)
            if not self.observer.receivers(self.observer.search_started):
                # self.observer.search_started.connect(self._handle_search_start)
                self.observer.search_completed.connect(self._handle_search_completion)
                self.observer.error_occurred.connect(self._handle_error)
                self.observer.search_last_tried.connect(self._handle_last_tried)
            self._proceed_with_search()
        else:
            QMessageBox.critical(self, "Error", header)
            self.statusBar.showMessage("Authentication: fail")

            self.start_button.setEnabled(True)
            self.auth_header = None
            self.selenium_worker = None

    def _handle_run_request(self, search):
        self.observer.add_search(search)

    # @pyqtSlot(object)
    # def _handle_search_start(self, search):
    #     self.statusBar.showMessage(
    #         f"Started search: {search.departure}→{search.arrival}", 3000
    #     )

    @pyqtSlot(object, object)
    def _handle_search_completion(self, search, result):
        widget = self.search_widget_map.get(search)
        if widget:
            widget.update_result(result)
            if result.success:
                widget.pause_btn.hide()
                widget.run_btn.hide()
                widget.show_results_btn.show()
                QMessageBox.information(self, "Success!", "Train(s) found, click show results")

    @pyqtSlot(object, str)
    def _handle_last_tried(self, search, message):
        widget = self.search_widget_map.get(search)
        if widget:
            widget.set_last_tried(message)

    def _remove_search(self, search):
        if search in self.search_widget_map:
            widget = self.search_widget_map.pop(search)
            search.paused = False
            if search in self.observer.searches:
                self.observer.searches.remove(search)
            widget.deleteLater()

    @pyqtSlot(object, object)
    def _handle_error(self, search, result):
        widget = self.search_widget_map.get(search)
        if widget:
            widget.update_result(result)
            if not result.success:
                widget.pause_btn.hide()
                widget.run_btn.hide()
                widget.show_results_btn.show()
        QMessageBox.critical(self, "Error", result.message)

    def closeEvent(self, event):
        if self.observer:
            self.observer.shutdown()
        super().closeEvent(event)


    @pyqtSlot()
    def _on_selenium_finished(self):
        if self.selenium_worker:
            self.selenium_worker.deleteLater()
            # self.selenium_worker = None

    def start_button_enabled(self,status):
        if status:
            self.start_button.setEnabled(True)
        else:
            self.start_button.setEnabled(False)



class UserWidget(QGroupBox):

    clicked = pyqtSignal(object)
    remove_requested = pyqtSignal(object)
    run_requested = pyqtSignal(object)

    def __init__(self, search: TrainSearch):
        super().__init__()
        self.search = search
        self.init_ui()
        search.status_changed.connect(self._update_status)

    def init_ui(self):
        layout = QHBoxLayout()

        true_positions = [str(i+1) for i, val in enumerate(self.search.options) if val]
        if not true_positions:
            joined_true_positions = "No options chosen"
        else:
            joined_true_positions = ", ".join(true_positions)
        
        if self.search.time_flag:
            time_label = "No time interval chosen"
        else:
            time_label = f"Start time: {self.search.start_time[:-3]} End time: {self.search.end_time[:-3]}"

        if self.search.email and self.search.password:
            email_and_password = "email and password set"
        else:
            email_and_password = "email and password not set"

        self.route_label = QLabel(
            f"{self.search.departure} → {self.search.arrival}\nDate: {(self.search.date + timedelta(days=1)).strftime("%d-%m-%Y")}\nOptions: {joined_true_positions}\n{time_label}\n{email_and_password}"
        )

        self.status_label = QLabel("Running")
        self.last_tried_label = QLabel("Last tried: None")

        self.pause_btn = QPushButton("Pause")
        self.run_btn = QPushButton("Run")
        self.show_results_btn = QPushButton("Show Results")
        self.remove_btn = QPushButton("Remove")

        self.run_btn.hide()
        self.show_results_btn.hide()

        self.pause_btn.clicked.connect(self.pause_user)
        self.run_btn.clicked.connect(self.run_user)
        self.show_results_btn.clicked.connect(self.show_results)
        self.remove_btn.clicked.connect(self.request_removal)

        layout.addWidget(self.route_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.last_tried_label)
        layout.addWidget(self.pause_btn)
        layout.addWidget(self.run_btn)
        layout.addWidget(self.show_results_btn)
        layout.addWidget(self.remove_btn)
        
        self.setLayout(layout)

    def mousePressEvent(self, event):
        self.clicked.emit(self.search)
        super().mousePressEvent(event)

    def pause_user(self):
        self.search.paused = True
        # self.status_label.setText("Paused")

        self.pause_btn.hide()
        self.run_btn.show()
        self.show_results_btn.hide()

    def request_removal(self):
        self.remove_requested.emit(self.search)

    def run_user(self):
        self.search.paused = False
        # self.status_label.setText("Running")
        self.pause_btn.show()
        self.run_btn.hide()
        self.show_results_btn.hide()
        self.run_requested.emit(self.search)

    def set_last_tried(self, text):
        self.last_tried_label.setText('Last tried: ' + text)

    @pyqtSlot(str)
    def _update_status(self, status):
        self.status_label.setText(status.capitalize())

    def update_result(self, result: SearchResult):
        color = "#e6ffe6" if result.success else "#ffe6e6"
        self.setStyleSheet(f"""
            background-color: {color}
        """)
    def show_results(self):
        QMessageBox.information(self, "Search Results", self.search.result.message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TrainAlertApp()
    ex.show()
    sys.exit(app.exec_())