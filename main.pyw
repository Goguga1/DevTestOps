from PyQt5 import QtWidgets, QtCore, QtGui
import sys, datetime, math
from MainWindowWide import Ui_MainWindow
from AuthWindow import Ui_AuthWindow
from AuthorizationWindow import Ui_AuthorizationWindow
from AckWindow import Ui_AckWindow
from data import People, ListOfExaminations, Settings, Database, Templates, ExaminationTemplates
from ChangePasswdWindow import Ui_ChangePassword
from TemplatesWindow import Ui_TemplatesWindow
import zipfile, os
from random import randint
from lxml import etree
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter, QPrintPreviewDialog
#from fitz import open as fitz_open
from printing import convert_docx_to_pdf
#from docx import Document
#from docx.shared import Pt


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        def prepare_widgets():
            self.search_for_patient_table.horizontalHeader().resizeSection(0, int(self.search_for_patient_table.viewport().width()*0.1))
            self.search_for_patient_table.horizontalHeader().resizeSection(1, int(self.search_for_patient_table.viewport().width()*0.47))
            self.search_for_patient_table.horizontalHeader().resizeSection(2, int(self.search_for_patient_table.viewport().width()*0.14))
            self.search_for_patient_table.horizontalHeader().resizeSection(3, int(self.search_for_patient_table.viewport().width()*0.12))
            self.search_for_patient_table.horizontalHeader().resizeSection(4, int(self.search_for_patient_table.viewport().width()*0.17))
            self.search_for_patient_table.setFocusPolicy(QtCore.Qt.NoFocus)
            self.search_for_patient_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            self.search_for_patient_table.customContextMenuRequested.connect(self.show_search_for_patient_table_context_menu)
            self.exam_personal_data_birthdate_date_edit.setMaximumDate(datetime.datetime.now().date())
            self.change_data_birthdate_date_edit.setMaximumDate(datetime.datetime.now().date())
            self.change_person_birthdate_date_edit.setMaximumDate(datetime.datetime.now().date())
            self.exam_personal_data_new_patient_checkbox.setVisible(False)
            self.remove_all_values_from_change_data()

        def last_position(event):
            self.last_position_x = event.x()
            self.last_position_y = event.y()
        
        self.__db = Database()
        use_password = self.__db.execute("SELECT Use_password FROM Settings").fetchone()[0]

        if use_password:
            auth = AuthWindow(self.__db)
            auth.exec_()
            if auth.forbidden:
                sys.exit()

        super().__init__()
        self.setupUi(self)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowIcon(QtGui.QIcon("img/icon.ico"))
        self.__people = People(self.__db)
        self.__examinations = ListOfExaminations(self.__db)
        self.__settings = Settings(self.__db)
        self.__templates = Templates(self.__db)
        self.__exam_templates = ExaminationTemplates(self.__db)
        self.default_data = {'birthdate': [15, 6, 2016]}

        qcompleter_css = """
            QListView {
                border: 1px solid #ccc;
                font-size: 11pt;
                font-family: "Comfortaa";
                border-radius: 8px;
                background: #ccc;
            }
            QListView::item {
                min-height: 0px;
                white-space: normal;
            }

            QScrollBar:vertical {
                background: rgba(0,0,0,0);
                width: 10px;
                margin: 0px;
                border-radius: 3px;
            }

            QScrollBar::handle:vertical {
                background-color: #444;
                min-height: 20px;
                border-radius: 3px;
                margin: 2px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: #222;
            }


            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
            }
            """
        
        self.exam_personal_data_completer = QtWidgets.QCompleter()
        self.exam_personal_data_completer.popup().setStyleSheet(qcompleter_css)
        self.exam_personal_data_completer.setCompletionMode(QtWidgets.QCompleter.CompletionMode.PopupCompletion)

        self.change_data_search_for_name_completer = QtWidgets.QCompleter()
        self.change_data_search_for_name_completer.popup().setStyleSheet(qcompleter_css)
        self.change_data_search_for_name_completer.setCompletionMode(QtWidgets.QCompleter.CompletionMode.PopupCompletion)
        
        self.search_for_patient_completer = QtWidgets.QCompleter()
        self.search_for_patient_completer.popup().setStyleSheet(qcompleter_css)
        self.search_for_patient_completer.setCompletionMode(QtWidgets.QCompleter.CompletionMode.PopupCompletion)
        
        self.change_person_search_for_name_completer = QtWidgets.QCompleter()
        self.change_person_search_for_name_completer.popup().setStyleSheet(qcompleter_css)
        self.change_person_search_for_name_completer.setCompletionMode(QtWidgets.QCompleter.CompletionMode.PopupCompletion)

        self.print_search_for_name_completer = QtWidgets.QCompleter()
        self.print_search_for_name_completer.popup().setStyleSheet(qcompleter_css)
        self.print_search_for_name_completer.setCompletionMode(QtWidgets.QCompleter.CompletionMode.PopupCompletion)

        self.schiascopy_combobox_indexes = {"Hm": 0, "M": 1, "Em": 2}
 
        self.exam_objective_values = {
                                        'od': {
                                            'od_eye_position': "", 'od_oi': "", 'od_eyelid': "", 'od_lacrimal_organs': "",
                                            'od_conjunctiva': "", 'od_discharge': "", 'od_iris': "",
                                            'od_anterior_chamber': "", 'od_refractive_medium': "", 'od_optic_disk': "",
                                            'od_vessels': "", 'od_macular_reflex': "", 'od_visible_periphery': "",
                                            'od_diagnosis': "", 'od_icd_code': ""
                                        },
                                        'os': {
                                            'os_eye_position': "", 'os_oi': "", 'os_eyelid': "", 'os_lacrimal_organs': "",
                                            'os_conjunctiva': "", 'os_discharge': "", 'os_iris': "",
                                            'os_anterior_chamber': "", 'os_refractive_medium': "", 'os_optic_disk': "",
                                            'os_vessels': "", 'os_macular_reflex': "", 'os_visible_periphery': "",
                                            'os_diagnosis': "", 'os_icd_code': ""
                                        }
                                    }
        self.change_data_objective_values = {
                                            'od': {
                                                'od_eye_position': "", 'od_oi': "", 'od_eyelid': "", 'od_lacrimal_organs': "",
                                                'od_conjunctiva': "", 'od_discharge': "", 'od_iris': "",
                                                'od_anterior_chamber': "", 'od_refractive_medium': "", 'od_optic_disk': "",
                                                'od_vessels': "", 'od_macular_reflex': "", 'od_visible_periphery': "",
                                                'od_diagnosis': "", 'od_icd_code': ""
                                            },
                                            'os': {
                                                'os_eye_position': "", 'os_oi': "", 'os_eyelid': "", 'os_lacrimal_organs': "",
                                                'os_conjunctiva': "", 'os_discharge': "", 'os_iris': "",
                                                'os_anterior_chamber': "", 'os_refractive_medium': "", 'os_optic_disk': "",
                                                'os_vessels': "", 'os_macular_reflex': "", 'os_visible_periphery': "",
                                                'os_diagnosis': "", 'os_icd_code': ""
                                            }
                                        }
        self.print_objective_values = {
                                        'od': {
                                            'od_eye_position': "", 'od_oi': "", 'od_eyelid': "", 'od_lacrimal_organs': "",
                                            'od_conjunctiva': "", 'od_discharge': "", 'od_iris': "",
                                            'od_anterior_chamber': "", 'od_refractive_medium': "", 'od_optic_disk': "",
                                            'od_vessels': "", 'od_macular_reflex': "", 'od_visible_periphery': "",
                                            'od_diagnosis': "", 'od_icd_code': ""
                                        },
                                        'os': {
                                            'os_eye_position': "", 'os_oi': "", 'os_eyelid': "", 'os_lacrimal_organs': "",
                                            'os_conjunctiva': "", 'os_discharge': "", 'os_iris': "",
                                            'os_anterior_chamber': "", 'os_refractive_medium': "", 'os_optic_disk': "",
                                            'os_vessels': "", 'os_macular_reflex': "", 'os_visible_periphery': "",
                                            'os_diagnosis': "", 'os_icd_code': ""
                                        }
                                    }

        self.ive_asked_not_to_click_messages = {"Ну просили же не кликать": "Простите", "Зачем": "Просто", "Вот зачем это делать, чтобы что?": "Не знаю", "Больше чтобы такого не было": "Так точно",
                                                "Молодец, и чего добились?": "Простите", "За что...": "Да так", "По-человечески же попросили...": "Простите", "Поигрались? Теперь хватит": "Не-а",
                                                "Ещё один раз, и система будет удалена": "Боюсь-боюсь", "Читать разучились?": "Что здесь написано", "Не видно что написано было??? Проверьте зрение!!!": "И идти далеко не надо",
                                                "Достижение... нажали туда, куда не просили...": "Простите...", "Я что, шутка?!": "Как будто бы да", "И? В чём смысл тогда?": "Действительно", "Вот каждому надо же потыкать...": "Конечно"}

        prepare_widgets()

        self.label_window_dragging.mousePressEvent = lambda event: last_position(event)
        self.label_window_dragging.mouseMoveEvent = lambda event: self.move(self.x()+event.x()-self.last_position_x, self.y()+event.y()-self.last_position_y)
        self.label_line_of_dragging.mousePressEvent = lambda event: last_position(event)
        self.label_line_of_dragging.mouseMoveEvent = lambda event: self.move(self.x()+event.x()-self.last_position_x, self.y()+event.y()-self.last_position_y)

        self.launch_close_animation = QtCore.QPropertyAnimation(self, b'windowOpacity', duration=100)

        self.right_panel_examination_of_patient.mouseReleaseEvent = lambda event: self.distribute_right_panel_buttons("examination_of_patient")
        self.right_panel_data_changing.mouseReleaseEvent = lambda event: self.distribute_right_panel_buttons("changing_data")
        self.right_panel_person_changing.mouseReleaseEvent = lambda event: self.distribute_right_panel_buttons("changing_person")
        self.right_panel_search_for_patient.mouseReleaseEvent = lambda event: self.distribute_right_panel_buttons("search_for_patient")
        self.right_panel_print.mouseReleaseEvent = lambda event:self.distribute_right_panel_buttons("print")
        self.right_panel_settings.mouseReleaseEvent = lambda event: self.distribute_right_panel_buttons("settings")
        self.right_panel_quit.mouseReleaseEvent = lambda event: self.distribute_right_panel_buttons("quit")
        self.right_panel_quit.mouseReleaseEvent = lambda event: self.distribute_right_panel_buttons("quit")
        self.label_window_minimize.mouseReleaseEvent = lambda event: self.distribute_right_panel_buttons("minimize")

        self.exam_personal_data_id_combobox.currentIndexChanged.connect(lambda: self.set_exam_personal_data_by_id(self.exam_personal_data_id_combobox.currentText()))
        self.change_data_id_combobox.currentIndexChanged.connect(lambda: self.set_change_data_personal_data_by_id(self.change_data_id_combobox.currentText()))
        self.change_data_date_of_examination_combobox.currentIndexChanged.connect(lambda: self.set_change_data_examination_data(self.change_data_date_of_examination_combobox.currentText()))
        self.change_person_id_combobox.currentIndexChanged.connect(lambda: self.set_change_person_by_id(self.change_person_id_combobox.currentText()))

        self.right_panel_blue_normal_css = """
                                            QFrame {
                                                border-top-right-radius: 0px;
                                                border-bottom-right-radius: 0px;
                                                background: rgba(200,200,200,75);
                                                border-top: 1px solid rgba(255,255,255,80);
                                                }

                                                QFrame:hover {
                                                background: rgba(182, 240, 219, 90);
                                                border-left: 0px;
                                                }
                                            """
        self.right_panel_blue_normal_css_with_border_radius = """
                                            QFrame {
                                                border-top-right-radius: 10px;
                                                border-bottom-right-radius: 0px;
                                                background: rgba(200,200,200,75);
                                                border-top: 1px solid rgba(255,255,255,80);
                                                }

                                                QFrame:hover {
                                                background: rgba(182, 240, 219, 90);
                                                border-left: 0px;
                                                }
                                            """
        self.right_panel_red_normal_css = """
                                            QFrame {
                                                border-top-right-radius: 0px;
                                                border-bottom-right-radius: 0px;
                                                background: rgba(200,200,200,75);
                                                border-top: 1px solid rgba(255,255,255,80);
                                                }

                                                QFrame:hover {
                                                background: rgba(246, 176, 219, 90);
                                                border-left: 0px;
                                                }
                                            """

        self.exam_personal_data_new_patient_checkbox.stateChanged.connect(lambda: self.set_exam_default_personal_data(True))

        self.set_current_settings()

        self.programm_window_settings_on_top_of_all_checkbox.stateChanged.connect(lambda: self.change_settings("on_top"))
        self.programm_window_settings_remember_last_position.stateChanged.connect(lambda: self.change_settings("remember_last_position"))
        self.programm_window_settings_run_with_system_checkbox.mouseReleaseEvent = lambda event: self.change_settings("run_with_system")
        self.security_settings_use_password_checkbox.mouseReleaseEvent = lambda event: self.change_settings("use_password")
        self.programm_acknowledge_settings_examination_ack_save_data_checkbox.stateChanged.connect(lambda: self.change_settings("ack_save_examination"))
        self.programm_acknowledge_settings_examination_ack_erase_data_checkbox.stateChanged.connect(lambda: self.change_settings("ack_erase_examination"))
        self.programm_acknowledge_settings_change_data_ack_save_data_checkbox.stateChanged.connect(lambda: self.change_settings("ack_save_change_data"))
        self.programm_acknowledge_settings_change_data_ack_delete_data_checkbox.stateChanged.connect(lambda: self.change_settings("ack_delete_change_data"))
        self.programm_acknowledge_settings_change_person_ack_save_data_checkbox.stateChanged.connect(lambda: self.change_settings("ack_save_person"))
        self.programm_acknowledge_settings_change_person_ack_delete_data_checkbox.stateChanged.connect(lambda: self.change_settings("ack_delete_person"))
        self.programm_acknowledge_settings_objective_synchronize_eyes_checkbox.stateChanged.connect(lambda: self.change_settings("objective_synchronize_eyes"))


        self.exam_personal_data_name_line_edit.textChanged.connect(lambda: self.set_exam_personal_data_by_name(self.exam_personal_data_name_line_edit.text()))
        self.exam_personal_data_name_line_edit.setCompleter(self.exam_personal_data_completer)
        self.exam_personal_data_last_examinations_date_combobox.currentIndexChanged.connect(self.set_exam_examination_data)
        self.exam_save_button.clicked.connect(self.save_examination)
        self.exam_erase_button.clicked.connect(self.erase_examination)
        self.exam_recommendations_reappointment_checkbox.toggled.connect(lambda: (self.exam_recommendations_reappointment_time_line_edit.clear(), self.exam_recommendations_reappointment_time_line_edit.setEnabled(self.exam_recommendations_reappointment_checkbox.isChecked()), self.exam_recommendations_reappointment_time_templates_button.setEnabled(self.exam_recommendations_reappointment_checkbox.isChecked())))
        self.exam_objective_eye_combobox.currentTextChanged.connect(lambda: self.change_eye_objective("Exam"))
        self.exam_objective_transfer_from_OD_button.clicked.connect(lambda: self.transfer_objective_data_from_OD("Exam"))
        self.exam_reset_exam_data_button.clicked.connect(self.reset_exam_data)
        self.exam_misc_examination_templates_OD_combobox.currentIndexChanged.connect(lambda: self.set_exam_examination_data([self.exam_misc_examination_templates_OD_combobox.currentText(), 0]))
        self.exam_misc_examination_templates_OS_combobox.currentIndexChanged.connect(lambda: self.set_exam_examination_data([self.exam_misc_examination_templates_OS_combobox.currentText(), 1]))

        self.exam_eyesight_visual_acuity_with_OD_sph_box.valueChanged.connect(lambda: self.exam_glasses_OD_sph_box.setValue(self.exam_eyesight_visual_acuity_with_OD_sph_box.value()))
        self.exam_eyesight_visual_acuity_with_OD_cyl_box.valueChanged.connect(lambda: self.exam_glasses_OD_cyl_box.setValue(self.exam_eyesight_visual_acuity_with_OD_cyl_box.value()))
        self.exam_eyesight_visual_acuity_with_OD_ax_box.valueChanged.connect(lambda: self.exam_glasses_OD_ax_box.setValue(self.exam_eyesight_visual_acuity_with_OD_ax_box.value()))
        self.exam_eyesight_visual_acuity_with_OS_sph_box.valueChanged.connect(lambda: self.exam_glasses_OS_sph_box.setValue(self.exam_eyesight_visual_acuity_with_OS_sph_box.value()))
        self.exam_eyesight_visual_acuity_with_OS_cyl_box.valueChanged.connect(lambda: self.exam_glasses_OS_cyl_box.setValue(self.exam_eyesight_visual_acuity_with_OS_cyl_box.value()))
        self.exam_eyesight_visual_acuity_with_OS_ax_box.valueChanged.connect(lambda: self.exam_glasses_OS_ax_box.setValue(self.exam_eyesight_visual_acuity_with_OS_ax_box.value()))

        self.current_exam_OD_template = ''
        self.current_exam_OS_template = ''

        self.change_data_search_for_name_of_patient_line_edit.textChanged.connect(lambda: self.set_change_data_personal_data_by_name(self.change_data_search_for_name_of_patient_line_edit.text()))
        self.change_data_search_for_name_of_patient_line_edit.setCompleter(self.change_data_search_for_name_completer)
        self.change_data_search_for_name_of_patient_line_edit.setFocus(True)
        self.change_data_save_button.clicked.connect(lambda: self.update_examination(None, None))
        self.change_data_delete_button.clicked.connect(lambda: self.delete_examination(self.change_data_id_combobox.currentText(), self.change_data_diagnosis_date_label.text()))
        self.change_data_objective_eye_combobox.currentTextChanged.connect(lambda: self.change_eye_objective("Change data"))
        self.change_data_objective_transfer_from_OD_button.clicked.connect(lambda: self.transfer_objective_data_from_OD("Change data"))

        self.change_data_eyesight_visual_acuity_with_OD_sph_box.valueChanged.connect(lambda: self.change_data_glasses_OD_sph_box.setValue(self.change_data_eyesight_visual_acuity_with_OD_sph_box.value()))
        self.change_data_eyesight_visual_acuity_with_OD_cyl_box.valueChanged.connect(lambda: self.change_data_glasses_OD_cyl_box.setValue(self.change_data_eyesight_visual_acuity_with_OD_cyl_box.value()))
        self.change_data_eyesight_visual_acuity_with_OD_ax_box.valueChanged.connect(lambda: self.change_data_glasses_OD_ax_box.setValue(self.change_data_eyesight_visual_acuity_with_OD_ax_box.value()))
        self.change_data_eyesight_visual_acuity_with_OS_sph_box.valueChanged.connect(lambda: self.change_data_glasses_OS_sph_box.setValue(self.change_data_eyesight_visual_acuity_with_OS_sph_box.value()))
        self.change_data_eyesight_visual_acuity_with_OS_cyl_box.valueChanged.connect(lambda: self.change_data_glasses_OS_cyl_box.setValue(self.change_data_eyesight_visual_acuity_with_OS_cyl_box.value()))
        self.change_data_eyesight_visual_acuity_with_OS_ax_box.valueChanged.connect(lambda: self.change_data_glasses_OS_ax_box.setValue(self.change_data_eyesight_visual_acuity_with_OS_ax_box.value()))
        
        
        self.change_person_search_for_name_of_patient_line_edit.textChanged.connect(lambda: self.set_change_person_data_by_name(self.change_person_search_for_name_of_patient_line_edit.text()))
        self.change_person_search_for_name_of_patient_line_edit.setCompleter(self.change_person_search_for_name_completer)
        self.change_data_recommendations_reappointment_checkbox.toggled.connect(lambda: (self.change_data_recommendations_reappointment_time_line_edit.clear(), self.change_data_recommendations_reappointment_time_line_edit.setEnabled(self.change_data_recommendations_reappointment_checkbox.isChecked()), self.change_data_recommendations_reappointment_time_templates_button.setEnabled(self.change_data_recommendations_reappointment_checkbox.isChecked())))
        self.change_person_save_button.clicked.connect(lambda: self.update_person(self.change_person_set_id_label.text()))
        self.change_person_delete_button.clicked.connect(lambda: self.delete_person(self.change_person_set_id_label.text()))

        self.security_sttings_change_password_button.clicked.connect(self.__change_password)

        self.search_for_patient_name_line_edit.textChanged.connect(lambda: self.fill_search_table(name=self.search_for_patient_name_line_edit.text()))
        self.search_for_patient_name_line_edit.setCompleter(self.search_for_patient_completer)
        self.search_for_patient_id_combobox.currentIndexChanged.connect(lambda: self.fill_search_table(id=int(self.search_for_patient_id_combobox.currentText())))
        self.search_settings_number_of_visible_records_box.textChanged.connect(lambda: self.__settings.update_number_of_visible_records(int(self.search_settings_number_of_visible_records_box.text())))

        self.print_objective_eye_combobox.currentTextChanged.connect(lambda: self.change_eye_objective("Print"))
        self.print_search_for_name_of_patient_line_edit.setCompleter(self.print_search_for_name_completer)
        self.print_id_combobox.currentIndexChanged.connect(lambda: self.set_print_personal_data_by_id(self.print_id_combobox.currentText()))
        self.print_search_for_name_of_patient_line_edit.textChanged.connect(lambda: self.set_print_personal_data_by_name(self.print_search_for_name_of_patient_line_edit.text()))
        self.print_date_of_examination_combobox.currentIndexChanged.connect(lambda: self.set_print_examination_data(self.print_date_of_examination_combobox.currentText()))
        self.print_button.clicked.connect(self.print_examination)
        self.preview_button.clicked.connect(lambda: self.print_examination(preview=True))
        self.open_in_word_button.clicked.connect(lambda: self.print_document(show_in_word=True))

        self.exam_diagnosis_date_label_qtimer = QtCore.QTimer(self)
        self.exam_diagnosis_date_label_qtimer.timeout.connect(self.set_current_time_on_exam_date_label)
        self.exam_diagnosis_date_label_qtimer.start(1000)
        self.exam_diagnosis_date_label.setText(datetime.datetime.strftime(datetime.datetime.now(), "%d.%m.%Y %H:%M"))

        self.exam_diagnosis_subscription_text_edit.clear()
        self.print_diagnosis_subscription_text_edit.clear()
        self.exam_common_complaints_line_edit.clear()

        [child.installEventFilter(self) for child in self.findChildren(QtWidgets.QDoubleSpinBox)]

        self.fill_search_table(all=True)

        self.distribute_right_panel_buttons("examination_of_patient")
        
        self.set_objective_line_edits()
        self.set_templates_buttons()

        self.launch_animated()


    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Wheel and isinstance(obj, QtWidgets.QDoubleSpinBox):
            if event.modifiers() == QtCore.Qt.AltModifier:
                step = 0.01
                delta = event.angleDelta().x() / 120
                obj.setValue(obj.value() + step * delta)
                return True
        return False


    def backup_database(self):
        self.__db.do_backup_of_database()

    def set_current_settings(self):
        self.programm_window_settings_on_top_of_all_checkbox.setChecked(self.__settings.on_top)
        self.programm_window_settings_remember_last_position.setChecked(self.__settings.remember_last_position)
        self.programm_window_settings_run_with_system_checkbox.setChecked(self.__settings.run_with_system)
        self.security_settings_use_password_checkbox.setChecked(self.__settings.use_password)
        self.programm_acknowledge_settings_examination_ack_save_data_checkbox.setChecked(self.__settings.ack_save_examination)
        self.programm_acknowledge_settings_examination_ack_erase_data_checkbox.setChecked(self.__settings.ack_erase_examination)
        self.programm_acknowledge_settings_change_data_ack_save_data_checkbox.setChecked(self.__settings.ack_save_change_data)
        self.programm_acknowledge_settings_change_data_ack_delete_data_checkbox.setChecked(self.__settings.ack_delete_change_data)
        self.programm_acknowledge_settings_change_person_ack_save_data_checkbox.setChecked(self.__settings.ack_save_person)
        self.programm_acknowledge_settings_change_person_ack_delete_data_checkbox.setChecked(self.__settings.ack_delete_person)
        self.programm_acknowledge_settings_objective_synchronize_eyes_checkbox.setChecked(self.__settings.objective_synchronize_eyes)
        self.search_settings_number_of_visible_records_box.setValue(self.__settings.number_of_visible_records)

        if self.__settings.on_top:
            self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        if self.__settings.remember_last_position:
            self.move(int(self.__settings.last_position.split(',')[0]), int(self.__settings.last_position.split(',')[1]))


    def change_settings(self, checkbox):
        if checkbox == "on_top":
            state_checked = self.programm_window_settings_on_top_of_all_checkbox.isChecked()
            if state_checked:
                self.show_message_window("Crystal", "Настройка применится при следующем запуске приложения")
            else:
                self.show_message_window("Crystal", "Настройка применится при следующем запуске приложения")
            self.__settings.update_on_top(state_checked)
        elif checkbox == "remember_last_position":
            state_checked = self.programm_window_settings_remember_last_position.isChecked()
            self.__settings.update_remember_last_position(state_checked)
        elif checkbox == "run_with_system":
            state_checked = self.programm_window_settings_run_with_system_checkbox.isChecked()
            self.programm_window_settings_run_with_system_checkbox.setChecked(not(state_checked))
            self.show_acknowledge_window("Settings", None)
        #   Крайне важный код, который не рекомендуется стирать и удалять вообще в принципе, потому что это очень-очень важно, я когда-нибудь его добью, но не сейчас
        #elif checkbox == "run_with_system":
        #    state_checked = self.programm_window_settings_run_with_system_checkbox.isChecked()
        #    if not(state_checked):
        #        try:
        #            add_to_autorun()
        #        except:
        #            self.show_message_window("Ошибка", "Возможно, для этой настройки требуется запустить приложение с правами администратора")
        #            return
        #    else:
        #        try:
        #            delete_from_autorun()
        #        except:
        #            self.show_message_window("Ошибка", "Возможно, для этой настройки требуется запустить приложение с правами администратора")    
        #            return
        #    self.programm_window_settings_run_with_system_checkbox.setChecked(not(state_checked))
        #    self.__settings.update_run_with_system(state_checked)
        elif checkbox == "use_password":
            state_checked = self.security_settings_use_password_checkbox.isChecked()
            if state_checked:
                authorization = AuthorizationWindow(self, self.__db)
                authorization.exec_()
                if authorization.exit_pressed:
                    return
                if authorization.forbidden:
                    self.show_message_window("Запрещено", "Неверный пароль")
                    return
            self.security_settings_use_password_checkbox.setChecked(not(state_checked))
            self.__settings.update_use_password(not(state_checked))
        elif checkbox == "ack_save_examination":
            state_checked = self.programm_acknowledge_settings_examination_ack_save_data_checkbox.isChecked()
            self.__settings.update_ack_save_examination(state_checked)
        elif checkbox == "ack_erase_examination":
            state_checked = self.programm_acknowledge_settings_examination_ack_erase_data_checkbox.isChecked()
            self.__settings.update_ack_erase_examination(state_checked)
        elif checkbox == "ack_save_change_data":
            state_checked = self.programm_acknowledge_settings_change_data_ack_save_data_checkbox.isChecked()
            self.__settings.update_ack_save_change_data(state_checked)
        elif checkbox == "ack_delete_change_data":
            state_checked = self.programm_acknowledge_settings_change_data_ack_delete_data_checkbox.isChecked()
            self.__settings.update_ack_delete_change_data(state_checked)
        elif checkbox == "ack_save_person":
            state_checked = self.programm_acknowledge_settings_change_person_ack_save_data_checkbox.isChecked()
            self.__settings.update_ack_save_person(state_checked)
        elif checkbox == "ack_delete_person":
            state_checked = self.programm_acknowledge_settings_change_person_ack_delete_data_checkbox.isChecked()
            self.__settings.update_ack_delete_person(state_checked)
        elif checkbox == "objective_synchronize_eyes":
            state_checked = self.programm_acknowledge_settings_objective_synchronize_eyes_checkbox.isChecked()
            self.__settings.update_objective_synchronize_eyes(state_checked)
        
    def __change_password(self):
        authorization = AuthorizationWindow(self, self.__db)
        authorization.exec_()
        if authorization.exit_pressed:
            return
        if authorization.forbidden:
            self.show_message_window("Запрещено", "Неверный пароль")
            return
        change_password_window = ChangePasswordWindow(self, self.__db)
        change_password_window.exec_()
        if change_password_window.password_changed:
            self.show_message_window("Смена пароля", "Пароль успешно изменён")

    def show_template_window(self, location, field):
        spec = "line_edit" if field != "recommendations" else "text_edit"
        if field in ["recommendations", "reappointment_time"]:
            frame ="recommendations"
        elif field in ["complaints", "disease_anamnesis", "life_anamnesis", "eyesight_type", "schober_test", "pupils"]:
            frame = "common"
        else:
            frame = "objective"
        target_field = getattr(self, f"{location.replace(' ', '_').lower()}_{frame}_{field}_{spec}")
        
        templates = TemplatesWindow(self, field, self.__templates)
        templates.exec_()
        
        text = ""
        for variant in templates.chosen:
            text += variant + ", "

        if templates.chosen:
            if field not in ["recommendations"]:
                target_field.setText(text[:-2])
            else:
                target_field.setPlainText(text[:-2])

    def set_objective_line_edits(self):
        self.exam_objective_eye_position_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Exam", "eye_position"))
        self.exam_objective_oi_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Exam", "oi"))
        self.exam_objective_eyelid_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Exam", "eyelid"))
        self.exam_objective_lacrimal_organs_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Exam", "lacrimal_organs"))
        self.exam_objective_conjunctiva_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Exam", "conjunctiva"))
        self.exam_objective_discharge_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Exam", "discharge"))
        self.exam_objective_iris_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Exam", "iris"))
        self.exam_objective_anterior_chamber_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Exam", "anterior_chamber"))
        self.exam_objective_refractive_medium_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Exam", "refractive_medium"))
        self.exam_objective_optic_disk_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Exam", "optic_disk"))
        self.exam_objective_vessels_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Exam", "vessels"))
        self.exam_objective_macular_reflex_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Exam", "macular_reflex"))
        self.exam_objective_visible_periphery_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Exam", "visible_periphery"))
        self.exam_objective_diagnosis_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Exam", "diagnosis"))
        self.exam_objective_icd_code_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Exam", "icd_code"))

        self.change_data_objective_eye_position_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Change data", "eye_position"))
        self.change_data_objective_oi_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Change data", "oi"))
        self.change_data_objective_eyelid_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Change data", "eyelid"))
        self.change_data_objective_lacrimal_organs_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Change data", "lacrimal_organs"))
        self.change_data_objective_conjunctiva_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Change data", "conjunctiva"))
        self.change_data_objective_discharge_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Change data", "discharge"))
        self.change_data_objective_iris_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Change data", "iris"))
        self.change_data_objective_anterior_chamber_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Change data", "anterior_chamber"))
        self.change_data_objective_refractive_medium_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Change data", "refractive_medium"))
        self.change_data_objective_optic_disk_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Change data", "optic_disk"))
        self.change_data_objective_vessels_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Change data", "vessels"))
        self.change_data_objective_macular_reflex_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Change data", "macular_reflex"))
        self.change_data_objective_visible_periphery_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Change data", "visible_periphery"))
        self.change_data_objective_diagnosis_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Change data", "diagnosis"))
        self.change_data_objective_icd_code_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Change data", "icd_code"))
        
        self.print_objective_eye_position_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Print", "eye_position"))
        self.print_objective_oi_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Print", "oi"))
        self.print_objective_eyelid_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Print", "eyelid"))
        self.print_objective_lacrimal_organs_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Print", "lacrimal_organs"))
        self.print_objective_conjunctiva_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Print", "conjunctiva"))
        self.print_objective_discharge_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Print", "discharge"))
        self.print_objective_iris_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Print", "iris"))
        self.print_objective_anterior_chamber_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Print", "anterior_chamber"))
        self.print_objective_refractive_medium_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Print", "refractive_medium"))
        self.print_objective_optic_disk_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Print", "optic_disk"))
        self.print_objective_vessels_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Print", "vessels"))
        self.print_objective_macular_reflex_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Print", "macular_reflex"))
        self.print_objective_visible_periphery_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Print", "visible_periphery"))
        self.print_objective_diagnosis_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Print", "diagnosis"))
        self.print_objective_icd_code_line_edit.textChanged.connect(lambda: self.save_objective_line_edits("Print", "icd_code"))

    def set_templates_buttons(self):
        self.exam_objective_eye_position_templates_button.clicked.connect(lambda: self.show_template_window('exam', 'eye_position'))
        self.exam_objective_oi_templates_button.clicked.connect(lambda: self.show_template_window('exam', 'oi'))
        self.exam_objective_eyelid_templates_button.clicked.connect(lambda: self.show_template_window('exam', 'eyelid'))
        self.exam_objective_lacrimal_organs_templates_button.clicked.connect(lambda: self.show_template_window('exam', 'lacrimal_organs'))
        self.exam_objective_conjunctiva_templates_button.clicked.connect(lambda: self.show_template_window('exam', 'conjunctiva'))
        self.exam_objective_discharge_templates_button.clicked.connect(lambda: self.show_template_window('exam', 'discharge'))
        self.exam_objective_iris_templates_button.clicked.connect(lambda: self.show_template_window('exam', 'iris'))
        self.exam_objective_anterior_chamber_templates_button.clicked.connect(lambda: self.show_template_window('exam', 'anterior_chamber'))
        self.exam_objective_refractive_medium_templates_button.clicked.connect(lambda: self.show_template_window('exam', 'refractive_medium'))
        self.exam_objective_optic_disk_templates_button.clicked.connect(lambda: self.show_template_window('exam', 'optic_disk'))
        self.exam_objective_vessels_templates_button.clicked.connect(lambda: self.show_template_window('exam', 'vessels'))
        self.exam_objective_macular_reflex_templates_button.clicked.connect(lambda: self.show_template_window('exam', 'macular_reflex'))
        self.exam_objective_visible_periphery_templates_button.clicked.connect(lambda: self.show_template_window('exam', 'visible_periphery'))
        self.exam_objective_diagnosis_templates_button.clicked.connect(lambda: self.show_template_window('exam', 'diagnosis'))
        self.exam_objective_icd_code_templates_button.clicked.connect(lambda: self.show_template_window('exam', 'icd_code'))
        self.exam_recommendations_recommendations_templates_button.clicked.connect(lambda: self.show_template_window('exam', 'recommendations'))
        self.exam_recommendations_reappointment_time_templates_button.clicked.connect(lambda: self.show_template_window('exam', 'reappointment_time'))
        self.exam_common_complaints_templates_button.clicked.connect(lambda: self.show_template_window('exam', 'complaints'))
        self.exam_common_disease_anamnesis_templates_button.clicked.connect(lambda: self.show_template_window('exam', 'disease_anamnesis'))
        self.exam_common_life_anamnesis_templates_button.clicked.connect(lambda: self.show_template_window('exam', 'life_anamnesis'))
        self.exam_common_eyesight_type_templates_button.clicked.connect(lambda: self.show_template_window('exam', 'eyesight_type'))
        self.exam_common_schober_test_templates_button.clicked.connect(lambda: self.show_template_window('exam', 'schober_test'))
        self.exam_common_pupils_templates_button.clicked.connect(lambda: self.show_template_window('exam', 'pupils'))

        self.change_data_objective_eye_position_templates_button.clicked.connect(lambda: self.show_template_window('change_data', 'eye_position'))
        self.change_data_objective_oi_templates_button.clicked.connect(lambda: self.show_template_window('change_data', 'oi'))
        self.change_data_objective_eyelid_templates_button.clicked.connect(lambda: self.show_template_window('change_data', 'eyelid'))
        self.change_data_objective_lacrimal_organs_templates_button.clicked.connect(lambda: self.show_template_window('change_data', 'lacrimal_organs'))
        self.change_data_objective_conjunctiva_templates_button.clicked.connect(lambda: self.show_template_window('change_data', 'conjunctiva'))
        self.change_data_objective_discharge_templates_button.clicked.connect(lambda: self.show_template_window('change_data', 'discharge'))
        self.change_data_objective_iris_templates_button.clicked.connect(lambda: self.show_template_window('change_data', 'iris'))
        self.change_data_objective_anterior_chamber_templates_button.clicked.connect(lambda: self.show_template_window('change_data', 'anterior_chamber'))
        self.change_data_objective_refractive_medium_templates_button.clicked.connect(lambda: self.show_template_window('change_data', 'refractive_medium'))
        self.change_data_objective_optic_disk_templates_button.clicked.connect(lambda: self.show_template_window('change_data', 'optic_disk'))
        self.change_data_objective_vessels_templates_button.clicked.connect(lambda: self.show_template_window('change_data', 'vessels'))
        self.change_data_objective_macular_reflex_templates_button.clicked.connect(lambda: self.show_template_window('change_data', 'macular_reflex'))
        self.change_data_objective_visible_periphery_templates_button.clicked.connect(lambda: self.show_template_window('change_data', 'visible_periphery'))
        self.change_data_objective_diagnosis_templates_button.clicked.connect(lambda: self.show_template_window('change_data', 'diagnosis'))
        self.change_data_objective_icd_code_templates_button.clicked.connect(lambda: self.show_template_window('change_data', 'icd_code'))
        self.change_data_recommendations_recommendations_templates_button.clicked.connect(lambda: self.show_template_window('change_data', 'recommendations'))
        self.change_data_recommendations_reappointment_time_templates_button.clicked.connect(lambda: self.show_template_window('change_data', 'reappointment_time'))
        self.change_data_common_complaints_templates_button.clicked.connect(lambda: self.show_template_window('change_data', 'complaints'))
        self.change_data_common_disease_anamnesis_templates_button.clicked.connect(lambda: self.show_template_window('change_data', 'disease_anamnesis'))
        self.change_data_common_life_anamnesis_templates_button.clicked.connect(lambda: self.show_template_window('change_data', 'life_anamnesis'))
        self.change_data_common_eyesight_type_templates_button.clicked.connect(lambda: self.show_template_window('change_data', 'eyesight_type'))
        self.change_data_common_schober_test_templates_button.clicked.connect(lambda: self.show_template_window('change_data', 'schober_test'))
        self.change_data_common_pupils_templates_button.clicked.connect(lambda: self.show_template_window('change_data', 'pupils'))

        self.print_objective_eye_position_templates_button.clicked.connect(lambda: self.show_template_window('print', 'eye_position'))
        self.print_objective_oi_templates_button.clicked.connect(lambda: self.show_template_window('print', 'oi'))
        self.print_objective_eyelid_templates_button.clicked.connect(lambda: self.show_template_window('print', 'eyelid'))
        self.print_objective_lacrimal_organs_templates_button.clicked.connect(lambda: self.show_template_window('print', 'lacrimal_organs'))
        self.print_objective_conjunctiva_templates_button.clicked.connect(lambda: self.show_template_window('print', 'conjunctiva'))
        self.print_objective_discharge_templates_button.clicked.connect(lambda: self.show_template_window('print', 'discharge'))
        self.print_objective_iris_templates_button.clicked.connect(lambda: self.show_template_window('print', 'iris'))
        self.print_objective_anterior_chamber_templates_button.clicked.connect(lambda: self.show_template_window('print', 'anterior_chamber'))
        self.print_objective_refractive_medium_templates_button.clicked.connect(lambda: self.show_template_window('print', 'refractive_medium'))
        self.print_objective_optic_disk_templates_button.clicked.connect(lambda: self.show_template_window('print', 'optic_disk'))
        self.print_objective_vessels_templates_button.clicked.connect(lambda: self.show_template_window('print', 'vessels'))
        self.print_objective_macular_reflex_templates_button.clicked.connect(lambda: self.show_template_window('print', 'macular_reflex'))
        self.print_objective_visible_periphery_templates_button.clicked.connect(lambda: self.show_template_window('print', 'visible_periphery'))
        self.print_objective_diagnosis_templates_button.clicked.connect(lambda: self.show_template_window('print', 'diagnosis'))
        self.print_objective_icd_code_templates_button.clicked.connect(lambda: self.show_template_window('print', 'icd_code'))
        self.print_recommendations_recommendations_templates_button.clicked.connect(lambda: self.show_template_window('print', 'recommendations'))
        self.print_recommendations_reappointment_time_templates_button.clicked.connect(lambda: self.show_template_window('print', 'reappointment_time'))
        self.print_common_complaints_templates_button.clicked.connect(lambda: self.show_template_window('print', 'complaints'))
        self.print_common_disease_anamnesis_templates_button.clicked.connect(lambda: self.show_template_window('print', 'disease_anamnesis'))
        self.print_common_life_anamnesis_templates_button.clicked.connect(lambda: self.show_template_window('print', 'life_anamnesis'))
        self.print_common_eyesight_type_templates_button.clicked.connect(lambda: self.show_template_window('print', 'eyesight_type'))
        self.print_common_schober_test_templates_button.clicked.connect(lambda: self.show_template_window('print', 'schober_test'))
        self.print_common_pupils_templates_button.clicked.connect(lambda: self.show_template_window('print', 'pupils'))

    def distribute_right_panel_buttons(self, button):
        if button == "examination_of_patient":
            self.show_page_examination()
        elif button == "changing_data":
            self.show_page_changing()
        elif button == "changing_person":
            self.show_page_person_changing()
        elif button == "search_for_patient":
            self.show_page_search()
        elif button == "print":
            self.show_page_print()
        elif button == "settings":
            self.show_page_settings()
        elif button == "quit":
            self.close_animated()
        elif button == "minimize":
            self.minimize_animated()

    def show_search_for_patient_table_context_menu(self, position):
        menu = QtWidgets.QMenu()
        menu.setStyleSheet("""
            border: 1px solid #444;
            border-radius: 4px;
            font-family: Comfortaa;
            font-size: 13px;
                           """)

        items = list(map(lambda x: x.text(), self.search_for_patient_table.selectedItems())) #["ID", "Пациент", "Дата рождения", "ID осмотра", "Дата осмотра"]

        action_edit = QtWidgets.QAction("Изменить", self)
        action_edit.triggered.connect(lambda: (self.show_page_changing(), self.set_change_data_personal_data_by_id(items[0]), self.change_data_date_of_examination_combobox.setCurrentIndex([self.change_data_date_of_examination_combobox.itemText(index) for index in range(self.change_data_date_of_examination_combobox.count())].index(items[4]))))
        menu.addAction(action_edit)

        action_print = QtWidgets.QAction("Печать", self)
        action_print.triggered.connect(lambda: (self.show_page_print(), self.set_print_personal_data_by_id(items[0]), self.print_date_of_examination_combobox.setCurrentIndex([self.print_date_of_examination_combobox.itemText(index) for index in range(self.print_date_of_examination_combobox.count())].index(items[4]))))
        menu.addAction(action_print)

        menu.exec_(self.search_for_patient_table.mapToGlobal(position))

    def change_eye_objective(self, location):
        if location == "Exam":
            current_values = self.exam_objective_values
        elif location == "Change data":
            current_values = self.change_data_objective_values
        elif location == "Print":
            current_values = self.print_objective_values
        else:
            print("Wrong location")
            return
        parameters = ["eye_position", "oi", "eyelid", "lacrimal_organs", "conjunctiva", "discharge",
                  "iris", "anterior_chamber", "refractive_medium", "optic_disk",
                  "vessels", "macular_reflex", "visible_periphery", "diagnosis", "icd_code"]

        eye = getattr(self, f"{location.replace(' ', '_').lower()}_objective_eye_combobox").currentText().lower()
        for field in parameters:
            getattr(self, f"{location.replace(' ', '_').lower()}_objective_{field}_line_edit").setText(current_values[eye][eye+'_'+field])

    def save_objective_line_edits(self, location, field):
        if location == "Exam":
            current_values = self.exam_objective_values
        elif location == "Change data":
            current_values = self.change_data_objective_values
        elif location == "Print":
            current_values = self.print_objective_values
        else:
            print("Wrong location")
            return

        #if field == "diagnosis":
            #diagnosis = getattr(self, f"{location.replace(' ', '_').lower()}_objective_{field}_line_edit")
            #if diagnosis.text():
            #    diagnosis.textChanged.disconnect()
            #    diagnosis.textChanged.connect(lambda: self.save_objective_line_edits(location, "diagnosis"))

        eye = getattr(self, f"{location.replace(' ', '_').lower()}_objective_eye_combobox").currentText().lower()
        another_eye = "od" if eye == "os" else "os"
        if field == "oi":
            current_values[eye][eye+'_'+field] = getattr(self, f"{location.replace(' ', '_').lower()}_objective_{field}_line_edit").text()
            current_values[another_eye][another_eye+'_'+field] = getattr(self, f"{location.replace(' ', '_').lower()}_objective_{field}_line_edit").text()
        else:
            current_values[eye][eye+'_'+field] = getattr(self, f"{location.replace(' ', '_').lower()}_objective_{field}_line_edit").text()
            if self.__settings.objective_synchronize_eyes and eye == "od" and not current_values["os"]['os_'+field]:
                current_values["os"]['os_'+field] = getattr(self, f"{location.replace(' ', '_').lower()}_objective_{field}_line_edit").text()

        if location == "Exam":
            self.exam_objective_values = current_values
        elif location == "Change data":
            self.change_data_objective_values = current_values
        elif location == "Print":
            self.print_objective_values = current_values

    def transfer_objective_data_from_OD(self, location):
        parameters = ["eye_position", "eyelid", "lacrimal_organs", "conjunctiva", "discharge",
                  "iris", "anterior_chamber", "refractive_medium", "optic_disk",
                  "vessels", "macular_reflex", "visible_periphery", "diagnosis", "icd_code"]
        if location == "Exam":
            current_values = self.exam_objective_values
        elif location == "Change data":
            current_values = self.change_data_objective_values
        elif location == "Print":
            current_values = self.print_objective_values
        else:
            print("Wrong location")
            return
        
        current_index = getattr(self, f"{location.replace(' ', '_').lower()}_objective_eye_combobox").currentIndex()
        getattr(self, f"{location.replace(' ', '_').lower()}_objective_eye_combobox").setCurrentIndex(1)
        for field in parameters:
            getattr(self, f"{location.replace(' ', '_').lower()}_objective_{field}_line_edit").setText(current_values["od"]['od_'+field])
        getattr(self, f"{location.replace(' ', '_').lower()}_objective_eye_combobox").setCurrentIndex(current_index)

    def set_standard_right_panel_csses(self):
        self.right_panel_examination_of_patient.setStyleSheet(self.right_panel_blue_normal_css_with_border_radius)
        self.right_panel_data_changing.setStyleSheet(self.right_panel_red_normal_css)
        self.right_panel_person_changing.setStyleSheet(self.right_panel_blue_normal_css)
        self.right_panel_search_for_patient.setStyleSheet(self.right_panel_red_normal_css)
        self.right_panel_print.setStyleSheet(self.right_panel_blue_normal_css)
        self.right_panel_settings.setStyleSheet(self.right_panel_red_normal_css)

    def show_acknowledge_window(self, location, operation):
        if location not in ["Examination", "Change", "Person", "Settings"] or operation not in ["Save", "Delete", "Erase", None]:
            raise Exception(f"ValueError: location must be Examination or Change, operation must be Save, Delete or Erase. Values: {location} {operation}")
        if location == "Examination" and operation == "Delete":
            raise Exception(f"ValueCompatibilityError: there is no Delete in location Examination")
        elif location == "Change" and operation == "Erase":
            raise Exception(f"ValueCompatibilityError: there is no Erase in location Change")
        elif location == "Person" and operation == "Erase":
            raise Exception(f"ValueCompatibilityError: there is no Erase in location Change")
        
        if location == 'Examination':
            message = "Вы действительно хотите сохранить новые данные осмотра?" if operation == "Save" else "Вы действительно хотите очистить данные осмотра?\n(Данные не удалятся из базы)"
            ok_button_text = "Сохранить" if operation == "Save" else "Очистить"
        elif location == "Change":
            message = "Вы действительно хотите изменить данные осмотра?" if operation == "Save" else "Вы действительно хотите удалить осмотр?"
            ok_button_text = "Изменить" if operation == "Save" else "Удалить"
        elif location == 'Person':
            message = "Вы действительно хотите сохранить новые данные пациента?" if operation == "Save" else "Вы действительно хотите удалить все данные пациента, включая все осмотры?"
            ok_button_text = "Сохранить" if operation == "Save" else "Удалить"

        if location == "Settings":
            message = list(self.ive_asked_not_to_click_messages.keys())[randint(0, len(self.ive_asked_not_to_click_messages)-1)]
            ok_button_text = self.ive_asked_not_to_click_messages[message]

        acknowledge_window = AckWindow(self)
        acknowledge_window.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        acknowledge_window.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        acknowledge_window.setWindowTitle("Crystal - Подтвердите действие")
        acknowledge_window.setWindowIcon(QtGui.QIcon("img/icon.ico"))
        acknowledge_window.message_label.setText(message)
        acknowledge_window.ok_button.setText(ok_button_text)
        acknowledge_window.cancel_button.setText("Отмена")
        if location == "Settings":
            acknowledge_window.cancel_button.setVisible(False)
            acknowledge_window.ok_button.setGeometry(20, 116, 260, 26)

        return acknowledge_window.exec_()
    
    def show_message_window(self, title, message, joke_button=None):
        message_window = CustomMessageBox(self)
        message_window.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        message_window.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        message_window.setWindowTitle(title)
        message_window.setWindowIcon(QtGui.QIcon("img/icon.ico"))
        message_window.setText(message)
        message_window.setStandardButtons(QtWidgets.QMessageBox.Ok)
        message_window.setStyleSheet("""
                            QMessageBox {
                                background-color: rgba(0, 0, 0, 0.7);
                                border: 1px solid #888;
                                border-radius: 10px;
                            }
                            QLabel {
                                font-size: 14px;
                                color: #333;
                            }
                            QPushButton {
                                background-color: #eee;
                                color: #555;
                                border-radius: 8px;
                                padding: 5px 10px;
                                border: 1px solid #555;
                            }
                            QPushButton:hover {
                                color: black;
                                border: 1px solid black;
                            }
                        """)
        return message_window.exec_()
    
    def print_examination(self, preview=False):
        if not self.print_id_combobox.currentText() or not self.print_date_of_examination_combobox.currentText():
            self.show_message_window("Ошибка", "Не выбран пациент и его осмотр")
            return
        self.print_document(preview=preview)


    def show_page_examination(self):
        self.working_area_stacked_widget.setCurrentIndex(0)
        self.set_standard_right_panel_csses()
        self.right_panel_examination_of_patient.setStyleSheet("""
                                QFrame {
                                    border-top-right-radius: 10px;
                                    border-bottom-right-radius: 0px;
                                    background: rgba(182, 240, 219, 90);
                                    }

                                    QFrame:hover {
                                    background: rgba(172, 255, 210, 100);
                                    border-left: 0px;
                                    }
                                """)

    def show_page_changing(self):
        self.working_area_stacked_widget.setCurrentIndex(1)
        self.set_standard_right_panel_csses()
        self.right_panel_data_changing.setStyleSheet("""
                                QFrame {
                                    border-top-right-radius: 0px;
                                    border-bottom-right-radius: 0px;
                                    background: rgba(246, 176, 219, 90);
                                    border-top: 1px solid rgba(255,255,255,80);
                                    }

                                    QFrame:hover {
                                    background: rgba(255, 166, 209, 90);
                                    border-left: 0px;
                                    }
                                    """)

    def show_page_person_changing(self):
        self.working_area_stacked_widget.setCurrentIndex(2)
        self.set_standard_right_panel_csses()
        self.right_panel_person_changing.setStyleSheet("""
                                QFrame {
                                    border-top-right-radius: 0px;
                                    border-bottom-right-radius: 0px;
                                    background: rgba(182, 240, 219, 90);
                                    }

                                    QFrame:hover {
                                    background: rgba(172, 255, 210, 100);
                                    border-left: 0px;
                                    }
                                """)

    def show_page_search(self):
        self.working_area_stacked_widget.setCurrentIndex(3)
        self.set_standard_right_panel_csses()
        self.right_panel_search_for_patient.setStyleSheet("""
                                QFrame {
                                    border-top-right-radius: 0px;
                                    border-bottom-right-radius: 0px;
                                    background: rgba(246, 176, 219, 90);
                                    border-top: 1px solid rgba(255,255,255,80);
                                    }

                                    QFrame:hover {
                                    background: rgba(255, 166, 209, 90);
                                    border-left: 0px;
                                    }
                                    """)

    def show_page_print(self):
        self.working_area_stacked_widget.setCurrentIndex(4)
        self.set_standard_right_panel_csses()
        self.right_panel_print.setStyleSheet("""
                                QFrame {
                                    border-top-right-radius: 0px;
                                    border-bottom-right-radius: 0px;
                                    background: rgba(182, 240, 219, 90);
                                    }

                                    QFrame:hover {
                                    background: rgba(172, 255, 210, 100);
                                    border-left: 0px;
                                    }
                                """)

    def show_page_settings(self):
        self.working_area_stacked_widget.setCurrentIndex(5)
        self.set_standard_right_panel_csses()
        self.right_panel_settings.setStyleSheet("""
                                QFrame {
                                    border-top-right-radius: 0px;
                                    border-bottom-right-radius: 0px;
                                    background: rgba(246, 176, 219, 90);
                                    border-top: 1px solid rgba(255,255,255,80);
                                    }

                                    QFrame:hover {
                                    background: rgba(255, 166, 209, 90);
                                    border-left: 0px;
                                    }
                                    """)

    def launch_animated(self):
        self.launch_close_animation.setStartValue(0)
        self.launch_close_animation.setEndValue(1)
        self.launch_close_animation.start()

    def close_animated(self):
        if self.__settings.remember_last_position:
            self.__settings.update_last_position(str(self.x()) + ',' + str(self.y()))
            self.__settings.update_number_of_visible_records(int(self.search_settings_number_of_visible_records_box.text()), to_db=True)

        window.backup_database()
        #p = Process(target=self.__db.upload_database)
        #p.start()

        self.launch_close_animation.setStartValue(1)
        self.launch_close_animation.setEndValue(0)
        self.launch_close_animation.start()
        self.launch_close_animation.finished.connect(self.close)

    def minimize_animated(self):
        self.launch_close_animation.setStartValue(1)
        self.launch_close_animation.setEndValue(0)
        self.launch_close_animation.start()
        self.launch_close_animation.finished.connect(lambda: (self.showMinimized(), self.setWindowOpacity(1)))

    def update_all_frames_with_data(self):
        self.exam_personal_data_completer.setModel(None)
        self.change_data_search_for_name_completer.setModel(None)
        self.change_person_search_for_name_completer.setModel(None)
        self.search_for_patient_completer.setModel(None)
        self.print_search_for_name_completer.setModel(None)
        self.exam_personal_data_new_patient_checkbox.setChecked(False)
        if self.exam_personal_data_name_line_edit.text():
            id_index = self.exam_personal_data_id_combobox.currentIndex()
            exam_date_index = self.exam_personal_data_last_examinations_date_combobox.currentIndex()
            exam_date_count = self.exam_personal_data_last_examinations_date_combobox.count()
            exam_name = self.exam_personal_data_name_line_edit.text()
            self.exam_personal_data_name_line_edit.clear()
            self.exam_personal_data_name_line_edit.setText(exam_name)
            if id_index == -1:
                self.exam_personal_data_id_combobox.setCurrentIndex(0)
            elif id_index and id_index <= self.exam_personal_data_id_combobox.count() - 1:
                self.exam_personal_data_id_combobox.setCurrentIndex(id_index)
            if exam_date_index == -1:
                self.exam_personal_data_last_examinations_date_combobox.setCurrentIndex(0)
            elif exam_date_index and exam_date_index <= self.exam_personal_data_last_examinations_date_combobox.count() - 1:
                if exam_date_count != self.exam_personal_data_last_examinations_date_combobox.count() - 1:
                    self.exam_personal_data_last_examinations_date_combobox.setCurrentIndex(exam_date_index)
                else:
                    self.exam_personal_data_last_examinations_date_combobox.setCurrentIndex(self.exam_personal_data_last_examinations_date_combobox.count()-1)
        if self.change_data_search_for_name_of_patient_line_edit.text():
            id_index = self.change_data_id_combobox.currentIndex()
            exam_date_index = self.change_data_date_of_examination_combobox.currentIndex()
            change_data_search_name = self.change_data_search_for_name_of_patient_line_edit.text()
            self.change_data_search_for_name_of_patient_line_edit.clear()
            self.change_data_search_for_name_of_patient_line_edit.setText(change_data_search_name)
            if id_index == -1:
                self.change_data_id_combobox.setCurrentIndex(0)
            elif id_index <= self.change_data_id_combobox.count() - 1:
                self.change_data_id_combobox.setCurrentIndex(id_index)
            if exam_date_index == -1:
                self.change_data_date_of_examination_combobox.setCurrentIndex(0)
            elif exam_date_index and exam_date_index <= self.change_data_date_of_examination_combobox.count() - 1:
                self.change_data_date_of_examination_combobox.setCurrentIndex(exam_date_index)
        if self.change_person_search_for_name_of_patient_line_edit.text():
            id_index = self.change_person_id_combobox.currentIndex()
            change_person_name = self.change_person_search_for_name_of_patient_line_edit.text()
            self.change_person_search_for_name_of_patient_line_edit.clear()
            self.change_person_search_for_name_of_patient_line_edit.setText(change_person_name)
            if id_index == -1:
                self.change_person_id_combobox.setCurrentIndex(0)
            elif id_index <= self.change_person_id_combobox.count() - 1:
                self.change_person_id_combobox.setCurrentIndex(id_index)
        if self.search_for_patient_name_line_edit.text():
            search_name = self.search_for_patient_name_line_edit.text()
            self.search_for_patient_name_line_edit.clear()
            self.search_for_patient_name_line_edit.setText(search_name)
        else:
            self.fill_search_table(all=True)
        if self.print_search_for_name_of_patient_line_edit.text():
            id_index = self.print_id_combobox.currentIndex()
            exam_date_index = self.print_date_of_examination_combobox.currentIndex()
            print_persion_name = self.print_search_for_name_of_patient_line_edit.text()
            self.print_search_for_name_of_patient_line_edit.clear()
            self.print_search_for_name_of_patient_line_edit.setText(print_persion_name)
            if id_index == -1:
                self.print_id_combobox.setCurrentIndex(0)
            elif id_index <= self.print_id_combobox.count() - 1:
                self.print_id_combobox.setCurrentIndex(id_index)
            if exam_date_index == -1:
                self.print_date_of_examination_combobox.setCurrentIndex(0)
            elif exam_date_index and exam_date_index <= self.print_date_of_examination_combobox.count() - 1:
                self.print_date_of_examination_combobox.setCurrentIndex(exam_date_index)

    def set_current_time_on_exam_date_label(self):
        self.exam_diagnosis_date_label.setText(datetime.datetime.strftime(datetime.datetime.now(), "%d.%m.%Y %H:%M"))

    def reset_exam_data(self):
        if self.exam_reset_exam_data_button.text() == "Сбросить":
            self.set_default_examination()
            self.exam_reset_exam_data_button.setText("Заполнить")
        else:
            exam_time = self.exam_personal_data_last_examinations_date_combobox.currentIndex()
            self.exam_personal_data_last_examinations_date_combobox.setCurrentIndex(-1)
            self.exam_personal_data_last_examinations_date_combobox.setCurrentIndex(exam_time)
            self.exam_reset_exam_data_button.setText("Сбросить")

    def set_exam_default_personal_data(self, new_patient_checkbox = False):
        self.exam_reset_exam_data_button.setText("Сбросить")
        if new_patient_checkbox:
            if self.exam_personal_data_new_patient_checkbox.isChecked():
                self.exam_personal_data_birthdate_date_edit.setEnabled(True)
                self.exam_personal_data_birthdate_date_edit.setDate(QtCore.QDate(self.default_data['birthdate'][2], self.default_data['birthdate'][1], self.default_data['birthdate'][0]))
                self.exam_personal_data_id_combobox.clear()
                self.set_default_examination()
            else:
                self.exam_personal_data_birthdate_date_edit.setDisabled(True)
                self.set_exam_personal_data_by_name(self.exam_personal_data_name_line_edit.text())
        else:
            self.exam_personal_data_birthdate_date_edit.setDate(QtCore.QDate(self.default_data['birthdate'][2], self.default_data['birthdate'][1], self.default_data['birthdate'][0]))
            self.exam_personal_data_id_combobox.clear()
            self.exam_personal_data_name_line_edit.clear()

    def set_exam_personal_data_by_name(self, name: str):
        self.exam_reset_exam_data_button.setText("Сбросить")
        if not name:
            self.set_default_examination()
            self.exam_personal_data_last_examinations_date_combobox.clear()
            self.exam_personal_data_new_patient_checkbox.setVisible(False)
            self.exam_personal_data_id_combobox.clear()
            self.exam_personal_data_birthdate_date_edit.setDate(QtCore.QDate(self.default_data['birthdate'][2], self.default_data['birthdate'][1], self.default_data['birthdate'][0]))
            self.exam_personal_data_birthdate_date_edit.setEnabled(True)
            return
        data = self.__people.search(name=name)
        if data:
            self.exam_personal_data_new_patient_checkbox.setVisible(True)
            if not self.exam_personal_data_new_patient_checkbox.isChecked():
                self.exam_personal_data_birthdate_date_edit.setDisabled(True)
            self.exam_personal_data_id_combobox.currentIndexChanged.disconnect()
            self.exam_personal_data_id_combobox.clear()
            birthdate = data[0].birthdate
            year, month, day = birthdate.split('.')[2], birthdate.split('.')[1], birthdate.split('.')[0]
            id = list(map(lambda x: str(x.id), data))
            self.exam_personal_data_id_combobox.addItems(id)
            full_name = list(map(lambda x: x.full_name, data))
            self.exam_personal_data_last_examinations_date_combobox.clear()
            self.exam_personal_data_last_examinations_date_combobox.addItems(list(map(lambda examination: examination.visit_date, self.__examinations.get_examinations_by_person_id(data[0].id))))

            self.exam_personal_data_birthdate_date_edit.setDate(QtCore.QDate(int(year), int(month), int(day)))
            self.exam_personal_data_completer.setModel(QtCore.QStringListModel(full_name))
            self.exam_personal_data_id_combobox.currentIndexChanged.connect(lambda: self.set_exam_personal_data_by_id(self.exam_personal_data_id_combobox.currentText()))
        else:
            self.set_default_examination()
            self.exam_personal_data_last_examinations_date_combobox.clear()
            self.exam_personal_data_birthdate_date_edit.setEnabled(True)
            self.exam_personal_data_new_patient_checkbox.setVisible(False)
            self.exam_personal_data_birthdate_date_edit.setDate(QtCore.QDate(self.default_data['birthdate'][2], self.default_data['birthdate'][1], self.default_data['birthdate'][0]))
            self.exam_personal_data_id_combobox.clear()

    def set_exam_personal_data_by_id(self, id: str):
        self.exam_reset_exam_data_button.setText("Сбросить")
        self.exam_personal_data_last_examinations_date_combobox.clear()
        if id:
            self.exam_personal_data_new_patient_checkbox.setVisible(True)
            data = self.__people.search(id=int(id))
            birthdate = data.birthdate
            year, month, day = birthdate.split('.')[2], birthdate.split('.')[1], birthdate.split('.')[0]
            self.exam_personal_data_birthdate_date_edit.setDate(QtCore.QDate(int(year), int(month), int(day)))
            self.exam_personal_data_name_line_edit.setText(data.full_name)
            self.exam_personal_data_last_examinations_date_combobox.addItems(list(map(lambda examination: examination.visit_date, self.__examinations.get_examinations_by_person_id(data.id))))

    def set_exam_examination_data(self, template=None): # template - это [Текст комбобокса (название шаблона), глаз (OD=0, OS=1)]
        self.exam_reset_exam_data_button.setText("Сбросить")
        examination_datetime = self.exam_personal_data_last_examinations_date_combobox.currentText()
        person_id = self.exam_personal_data_id_combobox.currentText()

        if template not in [0, -1, None] and isinstance(template, list):
            if template[0] != '':
                exam_template = self.__exam_templates.get_template(template[0])
            else:
                exam_template = self.__exam_templates.get_template("Empty")
            if not exam_template:
                self.show_message_window("Ошибка", "Шаблона не существует")
                return
            ### Чё я тут понаписал такое (в целом применимо ко всему коду)
            another_template = self.exam_misc_examination_templates_OS_combobox.currentText() if template[1] == 0 else self.exam_misc_examination_templates_OD_combobox.currentText()
            if another_template != "":
                another_exam_template = self.__exam_templates.get_template(another_template)
                if another_exam_template:
                    if template[1] == 0:
                        complaints = exam_template.complaints + ",\n"*int(bool(exam_template.complaints)) + another_exam_template.complaints if exam_template.complaints != another_exam_template.complaints and another_exam_template.complaints != '' else exam_template.complaints
                        recommmendations = exam_template.recommendations + ",\n"*int(bool(exam_template.recommendations)) + another_exam_template.recommendations if exam_template.recommendations != another_exam_template.recommendations and another_exam_template.recommendations != ''  else exam_template.recommendations
                    else:
                        complaints = another_exam_template.complaints + ",\n"*int(bool(another_exam_template.complaints)) + exam_template.complaints if exam_template.complaints != another_exam_template.complaints and exam_template.complaints != ''  else another_exam_template.complaints
                        recommmendations = another_exam_template.recommendations + ",\n"*int(bool(another_exam_template.complaints)) + exam_template.recommendations if exam_template.recommendations != another_exam_template.recommendations and exam_template.recommendations != '' else another_exam_template.recommendations

                    if len(complaints.split("\n")) >= 2:
                        left = complaints.split("\n")[0]
                        for right in complaints.split("\n")[1:]:
                            for complaint in left.split(", "):
                                if complaint in right:
                                    if complaint + ", " in right:
                                        right = right.replace(complaint + ", ", '')
                                    elif ", " + complaint in right:
                                        right = right.replace(", " + complaint, '')
                                    else:
                                        right = right.replace(complaint, '').replace("\n", "")
                            complaints = left + "\n" + right

                    self.exam_common_complaints_line_edit.setText(complaints)
                    self.exam_recommendations_recommendations_text_edit.setPlainText(recommmendations)
            else:
                complaints = exam_template.complaints
                recommmendations = exam_template.recommendations

            parameters = ["eye_position", "oi", "eyelid", "lacrimal_organs", "conjunctiva", "discharge",
                                "iris", "anterior_chamber", "refractive_medium", "optic_disk",
                                "vessels", "macular_reflex", "visible_periphery", "diagnosis", "icd_code"]
            if template[0] == '':
                if template[1] == 0:
                    self.exam_eyesight_schiascopy_OD_line_edit.setText(exam_template.schiascopy_od)
                elif template[1] == 1:
                    self.exam_eyesight_schiascopy_OS_line_edit.setText(exam_template.schiascopy_os)

                eye = template[1]

                self.exam_objective_eye_combobox.setCurrentIndex(eye)
                eye = ["od", "os"][eye]
                for field in parameters:
                    current_value = getattr(exam_template, eye+'_'+field)
                    getattr(self, f"exam_objective_{field}_line_edit").setText(current_value)

                old_complaints = self.__exam_templates.get_template(self.current_exam_OD_template).complaints if template[1] == 0 else self.__exam_templates.get_template(self.current_exam_OS_template).complaints
                old_recommendations = self.__exam_templates.get_template(self.current_exam_OD_template).recommendations if template[1] == 0 else self.__exam_templates.get_template(self.current_exam_OS_template).recommendations

                if self.current_exam_OD_template != self.current_exam_OS_template:
                    self.exam_common_complaints_line_edit.setText(self.exam_common_complaints_line_edit.text().replace(old_complaints, '').replace("\n", '', 1))
                    self.exam_recommendations_recommendations_text_edit.setPlainText(self.exam_recommendations_recommendations_text_edit.toPlainText().replace(old_recommendations, '').replace("\n", '', 1))
            else:
                if template[1] == 0: #For OD
                    self.exam_eyesight_schiascopy_OD_line_edit.setText(exam_template.schiascopy_od)
                elif template[1] == 1: #For OS
                    self.exam_eyesight_schiascopy_OS_line_edit.setText(exam_template.schiascopy_os)

                self.exam_common_complaints_line_edit.setText(complaints)

                self.exam_objective_eye_combobox.setCurrentIndex(template[1])

                eye = template[1]

                self.exam_objective_eye_combobox.setCurrentIndex(eye)
                eye = ["od", "os"][eye]
                for field in parameters:
                    current_value = getattr(exam_template, eye+'_'+field)
                    getattr(self, f"exam_objective_{field}_line_edit").setText(current_value)
                
                self.exam_recommendations_recommendations_text_edit.setPlainText(recommmendations)
                self.exam_recommendations_direction_to_aokb_checkbox.setChecked(bool(exam_template.direction_to_aokb))
                self.exam_recommendations_reappointment_checkbox.setChecked(bool(exam_template.reappointment))
                self.exam_recommendations_reappointment_time_line_edit.setText(exam_template.reappointment_time)

            self.current_exam_OD_template = self.exam_misc_examination_templates_OD_combobox.currentText()
            self.current_exam_OS_template = self.exam_misc_examination_templates_OS_combobox.currentText()

        elif (examination_datetime and person_id):
            examination = self.__examinations.get_examination_by_person_id_and_examination_datetime(person_id, examination_datetime)
            if not examination:
                self.show_message_window("Ошибка", "Внутренняя ошибка, не найден пациент по ID и времени осмотра")
                return
            
            self.exam_eyesight_visual_acuity_without_OD_box.setValue(examination.eyesight_without_od)
            self.exam_eyesight_visual_acuity_without_OS_box.setValue(examination.eyesight_without_os)

            self.exam_eyesight_visual_acuity_with_OD_box.setValue(examination.eyesight_with_od)
            self.exam_eyesight_visual_acuity_with_OD_sph_box.setValue(examination.eyesight_with_od_sph)
            self.exam_eyesight_visual_acuity_with_OD_cyl_box.setValue(examination.eyesight_with_od_cyl)
            self.exam_eyesight_visual_acuity_with_OD_ax_box.setValue(examination.eyesight_with_od_ax)

            self.exam_eyesight_visual_acuity_with_OS_box.setValue(examination.eyesight_with_os)
            self.exam_eyesight_visual_acuity_with_OS_sph_box.setValue(examination.eyesight_with_os_sph)
            self.exam_eyesight_visual_acuity_with_OS_cyl_box.setValue(examination.eyesight_with_os_cyl)
            self.exam_eyesight_visual_acuity_with_OS_ax_box.setValue(examination.eyesight_with_os_ax)

            self.exam_eyesight_schiascopy_OD_line_edit.setText(examination.schiascopy_od)

            self.exam_eyesight_schiascopy_OS_line_edit.setText(examination.schiascopy_os)

            self.exam_glasses_OD_sph_box.setValue(examination.glasses_od_sph)
            self.exam_glasses_OD_cyl_box.setValue(examination.glasses_od_cyl)
            self.exam_glasses_OD_ax_box.setValue(examination.glasses_od_ax)

            self.exam_glasses_OS_sph_box.setValue(examination.glasses_os_sph)
            self.exam_glasses_OS_cyl_box.setValue(examination.glasses_os_cyl)
            self.exam_glasses_OS_ax_box.setValue(examination.glasses_os_ax)

            self.exam_glasses_dpp_box.setValue(examination.glasses_dpp)

            self.exam_diagnosis_subscription_text_edit.setPlainText(examination.diagnosis_subscription)

            self.exam_common_complaints_line_edit.setText(examination.complaints)
            self.exam_common_disease_anamnesis_line_edit.setText(examination.disease_anamnesis)
            self.exam_common_life_anamnesis_line_edit.setText(examination.life_anamnesis)
            self.exam_common_eyesight_type_line_edit.setText(examination.eyesight_type)
            self.exam_common_relative_accommodation_reserve_box.setValue(examination.relative_accommodation_reserve)
            self.exam_common_schober_test_line_edit.setText(examination.schober_test)
            self.exam_common_pupils_line_edit.setText(examination.pupils)

            parameters = ["eye_position", "oi", "eyelid", "lacrimal_organs", "conjunctiva", "discharge",
                        "iris", "anterior_chamber", "refractive_medium", "optic_disk",
                        "vessels", "macular_reflex", "visible_periphery", "diagnosis", "icd_code"]

            for eye in range(2):
                self.exam_objective_eye_combobox.setCurrentIndex(eye)
                eye = ["od", "os"][eye]
                for field in parameters:
                    current_value = getattr(examination, eye+'_'+field)
                    getattr(self, f"exam_objective_{field}_line_edit").setText(current_value)
            self.exam_objective_eye_combobox.setCurrentIndex(0)

            self.exam_recommendations_recommendations_text_edit.setPlainText(examination.recommendations)
            self.exam_recommendations_direction_to_aokb_checkbox.setChecked(bool(examination.direction_to_aokb))
            self.exam_recommendations_reappointment_checkbox.setChecked(bool(examination.reappointment))
            self.exam_recommendations_reappointment_time_line_edit.setText(examination.reappointment_time)

        else:
            self.set_default_examination()

    def gather_examination_data(self):
        data = {}
        recommendations = {}

        if self.exam_personal_data_id_combobox.currentText():
            data['person_id'] = int(self.exam_personal_data_id_combobox.currentText())
        else:
            full_person_name = self.exam_personal_data_name_line_edit.text()
            new_person = self.__people.add_person(full_person_name, self.exam_personal_data_birthdate_date_edit.text())
            data['person_id'] = new_person.id
            self.set_exam_personal_data_by_id(str(new_person.id))

        data['eyesight_without_od'] = self.exam_eyesight_visual_acuity_without_OD_box.value()
        data['eyesight_without_os'] = self.exam_eyesight_visual_acuity_without_OS_box.value()

        data['eyesight_with_od'] = self.exam_eyesight_visual_acuity_with_OD_box.value()
        data['eyesight_with_od_sph'] = self.exam_eyesight_visual_acuity_with_OD_sph_box.value()
        data['eyesight_with_od_cyl'] = self.exam_eyesight_visual_acuity_with_OD_cyl_box.value()
        data['eyesight_with_od_ax'] = self.exam_eyesight_visual_acuity_with_OD_ax_box.value()

        data['eyesight_with_os'] = self.exam_eyesight_visual_acuity_with_OS_box.value()
        data['eyesight_with_os_sph'] = self.exam_eyesight_visual_acuity_with_OS_sph_box.value()
        data['eyesight_with_os_cyl'] = self.exam_eyesight_visual_acuity_with_OS_cyl_box.value()
        data['eyesight_with_os_ax'] = self.exam_eyesight_visual_acuity_with_OS_ax_box.value()

        data['schiascopy_od'] = self.exam_eyesight_schiascopy_OD_line_edit.text()

        data['schiascopy_os'] = self.exam_eyesight_schiascopy_OS_line_edit.text()

        data['glasses_od_sph'] = self.exam_glasses_OD_sph_box.value()
        data['glasses_od_cyl'] = self.exam_glasses_OD_cyl_box.value()
        data['glasses_od_ax'] = self.exam_glasses_OD_ax_box.value()

        data['glasses_os_sph'] = self.exam_glasses_OS_sph_box.value()
        data['glasses_os_cyl'] = self.exam_glasses_OS_cyl_box.value()
        data['glasses_os_ax'] = self.exam_glasses_OS_ax_box.value()

        data['glasses_dpp'] = self.exam_glasses_dpp_box.value()

        data['diagnosis_subscription'] = self.exam_diagnosis_subscription_text_edit.toPlainText()

        data['visit_date'] = self.exam_diagnosis_date_label.text()

        data["complaints"] = self.exam_common_complaints_line_edit.text()
        data["disease_anamnesis"] = self.exam_common_disease_anamnesis_line_edit.text()
        data["life_anamnesis"] = self.exam_common_life_anamnesis_line_edit.text()
        data["eyesight_type"] = self.exam_common_eyesight_type_line_edit.text()
        data['relative_accommodation_reserve'] = self.exam_common_relative_accommodation_reserve_box.value()
        data["schober_test"] = self.exam_common_schober_test_line_edit.text()
        data["pupils"] = self.exam_common_pupils_line_edit.text()

        recommendations['recommendations'] = self.exam_recommendations_recommendations_text_edit.toPlainText()
        recommendations['direction'] = int(self.exam_recommendations_direction_to_aokb_checkbox.isChecked())
        recommendations['reappointment'] = int(self.exam_recommendations_reappointment_checkbox.isChecked())
        recommendations['reappointment_time'] = self.exam_recommendations_reappointment_time_line_edit.text()

        return data | self.exam_objective_values["od"] | self.exam_objective_values["os"] | recommendations

    def gather_change_data_data(self) -> dict:
        data = {}
        recommendations = {}

        data['eyesight_without_od'] = self.change_data_eyesight_visual_acuity_without_OD_box.value()
        data['eyesight_without_os'] = self.change_data_eyesight_visual_acuity_without_OS_box.value()

        data['eyesight_with_od'] = self.change_data_eyesight_visual_acuity_with_OD_box.value()
        data['eyesight_with_od_sph'] = self.change_data_eyesight_visual_acuity_with_OD_sph_box.value()
        data['eyesight_with_od_cyl'] = self.change_data_eyesight_visual_acuity_with_OD_cyl_box.value()
        data['eyesight_with_od_ax'] = self.change_data_eyesight_visual_acuity_with_OD_ax_box.value()

        data['eyesight_with_os'] = self.change_data_eyesight_visual_acuity_with_OS_box.value()
        data['eyesight_with_os_sph'] = self.change_data_eyesight_visual_acuity_with_OS_sph_box.value()
        data['eyesight_with_os_cyl'] = self.change_data_eyesight_visual_acuity_with_OS_cyl_box.value()
        data['eyesight_with_os_ax'] = self.change_data_eyesight_visual_acuity_with_OS_ax_box.value()

        data['schiascopy_od'] = self.change_data_eyesight_schiascopy_OD_line_edit.text()
        data['schiascopy_os'] = self.change_data_eyesight_schiascopy_OS_line_edit.text()

        data['glasses_od_sph'] = self.change_data_glasses_OD_sph_box.value()
        data['glasses_od_cyl'] = self.change_data_glasses_OD_cyl_box.value()
        data['glasses_od_ax'] = self.change_data_glasses_OD_ax_box.value()

        data['glasses_os_sph'] = self.change_data_glasses_OS_sph_box.value()
        data['glasses_os_cyl'] = self.change_data_glasses_OS_cyl_box.value()
        data['glasses_os_ax'] = self.change_data_glasses_OS_ax_box.value()

        data['glasses_dpp'] = self.change_data_glasses_dpp_box.value()

        data['diagnosis_subscription'] = self.change_data_diagnosis_subscription_text_edit.toPlainText()

        data["complaints"] = self.change_data_common_complaints_line_edit.text()
        data["disease_anamnesis"] = self.change_data_common_disease_anamnesis_line_edit.text()
        data["life_anamnesis"] = self.change_data_common_life_anamnesis_line_edit.text()
        data["eyesight_type"] = self.change_data_common_eyesight_type_line_edit.text()
        data['relative_accommodation_reserve'] = self.change_data_common_relative_accommodation_reserve_box.value()
        data["schober_test"] = self.change_data_common_schober_test_line_edit.text()
        data["pupils"] = self.change_data_common_pupils_line_edit.text()

        recommendations['recommendations'] = self.change_data_recommendations_recommendations_text_edit.toPlainText()
        recommendations['direction'] = int(self.change_data_recommendations_direction_to_aokb_checkbox.isChecked())
        recommendations['reappointment'] = int(self.change_data_recommendations_reappointment_checkbox.isChecked())
        recommendations['reappointment_time'] = self.change_data_recommendations_reappointment_time_line_edit.text()

        return data | self.change_data_objective_values["od"] | self.change_data_objective_values["os"] | recommendations
    
    def gather_print_data(self):
        def get_age(date):
            date = datetime.datetime.strptime(date, "%d.%m.%Y")
            today = datetime.datetime.strptime(datetime.datetime.now().strftime("%d.%m.%Y"), "%d.%m.%Y")

            delta = today - date
            delta = delta.days - 1

            years = delta // 365
            delta = delta % 365
            months = delta // 30
            delta = delta % 30

            if 0 < years < 5:
                age = f"{years}г {months}м"
            elif years == 0:
                age = f"{months}м."
            else:
                word = "лет" if 20 > years > 10 else {"0": "лет", "1": "год", "2": "года", "3": "года", "4": "года", "5": "лет", "6": "лет", "7": "лет", "8": "лет", "9": "лет"}[str(years)[-1]]
                age = f"{years} {word}"

            return age

        data = {}
        recommendations = {}

        data["patient_name"] = self.__people.search(id=int(self.print_id_combobox.currentText())).full_name

        data["patient_age"] = get_age(self.print_birthdate_date_edit.text())
        data["date"] = self.print_diagnosis_date_label.text().split()[0]

        data['eyesight_without_od'] = self.print_eyesight_visual_acuity_without_OD_box.value()
        data['eyesight_without_os'] = self.print_eyesight_visual_acuity_without_OS_box.value()

        data['eyesight_with_od'] = self.print_eyesight_visual_acuity_with_OD_box.value()
        data['eyesight_with_od_sph'] = self.print_eyesight_visual_acuity_with_OD_sph_box.value()
        data['eyesight_with_od_cyl'] = self.print_eyesight_visual_acuity_with_OD_cyl_box.value()
        data['eyesight_with_od_ax'] = int(self.print_eyesight_visual_acuity_with_OD_ax_box.value())

        data['eyesight_with_os'] = self.print_eyesight_visual_acuity_with_OS_box.value()
        data['eyesight_with_os_sph'] = self.print_eyesight_visual_acuity_with_OS_sph_box.value()
        data['eyesight_with_os_cyl'] = self.print_eyesight_visual_acuity_with_OS_cyl_box.value()
        data['eyesight_with_os_ax'] = int(self.print_eyesight_visual_acuity_with_OS_ax_box.value())

        data['schiascopy_od'] = self.print_eyesight_schiascopy_OD_line_edit.text()

        data['schiascopy_os'] = self.print_eyesight_schiascopy_OS_line_edit.text()

        data['glasses_od_sph'] = self.print_glasses_OD_sph_box.value()
        data['glasses_od_cyl'] = self.print_glasses_OD_cyl_box.value()
        data['glasses_od_ax'] = self.print_glasses_OD_ax_box.value()

        data['glasses_os_sph'] = self.print_glasses_OS_sph_box.value()
        data['glasses_os_cyl'] = self.print_glasses_OS_cyl_box.value()
        data['glasses_os_ax'] = self.print_glasses_OS_ax_box.value()

        data['glasses_dpp'] = str(int(self.print_glasses_dpp_box.value()))

        data['diagnosis_subscription'] = self.print_diagnosis_subscription_text_edit.toPlainText()
        
        data["complaints"] = self.print_common_complaints_line_edit.text()
        data["disease_anamnesis"] = self.print_common_disease_anamnesis_line_edit.text()
        data["life_anamnesis"] = self.print_common_life_anamnesis_line_edit.text()
        data["eyesight_type"] = self.print_common_eyesight_type_line_edit.text()
        data['relative_accommodation_reserve'] = self.print_common_relative_accommodation_reserve_box.value()
        data["schober_test"] = self.print_common_schober_test_line_edit.text()
        data["pupils"] = self.print_common_pupils_line_edit.text()

        recommendations['recommendations'] = self.print_recommendations_recommendations_text_edit.toPlainText()
        recommendations['direction'] = int(self.print_recommendations_direction_to_aokb_checkbox.isChecked())
        recommendations['reappointment'] = int(self.print_recommendations_reappointment_checkbox.isChecked())
        recommendations['reappointment_time'] = self.print_recommendations_reappointment_time_line_edit.text()

        return data | self.print_objective_values["od"] | self.print_objective_values["os"] | recommendations

    def save_examination(self):
        full_person_name = self.exam_personal_data_name_line_edit.text()
        parameters = ["eye_position", "oi", "eyelid", "lacrimal_organs", "conjunctiva", "discharge",
                  "iris", "anterior_chamber", "refractive_medium", "optic_disk",
                  "vessels", "macular_reflex", "visible_periphery", "diagnosis", "icd_code"] ### Here is only line edits!!!

        for eye in ["od", "os"]:
            for field in parameters:
                if "'" in self.exam_objective_values[eye][eye+"_"+field]:
                    self.show_message_window("Ошибка", "Символ ' нельзя использовать в поле ввода")
                    return
        for text_field in [full_person_name, self.exam_diagnosis_subscription_text_edit.toPlainText(), self.exam_recommendations_recommendations_text_edit.toPlainText(), self.exam_common_complaints_line_edit.text(),
                           self.exam_common_disease_anamnesis_line_edit.text(), self.exam_common_life_anamnesis_line_edit.text(), self.exam_common_eyesight_type_line_edit.text(), self.exam_common_schober_test_line_edit.text(),
                           self.exam_common_pupils_line_edit.text()]:
            if "'" in text_field:
                self.show_message_window("Ошибка", "Символ ' нельзя использовать в поле ввода")
                return
            
        if not full_person_name:
            self.show_message_window("Ошибка", "Введите имя пациента")
            return
        if (self.exam_personal_data_id_combobox.currentText() and 
                self.__examinations.get_examination_by_person_id_and_examination_datetime(int(self.exam_personal_data_id_combobox.currentText()), self.exam_diagnosis_date_label.text())):
            self.show_message_window("Ошибка", "У данного человека уже есть запись в текущее время")
            return
        if self.__settings.ack_save_examination:
            ack_accepted = self.show_acknowledge_window("Examination", "Save")
            if ack_accepted == QtWidgets.QDialog.Rejected:
                return
        examination_data = self.gather_examination_data()
        self.__examinations.add_examination(*list(examination_data.values()))
        self.update_all_frames_with_data()

    def erase_examination(self):
        if self.__settings.ack_erase_examination:
            ack_accepted = self.show_acknowledge_window("Examination", "Erase")
            if ack_accepted == QtWidgets.QDialog.Rejected:
                return
        self.set_default_examination()
        self.exam_reset_exam_data_button.setText("Заполнить")

    def update_examination(self, examination_id: int, person_id: int):
        parameters = ["eye_position", "oi", "eyelid", "lacrimal_organs", "conjunctiva", "discharge",
                  "iris", "anterior_chamber", "refractive_medium", "optic_disk",
                  "vessels", "macular_reflex", "visible_periphery", "diagnosis", "icd_code"] ### Here is only line edits!!!
        for eye in ["od", "os"]:
            for field in parameters:
                if "'" in self.change_data_objective_values[eye][eye+"_"+field]:
                    self.show_message_window("Ошибка", "Символ ' нельзя использовать в поле ввода")
                    return
        for text_field in [self.change_data_diagnosis_subscription_text_edit.toPlainText(), self.change_data_recommendations_recommendations_text_edit.toPlainText(), self.change_data_common_complaints_line_edit.text(),
                           self.change_data_common_disease_anamnesis_line_edit.text(), self.change_data_common_life_anamnesis_line_edit.text(), self.change_data_common_eyesight_type_line_edit.text(), self.change_data_common_schober_test_line_edit.text(),
                           self.change_data_common_pupils_line_edit.text()]:
            if "'" in text_field:
                self.show_message_window("Ошибка", "Символ ' нельзя использовать в поле ввода")
                return
            
        if not person_id or not examination_id:
            self.show_message_window("Ошибка", "Выберите пациента")
            return
        if self.__settings.ack_save_change_data:
            ack_accepted = self.show_acknowledge_window("Change", "Save")
            if ack_accepted == QtWidgets.QDialog.Rejected:
                return

        self.__examinations.update_examination(int(examination_id), person_id, *list(self.gather_change_data_data().values()))
        self.update_all_frames_with_data()

    def delete_examination(self, person_id, datetime):
        if not id or not datetime:
            self.show_message_window("Ошибка", "Выберите пациента")
            return
        if self.__settings.ack_delete_change_data:
            ack_accepted = self.show_acknowledge_window("Change", "Delete")
            if ack_accepted == QtWidgets.QDialog.Rejected:
                return
        examination = self.__examinations.get_examination_by_person_id_and_examination_datetime(int(person_id), datetime)
        if not examination:
            self.show_message_window("Ошибка", "Не найден пациент по ID и времени посещения")
            return
        self.__examinations.delete_examination(examination.id, self.__people)
        self.update_all_frames_with_data()
        

    def update_person(self, person_id):
        parameters = ["eye_position", "oi", "eyelid", "lacrimal_organs", "conjunctiva", "discharge",
                  "iris", "anterior_chamber", "refractive_medium", "optic_disk",
                  "vessels", "macular_reflex", "visible_periphery", "diagnosis", "icd_code"] ### Here is only line edits!!!
        
        for eye in ["od", "os"]:
            for field in parameters:
                if "'" in self.exam_objective_values[eye][eye+"_"+field]:
                    self.show_message_window("Ошибка", "Символ ' нельзя использовать в поле ввода")
                    return
        if "'" in self.change_person_name_of_patient_line_edit.text():
            self.show_message_window("Ошибка", "Символ ' нельзя использовать в поле ввода")
            return
        if not person_id:
            self.show_message_window("Ошибка", "Выберите пациента")
            return
        if self.__settings.ack_delete_change_data:
            ack_accepted = self.show_acknowledge_window("Person", "Save")
            if ack_accepted == QtWidgets.QDialog.Rejected:
                return
        self.__people.update_person_data(int(person_id), self.change_person_name_of_patient_line_edit.text(), self.change_person_birthdate_date_edit.text())
        self.update_all_frames_with_data()
        

    def delete_person(self, person_id):
        if not person_id:
            self.show_message_window("Ошибка", "Выберите пациента")
            return
        if self.__settings.ack_delete_change_data:
            ack_accepted = self.show_acknowledge_window("Person", "Delete")
            if ack_accepted == QtWidgets.QDialog.Rejected:
                return
        self.__people.delete_person(int(person_id))
        self.change_person_search_for_name_of_patient_line_edit.clear()
        self.update_all_frames_with_data()
        self.change_data_search_for_name_completer.setModel(None)
        self.change_person_search_for_name_completer.setModel(None)
        

    def set_default_examination(self):
        self.exam_misc_examination_templates_OD_combobox.setCurrentIndex(0)
        self.exam_misc_examination_templates_OS_combobox.setCurrentIndex(0)

        self.exam_eyesight_visual_acuity_without_OD_box.setValue(1.0)
        self.exam_eyesight_visual_acuity_without_OS_box.setValue(1.0)

        self.exam_eyesight_visual_acuity_with_OD_box.setValue(1.0)
        self.exam_eyesight_visual_acuity_with_OD_sph_box.setValue(0)
        self.exam_eyesight_visual_acuity_with_OD_cyl_box.setValue(0)
        self.exam_eyesight_visual_acuity_with_OD_ax_box.setValue(0)

        self.exam_eyesight_visual_acuity_with_OS_box.setValue(1.0)
        self.exam_eyesight_visual_acuity_with_OS_sph_box.setValue(0)
        self.exam_eyesight_visual_acuity_with_OS_cyl_box.setValue(0)
        self.exam_eyesight_visual_acuity_with_OS_ax_box.setValue(0)

        self.exam_eyesight_schiascopy_OD_line_edit.clear()

        self.exam_eyesight_schiascopy_OS_line_edit.clear()

        self.exam_glasses_OD_sph_box.setValue(0)
        self.exam_glasses_OD_cyl_box.setValue(0)
        self.exam_glasses_OD_ax_box.setValue(0)

        self.exam_glasses_OS_sph_box.setValue(0)
        self.exam_glasses_OS_cyl_box.setValue(0)
        self.exam_glasses_OS_ax_box.setValue(0)

        self.exam_glasses_dpp_box.setValue(0)

        self.exam_diagnosis_subscription_text_edit.clear()

        self.exam_common_complaints_line_edit.clear()
        self.exam_common_disease_anamnesis_line_edit.clear()
        self.exam_common_life_anamnesis_line_edit.clear()
        self.exam_common_eyesight_type_line_edit.clear()
        self.exam_common_relative_accommodation_reserve_box.setValue(-1)
        self.exam_common_schober_test_line_edit.clear()
        self.exam_common_pupils_line_edit.clear()
        
        parameters = ["eye_position", "oi", "eyelid", "lacrimal_organs", "conjunctiva", "discharge",
                    "iris", "anterior_chamber", "refractive_medium", "optic_disk",
                    "vessels", "macular_reflex", "visible_periphery", "diagnosis", "icd_code"]
        
        for eye in range(2):
            self.exam_objective_eye_combobox.setCurrentIndex(eye)
            for field in parameters:
                getattr(self, f"exam_objective_{field}_line_edit").setText("")
        self.exam_objective_eye_combobox.setCurrentIndex(0)

        self.exam_recommendations_recommendations_text_edit.setPlainText("")
        self.exam_recommendations_direction_to_aokb_checkbox.setChecked(False)
        self.exam_recommendations_reappointment_checkbox.setChecked(False)
        self.exam_recommendations_reappointment_time_line_edit.setText("")

    def set_default_change_data(self):
        self.change_data_eyesight_visual_acuity_without_OD_box.setValue(1.0)
        self.change_data_eyesight_visual_acuity_without_OS_box.setValue(1.0)

        self.change_data_eyesight_visual_acuity_with_OD_box.setValue(1.0)
        self.change_data_eyesight_visual_acuity_with_OD_sph_box.setValue(0)
        self.change_data_eyesight_visual_acuity_with_OD_cyl_box.setValue(0)
        self.change_data_eyesight_visual_acuity_with_OD_ax_box.setValue(90)
        
        self.change_data_eyesight_visual_acuity_with_OS_box.setValue(1.0)
        self.change_data_eyesight_visual_acuity_with_OS_sph_box.setValue(0)
        self.change_data_eyesight_visual_acuity_with_OS_cyl_box.setValue(0)
        self.change_data_eyesight_visual_acuity_with_OS_ax_box.setValue(90)

        self.change_data_eyesight_schiascopy_OD_line_edit.clear()
        self.change_data_eyesight_schiascopy_OS_line_edit.clear()
        
        self.change_data_glasses_OD_sph_box.setValue(0)
        self.change_data_glasses_OD_cyl_box.setValue(0)
        self.change_data_glasses_OD_ax_box.setValue(90)

        self.change_data_glasses_OS_sph_box.setValue(0)
        self.change_data_glasses_OS_cyl_box.setValue(0)
        self.change_data_glasses_OS_ax_box.setValue(90)
        
        self.change_data_glasses_dpp_box.setValue(0)

        self.change_data_diagnosis_subscription_text_edit.clear()
        
        self.change_data_diagnosis_date_label.setText('')
        
        self.change_data_common_complaints_line_edit.clear()
        self.change_data_common_disease_anamnesis_line_edit.clear()
        self.change_data_common_life_anamnesis_line_edit.clear()
        self.change_data_common_eyesight_type_line_edit.clear()
        self.change_data_common_relative_accommodation_reserve_box.setValue(-1)
        self.change_data_common_schober_test_line_edit.clear()
        self.change_data_common_pupils_line_edit.clear()

        parameters = ["eye_position", "oi", "eyelid", "lacrimal_organs", "conjunctiva", "discharge",
                  "iris", "anterior_chamber", "refractive_medium", "optic_disk",
                  "vessels", "macular_reflex", "visible_periphery", "diagnosis", "icd_code"]
        
        for eye in range(2):
            self.change_data_objective_eye_combobox.setCurrentIndex(eye)
            for field in parameters:
                getattr(self, f"change_data_objective_{field}_line_edit").setText("")
        self.change_data_objective_eye_combobox.setCurrentIndex(0)
        
        self.change_data_recommendations_recommendations_text_edit.setPlainText("")
        self.change_data_recommendations_direction_to_aokb_checkbox.setChecked(False)
        self.change_data_recommendations_reappointment_checkbox.setChecked(False)
        self.change_data_recommendations_reappointment_time_line_edit.setText("")
        self.remove_all_values_from_change_data()


    def remove_all_values_from_change_data(self):
        self.change_data_eyesight_visual_acuity_without_OD_box.clear()
        self.change_data_eyesight_visual_acuity_without_OS_box.clear()
        self.change_data_eyesight_visual_acuity_with_OD_box.clear()
        self.change_data_eyesight_visual_acuity_with_OD_sph_box.clear()
        self.change_data_eyesight_visual_acuity_with_OD_cyl_box.clear()
        self.change_data_eyesight_visual_acuity_with_OD_ax_box.clear()
        self.change_data_eyesight_visual_acuity_with_OS_box.clear()
        self.change_data_eyesight_visual_acuity_with_OS_sph_box.clear()
        self.change_data_eyesight_visual_acuity_with_OS_cyl_box.clear()
        self.change_data_eyesight_visual_acuity_with_OS_ax_box.clear()

        self.change_data_eyesight_schiascopy_OD_line_edit.clear()
        self.change_data_eyesight_schiascopy_OS_line_edit.clear()
        
        self.change_data_glasses_OD_sph_box.clear()
        self.change_data_glasses_OD_cyl_box.clear()
        self.change_data_glasses_OD_ax_box.clear()

        self.change_data_glasses_OS_sph_box.clear()
        self.change_data_glasses_OS_cyl_box.clear()
        self.change_data_glasses_OS_ax_box.clear()
        
        self.change_data_glasses_dpp_box.clear()

        self.change_data_diagnosis_subscription_text_edit.clear()

    def set_change_data_personal_data_by_name(self, name: str):
        if not name:
            self.change_data_date_of_examination_combobox.clear()
            self.change_data_birthdate_date_edit.setDate(QtCore.QDate(self.default_data['birthdate'][2], self.default_data['birthdate'][1], self.default_data['birthdate'][0]))
            self.change_data_id_combobox.clear()
            return
        data = self.__people.search(name=name)
        ids = self.__examinations.get_people_ids()
        data = list(filter(lambda x: x.id in ids, data))
        if data:
            self.change_data_id_combobox.currentIndexChanged.disconnect()
            self.change_data_id_combobox.clear()
            self.change_data_date_of_examination_combobox.clear()
            birthdate = data[0].birthdate
            year, month, day = birthdate.split('.')[2], birthdate.split('.')[1], birthdate.split('.')[0]
            id = list(map(lambda x: str(x.id), data))
            self.change_data_id_combobox.addItems(id)
            full_name = list(map(lambda x: x.full_name, data))
            examinations = self.__examinations.get_examinations_by_person_id(int(id[0]))
            self.change_data_date_of_examination_combobox.addItems(list(map(lambda x: str(x.visit_date), examinations)))

            self.change_data_birthdate_date_edit.setDate(QtCore.QDate(int(year), int(month), int(day)))
            self.change_data_search_for_name_completer.setModel(QtCore.QStringListModel(full_name))
            self.change_data_id_combobox.currentIndexChanged.connect(lambda: self.set_change_data_personal_data_by_id(self.change_data_id_combobox.currentText()))

        else:
            self.change_data_date_of_examination_combobox.clear()
            self.change_data_birthdate_date_edit.setDate(QtCore.QDate(self.default_data['birthdate'][2], self.default_data['birthdate'][1], self.default_data['birthdate'][0]))
            self.change_data_id_combobox.clear()

    def set_change_data_personal_data_by_id(self, person_id):
        if person_id:
            data = self.__people.search(id=int(person_id))
            birthdate = data.birthdate
            year, month, day = birthdate.split('.')[2], birthdate.split('.')[1], birthdate.split('.')[0]
            self.change_data_birthdate_date_edit.setDate(QtCore.QDate(int(year), int(month), int(day)))
            self.change_data_search_for_name_of_patient_line_edit.setText(data.full_name)
            examinations = self.__examinations.get_examinations_by_person_id(int(person_id))
            self.change_data_date_of_examination_combobox.clear()
            self.change_data_date_of_examination_combobox.addItems(list(map(lambda x: x.visit_date, examinations)))

    def set_change_data_examination_data(self, examination_timedate):
        def check_actual_id_and_update_examination(examination):
            examination_id = self.__examinations.get_examination_by_person_id_and_examination_datetime(examination.person_id, self.change_data_date_of_examination_combobox.currentText())
            if examination_id:
                self.update_examination(examination_id.id, examination.person_id)
            else:
                self.show_message_window("Ошибка", "Не найдено записей")

        examination = self.__examinations.get_examination_by_person_id_and_examination_datetime(self.change_data_id_combobox.currentText(), examination_timedate)
        if not examination:
            self.set_default_change_data()
            return

        self.change_data_save_button.clicked.disconnect()
        self.change_data_save_button.clicked.connect(lambda: check_actual_id_and_update_examination(examination))

        self.change_data_eyesight_visual_acuity_without_OD_box.setValue(examination.eyesight_without_od)
        self.change_data_eyesight_visual_acuity_without_OS_box.setValue(examination.eyesight_without_os)
        
        self.change_data_eyesight_visual_acuity_with_OD_box.setValue(examination.eyesight_with_od)
        self.change_data_eyesight_visual_acuity_with_OD_sph_box.setValue(examination.eyesight_with_od_sph)
        self.change_data_eyesight_visual_acuity_with_OD_cyl_box.setValue(examination.eyesight_with_od_cyl)
        self.change_data_eyesight_visual_acuity_with_OD_ax_box.setValue(examination.eyesight_with_od_ax)
        
        self.change_data_eyesight_visual_acuity_with_OS_box.setValue(examination.eyesight_with_os)
        self.change_data_eyesight_visual_acuity_with_OS_sph_box.setValue(examination.eyesight_with_os_sph)
        self.change_data_eyesight_visual_acuity_with_OS_cyl_box.setValue(examination.eyesight_with_os_cyl)
        self.change_data_eyesight_visual_acuity_with_OS_ax_box.setValue(examination.eyesight_with_os_ax)

        self.change_data_eyesight_schiascopy_OD_line_edit.setText(examination.schiascopy_od)

        self.change_data_eyesight_schiascopy_OS_line_edit.setText(examination.schiascopy_os)

        self.change_data_glasses_OD_sph_box.setValue(examination.glasses_od_sph)
        self.change_data_glasses_OD_cyl_box.setValue(examination.glasses_od_cyl)
        self.change_data_glasses_OD_ax_box.setValue(examination.glasses_od_ax)

        self.change_data_glasses_OS_sph_box.setValue(examination.glasses_os_sph)
        self.change_data_glasses_OS_cyl_box.setValue(examination.glasses_os_cyl)
        self.change_data_glasses_OS_ax_box.setValue(examination.glasses_os_ax)

        self.change_data_glasses_dpp_box.setValue(examination.glasses_dpp)

        self.change_data_diagnosis_subscription_text_edit.setPlainText(examination.diagnosis_subscription)

        self.change_data_diagnosis_date_label.setText(examination.visit_date)

        self.change_data_common_complaints_line_edit.setText(examination.complaints)
        self.change_data_common_disease_anamnesis_line_edit.setText(examination.disease_anamnesis)
        self.change_data_common_life_anamnesis_line_edit.setText(examination.life_anamnesis)
        self.change_data_common_eyesight_type_line_edit.setText(examination.eyesight_type)
        self.change_data_common_relative_accommodation_reserve_box.setValue(examination.relative_accommodation_reserve)
        self.change_data_common_schober_test_line_edit.setText(examination.schober_test)
        self.change_data_common_pupils_line_edit.setText(examination.pupils)

        parameters = ["eye_position", "oi", "eyelid", "lacrimal_organs", "conjunctiva", "discharge",
                    "iris", "anterior_chamber", "refractive_medium", "optic_disk",
                    "vessels", "macular_reflex", "visible_periphery", "diagnosis", "icd_code"]

        for eye in range(2):
            self.change_data_objective_eye_combobox.setCurrentIndex(eye)
            eye = ["od", "os"][eye]
            for field in parameters:
                current_value = getattr(examination, eye+'_'+field)
                getattr(self, f"change_data_objective_{field}_line_edit").setText(current_value)
        self.change_data_objective_eye_combobox.setCurrentIndex(0)

        self.change_data_recommendations_recommendations_text_edit.setPlainText(examination.recommendations)
        self.change_data_recommendations_direction_to_aokb_checkbox.setChecked(bool(examination.direction_to_aokb))
        self.change_data_recommendations_reappointment_checkbox.setChecked(bool(examination.reappointment))
        self.change_data_recommendations_reappointment_time_line_edit.setText(examination.reappointment_time)


    def set_change_person_data_by_name(self, name):
        if not name:
            self.change_person_set_id_label.setText("")
            self.change_person_id_combobox.clear()
            self.change_person_name_of_patient_line_edit.clear()
            self.change_person_birthdate_date_edit.setDate(QtCore.QDate(self.default_data['birthdate'][2], self.default_data['birthdate'][1], self.default_data['birthdate'][0]))
            return
        
        self.change_person_id_combobox.clear()
        data = self.__people.search(name=name)
        
        if not data:
            self.change_person_set_id_label.setText("")
            self.change_person_id_combobox.clear()
            self.change_person_name_of_patient_line_edit.clear()
            self.change_person_birthdate_date_edit.setDate(QtCore.QDate(self.default_data['birthdate'][2], self.default_data['birthdate'][1], self.default_data['birthdate'][0]))
            return
        
        self.change_person_id_combobox.currentIndexChanged.disconnect()
        for person in data:
            self.change_person_id_combobox.addItem(str(person.id))
        self.change_person_id_combobox.currentIndexChanged.connect(lambda: self.set_change_person_by_id(self.change_person_id_combobox.currentText()))

        self.change_person_search_for_name_completer.setModel(QtCore.QStringListModel(list(map(lambda x: x.full_name, data))))
        self.change_person_id_combobox.setCurrentIndex(0)
        self.change_person_name_of_patient_line_edit.setText(data[0].full_name)
        birthdate = data[0].birthdate
        year, month, day = birthdate.split('.')[2], birthdate.split('.')[1], birthdate.split('.')[0]
        self.change_person_birthdate_date_edit.setDate(QtCore.QDate(int(year), int(month), int(day)))
        self.change_person_set_id_label.setText(str(data[0].id))

    def set_change_person_by_id(self, id):
        if not id:
            return
        data = self.__people.search(id=int(id))
        if not data:
            return
        self.change_person_name_of_patient_line_edit.setText(data.full_name)
        birthdate = data.birthdate
        year, month, day = birthdate.split('.')[2], birthdate.split('.')[1], birthdate.split('.')[0]
        self.change_person_birthdate_date_edit.setDate(QtCore.QDate(int(year), int(month), int(day)))
        self.change_person_set_id_label.setText(str(data.id))

    def set_print_personal_data_by_id(self, person_id):
        if person_id:
            data = self.__people.search(id=int(person_id))
            birthdate = data.birthdate
            year, month, day = birthdate.split('.')[2], birthdate.split('.')[1], birthdate.split('.')[0]
            self.print_birthdate_date_edit.setDate(QtCore.QDate(int(year), int(month), int(day)))
            self.print_search_for_name_of_patient_line_edit.setText(data.full_name)
            examinations = self.__examinations.get_examinations_by_person_id(int(person_id))
            self.print_date_of_examination_combobox.clear()
            self.print_date_of_examination_combobox.addItems(list(map(lambda x: x.visit_date, examinations)))

    def set_default_print(self):
        self.print_eyesight_visual_acuity_without_OD_box.setValue(1.0)
        self.print_eyesight_visual_acuity_without_OS_box.setValue(1.0)

        self.print_eyesight_visual_acuity_with_OD_box.setValue(1.0)
        self.print_eyesight_visual_acuity_with_OD_sph_box.setValue(0)
        self.print_eyesight_visual_acuity_with_OD_cyl_box.setValue(0)
        self.print_eyesight_visual_acuity_with_OD_ax_box.setValue(90)
        
        self.print_eyesight_visual_acuity_with_OS_box.setValue(1.0)
        self.print_eyesight_visual_acuity_with_OS_sph_box.setValue(0)
        self.print_eyesight_visual_acuity_with_OS_cyl_box.setValue(0)
        self.print_eyesight_visual_acuity_with_OS_ax_box.setValue(90)

        self.print_eyesight_schiascopy_OD_line_edit.clear()
        self.print_eyesight_schiascopy_OS_line_edit.clear()
        
        self.print_glasses_OD_sph_box.setValue(0)
        self.print_glasses_OD_cyl_box.setValue(0)
        self.print_glasses_OD_ax_box.setValue(90)

        self.print_glasses_OS_sph_box.setValue(0)
        self.print_glasses_OS_cyl_box.setValue(0)
        self.print_glasses_OS_ax_box.setValue(90)
        
        self.print_glasses_dpp_box.setValue(0)

        self.print_diagnosis_subscription_text_edit.clear()
        
        self.print_diagnosis_date_label.setText('')

        self.print_common_complaints_line_edit.clear()
        self.print_common_disease_anamnesis_line_edit.clear()
        self.print_common_life_anamnesis_line_edit.clear()
        self.print_common_eyesight_type_line_edit.clear()
        self.print_common_relative_accommodation_reserve_box.setValue(-1)
        self.print_common_schober_test_line_edit.clear()
        self.print_common_pupils_line_edit.clear()

        parameters = ["eye_position", "oi", "eyelid", "lacrimal_organs", "conjunctiva", "discharge",
                  "iris", "anterior_chamber", "refractive_medium", "optic_disk",
                  "vessels", "macular_reflex", "visible_periphery", "diagnosis", "icd_code"]
        
        for eye in range(2):
            self.print_objective_eye_combobox.setCurrentIndex(eye)
            for field in parameters:
                getattr(self, f"print_objective_{field}_line_edit").setText("")
        self.print_objective_eye_combobox.setCurrentIndex(0)
        
        self.print_recommendations_recommendations_text_edit.setPlainText("")
        self.print_recommendations_direction_to_aokb_checkbox.setChecked(False)
        self.print_recommendations_reappointment_checkbox.setChecked(False)
        self.print_recommendations_reappointment_time_line_edit.setText("")

    def set_print_personal_data_by_name(self, name: str):
        if not name:
            self.set_default_print()
            self.print_date_of_examination_combobox.clear()
            self.print_id_combobox.clear()
            self.print_birthdate_date_edit.setDate(QtCore.QDate(self.default_data['birthdate'][2], self.default_data['birthdate'][1], self.default_data['birthdate'][0]))
            return
        data = self.__people.search(name=name)
        if data:
            self.print_id_combobox.currentIndexChanged.disconnect()
            self.print_id_combobox.clear()
            birthdate = data[0].birthdate
            year, month, day = birthdate.split('.')[2], birthdate.split('.')[1], birthdate.split('.')[0]
            id = list(map(lambda x: str(x.id), data))
            self.print_id_combobox.addItems(id)
            full_name = list(map(lambda x: x.full_name, data))
            self.print_date_of_examination_combobox.clear()
            self.print_date_of_examination_combobox.addItems(list(map(lambda examination: examination.visit_date, self.__examinations.get_examinations_by_person_id(data[0].id))))
            
            self.print_birthdate_date_edit.setDate(QtCore.QDate(int(year), int(month), int(day)))
            self.print_search_for_name_completer.setModel(QtCore.QStringListModel(full_name))
            self.print_id_combobox.currentIndexChanged.connect(lambda: self.set_print_personal_data_by_id(self.print_id_combobox.currentText()))
        else:
            self.set_default_print()
            self.print_date_of_examination_combobox.clear()
            self.print_birthdate_date_edit.setEnabled(True)
            self.print_birthdate_date_edit.setDate(QtCore.QDate(self.default_data['birthdate'][2], self.default_data['birthdate'][1], self.default_data['birthdate'][0]))
            self.print_id_combobox.clear()

    def set_print_examination_data(self, examination_timedate):
        examination = self.__examinations.get_examination_by_person_id_and_examination_datetime(self.print_id_combobox.currentText(), examination_timedate)
        if not examination:
            self.set_default_print()
            return

        self.print_eyesight_visual_acuity_without_OD_box.setValue(examination.eyesight_without_od)
        self.print_eyesight_visual_acuity_without_OS_box.setValue(examination.eyesight_without_os)
        
        self.print_eyesight_visual_acuity_with_OD_box.setValue(examination.eyesight_with_od)
        self.print_eyesight_visual_acuity_with_OD_sph_box.setValue(examination.eyesight_with_od_sph)
        self.print_eyesight_visual_acuity_with_OD_cyl_box.setValue(examination.eyesight_with_od_cyl)
        self.print_eyesight_visual_acuity_with_OD_ax_box.setValue(examination.eyesight_with_od_ax)
        
        self.print_eyesight_visual_acuity_with_OS_box.setValue(examination.eyesight_with_os)
        self.print_eyesight_visual_acuity_with_OS_sph_box.setValue(examination.eyesight_with_os_sph)
        self.print_eyesight_visual_acuity_with_OS_cyl_box.setValue(examination.eyesight_with_os_cyl)
        self.print_eyesight_visual_acuity_with_OS_ax_box.setValue(examination.eyesight_with_os_ax)

        self.print_eyesight_schiascopy_OD_line_edit.setText(examination.schiascopy_od)

        self.print_eyesight_schiascopy_OS_line_edit.setText(examination.schiascopy_os)

        self.print_glasses_OD_sph_box.setValue(examination.glasses_od_sph)
        self.print_glasses_OD_cyl_box.setValue(examination.glasses_od_cyl)
        self.print_glasses_OD_ax_box.setValue(examination.glasses_od_ax)

        self.print_glasses_OS_sph_box.setValue(examination.glasses_os_sph)
        self.print_glasses_OS_cyl_box.setValue(examination.glasses_os_cyl)
        self.print_glasses_OS_ax_box.setValue(examination.glasses_os_ax)

        self.print_glasses_dpp_box.setValue(examination.glasses_dpp)

        self.print_diagnosis_subscription_text_edit.setPlainText(examination.diagnosis_subscription)

        self.print_diagnosis_date_label.setText(examination.visit_date)

        self.print_common_complaints_line_edit.setText(examination.complaints)
        self.print_common_disease_anamnesis_line_edit.setText(examination.disease_anamnesis)
        self.print_common_life_anamnesis_line_edit.setText(examination.life_anamnesis)
        self.print_common_eyesight_type_line_edit.setText(examination.eyesight_type)
        self.print_common_relative_accommodation_reserve_box.setValue(examination.relative_accommodation_reserve)
        self.print_common_schober_test_line_edit.setText(examination.schober_test)
        self.print_common_pupils_line_edit.setText(examination.pupils)


        parameters = ["eye_position", "oi", "eyelid", "lacrimal_organs", "conjunctiva", "discharge",
                    "iris", "anterior_chamber", "refractive_medium", "optic_disk",
                    "vessels", "macular_reflex", "visible_periphery", "diagnosis", "icd_code"]

        for eye in range(2):
            self.print_objective_eye_combobox.setCurrentIndex(eye)
            eye = ["od", "os"][eye]
            for field in parameters:
                current_value = getattr(examination, eye+'_'+field)
                getattr(self, f"print_objective_{field}_line_edit").setText(current_value)
        self.print_objective_eye_combobox.setCurrentIndex(0)
        
        self.print_recommendations_recommendations_text_edit.setPlainText(examination.recommendations)
        self.print_recommendations_direction_to_aokb_checkbox.setChecked(bool(examination.direction_to_aokb))
        self.print_recommendations_reappointment_checkbox.setChecked(bool(examination.reappointment))
        self.print_recommendations_reappointment_time_line_edit.setText(examination.reappointment_time)

    def fill_search_table(self, id: int = None, name: str = None, all: bool = False):
        self.search_for_patient_table.clear()
        self.search_for_patient_table.setRowCount(0)
        self.search_for_patient_table.setHorizontalHeaderLabels(["ID", "Пациент", "Дата рождения", "ID осмотра", "Дата осмотра"])
        if all:
            data = self.__people.get_all()
            self.search_for_patient_id_combobox.disconnect()
            self.search_for_patient_id_combobox.clear()
            self.search_for_patient_id_combobox.currentIndexChanged.connect(lambda: self.fill_search_table(id=int(self.search_for_patient_id_combobox.currentText())))
        elif id:
            data = [self.__people.search(id=id)]
        elif name:
            data = self.__people.search(name=name)
        else:
            data = self.__people.get_all()
            self.search_for_patient_id_combobox.disconnect()
            self.search_for_patient_id_combobox.clear()
            self.search_for_patient_id_combobox.currentIndexChanged.connect(lambda: self.fill_search_table(id=int(self.search_for_patient_id_combobox.currentText())))
        if not data:
            self.search_for_patient_id_combobox.disconnect()
            self.search_for_patient_id_combobox.clear()
            self.search_for_patient_id_combobox.currentIndexChanged.connect(lambda: self.fill_search_table(id=int(self.search_for_patient_id_combobox.currentText())))
            return
        names = list(map(lambda x: x.full_name, data))
        self.search_for_patient_completer.setModel(QtCore.QStringListModel(names))
        person_id = list(map(lambda person: str(person.id), data))
        if name:
            self.search_for_patient_id_combobox.disconnect()
            self.search_for_patient_id_combobox.clear()
            self.search_for_patient_id_combobox.addItems(person_id)
            self.search_for_patient_id_combobox.currentIndexChanged.connect(lambda: self.fill_search_table(id=int(self.search_for_patient_id_combobox.currentText())))
        if len(set(names)) == 1 and len(names) != 1:
            data = [self.__people.search(id=int(self.search_for_patient_id_combobox.currentText()))]
            person_id = list(map(lambda person: person.id, data))
        examinations = self.__examinations.get_examinations_by_person_id(person_id)[:self.__settings.number_of_visible_records]
        self.search_for_patient_table.setRowCount(len(examinations))
        row = 0
        for examination in examinations:
            person = self.__people.search(id=examination.person_id)
            self.search_for_patient_table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(person.id)))
            self.search_for_patient_table.setItem(row, 1, QtWidgets.QTableWidgetItem(person.full_name))
            self.search_for_patient_table.setItem(row, 2, QtWidgets.QTableWidgetItem(person.birthdate))
            self.search_for_patient_table.setItem(row, 3, QtWidgets.QTableWidgetItem(str(examination.id)))
            self.search_for_patient_table.setItem(row, 4, QtWidgets.QTableWidgetItem(examination.visit_date))
            
            self.search_for_patient_table.item(row, 0).setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.search_for_patient_table.item(row, 1).setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.search_for_patient_table.item(row, 2).setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.search_for_patient_table.item(row, 3).setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.search_for_patient_table.item(row, 4).setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            row += 1
        

    def print_document(self, preview=False, show_in_word=False):
        self.show_message_window("Низя", "На линухе низя-низя")
        return
        def preview_doc(printer):
            doc = None#fitz_open("print/current.pdf")
            page = doc.load_page(0)
            pix = page.get_pixmap(dpi=600)

            imgData = pix.samples
            imgFormat = QtGui.QImage.Format_RGB888
            doc.close()

            img = QtGui.QImage(imgData, pix.width, pix.height, pix.stride, imgFormat)
            pixmap = QtGui.QPixmap.fromImage(img)

            painter = QtGui.QPainter(printer)
            painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
            painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)
            painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
            painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing, True)
            rect = printer.pageRect()
            painter.drawPixmap(rect.topLeft(), pixmap.scaled(rect.size(), QtCore.Qt.KeepAspectRatio))
            painter.end()

        data = self.gather_print_data()
        data["direction"] = "Дано направление в АОКБ" if data["direction"] else ""
        data["reappointment_time"] = "Повторная явка " + data["reappointment_time"] if data['reappointment'] else ''
        data["eyesight_with_od_ax"] = int(data["eyesight_with_od_ax"])
        data["eyesight_with_os_ax"] = int(data["eyesight_with_os_ax"])
        data["glasses_od_ax"] = int(data["glasses_od_ax"])
        data["glasses_os_ax"] = int(data["glasses_os_ax"])
        data["diagnosis"] = data["od_diagnosis"] + " (OD), " + data["os_diagnosis"] + " (OS)" if data["os_diagnosis"] != data["od_diagnosis"] else data["od_diagnosis"] + " (OU)"
        data["diagnosis_code"] = f"{data['od_icd_code']} (OD), {data['os_icd_code']} (OS)" if data['od_icd_code'] != data['os_icd_code'] else data['od_icd_code']

        od_objective = f"Положение глаза: {self.print_objective_values['od']['od_eye_position']}; ОИ: {self.print_objective_values['od']['od_oi']}; веко: {self.print_objective_values['od']['od_eyelid']}; слёзные органы: {self.print_objective_values['od']['od_lacrimal_organs']}; конъюнктива: {self.print_objective_values['od']['od_conjunctiva']}; отделяемое: {self.print_objective_values['od']['od_discharge']}; радужка: {self.print_objective_values['od']['od_iris']}; передняя камера: {self.print_objective_values['od']['od_anterior_chamber']}; преломляющие среды: {self.print_objective_values['od']['od_refractive_medium']}; ДЗН: {self.print_objective_values['od']['od_optic_disk']}; сосуды: {self.print_objective_values['od']['od_vessels']}; макулярный рефлекс: {self.print_objective_values['od']['od_macular_reflex']}; видимая периферия: {self.print_objective_values['od']['od_visible_periphery']}."
        os_objective = f"Положение глаза: {self.print_objective_values['os']['os_eye_position']}; ОИ: {self.print_objective_values['os']['os_oi']}; веко: {self.print_objective_values['os']['os_eyelid']}; слёзные органы: {self.print_objective_values['os']['os_lacrimal_organs']}; конъюнктива: {self.print_objective_values['os']['os_conjunctiva']}; отделяемое: {self.print_objective_values['os']['os_discharge']}; радужка: {self.print_objective_values['os']['os_iris']}; передняя камера: {self.print_objective_values['os']['os_anterior_chamber']}; преломляющие среды: {self.print_objective_values['os']['os_refractive_medium']}; ДЗН: {self.print_objective_values['os']['os_optic_disk']}; сосуды: {self.print_objective_values['os']['os_vessels']}; макулярный рефлекс: {self.print_objective_values['os']['os_macular_reflex']}; видимая периферия: {self.print_objective_values['os']['os_visible_periphery']}."

        data["glasses"] = f"Sph: {data['glasses_od_sph'] if data['glasses_od_sph'] <= 0 else '+' + str(data['glasses_od_sph'])}; Cyl: {data['glasses_od_cyl'] if data['glasses_od_cyl'] <= 0 else '+' + str(data['glasses_od_cyl'])}; Ax: {data['glasses_od_ax']}; Sph: {data['glasses_os_sph'] if data['glasses_os_sph'] <= 0 else '+' + str(data['glasses_os_sph'])}; Cyl: {data['glasses_os_cyl'] if data['glasses_os_cyl'] <= 0 else '+' + str(data['glasses_os_cyl'])}; Ax: {data['glasses_os_ax']}; DPP: {data['glasses_dpp']}"
        if not (data['glasses_od_sph'] or data['glasses_od_cyl'] or data['glasses_od_ax'] or data['glasses_os_sph'] or data['glasses_os_cyl'] or data['glasses_os_ax']):
            data["glasses"] = ""

        if not data["glasses_od_sph"] and not data["glasses_os_sph"] and not data["glasses_od_cyl"] and not data["glasses_os_cyl"]:
            data["glasses_od_sph"], data["glasses_os_sph"], data["glasses_od_cyl"], data["glasses_os_cyl"], data["glasses_od_ax"], data["glasses_os_ax"], data["glasses_dpp"] = ("–")*7
        replace_values = {
                    'v-od': 'eyesight_without_od',
                    'v-os': 'eyesight_without_os',
                    'cor-d': 'eyesight_with_od',
                    's-d': 'eyesight_with_od_sph',
                    'c-d': 'eyesight_with_od_cyl',
                    'a-d': 'eyesight_with_od_ax',
                    'cor-s': 'eyesight_with_os',
                    's-s': 'eyesight_with_os_sph',
                    'c-s': 'eyesight_with_os_cyl',
                    'a-s': 'eyesight_with_os_ax',
                    'sdu': 'schiascopy_od',
                    'ssu': 'schiascopy_os',
                    'gsd': 'glasses_od_sph',
                    'gcd': 'glasses_od_cyl',
                    'gad': 'glasses_od_ax',
                    'gss': 'glasses_os_sph',
                    'gcs': 'glasses_os_cyl',
                    'gas': 'glasses_os_ax',
                    'gdp': 'glasses_dpp',
                    'eyesight-type': 'eyesight_type',
                    'eye-position-od': 'od_eye_position',
                    'oi': 'od_oi',
                    'eyelid-od': 'od_eyelid',
                    'lacrimal-organs-od': 'od_lacrimal_organs',
                    'conjunctiva-od': 'od_conjunctiva',
                    'discharge-od': 'od_discharge',
                    'iris-od': 'od_iris',
                    'anterior-chamber-od': 'od_anterior_chamber',
                    'refractive-medium-od': 'od_refractive_medium',
                    'optic-disk-od': 'od_optic_disk',
                    'vessels-od': 'od_vessels',
                    'macular-reflex-od': 'od_macular_reflex',
                    'visible-periphery-od': 'od_visible_periphery',
                    'eye-position-os': 'os_eye_position',
                    'oi': 'os_oi',
                    'eyelid-os': 'os_eyelid',
                    'lacrimal-organs-os': 'os_lacrimal_organs',
                    'conjunctiva-os': 'os_conjunctiva',
                    'discharge-os': 'os_discharge',
                    'iris-os': 'os_iris',
                    'anterior-chamber-os': 'os_anterior_chamber',
                    'refractive-medium-os': 'os_refractive_medium',
                    'optic-disk-os': 'os_optic_disk',
                    'vessels-os': 'os_vessels',
                    'macular-reflex-os': 'os_macular_reflex',
                    'visible-periphery-os': 'os_visible_periphery',
                    'diagnosis': 'diagnosis',
                    'recommendations': 'recommendations',
                    'reappointment': 'reappointment_time',
                    'patient-name': 'patient_name',
                    'patient-age': 'patient_age',
                    'date': 'date',
                    'direction': 'direction',
                    'patient-complaints': 'complaints'
                }
        replace_values = {
                    'patient-name': 'patient_name',
                    'patient-age': 'patient_age',
                    'patient-complaints': 'complaints',
                    'disease-anamnesis': 'disease_anamnesis',
                    'life-anamnesis': 'life_anamnesis',
                    'v-od': 'eyesight_without_od',
                    'v-os': 'eyesight_without_os',
                    'cor-d': 'eyesight_with_od',
                    's-d': 'eyesight_with_od_sph',
                    'c-d': 'eyesight_with_od_cyl',
                    'a-d': 'eyesight_with_od_ax',
                    'cor-s': 'eyesight_with_os',
                    's-s': 'eyesight_with_os_sph',
                    'c-s': 'eyesight_with_os_cyl',
                    'a-s': 'eyesight_with_os_ax',
                    'sod': 'schiascopy_od',
                    'sos': 'schiascopy_os',
                    'eyesight-type': 'eyesight_type',
                    'rel-acc-reserve': 'relative_accommodation_reserve',
                    'schober-test': 'schober_test',
                    'pupils': 'pupils',

                    'icdcode': 'diagnosis_code',
                    
                    'diagnosis': 'diagnosis',
                    'recommendations': 'recommendations',
                    'date': 'date'                    
        }
        with zipfile.ZipFile("print/template.docx", 'r') as zip:
            zip.extractall("print/.current")

        xml_file = "print/.current/word/document.xml"

        tree = etree.parse(xml_file)
        root = tree.getroot()
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

        for elem in root.xpath('.//w:t', namespaces=ns):
            if elem.text in replace_values:
                if "sph" in replace_values[elem.text] or "cyl" in replace_values[elem.text]:
                    if isinstance(data[replace_values[elem.text]], float):
                        if data[replace_values[elem.text]] > 0:
                            data[replace_values[elem.text]] = "+" + str(data[replace_values[elem.text]])
                elem.text = str(data[replace_values[elem.text]])

        tree.write(xml_file, encoding='utf-8', xml_declaration=True)

        try:
            with zipfile.ZipFile("print/current.docx", 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk("print/.current"):
                    for file in files:
                        filepath = root + "/" + file
                        arcname = os.path.relpath(filepath, "print/.current")
                        zipf.write(filepath, arcname)
        except PermissionError:
            self.show_message_window("Ошибка", "Ошибка доступа к документу\nВозможно, он уже открыт в данный момент, и его необходимо закрыть")
            return()
        
        document = None#Document("print/current.docx")
        objective_od_equals_os = od_objective.lower() == os_objective.lower()
        target_text = "od_objective" if not objective_od_equals_os else "os_objective"
        new_paragraph_text = od_objective
        for paragraph in document.paragraphs:
            if (paragraph.text == "Объективно для OD" or paragraph.text == "od_objective")  and objective_od_equals_os:
                p = paragraph._element
                p.getparent().remove(p)
                paragraph._p = paragraph._element = None
                continue
            elif paragraph.text == "Объективно для OS" and objective_od_equals_os:
                paragraph.text = paragraph.text.replace("OS", "OU")
                paragraph.runs[0].bold = True
                paragraph.runs[0].font.size = None#Pt(11)
            elif target_text in paragraph.text:
                paragraph.clear()
                bold_words = list(map(lambda word: word.split("; ")[-1], new_paragraph_text.split(": ")))[:-1]
                values = list(map(lambda word: word.split(": ")[-1], new_paragraph_text.split("; ")))
                for word in range(len(bold_words)):
                    paragraph.add_run(bold_words[word] + ": ")
                    paragraph.runs[-1].bold = True
                    paragraph.add_run(values[word])
                    #paragraph.runs[-1].underline = True #She did not want it
                    if word != len(bold_words) - 1:
                        paragraph.add_run("; ")
                    paragraph.runs[-1].font.size = None#Pt(11)
                    paragraph.runs[-2].font.size = None#Pt(11)
                    paragraph.runs[-3].font.size = None#Pt(11)
                if not objective_od_equals_os:
                    target_text = "os_objective"
                    new_paragraph_text = os_objective
                paragraph.alignment = 0
            elif paragraph.text == "glasses":
                if not data["glasses"]:
                    p = paragraph._element
                    p.getparent().remove(p)
                    paragraph._p = paragraph._element = None
                    continue
                paragraph.clear()

                bold_words = list(map(lambda word: word.split("; ")[-1], data["glasses"].split(": ")))[:-1]
                values = list(map(lambda word: word.split(": ")[-1], data["glasses"].split("; ")))
                paragraph.add_run("Очковая коррекция: ")
                paragraph.runs[-1].font.size = None#Pt(11)
                paragraph.runs[-1].font.bold = True
                for word in range(len(bold_words)):
                    if word == 0:
                        paragraph.add_run("OD ")
                        paragraph.runs[-1].font.size = None#Pt(11)
                    elif word == 3:
                        paragraph.add_run("    OS ")
                        paragraph.runs[-1].font.size = None#Pt(11)
                    paragraph.add_run(bold_words[word])
                    paragraph.runs[-1].bold = True
                    paragraph.add_run(": ")
                    paragraph.add_run(values[word])
                    if word != len(bold_words) - 1:
                        paragraph.add_run("; ")
                    paragraph.runs[-1].font.size = None#Pt(11)
                    paragraph.runs[-2].font.size = None#Pt(11)
                    paragraph.runs[-3].font.size = None#Pt(11)
                    paragraph.runs[-4].font.size = None#Pt(11)
                paragraph.alignment = 0
            elif paragraph.text == "direction":
                if not data["direction"]:
                    p = paragraph._element
                    p.getparent().remove(p)
                    paragraph._p = paragraph._element = None
                    continue
                paragraph.text = paragraph.text.replace("direction", data["direction"])
                paragraph.runs[0].font.size = None#Pt(11)
                paragraph.alignment = 0
            elif paragraph.text == "reappointment":
                if not data["reappointment"]:
                    p = paragraph._element
                    p.getparent().remove(p)
                    paragraph._p = paragraph._element = None
                    continue
                paragraph.text = paragraph.text.replace("reappointment", data["reappointment_time"])
                paragraph.runs[0].font.size = None#Pt(11)
                paragraph.alignment = 0
                break
        document.save("print/current.docx")

        if show_in_word:
            os.startfile("print\current.docx")
            return

        convert_docx_to_pdf(os.path.abspath("print/current.docx"), os.path.abspath("print/current.pdf"))

        printer = QPrinter(QPrinter.HighResolution)
        if preview:
            preview_dialog = QPrintPreviewDialog(printer, self)
            preview_dialog.paintRequested.connect(lambda: preview_doc(printer))
            preview_dialog.setFixedSize(int(QtWidgets.QApplication.desktop().width()//1.2), int(QtWidgets.QApplication.desktop().height()//1.2))
            preview_dialog.adjustSize()
            preview_dialog.exec_()
            return

        if QPrintDialog(parent=self).exec_():
            doc = None#fitz_open("print/current.pdf")
            page = doc.load_page(0)
            pix = page.get_pixmap(dpi=600)

            imgData = pix.samples
            imgFormat = QtGui.QImage.Format_RGB888

            img = QtGui.QImage(imgData, pix.width, pix.height, pix.stride, imgFormat)
            pixmap = QtGui.QPixmap.fromImage(img)

            painter = QtGui.QPainter(printer)
            rect = printer.pageRect()
            painter.drawPixmap(rect.topLeft(), pixmap.scaled(rect.size(), QtCore.Qt.KeepAspectRatio))
            painter.end()

            doc.close()


class AuthWindow(QtWidgets.QDialog, Ui_AuthWindow):
    def __init__(self, db):
        super().__init__()

        self.setupUi(self)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        self.setWindowIcon(QtGui.QIcon("img/icon.ico"))
        self.setWindowTitle("Crystal - Вход")

        self.launch_close_animation = QtCore.QPropertyAnimation(self, b'windowOpacity', duration=200)

        self.__forbidden = True

        self.mouse_button_pressed = False

        self.passwd_css_normal = """
                                QLineEdit {
                                    border-radius: 10px;
                                    background: #fff5f5;
                                    border: 0px;
                                    border-bottom: 1px solid #999;
                                }

                                QLineEdit:hover {
                                    border-bottom: 1px solid #444;
                                }
                                """
        self.passwd_css_forbidden = """
                                QLineEdit {
                                    border-radius: 10px;
                                    background: #fff5f5;
                                    border: 1px solid red;
                                    border-bottom: 1px solid red;
                                }

                                QLineEdit:hover {
                                    border-bottom: 1px solid red;
                                }
                                """

        self.installEventFilter(self)

        self.avatar_number = datetime.datetime.now().weekday()
        self.avatar_label.setPixmap(QtGui.QPixmap(f'img/avatars/{self.avatar_number}.png'))
        self.avatar_label.mouseReleaseEvent = lambda event: self.change_avatar(event)

        self.ears_down = False
        self.auth_cat_label.mouseReleaseEvent = lambda event: self.set_cats_ears()
        self.left_eye_label.mouseReleaseEvent = lambda event: self.set_cats_ears()
        self.right_eye_label.mouseReleaseEvent = lambda event: self.set_cats_ears()

        self.close_label.mouseEnterEvent = lambda event: self.close_label.setPixmap(QtGui.QPixmap("img/close_enter.png"))
        self.close_label.mouseLeaveEvent = lambda event: self.close_label.setPixmap(QtGui.QPixmap("img/close.png"))
        self.close_label.mouseReleaseEvent = lambda event: self.close_animated()

        self.minimize_label.mouseReleaseEvent = lambda event: self.minimize_animated()

        self.password_line_edit.textChanged.connect(lambda: self.__wait_and_verify(db))
        self.password_line_edit.installEventFilter(self)

        self.center_of_eyes = {'x': 335, 'y': 243}

        self.last_update_time = 0
        self.update_interval = 30

        self.launch_animated()


    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.MouseButtonPress and event.button() == QtCore.Qt.LeftButton:
            self.mouse_button_pressed = True
        elif event.type() == QtCore.QEvent.MouseButtonRelease and event.button() == QtCore.Qt.LeftButton:
            self.mouse_button_pressed = False
        elif event.type() == QtCore.QEvent.MouseMove and self.mouse_button_pressed:
            self.move(self.x()+event.x()-self.last_position_x, self.y()+event.y()-self.last_position_y)

        if event.type() == QtCore.QEvent.KeyPress and event.key() == QtCore.Qt.Key_Escape:
            self.close_animated()
        if event.type() == QtCore.QEvent.MouseMove:
            if not self.mouse_button_pressed:
                self.last_position_x = event.x()
                self.last_position_y = event.y()
            self.move_auth_cat_eyes()
        return super().eventFilter(obj, event)

    def launch_animated(self):
        self.launch_close_animation.setStartValue(0)
        self.launch_close_animation.setEndValue(1)
        self.launch_close_animation.start()

    def close_animated(self):
        self.mouse_button_pressed = False

        self.launch_close_animation.setStartValue(1)
        self.launch_close_animation.setEndValue(0)
        self.launch_close_animation.start()
        self.launch_close_animation.finished.connect(self.close)

    def minimize_animated(self):
        self.mouse_button_pressed = False

        self.launch_close_animation.setStartValue(1)
        self.launch_close_animation.setEndValue(0)
        self.launch_close_animation.start()
        self.launch_close_animation.finished.connect(lambda: (self.showMinimized(), self.setWindowOpacity(1)))

    def __wait_and_verify(self, db):
        self.password_line_edit.setStyleSheet(self.passwd_css_normal)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(lambda: self.__verify_password(db))
        self.timer.start(1500)

    def __verify_password(self, db):
        self.timer.stop()
        from security import Passwd
        if Passwd().verify_password(self.password_line_edit.text(), db):
            self.__forbidden = False
            self.close_animated()
        else:
            self.password_line_edit.setStyleSheet(self.passwd_css_forbidden)

    @property
    def forbidden(self):
        return self.__forbidden
    
    def change_avatar(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.avatar_number += 1
            self.avatar_number %= 7
        elif event.button() == QtCore.Qt.RightButton:
            self.avatar_number -= 1
            self.avatar_number = 6 if self.avatar_number < 0 else self.avatar_number
        self.mouse_button_pressed = False
        self.avatar_label.setPixmap(QtGui.QPixmap(f'img/avatars/{self.avatar_number}.png'))

    def set_cats_ears(self):
        self.mouse_button_pressed = False
        if self.ears_down:
            self.auth_cat_label.setPixmap(QtGui.QPixmap("img/kitty_ears_up.png"))
        else:
            self.auth_cat_label.setPixmap(QtGui.QPixmap("img/kitty_ears_down.png"))
        self.ears_down = not(self.ears_down)

    def move_auth_cat_eyes(self):
        current_time = QtCore.QDateTime.currentMSecsSinceEpoch()
        if current_time - self.last_update_time < self.update_interval:
            return
        else:
            self.last_update_time = current_time

        cursor_pos = self.main_frame.mapFromGlobal(QtGui.QCursor.pos())

        center_left = self.left_eye_label.rect().center()
        center_right = self.right_eye_label.rect().center()

        initial_pos_left = (self.center_of_eyes['x'] + center_left.x() - 9,
                            self.center_of_eyes['y'] + center_left.y())

        new_left_pos = self.calculate_eye_position(initial_pos_left, (cursor_pos.x()+3, cursor_pos.y()), 3)

        initial_pos_right = (self.center_of_eyes['x'] + center_right.x() + 9,
                             self.center_of_eyes['y'] + center_right.y())
        new_right_pos = self.calculate_eye_position(initial_pos_right, (cursor_pos.x()+3, cursor_pos.y()), 3)

        self.left_eye_label.move(int(new_left_pos[0] - self.left_eye_label.width() / 2),
                                 int(new_left_pos[1] - self.left_eye_label.height() / 2))
        self.right_eye_label.move(int(new_right_pos[0] - self.right_eye_label.width() / 2),
                                  int(new_right_pos[1] - self.right_eye_label.height() / 2))

    def calculate_eye_position(self, initial_pos, cursor_pos, max_eye_radius):
        dx = cursor_pos[0] - initial_pos[0]
        dy = cursor_pos[1] - initial_pos[1]
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > max_eye_radius:
            angle = math.atan2(dy, dx)
            dx = math.cos(angle) * max_eye_radius
            dy = math.sin(angle) * max_eye_radius

        return (initial_pos[0] + dx, initial_pos[1] + dy)

class AuthorizationWindow(QtWidgets.QDialog, Ui_AuthorizationWindow):
    def __init__(self, parent, db):
        super().__init__(parent)

        self.setupUi(self)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        self.setWindowIcon(QtGui.QIcon("img/icon.ico"))
        self.setWindowTitle("Crystal")

        self.launch_close_animation = QtCore.QPropertyAnimation(self, b'windowOpacity', duration=200)
        
        self.__forbidden = True

        self.mouse_button_pressed = False

        self.passwd_css_normal = """
                                QLineEdit {
                                    border-radius: 10px;
                                    background: #fff5f5;
                                    border: 0px;
                                    border-bottom: 1px solid #999;
                                }

                                QLineEdit:hover {
                                    border-bottom: 1px solid #444;
                                }
                                """
        self.passwd_css_forbidden = """
                                QLineEdit {
                                    border-radius: 10px;
                                    background: #fff5f5;
                                    border: 1px solid red;
                                    border-bottom: 1px solid red;
                                }

                                QLineEdit:hover {
                                    border-bottom: 1px solid red;
                                }
                                """

        self.installEventFilter(self)

        self.ears_down = False
        self.auth_cat_label.mouseReleaseEvent = lambda event: self.set_cats_ears()
        self.left_eye_label.mouseReleaseEvent = lambda event: self.set_cats_ears()
        self.right_eye_label.mouseReleaseEvent = lambda event: self.set_cats_ears()

        self.exit_pressed = False

        self.close_label.mouseEnterEvent = lambda event: self.close_label.setPixmap(QtGui.QPixmap("img/close_enter.png"))
        self.close_label.mouseLeaveEvent = lambda event: self.close_label.setPixmap(QtGui.QPixmap("img/close.png"))
        self.close_label.mouseReleaseEvent = lambda event: self.close_animated(exit_pressed=True)

        self.password_line_edit.textChanged.connect(lambda: self.__wait_and_verify(db))
        self.password_line_edit.installEventFilter(self)

        self.center_of_eyes = {'x': 235, 'y': 143}

        self.last_update_time = 0
        self.update_interval = 30

        self.launch_animated()


    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.MouseButtonPress and event.button() == QtCore.Qt.LeftButton:
            self.mouse_button_pressed = True
        elif event.type() == QtCore.QEvent.MouseButtonRelease and event.button() == QtCore.Qt.LeftButton:
            self.mouse_button_pressed = False
        elif event.type() == QtCore.QEvent.MouseMove and self.mouse_button_pressed:
            self.move(self.x()+event.x()-self.last_position_x, self.y()+event.y()-self.last_position_y)

        if event.type() == QtCore.QEvent.KeyPress and event.key() == QtCore.Qt.Key_Escape:
            self.close_animated(exit_pressed=True)
        if event.type() == QtCore.QEvent.MouseMove:
            if not self.mouse_button_pressed:
                self.last_position_x = event.x()
                self.last_position_y = event.y()
            self.move_auth_cat_eyes()
        return super().eventFilter(obj, event)

    def launch_animated(self):
        self.launch_close_animation.setStartValue(0)
        self.launch_close_animation.setEndValue(1)
        self.launch_close_animation.start()

    def close_animated(self, exit_pressed=False):
        self.mouse_button_pressed = False

        if exit_pressed:
            self.exit_pressed = "Closed"
        self.launch_close_animation.setStartValue(1)
        self.launch_close_animation.setEndValue(0)
        self.launch_close_animation.start()
        self.launch_close_animation.finished.connect(self.close)

    def __wait_and_verify(self, db):
        self.password_line_edit.setStyleSheet(self.passwd_css_normal)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(lambda: self.__verify_password(db))
        self.timer.start(1500)

    def __verify_password(self, db):
        self.timer.stop()
        from security import Passwd
        if Passwd().verify_password(self.password_line_edit.text(), db):
            self.__forbidden = False
            self.close_animated()
        else:
            self.close_animated()

    @property
    def forbidden(self):
        return self.__forbidden

    def set_cats_ears(self):
        self.mouse_button_pressed = False
        if self.ears_down:
            self.auth_cat_label.setPixmap(QtGui.QPixmap("img/kitty_ears_up.png"))
        else:
            self.auth_cat_label.setPixmap(QtGui.QPixmap("img/kitty_ears_down.png"))
        self.ears_down = not(self.ears_down)

    def move_auth_cat_eyes(self):
        current_time = QtCore.QDateTime.currentMSecsSinceEpoch()
        if current_time - self.last_update_time < self.update_interval:
            return
        else:
            self.last_update_time = current_time

        cursor_pos = self.main_frame.mapFromGlobal(QtGui.QCursor.pos())

        center_left = self.left_eye_label.rect().center()
        center_right = self.right_eye_label.rect().center()

        initial_pos_left = (self.center_of_eyes['x'] + center_left.x() - 9,
                            self.center_of_eyes['y'] + center_left.y())

        new_left_pos = self.calculate_eye_position(initial_pos_left, (cursor_pos.x()+3, cursor_pos.y()), 3)

        initial_pos_right = (self.center_of_eyes['x'] + center_right.x() + 9,
                             self.center_of_eyes['y'] + center_right.y())
        new_right_pos = self.calculate_eye_position(initial_pos_right, (cursor_pos.x()+3, cursor_pos.y()), 3)

        self.left_eye_label.move(int(new_left_pos[0] - self.left_eye_label.width() / 2),
                                 int(new_left_pos[1] - self.left_eye_label.height() / 2))
        self.right_eye_label.move(int(new_right_pos[0] - self.right_eye_label.width() / 2),
                                  int(new_right_pos[1] - self.right_eye_label.height() / 2))

    def calculate_eye_position(self, initial_pos, cursor_pos, max_eye_radius):
        dx = cursor_pos[0] - initial_pos[0]
        dy = cursor_pos[1] - initial_pos[1]
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > max_eye_radius:
            angle = math.atan2(dy, dx)
            dx = math.cos(angle) * max_eye_radius
            dy = math.sin(angle) * max_eye_radius

        return (initial_pos[0] + dx, initial_pos[1] + dy)

class CustomMessageBox(QtWidgets.QMessageBox):
    def __init__(self, parent, joke_button=None):
        super().__init__(parent)
        
        self.setWindowIcon(QtGui.QIcon("img/icon.ico"))
        self.setWindowTitle("Crystal")

        self.accepted_ = False

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        rect = self.rect()
        brush = QtGui.QBrush(QtGui.QColor(240, 240, 240, 250))
        painter.setBrush(brush)
        #painter.setPen(QtCore.Qt.NoPen)
        radius = 10
        painter.drawRoundedRect(rect, radius, radius)
        super().paintEvent(event)

class AckWindow(QtWidgets.QDialog, Ui_AckWindow):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)

        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        self.setStyleSheet("""
                            QLabel {
                                font-size: 14px;
                                color: #333;
                            }
                            QPushButton {
                                background: none;
                                color: #555;
                                border-radius: 8px;
                                padding: 5px 10px;
                                border: 1px solid #555;
                                font-size: 10px;
                            }
                            QPushButton:hover {
                                color: black;
                                border: 1px solid black;
                            }
                        """)

class ChangePasswordWindow(QtWidgets.QDialog, Ui_ChangePassword):
    def __init__(self, parent, db):
        def last_position(event):
            self.last_position_x = event.x()
            self.last_position_y = event.y()

        super().__init__(parent)

        self.setupUi(self)

        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        self.setWindowIcon(QtGui.QIcon("img/icon.ico"))
        self.setWindowTitle("Crystal - смена пароля")

        self.background_label.mousePressEvent = lambda event: last_position(event)
        self.background_label.mouseMoveEvent = lambda event: self.move(self.x()+event.x()-self.last_position_x, self.y()+event.y()-self.last_position_y)

        self.mouse_button_pressed = False

        self.launch_close_animation = QtCore.QPropertyAnimation(self, b'windowOpacity', duration=200)

        self.message_label.setVisible(False)

        self.password_changed = False

        self.new_password_line_edit.textChanged.connect(lambda: self.message_label.setVisible(False))
        self.new_password_confirmation_line_edit.textChanged.connect(lambda: self.message_label.setVisible(False))

        self.change_button.clicked.connect(lambda: self.__change_password(db))
        self.cancel_button.clicked.connect(self.close_animated)

        self.installEventFilter(self)
        

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress and event.key() == QtCore.Qt.Key_Escape:
            self.close_animated()
        return super().eventFilter(obj, event)

    def launch_animated(self):
        self.launch_close_animation.setStartValue(0)
        self.launch_close_animation.setEndValue(1)
        self.launch_close_animation.start()

    def close_animated(self):
        self.mouse_button_pressed = False
        self.launch_close_animation.setStartValue(1)
        self.launch_close_animation.setEndValue(0)
        self.launch_close_animation.start()
        self.launch_close_animation.finished.connect(self.close)

    def __change_password(self, db):
        if not self.new_password_line_edit.text() or not self.new_password_confirmation_line_edit.text():
            self.message_label.setText("Заполните оба поля")
            self.message_label.setVisible(True)
            return
        elif len(self.new_password_line_edit.text()) <= 4:
            self.message_label.setText("Пароль должен быть от 5 символов")
            self.message_label.setVisible(True)
            return
        elif self.new_password_line_edit.text() != self.new_password_confirmation_line_edit.text():
            self.message_label.setText("Пароли не совпадают")
            self.message_label.setVisible(True)
            return
        from security import Passwd
        Passwd().set_new_password(self.new_password_line_edit.text(), db)
        self.password_changed = True
        self.close_animated()        

class TemplatesWindow(QtWidgets.QDialog, Ui_TemplatesWindow):
    def __init__(self, parent, field: str, templates: Templates):
        super().__init__(parent)

        self.setupUi(self)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        self.setWindowIcon(QtGui.QIcon("img/icon.ico"))
        self.setWindowTitle("Crystal")

        self.launch_close_animation = QtCore.QPropertyAnimation(self, b'windowOpacity', duration=60)

        self.css_checkbox = """
                    QCheckBox {
                        background: rgba(0,0,0,0);
                        spacing: 5px;
                        font-family: comfortaa;
                        font-size: 15px;
                    }

                    QCheckBox::indicator {
                        width: 14px;
                        height: 14px;
                        border: 1px solid #444;
                        border-radius: 3px;
                        background: rgba(0,0,0,0);
                    }

                    QCheckBox::indicator:hover {
                        border-color: #222;
                    }

                    QCheckBox::indicator:checked {
                        background-color: #45d;
                        border-color: #44b;
                    }

                    QCheckBox:disabled {
                        color: #999;
                    }

                    QCheckBox::indicator:disabled {
                        background-color: #eee;
                        border-color: #ccc;
                    }

                    QCheckBox::indicator:checked:disabled {
                    background-color: #ccc;
                    border-color: #aaa;
                    }

                    QToolTip {
                        color: black;
                        font-family: "Comfortaa";
                        font-size: 10px;
                        background-color: #fff;
                        border: 1px solid #aaa;
                        border-radius: 5px;
                    }
                    """
        self.interval = 30

        self.field = field
        
        self.variant_objects = []

        self.__templates = templates

        self.chosen = []

        self.ok_button.clicked.connect(self.set_chosen_variants)
        self.create_button.clicked.connect(self.create_template)
        self.delete_button.clicked.connect(self.delete_templates)
        self.cancel_button.clicked.connect(self.close_animated)

        self.set_variants()

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress and event.key() == QtCore.Qt.Key_Escape:
            self.close_animated()
        return super().eventFilter(obj, event)

    def launch_animated(self):
        self.launch_close_animation.setStartValue(0)
        self.launch_close_animation.setEndValue(1)
        self.launch_close_animation.start()

    def close_animated(self):
        self.mouse_button_pressed = False
        self.launch_close_animation.setStartValue(1)
        self.launch_close_animation.setEndValue(0)
        self.launch_close_animation.start()
        self.launch_close_animation.finished.connect(self.close)

    def create_template(self):
        create_window = QtWidgets.QDialog(self)
        create_window.setFixedSize(300, 120)
        create_window.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        create_window.setStyleSheet("""
                                    color: black;
                                    background: none;
                                    border-radius: 5px;
                                    border: 1px solid black;
                                    font-family: comfortaa;
                                    font-size: 12px;
                                    """)
        label = QtWidgets.QLabel("Значение шаблона", create_window)
        label.setStyleSheet("border: 0px; font-size: 14px;")
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setGeometry(50, 15, 200, 26)

        name_line_edit = QtWidgets.QLineEdit(create_window)
        name_line_edit.setGeometry(20, 40, 260, 26)
        
        ok = QtWidgets.QPushButton("Добавить", create_window)
        ok.clicked.connect(create_window.accept)
        ok.setGeometry(10, 86, 80, 24)
        
        cancel = QtWidgets.QPushButton("Отмена", create_window)
        cancel.clicked.connect(create_window.reject)
        cancel.setGeometry(210, 86, 80, 24)
        
        result = create_window.exec_()
        if result == QtWidgets.QDialog.Accepted:
            name = name_line_edit.text()
            if not name:
                window.show_message_window("Ошибка", "Задайте значение шаблона")
                return
            if "'" in name:
                window.show_message_window("Ошибка", "Нельзя использовать символ ' в поле ввода")
                return
            self.__templates.add_template(self.field, name)
            self.set_variants()

    def delete_templates(self):
        checked = []
        for template in self.variant_objects:
            if template.isChecked():
                checked.append(template)

        if not checked:
            window.show_message_window("Ошибка", "Не выбрано ни одного элемента для удаления")
            return

        acknowledge_window = AckWindow(self)
        acknowledge_window.setWindowTitle("Crystal - Подтвердите действие")
        acknowledge_window.setWindowIcon(QtGui.QIcon("img/icon.ico"))
        acknowledge_window.message_label.setText("Вы действительно хотите удалить выбранные элементы?")
        acknowledge_window.ok_button.setText("Удалить")
        acknowledge_window.cancel_button.setText("Отмена")
        result = acknowledge_window.exec_()

        if result == QtWidgets.QDialog.Accepted:
            for template in checked:
                self.__templates.delete_template(self.field, template.text())
            self.set_variants()

    def set_variants(self):
        for obj in self.variant_objects:
            obj.setParent(None)
            obj.deleteLater()
        self.variant_objects = []

        if self.templates_widget_contents.layout() is not None:
            layout = self.templates_widget_contents.layout()
            while layout.count() > 0:
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().setParent(None)
                    item.widget().deleteLater()
                del item

        variants = getattr(self.__templates, self.field)

        if self.templates_widget_contents.layout() is None:
                layout = QtWidgets.QVBoxLayout(self.templates_widget_contents)
        else:
            layout = self.templates_widget_contents.layout()
        layout.setSpacing(7)

        current_y_position = 10
        for variant in variants:
            checkbox = QtWidgets.QCheckBox(text=variant[1], parent=self.templates_widget_contents)
            layout.addWidget(checkbox)

            checkbox.setStyleSheet(self.css_checkbox)
            self.variant_objects.append(checkbox)
            current_y_position += self.interval
        layout.addStretch(1)

        self.templates_widget_contents.update()
        self.scroll_area_templates.update()
        self.updateGeometry()

    def set_chosen_variants(self):
        for checkbox in self.variant_objects:
            if checkbox.isChecked():
                self.chosen.append(checkbox.text())
        if not self.chosen:
            self.chosen.append('')
        self.close_animated()



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
