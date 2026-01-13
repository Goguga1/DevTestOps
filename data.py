from pysqlcipher3 import dbapi2 as sql
import os, datetime, shutil
#from yadisk import YaDisk


class Database():
    def __init__(self):
        self.__path = "data/data.db"
        self.__key = 'P@ssw0rd'
        self.__connection = sql.connect(self.__path)
        self.__cursor = self.__connection.cursor()
        self.__cursor.execute(f"PRAGMA key='{self.__key}';")
        try:
            self.__cursor.execute("SELECT Id FROM Examinations")
            self.__cursor.execute("SELECT Id FROM People")
            self.__cursor.execute("SELECT On_top FROM Settings")
        except:
            self.create_tables()

    def create_tables(self):
        examinstaions_table = """
            CREATE TABLE Examinations (
                            Id                             INTEGER PRIMARY KEY
                                                                UNIQUE
                                                                NOT NULL,
                            Person_id                      INTEGER REFERENCES People (Id) ON DELETE CASCADE
                                                                NOT NULL,
                            Eyesight_without_od            DOUBLE  NOT NULL,
                            Eyesight_without_os            DOUBLE  NOT NULL,
                            Eyesight_with_od               DOUBLE  NOT NULL,
                            Eyesight_with_od_sph           DOUBLE  NOT NULL,
                            Eyesight_with_od_cyl           DOUBLE  NOT NULL,
                            Eyesight_with_od_ax            INTEGER NOT NULL,
                            Eyesight_with_os               DOUBLE  NOT NULL,
                            Eyesight_with_os_sph           DOUBLE  NOT NULL,
                            Eyesight_with_os_cyl           DOUBLE  NOT NULL,
                            Eyesight_with_os_ax            INTEGER NOT NULL,
                            Schiascopy_od                  TEXT    NOT NULL,
                            Schiascopy_os                  TEXT    NOT NULL,
                            Glasses_od_sph                 DOUBLE  NOT NULL,
                            Glasses_od_cyl                 DOUBLE  NOT NULL,
                            Glasses_od_ax                  INTEGER NOT NULL,
                            Glasses_os_sph                 DOUBLE  NOT NULL,
                            Glasses_os_cyl                 DOUBLE  NOT NULL,
                            Glasses_os_ax                  INTEGER NOT NULL,
                            Glasses_dpp                    INTEGER NOT NULL,
                            Diagnosis_subscription         TEXT,
                            Visit_date                     TEXT    NOT NULL,
                            Complaints                     TEXT,
                            Disease_anamnesis              TEXT,
                            Life_anamnesis                 TEXT,
                            Eyesight_type                  TEXT,
                            Relative_accommodation_reserve DOUBLE,
                            Schober_test                   TEXT,
                            Pupils                         TEXT,
                            Od_eye_position                TEXT,
                            Od_oi                          TEXT,
                            Od_eyelid                      TEXT,
                            Od_lacrimal_organs             TEXT,
                            Od_conjunctiva                 TEXT,
                            Od_discharge                   TEXT,
                            Od_iris                        TEXT,
                            Od_anterior_chamber            TEXT,
                            Od_refractive_medium           TEXT,
                            Od_optic_disk                  TEXT,
                            Od_vessels                     TEXT,
                            Od_macular_reflex              TEXT,
                            Od_visible_periphery           TEXT,
                            Od_diagnosis                   TEXT,
                            Od_icd_code                    TEXT,
                            Os_eye_position                TEXT,
                            Os_oi                          TEXT,
                            Os_eyelid                      TEXT,
                            Os_lacrimal_organs             TEXT,
                            Os_conjunctiva                 TEXT,
                            Os_discharge                   TEXT,
                            Os_iris                        TEXT,
                            Os_anterior_chamber            TEXT,
                            Os_refractive_medium           TEXT,
                            Os_optic_disk                  TEXT,
                            Os_vessels                     TEXT,
                            Os_macular_reflex              TEXT,
                            Os_visible_periphery           TEXT,
                            Os_diagnosis                   TEXT,
                            Os_icd_code                    TEXT,
                            Recommendations                TEXT,
                            Direction_to_aokb              BOOLEAN,
                            Reappointment                  BOOLEAN,
                            Reappointment_time             TEXT
                        );"""
        people_table = """
                    CREATE TABLE IF NOT EXISTS People (
        Id        INTEGER PRIMARY KEY
                        NOT NULL
                        UNIQUE,
        Full_name TEXT    NOT NULL,
        Birthdate TEXT    NOT NULL
        );"""
        settings_table = """
        CREATE TABLE Settings (
            On_top                     BOOLEAN NOT NULL,
            Remember_last_position     BOOLEAN NOT NULL,
            Run_with_system            BOOLEAN NOT NULL,
            Use_password               BOOLEAN NOT NULL,
            Last_position              TEXT    NOT NULL,
            Password_hash              TEXT    NOT NULL,
            Ack_save_examination       BOOLEAN NOT NULL,
            Ack_erase_examination      BOOLEAN NOT NULL,
            Ack_save_change_data       BOOLEAN NOT NULL,
            Ack_delete_change_data     BOOLEAN NOT NULL,
            Ack_save_person            BOOLEAN NOT NULL,
            Ack_delete_person          BOOLEAN NOT NULL,
            Number_of_visible_records  INTEGER NOT NULL,
            Backup                     TEXT,
            Objective_synchronize_eyes BOOLEAN
        );
        """
        templats_table = """
        CREATE TABLE Templates (
                    Id       INTEGER PRIMARY KEY
                                    UNIQUE,
                    Field    TEXT,
                    Template TEXT
                    );
        """
        self.__cursor.execute(examinstaions_table)
        self.__cursor.execute(people_table)
        self.__cursor.execute(settings_table)
        self.__cursor.execute(templats_table)
        self.__cursor.execute("INSERT INTO Settings\
                              VALUES (0, 1, 0, 1, '0,0', '$argon2id$v=19$m=102400,t=8,p=4$OE+LhKiUd7K6mIW88jv4GZ7eIgMwQMYjhe5PUrVZDCUqw8QwCjnC6KavtJJc5wIvSMso4JB+j80cRNx2sLjcEb4Bg72rG2O/ecKAH43tdyZpmUNgOe5/mlzrkFlbKm+PYRPAV0yS4VIbWOPOdbdJ03MdG5PYi2aoxe+h6g9+UWM$NZ5Vhi0N1hpPyyi/eox1925AlVCq58Zvw38kE62YRbYUqdwY66+NqgwbyqREzhJ6VX6MkJmCLgKaRlLgFCsLdAmPpptqITYTs+zXYrsSphbR+4vn5JIYEvVk+3ZdgYbUulR6MqRaHVXv/cs8N7nvRGy++ccOvLRQln/GgI5RpZI', 1, 1, 1, 1, 1, 1, 1000, 0, 0)")   
        self.__cursor.execute("""INSERT INTO Templates (
                          Template,
                          Field,
                          Id
                      )
                      VALUES (
                          'ортофория',
                          'eye_position',
                          1
                      ),
                      (
                          'экзофория',
                          'eye_position',
                          2
                      ),
                      (
                          'эзофория',
                          'eye_position',
                          3
                      ),
                      (
                          'альтернирующее косоглазие',
                          'eye_position',
                          4
                      ),
                      (
                          'с 5 м - бинокулярное',
                          'eyesight_type',
                          5
                      ),
                      (
                          'с 5 м - одновременное',
                          'eyesight_type',
                          6
                      ),
                      (
                          'с 5 м - монокулярное OD',
                          'eyesight_type',
                          7
                      ),
                      (
                          'с 5 м - монокулярное OS',
                          'eyesight_type',
                          8
                      ),
                      (
                          'спокойны',
                          'oi',
                          9
                      ),
                      (
                          'инъекция слабая',
                          'oi',
                          10
                      ),
                      (
                          'инъекция умеренная',
                          'oi',
                          11
                      ),
                      (
                          'инъекция выраженная',
                          'oi',
                          12
                      ),
                      (
                          'перикорнеальная инъекция',
                          'oi',
                          13
                      ),
                      (
                          'смешанная инъекция',
                          'oi',
                          14
                      ),
                      (
                          'отечность конъюнктивы',
                          'oi',
                          16
                      ),
                      (
                          'без изменений',
                          'eyelid',
                          17
                      ),
                      (
                          'отек',
                          'eyelid',
                          18
                      ),
                      (
                          'гиперемия века',
                          'eyelid',
                          19
                      ),
                      (
                          'гиперемия ресничного края',
                          'eyelid',
                          20
                      ),
                      (
                          'птоз',
                          'eyelid',
                          21
                      ),
                      (
                          'округлое образование верхнее веко',
                          'eyelid',
                          22
                      ),
                      (
                          'округлое образование нижнее веко',
                          'eyelid',
                          23
                      ),
                      (
                          'новообразование',
                          'eyelid',
                          24
                      ),
                      (
                          'рубцовые изменения',
                          'eyelid',
                          25
                      ),
                      (
                          'закупорка мейбомиевых желёз',
                          'eyelid',
                          26
                      ),
                      (
                          'без изменений',
                          'lacrimal_organs',
                          27
                      ),
                      (
                          'слезостояние',
                          'lacrimal_organs',
                          28
                      ),
                      (
                          'при надавливании на слёзный мешок слизисто-гнойное отделяемое',
                          'lacrimal_organs',
                          29
                      ),
                      (
                          'бледная',
                          'conjunctiva',
                          30
                      ),
                      (
                          'розовая',
                          'conjunctiva',
                          31
                      ),
                      (
                          'инъекция слабая',
                          'conjunctiva',
                          32
                      ),
                      (
                          'инъекция умеренная',
                          'conjunctiva',
                          33
                      ),
                      (
                          'инъекция выраженная',
                          'conjunctiva',
                          34
                      ),
                      (
                          'сосочки',
                          'conjunctiva',
                          35
                      ),
                      (
                          'кровоизлияние субконъюнктивальное',
                          'conjunctiva',
                          36
                      ),
                      (
                          'рубцы',
                          'conjunctiva',
                          37
                      ),
                      (
                          'отсутствует',
                          'discharge',
                          38
                      ),
                      (
                          'скудное слизистое',
                          'discharge',
                          39
                      ),
                      (
                          'умеренное слизистое',
                          'discharge',
                          40
                      ),
                      (
                          'гнойное',
                          'discharge',
                          41
                      ),
                      (
                          'слизисто-гнойное',
                          'discharge',
                          42
                      ),
                      (
                          'кровянистое',
                          'discharge',
                          43
                      ),
                      (
                          'обильное',
                          'discharge',
                          44
                      ),
                      (
                          'структура сохранена',
                          'iris',
                          45
                      ),
                      (
                          'рисунок четкий',
                          'iris',
                          46
                      ),
                      (
                          'гетерохромия',
                          'iris',
                          49
                      ),
                      (
                          'новообразования',
                          'iris',
                          50
                      ),
                      (
                          'колобома',
                          'iris',
                          51
                      ),
                      (
                          'средняя глубина',
                          'anterior_chamber',
                          52
                      ),
                      (
                          'глубокая',
                          'anterior_chamber',
                          53
                      ),
                      (
                          'мелкая',
                          'anterior_chamber',
                          54
                      ),
                      (
                          'гифема',
                          'anterior_chamber',
                          55
                      ),
                      (
                          'гипопион',
                          'anterior_chamber',
                          56
                      ),
                      (
                          'прозрачные',
                          'refractive_medium',
                          57
                      ),
                      (
                          'помутнение хрусталика (начальная стадия)',
                          'refractive_medium',
                          58
                      ),
                      (
                          'помутнение хрусталика (зрелая стадия)',
                          'refractive_medium',
                          59
                      ),
                      (
                          'деструкция стекловидного тела',
                          'refractive_medium',
                          60
                      ),
                      (
                          'бледно-розовый',
                          'optic_disk',
                          61
                      ),
                      (
                          'границы четкие',
                          'optic_disk',
                          62
                      ),
                      (
                          'границы стушеваны',
                          'optic_disk',
                          63
                      ),
                      (
                          'экскавация физиологическая',
                          'optic_disk',
                          64
                      ),
                      (
                          'экскавация расширена',
                          'optic_disk',
                          65
                      ),
                      (
                          'экскавация углублена',
                          'optic_disk',
                          66
                      ),
                      (
                          'отек диска зрительного нерва',
                          'optic_disk',
                          67
                      ),
                      (
                          'атрофия диска зрительного нерва',
                          'optic_disk',
                          68
                      ),
                      (
                          'неоваскуляризация диска зрительного нерва',
                          'optic_disk',
                          69
                      ),
                      (
                          'друзы диска зрительного нерва',
                          'optic_disk',
                          70
                      ),
                      (
                          'глиоз',
                          'optic_disk',
                          71
                      ),
                      (
                          'миопический конус',
                          'optic_disk',
                          72
                      ),
                      (
                          'миопическая стафилома',
                          'optic_disk',
                          73
                      ),
                      (
                          'норма',
                          'vessels',
                          74
                      ),
                      (
                          'артерии сужены (вены расширены)',
                          'vessels',
                          75
                      ),
                      (
                          'артерии расширены (вены сужены)',
                          'vessels',
                          76
                      ),
                      (
                          'расширены',
                          'vessels',
                          77
                      ),
                      (
                          'извиты',
                          'vessels',
                          78
                      ),
                      (
                          'кровоизлияния',
                          'vessels',
                          79
                      ),
                      (
                          'экссудаты',
                          'vessels',
                          80
                      ),
                      (
                          'сохранен',
                          'macular_reflex',
                          81
                      ),
                      (
                          'ослаблен',
                          'macular_reflex',
                          82
                      ),
                      (
                          'отсутствует',
                          'macular_reflex',
                          83
                      ),
                      (
                          'искажён',
                          'macular_reflex',
                          84
                      ),
                      (
                          'разрыв макулы',
                          'macular_reflex',
                          85
                      ),
                      (
                          'не осмотрен',
                          'macular_reflex',
                          87
                      ),
                      (
                          'без особенностей',
                          'visible_periphery',
                          88
                      ),
                      (
                          'дистрофия сетчатки (по типу «булыжной мостовой»)',
                          'visible_periphery',
                          89
                      ),
                      (
                          'разрывы сетчатки',
                          'visible_periphery',
                          90
                      ),
                      (
                          'отслойка сетчатки',
                          'visible_periphery',
                          91
                      ),
                      (
                          'кровоизлияния',
                          'visible_periphery',
                          92
                      ),
                      (
                          'экссудаты',
                          'visible_periphery',
                          93
                      ),
                      (
                          'новообразования',
                          'visible_periphery',
                          94
                      ),
                      (
                          'дегенеративные изменения',
                          'visible_periphery',
                          95
                      ),
                      (
                          'перераспределение пигмента',
                          'visible_periphery',
                          96
                      ),
                      (
                          'дистрофия по типу «след улитки»',
                          'visible_periphery',
                          97
                      ),
                      (
                          'не осмотрена',
                          'visible_periphery',
                          98
                      ),
                      (
                          'миопия слабой степени',
                          'diagnosis',
                          99
                      ),
                      (
                          'миопия средней степени',
                          'diagnosis',
                          100
                      ),
                      (
                          'миопия высокой степени',
                          'diagnosis',
                          101
                      ),
                      (
                          'гиперметропия слабой степени',
                          'diagnosis',
                          102
                      ),
                      (
                          'гиперметропия средней степени',
                          'diagnosis',
                          103
                      ),
                      (
                          'гиперметропия высокой степени',
                          'diagnosis',
                          104
                      ),
                      (
                          'астигматизм (миопический)',
                          'diagnosis',
                          105
                      ),
                      (
                          'астигматизм (гиперметропический)',
                          'diagnosis',
                          106
                      ),
                      (
                          'астигматизм (смешанный)',
                          'diagnosis',
                          107
                      ),
                      (
                          'катаракта (начальная)',
                          'diagnosis',
                          108
                      ),
                      (
                          'конъюнктивит (бактериальный)',
                          'diagnosis',
                          109
                      ),
                      (
                          'конъюнктивит (острый)',
                          'diagnosis',
                          110
                      ),
                      (
                          'конъюнктивит (П/О)',
                          'diagnosis',
                          111
                      ),
                      (
                          'конъюнктивит (вирусный)',
                          'diagnosis',
                          112
                      ),
                      (
                          'конъюнктивит (аллергический)',
                          'diagnosis',
                          113
                      ),
                      (
                          'кератит',
                          'diagnosis',
                          114
                      ),
                      (
                          'увеит',
                          'diagnosis',
                          115
                      ),
                      (
                          'блефарит',
                          'diagnosis',
                          116
                      ),
                      (
                          'халязион',
                          'diagnosis',
                          117
                      ),
                      (
                          'ячмень',
                          'diagnosis',
                          118
                      ),
                      (
                          'синдром сухого глаза',
                          'diagnosis',
                          119
                      ),
                      (
                          'птоз',
                          'diagnosis',
                          120
                      ),
                      (
                          'дакриоцистит',
                          'diagnosis',
                          121
                      ),
                      (
                          'привычно-избыточное напряжение аккомодации',
                          'diagnosis',
                          122
                      ),
                      (
                          'анизометропия',
                          'diagnosis',
                          123
                      ),
                      (
                          'соблюдение зрительного режима',
                          'recommendations',
                          124
                      ),
                      (
                          'гимнастика для глаз (по Аветисову)',
                          'recommendations',
                          125
                      ),
                      (
                          'увлажняющие капли (указать название)',
                          'recommendations',
                          126
                      ),
                      (
                          'очки для работы',
                          'recommendations',
                          127
                      ),
                      (
                          'очки для дали',
                          'recommendations',
                          128
                      ),
                      (
                          'очки для постоянного ношения',
                          'recommendations',
                          129
                      ),
                      (
                          'ночные линзы',
                          'recommendations',
                          130
                      ),
                      (
                          'ограничение зрительной нагрузки (использование гаджетов не более 30 минут в день)',
                          'recommendations',
                          131
                      ),
                      (
                          'консультация других специалистов (указать каких)',
                          'recommendations',
                          132
                      ),
                      (
                          'хирургическое лечение (указать какое)',
                          'recommendations',
                          133
                      ),
                      (
                          'исключить гаджеты',
                          'recommendations',
                          134
                      ),
                      (
                          'аппаратное лечение',
                          'recommendations',
                          135
                      ),
                      (
                          'прогулки на свежем воздухе не менее 2 часов в день',
                          'recommendations',
                          136
                      ),
                      (
                          'массаж век',
                          'recommendations',
                          137
                      ),
                      (
                          'Ирифрин 2,5% по 1 капле на ночь 1 месяц (курс 1 раз в 3 месяца)',
                          'recommendations',
                          138
                      ),
                      (
                          'Окомистин по 1 капле 3 раза в день 7-10 дней',
                          'recommendations',
                          139
                      ),
                      (
                          'Данцил по 1 капле 3 раза в день 7 дней',
                          'recommendations',
                          140
                      ),
                      (
                          'Офтаквикс по 1 капле 3 раза в день 7 дней',
                          'recommendations',
                          141
                      ),
                      (
                          'Комбинил по 1 капле 3 раза в день 10 дней',
                          'recommendations',
                          142
                      ),
                      (
                          'Вигамокс по 1 капле 3 раза в день 7 дней',
                          'recommendations',
                          143
                      ),
                      (
                          'Эритромициновая мазь за нижнее веко на сон 5 дней',
                          'recommendations',
                          144
                      ),
                      (
                          'Опатанол по 1 капле 2 раза в день 7 дней',
                          'recommendations',
                          145
                      ),
                      (
                          'Блефарогель №1 на ресничный край после массажа',
                          'recommendations',
                          146
                      ),
                      (
                          'посадка в школе 1 парта',
                          'recommendations',
                          147
                      ),
                      (
                          'посадка в школе не далее 2 парты',
                          'recommendations',
                          148
                      ),
                      (
                          'через 10 дней',
                          'reappointment_time',
                          149
                      ),
                      (
                          'через 1 неделю',
                          'reappointment_time',
                          150
                      ),
                      (
                          'через 2 недели',
                          'reappointment_time',
                          151
                      ),
                      (
                          'через 1 месяц',
                          'reappointment_time',
                          152
                      ),
                      (
                          'через 3 месяца',
                          'reappointment_time',
                          153
                      ),
                      (
                          'через 6 месяцев',
                          'reappointment_time',
                          154
                      ),
                      (
                          'после лечения',
                          'reappointment_time',
                          157
                      ),
                      (
                          'ухудшение зрения в даль',
                          'complaints',
                          158
                      ),
                      (
                          'ухудшение зрения вблизи',
                          'complaints',
                          159
                      ),
                      (
                          'боль в глазах',
                          'complaints',
                          160
                      ),
                      (
                          'сухость глаз',
                          'complaints',
                          161
                      ),
                      (
                          'слезотечение',
                          'complaints',
                          162
                      ),
                      (
                          'покраснение глаз',
                          'complaints',
                          163
                      ),
                      (
                          'выделения из глаз',
                          'complaints',
                          164
                      ),
                      (
                          'косоглазие',
                          'complaints',
                          165
                      ),
                      (
                          'двоение в глазах',
                          'complaints',
                          166
                      ),
                      (
                          'светобоязнь',
                          'complaints',
                          167
                      ),
                      (
                          'зуд в глазах',
                          'complaints',
                          168
                      ),
                      (
                          'быстрая утомляемость глаз',
                          'complaints',
                          169
                      ),
                      (
                          'головная боль',
                          'complaints',
                          170
                      ),
                      (
                          'чувство дискомфорта',
                          'complaints',
                          171
                      ),
                      (
                          'слезостояние',
                          'complaints',
                          172
                      ),
                      (
                          'недостаточность слезных канальцев',
                          'diagnosis',
                          173
                      ),
                      (
                          'с 2,5 м - бинокулярное',
                          'eyesight_type',
                          175
                      );""")

        self.__connection.commit()

    def execute(self, statement):
        if type(statement) == str:
            result = self.__cursor.execute(statement)
        elif type(statement) == list:
            for statement_ in statement:
                self.__cursor.execute(statement_)
        return result

    def commit(self):
        self.__connection.commit()

    def do_backup_of_database(self):
        if not os.path.exists('data/data.db'):
            return
        backup_files = sorted(list(filter(lambda file: ".db" in file, os.listdir('data/'))))[1:]
        backup_files = backup_files[::-1]
        now = datetime.datetime.now()
        if len(backup_files) > 10:
            if backup_files[-1] != "data.db":
                os.remove(f"data/{backup_files[-1]}")
        shutil.copyfile("data/data.db", f"data/data_{now.strftime('%y%m%d_%H%M')}.db")

    #def upload_database(self):
    #    t = self.__db.execute("SELECT Backup FROM Settings").fetchone()[0]
    #    if t:
    #        try:
    #            y = YaDisk(token='')
    #            if y.check_token():
    #                print(123)
    #                y.upload('data/data.db', f'/Crystal_backup/data{datetime.now().strftime("%y%m%d_%H%M")}', overwrite=True)
    #        except:
    #            print(321)
    #            return


class Person():
    def __init__(self, full_name, birthdate: str, id: int = None, db: Database = None):
        self.__id = id

        self.__full_name = full_name

        self.__birthdate = birthdate

        self.__db = db

        if not self.__id:
            last_id = self.__db.execute("SELECT Id FROM People ORDER BY Id").fetchall()
            if last_id:
                last_id = list(last_id[-1])[-1]
                self.__id = int(last_id) + 1
            else:
                self.__id = 1

    @property
    def full_name(self):
        return self.__full_name
    
    @property
    def id(self):
        return self.__id
    
    @property
    def birthdate(self):
        return self.__birthdate
    
    def execute_in_database(self, statements):
        if type(statements) == str:
            self.__db.execute(statements)
        elif type(statements) == list:
            for statement in statements:
                self.__db.execute(statement)
        self.__db.commit()

    def update_person(self, id: str, full_name: str, birthdate: str):
        self.__id = id
        self.__full_name
        self.__birthdate = birthdate

    def add_to_database(self):
        self.execute_in_database(f"INSERT INTO People VALUES({self.__id}, '{self.__full_name}', '{self.__birthdate}')")
    
    def update_data_in_database(self):
        self.execute_in_database(f"UPDATE People SET Full_name = '{self.__full_name}', Birthdate = '{self.__birthdate}' WHERE Id = {self.__id}")
    
    def delete_from_database(self):
        self.execute_in_database(["PRAGMA foreign_keys = ON;", f"DELETE FROM People WHERE Id = {self.__id}"])


class People():
    def __init__(self, db: Database):
        """
        Class starts with uploading all the data about people from the database
        """
        self.__db = db
        people = list(map(lambda x: list(x), self.__db.execute("SELECT * FROM People").fetchall()))
        self.__people = {}
        for person in people:
            self.__people[person[0]] = Person(full_name=person[1], birthdate=person[2], id=person[0], db=self.__db)

    def search(self, id: int = None, name: str = None):
        if not id and not name:
            print("Set one of the arg")
            return
        elif id and name:
            print("Set only one arg")
            return
        if id:
            if id in self.__people:
                return self.__people[id]
            else:
                return
        elif name:
            found = []
            for person_id in self.__people:
                if self.__people[person_id].full_name.startswith(name):
                    found.append(self.__people[person_id])
            return found

    def add_person(self, full_name: str, birthdate: str) -> Person:
        new_person = Person(full_name, birthdate, id=None, db=self.__db)
        self.__people[new_person.id] = new_person
        self.__people[new_person.id].add_to_database()
        return new_person

    def delete_person(self, id: int):
        self.__people[id].delete_from_database()
        self.__people.pop(id)

    def update_person_data(self, id: int, full_name: str, birthdate: str):
        self.__people[id] = Person(full_name, birthdate, id, self.__db)
        self.__people[id].update_data_in_database()

    def get_all(self) -> list:
        return list(self.__people.values())

class Examination():
    def __init__(self, person_id: int,
                eyesight_without_od: float,
                eyesight_without_os: float,
                eyesight_with_od: float,
                eyesight_with_od_sph: float,
                eyesight_with_od_cyl: float,
                eyesight_with_od_ax: int,
                eyesight_with_os: float,
                eyesight_with_os_sph: float,
                eyesight_with_os_cyl: float,
                eyesight_with_os_ax: int,
                schiascopy_od: str,
                schiascopy_os: str,
                glasses_od_sph: float,
                glasses_od_cyl: float,
                glasses_od_ax: int,
                glasses_os_sph: float,
                glasses_os_cyl: float,
                glasses_os_ax: int,
                glasses_dpp: int,
                diagnosis_subscription: str,
                visit_date: str,
                complaints: str,
                disease_anamnesis: str,
                life_anamnesis: str,
                eyesight_type: str,
                relative_accommodation_reserve: float,
                schober_test: str,
                pupils: str,
                od_eye_position: str,
                od_oi: str,
                od_eyelid: str,
                od_lacrimal_organs: str,
                od_conjunctiva: str,
                od_discharge: str,
                od_iris: str,
                od_anterior_chamber: str,
                od_refractive_medium: str,
                od_optic_disk: str,
                od_vessels: str,
                od_macular_reflex: str,
                od_visible_periphery: str,
                od_diagnosis: str,
                od_icd_code: str,
                os_eye_position: str,
                os_oi: str,
                os_eyelid: str,
                os_lacrimal_organs: str,
                os_conjunctiva: str,
                os_discharge: str,
                os_iris: str,
                os_anterior_chamber: str,
                os_refractive_medium: str,
                os_optic_disk: str,
                os_vessels: str,
                os_macular_reflex: str,
                os_visible_periphery: str,
                os_diagnosis: str,
                os_icd_code: str,
                recommendations: str,
                direction_to_aokb: bool,
                reappointment: bool,
                reappointment_time: str,
                id: int = None,
                db: Database = None):

        self.__db = db

        self.__id = id
        self.__person_id = person_id
        self.__eyesight_without_od = eyesight_without_od
        self.__eyesight_without_os = eyesight_without_os
        self.__eyesight_with_od = eyesight_with_od
        self.__eyesight_with_od_sph = eyesight_with_od_sph
        self.__eyesight_with_od_cyl = eyesight_with_od_cyl
        self.__eyesight_with_od_ax = eyesight_with_od_ax
        self.__eyesight_with_os = eyesight_with_os
        self.__eyesight_with_os_sph = eyesight_with_os_sph
        self.__eyesight_with_os_cyl = eyesight_with_os_cyl
        self.__eyesight_with_os_ax = eyesight_with_os_ax
        self.__schiascopy_od = schiascopy_od
        self.__schiascopy_os = schiascopy_os
        self.__glasses_od_sph = glasses_od_sph
        self.__glasses_od_cyl = glasses_od_cyl
        self.__glasses_od_ax = glasses_od_ax
        self.__glasses_os_sph = glasses_os_sph
        self.__glasses_os_cyl = glasses_os_cyl
        self.__glasses_os_ax = glasses_os_ax
        self.__glasses_dpp = glasses_dpp
        self.__diagnosis_subscription = diagnosis_subscription
        self.__visit_date = visit_date
        self.__complaints = complaints
        self.__disease_anamnesis = disease_anamnesis
        self.__life_anamnesis = life_anamnesis
        self.__eyesight_type = eyesight_type
        self.__relative_accommodation_reserve = relative_accommodation_reserve
        self.__schober_test = schober_test
        self.__pupils = pupils
        self.__od_eye_position = od_eye_position
        self.__od_oi = od_oi
        self.__od_eyelid = od_eyelid
        self.__od_lacrimal_organs = od_lacrimal_organs
        self.__od_conjunctiva = od_conjunctiva
        self.__od_discharge = od_discharge
        self.__od_iris = od_iris
        self.__od_anterior_chamber = od_anterior_chamber
        self.__od_refractive_medium = od_refractive_medium
        self.__od_optic_disk = od_optic_disk
        self.__od_vessels = od_vessels
        self.__od_macular_reflex = od_macular_reflex
        self.__od_visible_periphery = od_visible_periphery
        self.__od_diagnosis = od_diagnosis
        self.__od_icd_code = od_icd_code
        self.__os_eye_position = os_eye_position
        self.__os_oi = os_oi
        self.__os_eyelid = os_eyelid
        self.__os_lacrimal_organs = os_lacrimal_organs
        self.__os_conjunctiva = os_conjunctiva
        self.__os_discharge = os_discharge
        self.__os_iris = os_iris
        self.__os_anterior_chamber = os_anterior_chamber
        self.__os_refractive_medium = os_refractive_medium
        self.__os_optic_disk = os_optic_disk
        self.__os_vessels = os_vessels
        self.__os_macular_reflex = os_macular_reflex
        self.__os_visible_periphery = os_visible_periphery
        self.__os_diagnosis = os_diagnosis
        self.__os_icd_code = os_icd_code
        self.__recommendations = recommendations
        self.__direction_to_aokb = direction_to_aokb
        self.__reappointment = reappointment
        self.__reappointment_time = reappointment_time

        if not self.__id:
            last_id = self.__db.execute("SELECT Id FROM Examinations ORDER BY Id").fetchall()
            if last_id:
                last_id = list(last_id[-1])[-1]
                self.__id = int(last_id) + 1
            else:
                self.__id = 1

    @property
    def id(self):
        return self.__id

    @property
    def person_id(self):
        return self.__person_id

    @property
    def eyesight_without_od(self):
        return self.__eyesight_without_od

    @property
    def eyesight_without_os(self):
        return self.__eyesight_without_os

    @property
    def eyesight_with_od(self):
        return self.__eyesight_with_od

    @property
    def eyesight_with_od_sph(self):
        return self.__eyesight_with_od_sph

    @property
    def eyesight_with_od_cyl(self):
        return self.__eyesight_with_od_cyl

    @property
    def eyesight_with_od_ax(self):
        return self.__eyesight_with_od_ax

    @property
    def eyesight_with_os(self):
        return self.__eyesight_with_os

    @property
    def eyesight_with_os_sph(self):
        return self.__eyesight_with_os_sph

    @property
    def eyesight_with_os_cyl(self):
        return self.__eyesight_with_os_cyl

    @property
    def eyesight_with_os_ax(self):
        return self.__eyesight_with_os_ax

    @property
    def schiascopy_od(self):
        return self.__schiascopy_od

    @property
    def schiascopy_os(self):
        return self.__schiascopy_os
    
    @property
    def glasses_od_sph(self):
        return self.__glasses_od_sph

    @property
    def glasses_od_cyl(self):
        return self.__glasses_od_cyl

    @property
    def glasses_od_ax(self):
        return self.__glasses_od_ax

    @property
    def glasses_os_sph(self):
        return self.__glasses_os_sph

    @property
    def glasses_os_cyl(self):
        return self.__glasses_os_cyl

    @property
    def glasses_os_ax(self):
        return self.__glasses_os_ax

    @property
    def glasses_dpp(self):
        return self.__glasses_dpp

    @property
    def diagnosis_subscription(self):
        return self.__diagnosis_subscription

    @property
    def visit_date(self):
        return self.__visit_date
    
    @property
    def complaints(self):
        return self.__complaints
    
    @property
    def disease_anamnesis(self):
        return self.__disease_anamnesis

    @property
    def life_anamnesis(self):
        return self.__life_anamnesis

    @property
    def eyesight_type(self):
        return self.__eyesight_type

    @property
    def relative_accommodation_reserve(self):
        return self.__relative_accommodation_reserve

    @property
    def schober_test(self):
        return self.__schober_test

    @property
    def pupils(self):
        return self.__pupils
        
    @property
    def od_eye_position(self):
        return self.__od_eye_position
    
    @property
    def od_oi(self):
        return self.__od_oi

    @property
    def od_eyelid(self):
        return self.__od_eyelid

    @property
    def od_lacrimal_organs(self):
        return self.__od_lacrimal_organs

    @property
    def od_conjunctiva(self):
        return self.__od_conjunctiva

    @property
    def od_discharge(self):
        return self.__od_discharge

    @property
    def od_iris(self):
        return self.__od_iris

    @property
    def od_anterior_chamber(self):
        return self.__od_anterior_chamber

    @property
    def od_refractive_medium(self):
        return self.__od_refractive_medium

    @property
    def od_optic_disk(self):
        return self.__od_optic_disk

    @property
    def od_vessels(self):
        return self.__od_vessels

    @property
    def od_macular_reflex(self):
        return self.__od_macular_reflex

    @property
    def od_visible_periphery(self):
        return self.__od_visible_periphery

    @property
    def od_diagnosis(self):
        return self.__od_diagnosis
    
    @property
    def od_icd_code(self):
        return self.__od_icd_code

    @property
    def os_eye_position(self):
        return self.__os_eye_position

    @property
    def os_oi(self):
        return self.__os_oi

    @property
    def os_eyelid(self):
        return self.__os_eyelid

    @property
    def os_lacrimal_organs(self):
        return self.__os_lacrimal_organs

    @property
    def os_conjunctiva(self):
        return self.__os_conjunctiva

    @property
    def os_discharge(self):
        return self.__os_discharge

    @property
    def os_iris(self):
        return self.__os_iris

    @property
    def os_anterior_chamber(self):
        return self.__os_anterior_chamber

    @property
    def os_refractive_medium(self):
        return self.__os_refractive_medium

    @property
    def os_optic_disk(self):
        return self.__os_optic_disk

    @property
    def os_vessels(self):
        return self.__os_vessels

    @property
    def os_macular_reflex(self):
        return self.__os_macular_reflex

    @property
    def os_visible_periphery(self):
        return self.__os_visible_periphery

    @property
    def os_diagnosis(self):
        return self.__os_diagnosis
    
    @property
    def os_icd_code(self):
        return self.__os_icd_code

    @property
    def recommendations(self):
        return self.__recommendations
    
    @property
    def direction_to_aokb(self):
        return self.__direction_to_aokb
    
    @property
    def reappointment(self):
        return self.__reappointment
    
    @property
    def reappointment_time(self):
        return self.__reappointment_time

    def execute_in_database(self, statements):
        if type(statements) == str:
            self.__db.execute(statements)
        elif type(statements) == list:
            for statement in statements:
                self.__db.execute(statement)
        self.__db.commit()

    def add_examination_to_database(self):
        self.execute_in_database(f"INSERT INTO Examinations VALUES ({self.__id}, {self.__person_id}, '{self.__eyesight_without_od}', '{self.__eyesight_without_os}',\
                                    '{self.__eyesight_with_od}', '{self.__eyesight_with_od_sph}', '{self.__eyesight_with_od_cyl}', '{self.__eyesight_with_od_ax}',\
                                    '{self.__eyesight_with_os}', '{self.__eyesight_with_os_sph}', '{self.__eyesight_with_os_cyl}', '{self.__eyesight_with_os_ax}',\
                                    '{self.__schiascopy_od}',\
                                    '{self.__schiascopy_os}', '{self.__glasses_od_sph}', '{self.__glasses_od_cyl}',\
                                    '{self.__glasses_od_ax}', '{self.__glasses_os_sph}', '{self.__glasses_os_cyl}', '{self.__glasses_os_ax}', '{self.__glasses_dpp}',\
                                    '{self.__diagnosis_subscription}', '{self.__visit_date}', '{self.__complaints}',\
                                    '{self.__disease_anamnesis}', '{self.__life_anamnesis}', '{self.__eyesight_type}', '{self.__relative_accommodation_reserve}', '{self.__schober_test}', '{self.__pupils}',\
                                    '{self.__od_eye_position}', '{self.__od_oi}', '{self.__od_eyelid}',\
                                    '{self.__od_lacrimal_organs}', '{self.__od_conjunctiva}', '{self.__od_discharge}', '{self.__od_iris}',\
                                    '{self.__od_anterior_chamber}', '{self.__od_refractive_medium}', '{self.__od_optic_disk}', '{self.__od_vessels}', '{self.__od_macular_reflex}',\
                                    '{self.__od_visible_periphery}', '{self.__od_diagnosis}', '{self.__od_icd_code}', '{self.__os_eye_position}', '{self.__os_oi}', '{self.__os_eyelid}',\
                                    '{self.__os_lacrimal_organs}', '{self.__os_conjunctiva}', '{self.__os_discharge}', '{self.__os_iris}',\
                                    '{self.__os_anterior_chamber}', '{self.__os_refractive_medium}', '{self.__os_optic_disk}', '{self.__os_vessels}', '{self.__os_macular_reflex}',\
                                    '{self.__os_visible_periphery}', '{self.__os_diagnosis}', '{self.__os_icd_code}', '{self.__recommendations}', '{self.__direction_to_aokb}', '{self.__reappointment}', '{self.__reappointment_time}')")

    def update_examination_data(self, id, person_id, eyesight_without_od, eyesight_without_os, eyesight_with_od, eyesight_with_od_sph,
                 eyesight_with_od_cyl, eyesight_with_od_ax, eyesight_with_os, eyesight_with_os_sph,
                 eyesight_with_os_cyl, eyesight_with_os_ax, schiascopy_od, schiascopy_os,
                 glasses_od_sph, glasses_od_cyl, glasses_od_ax,
                 glasses_os_sph, glasses_os_cyl, glasses_os_ax, glasses_dpp,
                 diagnosis_subscription, complaints,
                 disease_anamnesis, life_anamnesis, eyesight_type, relative_accommodation_reserve, schober_test, pupils,
                 od_eye_position, od_oi, od_eyelid, od_lacrimal_organs,
                 od_conjunctiva, od_discharge, od_iris, od_anterior_chamber, od_refractive_medium, od_optic_disk,
                 od_vessels, od_macular_reflex, od_visible_periphery, od_diagnosis, od_icd_code, os_eye_position, os_oi, os_eyelid, os_lacrimal_organs,
                 os_conjunctiva, os_discharge, os_iris, os_anterior_chamber, os_refractive_medium, os_optic_disk, os_vessels,
                 os_macular_reflex, os_visible_periphery, os_diagnosis, os_icd_code, recommendations, direction_to_aokb, reappointment, reappointment_time):
        self.__id = id
        self.__person_id = person_id
        self.__eyesight_without_od = eyesight_without_od
        self.__eyesight_without_os = eyesight_without_os
        self.__eyesight_with_od = eyesight_with_od
        self.__eyesight_with_od_sph = eyesight_with_od_sph
        self.__eyesight_with_od_cyl = eyesight_with_od_cyl
        self.__eyesight_with_od_ax = eyesight_with_od_ax
        self.__eyesight_with_os = eyesight_with_os
        self.__eyesight_with_os_sph = eyesight_with_os_sph
        self.__eyesight_with_os_cyl = eyesight_with_os_cyl
        self.__eyesight_with_os_ax = eyesight_with_os_ax
        self.__schiascopy_od = schiascopy_od
        self.__schiascopy_os = schiascopy_os
        self.__glasses_od_sph = glasses_od_sph
        self.__glasses_od_cyl = glasses_od_cyl
        self.__glasses_od_ax = glasses_od_ax
        self.__glasses_os_sph = glasses_os_sph
        self.__glasses_os_cyl = glasses_os_cyl
        self.__glasses_os_ax = glasses_os_ax
        self.__glasses_dpp = glasses_dpp
        self.__diagnosis_subscription = diagnosis_subscription
        self.__complaints = complaints
        self.__disease_anamnesis = disease_anamnesis
        self.__life_anamnesis = life_anamnesis
        self.__eyesight_type = eyesight_type
        self.__relative_accommodation_reserve = relative_accommodation_reserve
        self.__schober_test = schober_test
        self.__pupils = pupils
        self.__od_eye_position = od_eye_position
        self.__od_oi = od_oi
        self.__od_eyelid = od_eyelid
        self.__od_lacrimal_organs = od_lacrimal_organs
        self.__od_conjunctiva = od_conjunctiva
        self.__od_discharge = od_discharge
        self.__od_iris = od_iris
        self.__od_anterior_chamber = od_anterior_chamber
        self.__od_refractive_medium = od_refractive_medium
        self.__od_optic_disk = od_optic_disk
        self.__od_vessels = od_vessels
        self.__od_macular_reflex = od_macular_reflex
        self.__od_visible_periphery = od_visible_periphery
        self.__od_diagnosis = od_diagnosis
        self.__od_icd_code = od_icd_code
        self.__os_eye_position = os_eye_position
        self.__os_oi = os_oi
        self.__os_eyelid = os_eyelid
        self.__os_lacrimal_organs = os_lacrimal_organs
        self.__os_conjunctiva = os_conjunctiva
        self.__os_discharge = os_discharge
        self.__os_iris = os_iris
        self.__os_anterior_chamber = os_anterior_chamber
        self.__os_refractive_medium = os_refractive_medium
        self.__os_optic_disk = os_optic_disk
        self.__os_vessels = os_vessels
        self.__os_macular_reflex = os_macular_reflex
        self.__os_visible_periphery = os_visible_periphery
        self.__os_diagnosis = os_diagnosis
        self.__os_icd_code = os_icd_code
        self.__recommendations = recommendations
        self.__direction_to_aokb=direction_to_aokb
        self.__reappointment=reappointment
        self.__reappointment_time=reappointment_time

    def update_data_in_database(self):
        self.execute_in_database(f"UPDATE Examinations SET Person_id = {self.__person_id}, Eyesight_without_od = '{self.__eyesight_without_od}',\
                                Eyesight_without_os = '{self.__eyesight_without_os}', Eyesight_with_od = '{self.__eyesight_with_od}',\
                                Eyesight_with_od_sph = '{self.__eyesight_with_od_sph}', Eyesight_with_od_cyl = '{self.__eyesight_with_od_cyl}',\
                                Eyesight_with_od_ax = '{self.__eyesight_with_od_ax}', Eyesight_with_os = '{self.__eyesight_with_os}',\
                                Eyesight_with_os_sph = '{self.__eyesight_with_os_sph}', Eyesight_with_os_cyl = '{self.__eyesight_with_os_cyl}',\
                                Eyesight_with_os_ax = '{self.__eyesight_with_os_ax}', Schiascopy_od = '{self.__schiascopy_od}', Schiascopy_os = '{self.__schiascopy_os}',\
                                Glasses_od_sph = '{self.__glasses_od_sph}',\
                                Glasses_od_cyl = '{self.__glasses_od_cyl}', Glasses_od_ax = '{self.__glasses_od_ax}', Glasses_os_sph = '{self.__glasses_os_sph}',\
                                Glasses_os_cyl = '{self.__glasses_os_cyl}', Glasses_os_ax = '{self.__glasses_os_ax}', Glasses_dpp = '{self.__glasses_dpp}',\
                                Diagnosis_subscription = '{self.__diagnosis_subscription}', Complaints = '{self.__complaints}',\
                                Disease_anamnesis = '{self.__disease_anamnesis}', Life_anamnesis = '{self.__life_anamnesis}', Eyesight_type = '{self.__eyesight_type}',\
                                Relative_accommodation_reserve = '{self.__relative_accommodation_reserve}', Schober_test = '{self.__schober_test}', Pupils = '{self.__pupils}',\
                                Od_eye_position = '{self.__od_eye_position}', Od_oi = '{self.__od_oi}', Od_eyelid = '{self.__od_eyelid}', Od_lacrimal_organs = '{self.__od_lacrimal_organs}',\
                                Od_conjunctiva = '{self.__od_conjunctiva}', Od_discharge = '{self.__od_discharge}', Od_iris = '{self.__od_iris}',\
                                Od_anterior_chamber = '{self.__od_anterior_chamber}', Od_refractive_medium = '{self.__od_refractive_medium}', Od_optic_disk = '{self.__od_optic_disk}',\
                                Od_vessels = '{self.__od_vessels}', Od_macular_reflex = '{self.__od_macular_reflex}', Od_visible_periphery = '{self.__od_visible_periphery}',\
                                Od_diagnosis = '{self.__od_diagnosis}', Od_icd_code = '{self.__od_icd_code}', Os_eye_position = '{self.__os_eye_position}', Os_oi = '{self.__os_oi}', Os_eyelid = '{self.__os_eyelid}',\
                                Os_lacrimal_organs = '{self.__os_lacrimal_organs}', Os_conjunctiva = '{self.__os_conjunctiva}', Os_discharge = '{self.__os_discharge}',\
                                Os_iris = '{self.__os_iris}', Os_anterior_chamber = '{self.__os_anterior_chamber}',\
                                Os_refractive_medium = '{self.__os_refractive_medium}', Os_optic_disk = '{self.__os_optic_disk}', Os_vessels = '{self.__os_vessels}',\
                                Os_macular_reflex = '{self.__os_macular_reflex}', Os_visible_periphery = '{self.__os_visible_periphery}', Os_diagnosis = '{self.__os_diagnosis}', Os_icd_code = '{self.__os_icd_code}',\
                                Recommendations = '{self.__recommendations}', Direction_to_aokb = '{self.__direction_to_aokb}', Reappointment = '{self.__reappointment}',\
                                Reappointment_time = '{self.__reappointment_time}'\
                                WHERE Id = {self.__id}")

    def delete_examination_from_database(self, people: People = None):
        person_id = self.__db.execute(f"SELECT Person_id FROM Examinations WHERE Id = {self.__id}").fetchone()[0]

        self.__db.execute(f"DELETE FROM Examinations WHERE Id = {self.__id}")

        person_records_count = self.__db.execute(f"SELECT Count(Id) FROM Examinations WHERE Person_id = {person_id}").fetchone()[0]
        if int(person_records_count) == 0:
            people.delete_person(person_id)


class ListOfExaminations():
    def __init__(self, db: Database):
        self.__db = db
        examinations = list(map(lambda x: list(x), self.__db.execute("SELECT * FROM Examinations").fetchall()))
        self.__examinations = {}
        for examination in examinations:
            self.__examinations[examination[0]] = Examination(person_id=examination[1],
                                                                eyesight_without_od=examination[2],
                                                                eyesight_without_os=examination[3],
                                                                eyesight_with_od=examination[4],
                                                                eyesight_with_od_sph=examination[5],
                                                                eyesight_with_od_cyl=examination[6],
                                                                eyesight_with_od_ax=examination[7],
                                                                eyesight_with_os=examination[8],
                                                                eyesight_with_os_sph=examination[9],
                                                                eyesight_with_os_cyl=examination[10],
                                                                eyesight_with_os_ax=examination[11],
                                                                schiascopy_od=examination[12],
                                                                schiascopy_os=examination[13],
                                                                glasses_od_sph=examination[14],
                                                                glasses_od_cyl=examination[15],
                                                                glasses_od_ax=examination[16],
                                                                glasses_os_sph=examination[17],
                                                                glasses_os_cyl=examination[18],
                                                                glasses_os_ax=examination[19],
                                                                glasses_dpp=examination[20],
                                                                diagnosis_subscription=examination[21],
                                                                visit_date=examination[22],
                                                                complaints=examination[23],
                                                                disease_anamnesis=examination[24],
                                                                life_anamnesis=examination[25],
                                                                eyesight_type=examination[26],
                                                                relative_accommodation_reserve=examination[27],
                                                                schober_test=examination[28],
                                                                pupils=examination[29],
                                                                od_eye_position=examination[30],
                                                                od_oi=examination[31],
                                                                od_eyelid=examination[32],
                                                                od_lacrimal_organs=examination[33],
                                                                od_conjunctiva=examination[34],
                                                                od_discharge=examination[35],
                                                                od_iris=examination[36],
                                                                od_anterior_chamber=examination[37],
                                                                od_refractive_medium=examination[38],
                                                                od_optic_disk=examination[39],
                                                                od_vessels=examination[40],
                                                                od_macular_reflex=examination[41],
                                                                od_visible_periphery=examination[42],
                                                                od_diagnosis=examination[43],
                                                                od_icd_code=examination[44],
                                                                os_eye_position=examination[45],
                                                                os_oi=examination[46],
                                                                os_eyelid=examination[47],
                                                                os_lacrimal_organs=examination[48],
                                                                os_conjunctiva=examination[49],
                                                                os_discharge=examination[50],
                                                                os_iris=examination[51],
                                                                os_anterior_chamber=examination[52],
                                                                os_refractive_medium=examination[53],
                                                                os_optic_disk=examination[54],
                                                                os_vessels=examination[55],
                                                                os_macular_reflex=examination[56],
                                                                os_visible_periphery=examination[57],
                                                                os_diagnosis=examination[58],
                                                                os_icd_code=examination[59],
                                                                recommendations=examination[60],
                                                                direction_to_aokb=examination[61],
                                                                reappointment=examination[62],
                                                                reappointment_time=examination[63],
                                                                id=examination[0],
                                                                db=self.__db
                                                                )
            
    def add_examination(self, person_id, eyesight_without_od, eyesight_without_os, eyesight_with_od, eyesight_with_od_sph,
                                eyesight_with_od_cyl, eyesight_with_od_ax, eyesight_with_os, eyesight_with_os_sph,
                                eyesight_with_os_cyl, eyesight_with_os_ax, schiascopy_od, 
                                schiascopy_os, glasses_od_sph, glasses_od_cyl, glasses_od_ax,
                                glasses_os_sph, glasses_os_cyl, glasses_os_ax, glasses_dpp, diagnosis_subscription, visit_date, complaints=None,
                                disease_anamnesis=None, life_anamnesis=None, eyesight_type=None, relative_accommodation_reserve=None, schober_test=None, pupils=None,
                                od_eye_position=None, od_oi=None, od_eyelid=None, od_lacrimal_organs=None, od_conjunctiva=None, od_discharge=None,
                                od_iris=None, od_anterior_chamber=None, od_refractive_medium=None, od_optic_disk=None, od_vessels=None,
                                od_macular_reflex=None, od_visible_periphery=None, od_diagnosis=None, od_icd_code=None, os_eye_position=None, os_oi=None, os_eyelid=None,
                                os_lacrimal_organs=None, os_conjunctiva=None, os_discharge=None, os_iris=None, os_anterior_chamber=None,
                                os_refractive_medium=None, os_optic_disk=None, os_vessels=None, os_macular_reflex=None, os_visible_periphery=None,
                                os_diagnosis=None, os_icd_code=None, recommendations=None, direction_to_aokb=None, reappointment=None, reappointment_time=None):
        new_examination = Examination(person_id=person_id,
                                    eyesight_without_od=eyesight_without_od,
                                    eyesight_without_os=eyesight_without_os,
                                    eyesight_with_od=eyesight_with_od,
                                    eyesight_with_od_sph=eyesight_with_od_sph,
                                    eyesight_with_od_cyl=eyesight_with_od_cyl,
                                    eyesight_with_od_ax=eyesight_with_od_ax,
                                    eyesight_with_os=eyesight_with_os,
                                    eyesight_with_os_sph=eyesight_with_os_sph,
                                    eyesight_with_os_cyl=eyesight_with_os_cyl,
                                    eyesight_with_os_ax=eyesight_with_os_ax,
                                    schiascopy_od=schiascopy_od,
                                    schiascopy_os=schiascopy_os,
                                    glasses_od_sph=glasses_od_sph,
                                    glasses_od_cyl=glasses_od_cyl,
                                    glasses_od_ax=glasses_od_ax,
                                    glasses_os_sph=glasses_os_sph,
                                    glasses_os_cyl=glasses_os_cyl,
                                    glasses_os_ax=glasses_os_ax,
                                    glasses_dpp=glasses_dpp,
                                    diagnosis_subscription=diagnosis_subscription,
                                    visit_date=visit_date,
                                    complaints=complaints,
                                    disease_anamnesis=disease_anamnesis,
                                    life_anamnesis=life_anamnesis,
                                    eyesight_type=eyesight_type,
                                    relative_accommodation_reserve=relative_accommodation_reserve,
                                    schober_test=schober_test,
                                    pupils=pupils,
                                    od_eye_position=od_eye_position,
                                    od_oi=od_oi,
                                    od_eyelid=od_eyelid, 
                                    od_lacrimal_organs=od_lacrimal_organs, 
                                    od_conjunctiva=od_conjunctiva, 
                                    od_discharge=od_discharge, 
                                    od_iris=od_iris,
                                    od_anterior_chamber=od_anterior_chamber, 
                                    od_refractive_medium=od_refractive_medium, 
                                    od_optic_disk=od_optic_disk, 
                                    od_vessels=od_vessels, 
                                    od_macular_reflex=od_macular_reflex, 
                                    od_visible_periphery=od_visible_periphery, 
                                    od_diagnosis=od_diagnosis,
                                    od_icd_code=od_icd_code,
                                    os_eye_position=os_eye_position,
                                    os_oi=os_oi, 
                                    os_eyelid=os_eyelid,
                                    os_lacrimal_organs=os_lacrimal_organs, 
                                    os_conjunctiva=os_conjunctiva, 
                                    os_discharge=os_discharge, 
                                    os_iris=os_iris,
                                    os_anterior_chamber=os_anterior_chamber, 
                                    os_refractive_medium=os_refractive_medium, 
                                    os_optic_disk=os_optic_disk, 
                                    os_vessels=os_vessels, 
                                    os_macular_reflex=os_macular_reflex, 
                                    os_visible_periphery=os_visible_periphery, 
                                    os_diagnosis=os_diagnosis,
                                    os_icd_code=os_icd_code,
                                    recommendations=recommendations,
                                    direction_to_aokb=direction_to_aokb,
                                    reappointment=reappointment,
                                    reappointment_time=reappointment_time,
                                    db=self.__db
                                    )
        self.__examinations[new_examination.id] = new_examination
        self.__examinations[new_examination.id].add_examination_to_database()

    def update_examination(self, id, person_id, eyesight_without_od, eyesight_without_os, eyesight_with_od, eyesight_with_od_sph,
                                eyesight_with_od_cyl, eyesight_with_od_ax, eyesight_with_os, eyesight_with_os_sph,
                                eyesight_with_os_cyl, eyesight_with_os_ax, schiascopy_od,
                                schiascopy_os, glasses_od_sph, glasses_od_cyl, glasses_od_ax,
                                glasses_os_sph, glasses_os_cyl, glasses_os_ax, glasses_dpp, diagnosis_subscription, complaints,
                                disease_anamnesis=None, life_anamnesis=None, eyesight_type=None, relative_accommodation_reserve=None, schober_test=None, pupils=None,
                                od_eye_position=None, od_oi=None, od_eyelid=None, od_lacrimal_organs=None, od_conjunctiva=None, od_discharge=None,
                                od_iris=None, od_anterior_chamber=None, od_refractive_medium=None, od_optic_disk=None, od_vessels=None,
                                od_macular_reflex=None, od_visible_periphery=None, od_diagnosis=None, od_icd_code=None, os_eye_position=None, os_oi=None, os_eyelid=None,
                                os_lacrimal_organs=None, os_conjunctiva=None, os_discharge=None, os_iris=None, os_anterior_chamber=None,
                                os_refractive_medium=None, os_optic_disk=None, os_vessels=None, os_macular_reflex=None, os_visible_periphery=None,
                                os_diagnosis=None, os_icd_code=None, recommendations=None, direction_to_aokb=None, reappointment=None, reappointment_time=None):
        self.__examinations[id].update_examination_data(id, person_id, eyesight_without_od, eyesight_without_os, eyesight_with_od, eyesight_with_od_sph,
                                eyesight_with_od_cyl, eyesight_with_od_ax, eyesight_with_os, eyesight_with_os_sph,
                                eyesight_with_os_cyl, eyesight_with_os_ax, schiascopy_od,
                                schiascopy_os, glasses_od_sph, glasses_od_cyl, glasses_od_ax,
                                glasses_os_sph, glasses_os_cyl, glasses_os_ax, glasses_dpp, diagnosis_subscription, complaints,
                                disease_anamnesis, life_anamnesis, eyesight_type, relative_accommodation_reserve, schober_test, pupils,
                                od_eye_position, od_oi, od_eyelid, od_lacrimal_organs, od_conjunctiva, od_discharge, 
                                od_iris, od_anterior_chamber, od_refractive_medium, od_optic_disk, od_vessels, 
                                od_macular_reflex, od_visible_periphery, od_diagnosis, od_icd_code, os_eye_position, os_oi, os_eyelid, 
                                os_lacrimal_organs, os_conjunctiva, os_discharge, os_iris, os_anterior_chamber, 
                                os_refractive_medium, os_optic_disk, os_vessels, os_macular_reflex, os_visible_periphery, 
                                os_diagnosis, os_icd_code, recommendations, direction_to_aokb, reappointment, reappointment_time)
        self.__examinations[id].update_data_in_database()

    def get_examination_by_id(self, id) -> Examination:
        if id:
            return self.__examinations[id]
        
    def get_examinations_by_person_id(self, person_id):
        if person_id and type(person_id) != list:
            person_id = int(person_id)
            examinations = []
            for id in self.__examinations:
                if self.__examinations[id].person_id == person_id:
                    examinations.append(self.__examinations[id])
            return examinations
        elif person_id and type(person_id) == list:
            id_for_statement = ''
            for id in person_id:
                id_for_statement += "'"+str(id)+"', "
            id_for_statement = id_for_statement[:-2]
            return list(map(lambda x: self.__examinations[x[0]], self.__db.execute(f"SELECT Id FROM Examinations WHERE Person_id IN ({id_for_statement})").fetchall()))
        
    def get_examination_by_person_id_and_examination_datetime(self, person_id: int, visit_date: str) -> Examination:
        match_examinations = self.get_examinations_by_person_id(person_id)
        if not match_examinations or not person_id:
            return
        else:
            for examination in match_examinations:
                if examination.visit_date == visit_date:
                    return examination

    def delete_examination(self, id, people: People = None):
        self.__examinations[id].delete_examination_from_database(people)
        self.__examinations.pop(id)

    def get_people_ids(self):
        ids = list(map(lambda x: x[0], self.__db.execute("SELECT Person_id FROM Examinations").fetchall()))
        return ids


class ExaminationTemplates():
    def __init__(self, db: Database):
        exams = ListOfExaminations(db)
        self.__templates = {
            'Здоровый осмотр': Examination(
                                    person_id=56,
                                    eyesight_without_od=1.0,
                                    eyesight_without_os=1.0,
                                    eyesight_with_od=1.0,
                                    eyesight_with_od_sph=0.0,
                                    eyesight_with_od_cyl=0.0,
                                    eyesight_with_od_ax=0,
                                    eyesight_with_os=1.0,
                                    eyesight_with_os_sph=0.0,
                                    eyesight_with_os_cyl=0.0,
                                    eyesight_with_os_ax=0,
                                    schiascopy_od='Em',
                                    schiascopy_os='Em',
                                    glasses_od_sph=0.0,
                                    glasses_od_cyl=0.0,
                                    glasses_od_ax=0,
                                    glasses_os_sph=0.0,
                                    glasses_os_cyl=0.0,
                                    glasses_os_ax=0,
                                    glasses_dpp=0,
                                    diagnosis_subscription='',
                                    visit_date='23.03.2025 13:09',
                                    complaints='',
                                    disease_anamnesis='',
                                    life_anamnesis='',
                                    eyesight_type='',
                                    relative_accommodation_reserve=-1.0,
                                    schober_test='',
                                    pupils='',
                                    od_eye_position='ортофория',
                                    od_oi='спокойны',
                                    od_eyelid='без изменений',
                                    od_lacrimal_organs='без изменений',
                                    od_conjunctiva='бледная, розовая',
                                    od_discharge='отсутствует',
                                    od_iris='структура сохранена, рисунок четкий',
                                    od_anterior_chamber='глубина обычная',
                                    od_refractive_medium='прозрачные',
                                    od_optic_disk='бледно-розовый, границы четкие',
                                    od_vessels='норма',
                                    od_macular_reflex='сохранен',
                                    od_visible_periphery='без особенностей',
                                    od_diagnosis='Здоров',
                                    od_icd_code='u13.1',
                                    os_eye_position='ортофория',
                                    os_oi='спокойны',
                                    os_eyelid='без изменений',
                                    os_lacrimal_organs='без изменений',
                                    os_conjunctiva='бледная, розовая',
                                    os_discharge='отсутствует',
                                    os_iris='структура сохранена, рисунок четкий',
                                    os_anterior_chamber='глубина обычная',
                                    os_refractive_medium='прозрачные',
                                    os_optic_disk='бледно-розовый, границы четкие',
                                    os_vessels='норма',
                                    os_macular_reflex='сохранен',
                                    os_visible_periphery='без особенностей',
                                    os_diagnosis='Здоров',
                                    os_icd_code='u13.2',
                                    recommendations='гигиена зрения',
                                    direction_to_aokb=0,
                                    reappointment=0,
                                    reappointment_time='',
                                    id=104,
                                    db=None
                                ),
            'Миопия': Examination(
                                    person_id=57,
                                    eyesight_without_od=1.0,
                                    eyesight_without_os=1.0,
                                    eyesight_with_od=1.0,
                                    eyesight_with_od_sph=0.0,
                                    eyesight_with_od_cyl=0.0,
                                    eyesight_with_od_ax=0,
                                    eyesight_with_os=1.0,
                                    eyesight_with_os_sph=0.0,
                                    eyesight_with_os_cyl=0.0,
                                    eyesight_with_os_ax=0,
                                    schiascopy_od='M 1.0',
                                    schiascopy_os='M 1.0',
                                    glasses_od_sph=0.0,
                                    glasses_od_cyl=0.0,
                                    glasses_od_ax=0,
                                    glasses_os_sph=0.0,
                                    glasses_os_cyl=0.0,
                                    glasses_os_ax=0,
                                    glasses_dpp=0,
                                    diagnosis_subscription='',
                                    visit_date='23.03.2025 13:16',
                                    complaints='ухудшение зрения в даль',
                                    disease_anamnesis='',
                                    life_anamnesis='',
                                    eyesight_type='',
                                    relative_accommodation_reserve=-1.0,
                                    schober_test='',
                                    pupils='',
                                    od_eye_position='ортофория',
                                    od_oi='спокойны',
                                    od_eyelid='без изменений',
                                    od_lacrimal_organs='без изменений',
                                    od_conjunctiva='бледная, розовая',
                                    od_discharge='отсутствует',
                                    od_iris='структура сохранена, рисунок четкий',
                                    od_anterior_chamber='глубина обычная',
                                    od_refractive_medium='прозрачные',
                                    od_optic_disk='бледно-розовый, границы четкие, миопический конус',
                                    od_vessels='норма',
                                    od_macular_reflex='сохранен',
                                    od_visible_periphery='без особенностей',
                                    od_diagnosis='миопия слабой степени школьная изометропическая неосложненная стационарная ',
                                    od_icd_code='u13.1',
                                    os_eye_position='ортофория',
                                    os_oi='спокойны',
                                    os_eyelid='без изменений',
                                    os_lacrimal_organs='без изменений',
                                    os_conjunctiva='бледная, розовая',
                                    os_discharge='отсутствует',
                                    os_iris='структура сохранена, рисунок четкий',
                                    os_anterior_chamber='глубина обычная',
                                    os_refractive_medium='прозрачные',
                                    os_optic_disk='бледно-розовый, границы четкие, миопический конус',
                                    os_vessels='норма',
                                    os_macular_reflex='сохранен',
                                    os_visible_periphery='без особенностей',
                                    os_diagnosis='миопия слабой степени школьная изометропическая неосложненная стационарная ',
                                    os_icd_code='u13.2',
                                    recommendations='соблюдение зрительного режима, гимнастика для глаз (по Аветисову), очки для дали, ограничение зрительной нагрузки (использование гаджетов не более 30 минут в день), исключить гаджеты, прогулки на свежем воздухе не менее 2 часов в день, посадка в школе не далее 2 парты',
                                    direction_to_aokb=0,
                                    reappointment=1,
                                    reappointment_time='через 6 месяцев',
                                    id=105,
                                    db=None
                                ),
            'Гиперметропия': Examination(
                                    person_id=58,
                                    eyesight_without_od=1.0,
                                    eyesight_without_os=1.0,
                                    eyesight_with_od=1.0,
                                    eyesight_with_od_sph=0.0,
                                    eyesight_with_od_cyl=0.0,
                                    eyesight_with_od_ax=0,
                                    eyesight_with_os=1.0,
                                    eyesight_with_os_sph=0.0,
                                    eyesight_with_os_cyl=0.0,
                                    eyesight_with_os_ax=0,
                                    schiascopy_od='Hm 1.0',
                                    schiascopy_os='Hm 1.0',
                                    glasses_od_sph=0.0,
                                    glasses_od_cyl=0.0,
                                    glasses_od_ax=0,
                                    glasses_os_sph=0.0,
                                    glasses_os_cyl=0.0,
                                    glasses_os_ax=0,
                                    glasses_dpp=0,
                                    diagnosis_subscription='',
                                    visit_date='23.03.2025 13:20',
                                    complaints='',
                                    disease_anamnesis='',
                                    life_anamnesis='',
                                    eyesight_type='',
                                    relative_accommodation_reserve=-1.0,
                                    schober_test='',
                                    pupils='',
                                    od_eye_position='ортофория',
                                    od_oi='спокойны',
                                    od_eyelid='без изменений',
                                    od_lacrimal_organs='без изменений',
                                    od_conjunctiva='бледная, розовая',
                                    od_discharge='отсутствует',
                                    od_iris='структура сохранена, рисунок четкий',
                                    od_anterior_chamber='глубина обычная',
                                    od_refractive_medium='прозрачные',
                                    od_optic_disk='бледно-розовый, границы четкие',
                                    od_vessels='норма',
                                    od_macular_reflex='сохранен',
                                    od_visible_periphery='без особенностей',
                                    od_diagnosis='Гиперметропия слабой степени',
                                    od_icd_code='u13.1',
                                    os_eye_position='ортофория',
                                    os_oi='спокойны',
                                    os_eyelid='без изменений',
                                    os_lacrimal_organs='без изменений',
                                    os_conjunctiva='бледная, розовая',
                                    os_discharge='отсутствует',
                                    os_iris='структура сохранена, рисунок четкий',
                                    os_anterior_chamber='глубина обычная',
                                    os_refractive_medium='прозрачные',
                                    os_optic_disk='бледно-розовый, границы четкие',
                                    os_vessels='норма',
                                    os_macular_reflex='сохранен',
                                    os_visible_periphery='без особенностей',
                                    os_diagnosis='Гиперметропия слабой степени',
                                    os_icd_code='u13.2',
                                    recommendations='соблюдение зрительного режима, очки для работы, ограничение зрительной нагрузки (использование гаджетов не более 30 минут в день), прогулки на свежем воздухе не менее 2 часов в день',
                                    direction_to_aokb=0,
                                    reappointment=1,
                                    reappointment_time='через 6 месяцев',
                                    id=106,
                                    db=None
                                ),
            'Конъюнктивит': Examination(
                                    person_id=59,
                                    eyesight_without_od=1.0,
                                    eyesight_without_os=1.0,
                                    eyesight_with_od=1.0,
                                    eyesight_with_od_sph=0.0,
                                    eyesight_with_od_cyl=0.0,
                                    eyesight_with_od_ax=0,
                                    eyesight_with_os=1.0,
                                    eyesight_with_os_sph=0.0,
                                    eyesight_with_os_cyl=0.0,
                                    eyesight_with_os_ax=0,
                                    schiascopy_od='Em 0',
                                    schiascopy_os='Em 0',
                                    glasses_od_sph=0.0,
                                    glasses_od_cyl=0.0,
                                    glasses_od_ax=0,
                                    glasses_os_sph=0.0,
                                    glasses_os_cyl=0.0,
                                    glasses_os_ax=0,
                                    glasses_dpp=0,
                                    diagnosis_subscription='',
                                    visit_date='23.03.2025 13:26',
                                    complaints='боль в глазах, слезотечение, покраснение глаз, выделения из глаз, зуд в глазах',
                                    disease_anamnesis='',
                                    life_anamnesis='',
                                    eyesight_type='',
                                    relative_accommodation_reserve=-1.0,
                                    schober_test='',
                                    pupils='',
                                    od_eye_position='ортофория',
                                    od_oi='инъекция слабая',
                                    od_eyelid='отек, гиперемия века',
                                    od_lacrimal_organs='слезостояние',
                                    od_conjunctiva='инъекция умеренная, сосочки',
                                    od_discharge='слизисто-гнойное',
                                    od_iris='структура сохранена, рисунок четкий',
                                    od_anterior_chamber='глубина обычная',
                                    od_refractive_medium='прозрачные',
                                    od_optic_disk='бледно-розовый, границы четкие',
                                    od_vessels='норма',
                                    od_macular_reflex='сохранен',
                                    od_visible_periphery='без особенностей',
                                    od_diagnosis='конъюнктивит (острый)',
                                    od_icd_code='u13.1',
                                    os_eye_position='ортофория',
                                    os_oi='инъекция слабая',
                                    os_eyelid='отек, гиперемия века',
                                    os_lacrimal_organs='слезостояние',
                                    os_conjunctiva='инъекция умеренная, сосочки',
                                    os_discharge='слизисто-гнойное',
                                    os_iris='структура сохранена, рисунок четкий',
                                    os_anterior_chamber='глубина обычная',
                                    os_refractive_medium='прозрачные',
                                    os_optic_disk='бледно-розовый, границы четкие',
                                    os_vessels='норма',
                                    os_macular_reflex='сохранен',
                                    os_visible_periphery='без особенностей',
                                    os_diagnosis='конъюнктивит (острый)',
                                    os_icd_code='u13.2',
                                    recommendations='Окомистин по 1 капле 3 раза в день 7-10 дней, Офтаквикс по 1 капле 3 раза в день 7 дней',
                                    direction_to_aokb=0,
                                    reappointment=1,
                                    reappointment_time='через 10 дней',
                                    id=107,
                                    db=None
                                ),
            'Осмотр новорождённого': Examination(
                                    person_id=60,
                                    eyesight_without_od=0.0,
                                    eyesight_without_os=0.0,
                                    eyesight_with_od=0.0,
                                    eyesight_with_od_sph=0.0,
                                    eyesight_with_od_cyl=0.0,
                                    eyesight_with_od_ax=0,
                                    eyesight_with_os=0.0,
                                    eyesight_with_os_sph=0.0,
                                    eyesight_with_os_cyl=0.0,
                                    eyesight_with_os_ax=0,
                                    schiascopy_od='Hm 1.0',
                                    schiascopy_os='Hm 1.0',
                                    glasses_od_sph=0.0,
                                    glasses_od_cyl=0.0,
                                    glasses_od_ax=0,
                                    glasses_os_sph=0.0,
                                    glasses_os_cyl=0.0,
                                    glasses_os_ax=0,
                                    glasses_dpp=0,
                                    diagnosis_subscription='',
                                    visit_date='23.03.2025 13:33',
                                    complaints='активно нет',
                                    disease_anamnesis='',
                                    life_anamnesis='',
                                    eyesight_type='',
                                    relative_accommodation_reserve=-1.0,
                                    schober_test='',
                                    pupils='',
                                    od_eye_position='ближе к правильному',
                                    od_oi='спокойны',
                                    od_eyelid='без изменений',
                                    od_lacrimal_organs='без изменений',
                                    od_conjunctiva='бледная, розовая',
                                    od_discharge='отсутствует',
                                    od_iris='структура сохранена, рисунок четкий',
                                    od_anterior_chamber='глубина обычная',
                                    od_refractive_medium='прозрачные',
                                    od_optic_disk='бледно-розовый, границы четкие',
                                    od_vessels='ближе к норме',
                                    od_macular_reflex='сохранен',
                                    od_visible_periphery='детально не осмотрена',
                                    od_diagnosis='Гиперметропия средней степени (физиологическая норма)',
                                    od_icd_code='u13.1',
                                    os_eye_position='ближе к правильному',
                                    os_oi='спокойны',
                                    os_eyelid='без изменений',
                                    os_lacrimal_organs='без изменений',
                                    os_conjunctiva='бледная, розовая',
                                    os_discharge='отсутствует',
                                    os_iris='структура сохранена, рисунок четкий',
                                    os_anterior_chamber='глубина обычная',
                                    os_refractive_medium='прозрачные',
                                    os_optic_disk='бледно-розовый, границы четкие',
                                    os_vessels='ближе к норме',
                                    os_macular_reflex='сохранен',
                                    os_visible_periphery='детально не осмотрена',
                                    os_diagnosis='Гиперметропия средней степени (физиологическая норма)',
                                    os_icd_code='u13.2',
                                    recommendations='гигиена (протирать веки ватным диском,смоченным теплой водой в направлении от наружного угла к внутреннему)',
                                    direction_to_aokb=0,
                                    reappointment=1,
                                    reappointment_time='в 1 год',
                                    id=108,
                                    db=None
                                ),
            'Блефарит': Examination(
                                    person_id=61,
                                    eyesight_without_od=1.0,
                                    eyesight_without_os=1.0,
                                    eyesight_with_od=1.0,
                                    eyesight_with_od_sph=0.0,
                                    eyesight_with_od_cyl=0.0,
                                    eyesight_with_od_ax=0,
                                    eyesight_with_os=1.0,
                                    eyesight_with_os_sph=0.0,
                                    eyesight_with_os_cyl=0.0,
                                    eyesight_with_os_ax=0,
                                    schiascopy_od='Em 0',
                                    schiascopy_os='Em 0',
                                    glasses_od_sph=0.0,
                                    glasses_od_cyl=0.0,
                                    glasses_od_ax=0,
                                    glasses_os_sph=0.0,
                                    glasses_os_cyl=0.0,
                                    glasses_os_ax=0,
                                    glasses_dpp=0,
                                    diagnosis_subscription='',
                                    visit_date='23.03.2025 13:40',
                                    complaints='зуд в глазах, чувство дискомфорта',
                                    disease_anamnesis='',
                                    life_anamnesis='',
                                    eyesight_type='',
                                    relative_accommodation_reserve=-1.0,
                                    schober_test='',
                                    pupils='',
                                    od_eye_position='ортофория',
                                    od_oi='инъекция слабая',
                                    od_eyelid='гиперемия ресничн. края, закупорка мейбом. желёз',
                                    od_lacrimal_organs='без изменений',
                                    od_conjunctiva='инъекция слабая',
                                    od_discharge='скудное слизистое',
                                    od_iris='структура сохранена, рисунок четкий',
                                    od_anterior_chamber='глубина обычная',
                                    od_refractive_medium='прозрачные',
                                    od_optic_disk='бледно-розовый, границы четкие',
                                    od_vessels='норма',
                                    od_macular_reflex='сохранен',
                                    od_visible_periphery='без особенностей',
                                    od_diagnosis='гиперметропия слабой степени',
                                    od_icd_code='u13.1',
                                    os_eye_position='ортофория',
                                    os_oi='инъекция слабая',
                                    os_eyelid='гиперемия ресничн. края, закупорка мейбом. желёз',
                                    os_lacrimal_organs='без изменений',
                                    os_conjunctiva='инъекция слабая',
                                    os_discharge='скудное слизистое',
                                    os_iris='структура сохранена, рисунок четкий',
                                    os_anterior_chamber='глубина обычная',
                                    os_refractive_medium='прозрачные',
                                    os_optic_disk='бледно-розовый, границы четкие',
                                    os_vessels='норма',
                                    os_macular_reflex='сохранен',
                                    os_visible_periphery='без особенностей',
                                    os_diagnosis='гиперметропия слабой степени',
                                    os_icd_code='u13.2',
                                    recommendations='Массаж век (греем окологлазничную область -> массаж век -> Блефарогель №1 на ресничный край -> капли:\nОкомистин по 1 капле 3 раза в день 7-10 дней\nОфтаквикс по 1 капле 3 раза в день 7 дней)',
                                    direction_to_aokb=0,
                                    reappointment=1,
                                    reappointment_time='через 14 дней',
                                    id=109,
                                    db=None
                                ),
            'ПИНА': Examination(
                                    person_id=62,
                                    eyesight_without_od=1.0,
                                    eyesight_without_os=1.0,
                                    eyesight_with_od=1.0,
                                    eyesight_with_od_sph=0.0,
                                    eyesight_with_od_cyl=0.0,
                                    eyesight_with_od_ax=0,
                                    eyesight_with_os=1.0,
                                    eyesight_with_os_sph=0.0,
                                    eyesight_with_os_cyl=0.0,
                                    eyesight_with_os_ax=0,
                                    schiascopy_od='Em 0',
                                    schiascopy_os='Em 0',
                                    glasses_od_sph=0.0,
                                    glasses_od_cyl=0.0,
                                    glasses_od_ax=0,
                                    glasses_os_sph=0.0,
                                    glasses_os_cyl=0.0,
                                    glasses_os_ax=0,
                                    glasses_dpp=0,
                                    diagnosis_subscription='',
                                    visit_date='23.03.2025 13:46',
                                    complaints='ухудшение зрения в даль, быстрая утомляемость глаз',
                                    disease_anamnesis='',
                                    life_anamnesis='',
                                    eyesight_type='',
                                    relative_accommodation_reserve=-1.0,
                                    schober_test='',
                                    pupils='',
                                    od_eye_position='ортофория',
                                    od_oi='спокойны',
                                    od_eyelid='без изменений',
                                    od_lacrimal_organs='без изменений',
                                    od_conjunctiva='бледная, розовая',
                                    od_discharge='отсутствует',
                                    od_iris='структура сохранена',
                                    od_anterior_chamber='глубина обычная',
                                    od_refractive_medium='прозрачные',
                                    od_optic_disk='бледно-розовый, границы четкие',
                                    od_vessels='норма',
                                    od_macular_reflex='сохранен',
                                    od_visible_periphery='без особенностей',
                                    od_diagnosis='Привычно-избыточное напряжение аккомодации',
                                    od_icd_code='u13.1',
                                    os_eye_position='ортофория',
                                    os_oi='спокойны',
                                    os_eyelid='без изменений',
                                    os_lacrimal_organs='без изменений',
                                    os_conjunctiva='бледная, розовая',
                                    os_discharge='отсутствует',
                                    os_iris='структура сохранена',
                                    os_anterior_chamber='глубина обычная',
                                    os_refractive_medium='прозрачные',
                                    os_optic_disk='бледно-розовый, границы четкие',
                                    os_vessels='норма',
                                    os_macular_reflex='сохранен',
                                    os_visible_periphery='без особенностей',
                                    os_diagnosis='Привычно-избыточное напряжение аккомодации',
                                    os_icd_code='u13.2',
                                    recommendations='Ирифрин 2,5% по 1 капле на ночь 1 месяц (курс 1 раз в 3 месяца), соблюдение зрительного режима, гимнастика для глаз (по Аветисову), ограничение зрительной нагрузки (использование гаджетов не более 30 минут в день), исключить гаджеты, прогулки на свежем воздухе не менее 2 часов в день',
                                    direction_to_aokb=0,
                                    reappointment=1,
                                    reappointment_time='через 1 месяц',
                                    id=110,
                                    db=None
                                ),
            'Недостаточность слёзных канальцев': Examination(
                                    person_id=63,
                                    eyesight_without_od=1.0,
                                    eyesight_without_os=1.0,
                                    eyesight_with_od=1.0,
                                    eyesight_with_od_sph=0.0,
                                    eyesight_with_od_cyl=0.0,
                                    eyesight_with_od_ax=0,
                                    eyesight_with_os=1.0,
                                    eyesight_with_os_sph=0.0,
                                    eyesight_with_os_cyl=0.0,
                                    eyesight_with_os_ax=0,
                                    schiascopy_od='M 1.0',
                                    schiascopy_os='M 1.0',
                                    glasses_od_sph=0.0,
                                    glasses_od_cyl=0.0,
                                    glasses_od_ax=0,
                                    glasses_os_sph=0.0,
                                    glasses_os_cyl=0.0,
                                    glasses_os_ax=0,
                                    glasses_dpp=0,
                                    diagnosis_subscription='',
                                    visit_date='23.03.2025 13:55',
                                    complaints='слезотечение, слезостояние',
                                    disease_anamnesis='',
                                    life_anamnesis='',
                                    eyesight_type='',
                                    relative_accommodation_reserve=-1.0,
                                    schober_test='',
                                    pupils='',
                                    od_eye_position='ортофория',
                                    od_oi='инъекция слабая',
                                    od_eyelid='без изменений',
                                    od_lacrimal_organs='слезостояние, при надавливании на слёзный мешок слизисто-гнойное отделяемое',
                                    od_conjunctiva='инъекция слабая',
                                    od_discharge='умеренное слизистое',
                                    od_iris='структура сохранена, рисунок четкий',
                                    od_anterior_chamber='глубина обычная',
                                    od_refractive_medium='прозрачные',
                                    od_optic_disk='бледно-розовый, границы четкие',
                                    od_vessels='норма',
                                    od_macular_reflex='сохранен',
                                    od_visible_periphery='не осмотрена',
                                    od_diagnosis='Недостаточность слезных канальцев',
                                    od_icd_code='u13.1',
                                    os_eye_position='ортофория',
                                    os_oi='инъекция слабая',
                                    os_eyelid='без изменений',
                                    os_lacrimal_organs='слезостояние, при надавливании на слёзный мешок слизисто-гнойное отделяемое',
                                    os_conjunctiva='инъекция слабая',
                                    os_discharge='умеренное слизистое',
                                    os_iris='структура сохранена, рисунок четкий',
                                    os_anterior_chamber='глубина обычная',
                                    os_refractive_medium='прозрачные',
                                    os_optic_disk='бледно-розовый, границы четкие',
                                    os_vessels='норма',
                                    os_macular_reflex='сохранен',
                                    os_visible_periphery='не осмотрена',
                                    os_diagnosis='Недостаточность слезных канальцев',
                                    os_icd_code='u13.2',
                                    recommendations='Массаж слезного мешка (нисходящий толчкообразный) не менее 100 раз 4 раза в день, длительно\nОкомистин по 1 капле 3 раза в день 7-10 дней, Данцил по 1 капле 3 раза в день 7 дней',
                                    direction_to_aokb=0,
                                    reappointment=1,
                                    reappointment_time='через 14 дней',
                                    id=111,
                                    db=None
                                ),
            'Empty': Examination(
                                    person_id=64,
                                    eyesight_without_od=1.0,
                                    eyesight_without_os=1.0,
                                    eyesight_with_od=1.0,
                                    eyesight_with_od_sph=0.0,
                                    eyesight_with_od_cyl=0.0,
                                    eyesight_with_od_ax=0,
                                    eyesight_with_os=1.0,
                                    eyesight_with_os_sph=0.0,
                                    eyesight_with_os_cyl=0.0,
                                    eyesight_with_os_ax=0,
                                    schiascopy_od='',
                                    schiascopy_os='',
                                    glasses_od_sph=0.0,
                                    glasses_od_cyl=0.0,
                                    glasses_od_ax=0,
                                    glasses_os_sph=0.0,
                                    glasses_os_cyl=0.0,
                                    glasses_os_ax=0,
                                    glasses_dpp=0,
                                    diagnosis_subscription='',
                                    visit_date='',
                                    complaints='',
                                    disease_anamnesis='',
                                    life_anamnesis='',
                                    eyesight_type='',
                                    relative_accommodation_reserve=-1.0,
                                    schober_test='',
                                    pupils='',
                                    od_eye_position='',
                                    od_oi='',
                                    od_eyelid='',
                                    od_lacrimal_organs='',
                                    od_conjunctiva='',
                                    od_discharge='',
                                    od_iris='',
                                    od_anterior_chamber='',
                                    od_refractive_medium='',
                                    od_optic_disk='',
                                    od_vessels='',
                                    od_macular_reflex='',
                                    od_visible_periphery='',
                                    od_diagnosis='',
                                    od_icd_code='',
                                    os_eye_position='',
                                    os_oi='',
                                    os_eyelid='',
                                    os_lacrimal_organs='',
                                    os_conjunctiva='',
                                    os_discharge='',
                                    os_iris='',
                                    os_anterior_chamber='',
                                    os_refractive_medium='',
                                    os_optic_disk='',
                                    os_vessels='',
                                    os_macular_reflex='',
                                    os_visible_periphery='',
                                    os_diagnosis='',
                                    os_icd_code='',
                                    recommendations='',
                                    direction_to_aokb=0,
                                    reappointment=0,
                                    reappointment_time='',
                                    id=112,
                                    db=None
                                )
}
        
    def get_template(self, name) -> Examination:
        if name in self.__templates:
            return self.__templates[name]


class Settings():
    def __init__(self, db: Database):
        self.__db = db
        settings = list(self.__db.execute("SELECT * FROM Settings").fetchall()[0])

        self.__settings = {}
        fields = ["on_top", "remember_last_position", "run_with_system", "use_password",
                  "last_position", "password_hash", "ack_save_examination",
                  "ack_erase_examination", "ack_save_change_data", "ack_delete_change_data",
                  "ack_save_person", "ack_delete_person", "number_of_visible_records", "backup", "objective_synchronize_eyes"]
        for x in range(len(fields)):
            self.__settings[fields[x]] = settings[x]
    
    def execute_in_database(self, statements):
        if type(statements) == str:
            self.__db.execute(statements)
        elif type(statements) == list:
            for statement in statements:
                self.__db.execute(statement)
        self.__db.commit()
    
    @property
    def on_top(self):
        return self.__settings["on_top"]

    @property
    def remember_last_position(self):
        return self.__settings["remember_last_position"]

    @property
    def run_with_system(self):
        return self.__settings["run_with_system"]

    @property
    def use_password(self):
        return self.__settings["use_password"]

    @property
    def last_position(self):
        return self.__settings["last_position"]

    @property
    def ack_save_examination(self):
        return self.__settings["ack_save_examination"]

    @property
    def ack_erase_examination(self):
         return self.__settings["ack_erase_examination"]

    @property
    def ack_save_change_data(self):
        return self.__settings["ack_save_change_data"]

    @property
    def ack_delete_change_data(self):
        return self.__settings["ack_delete_change_data"]
    
    @property
    def ack_save_person(self):
        return self.__settings["ack_save_person"]
    
    @property
    def ack_delete_person(self):
        return self.__settings["ack_delete_person"]
    
    @property
    def number_of_visible_records(self):
        return self.__settings["number_of_visible_records"]
    
    @property
    def objective_synchronize_eyes(self):
        return self.__settings["objective_synchronize_eyes"]
        

    def update_on_top(self, value):
        self.__settings["on_top"] = value
        self.execute_in_database(f"UPDATE Settings SET On_top = {value}")
    
    def update_remember_last_position(self, value):
        self.__settings["remember_last_position"] = value
        self.execute_in_database(f"UPDATE Settings SET Remember_last_position = {value}")
    
    def update_run_with_system(self, value):
        self.__settings["run_with_system"] = value
        self.execute_in_database(f"UPDATE Settings SET Run_with_system = {value}")
    
    def update_use_password(self, value):
        self.__settings["use_password"] = value
        self.execute_in_database(f"UPDATE Settings SET Use_password = {value}")
    
    def update_last_position(self, value):
        self.__settings["last_position"] = value
        self.execute_in_database(f"UPDATE Settings SET Last_position = '{value}'")
    
    def update_ack_save_examination(self, value):
        self.__settings["ack_save_examination"] = value
        self.execute_in_database(f"UPDATE Settings SET Ack_save_examination = {value}")
        
    def update_ack_erase_examination(self, value):
        self.__settings["ack_erase_examination"] = value
        self.execute_in_database(f"UPDATE Settings SET Ack_erase_examination = {value}")
        
    def update_ack_save_change_data(self, value):
        self.__settings["ack_save_change_data"] = value
        self.execute_in_database(f"UPDATE Settings SET Ack_save_change_data = {value}")
        
    def update_ack_delete_change_data(self, value):
        self.__settings["ack_delete_change_data"] = value
        self.execute_in_database(f"UPDATE Settings SET Ack_delete_change_data = {value}")
        
    def update_ack_save_person(self, value):
        self.__settings["ack_save_person"] = value
        self.execute_in_database(f"UPDATE Settings SET Ack_save_person = {value}")
        
    def update_ack_delete_person(self, value):
        self.__settings["ack_delete_person"] = value
        self.execute_in_database(f"UPDATE Settings SET Ack_delete_person = {value}")
        
    def update_number_of_visible_records(self, value, to_db = False):
        self.__settings["number_of_visible_records"] = value
        if to_db:
            self.execute_in_database(f"UPDATE Settings SET Number_of_visible_records = {value}")

    def update_objective_synchronize_eyes(self, value):
        self.__settings["objective_synchronize_eyes"] = value
        self.execute_in_database(f"UPDATE Settings SET Objective_synchronize_eyes = {value}")


class Templates():
    def __init__(self, db: Database):
        self.__db = db
        templates = list(self.__db.execute("SELECT * FROM Templates").fetchall())
        self.__last_id = templates[-1][0]

        fields = ['complaints', 'eye_position', 'eyesight_type', 'oi', 'eyelid', 'lacrimal_organs', 'conjunctiva', 'discharge', 'iris',
                  'anterior_chamber', 'refractive_medium', 'optic_disk', 'vessels', 'macular_reflex', 'visible_periphery',
                  'diagnosis', 'icd_code', 'recommendations', 'reappointment_time', 'disease_anamnesis', 'life_anamnesis', 'schober_test', 'pupils', 'abc']
        self.__templates = {}
        for field in fields:
            self.__templates[field] = []
        for template in templates:
            self.__templates[template[1]].append([template[0], template[2]])

    @property
    def eye_position(self):
        return self.__templates["eye_position"]

    @property
    def complaints(self):
        return self.__templates["complaints"]

    @property
    def eyesight_type(self):
        return self.__templates["eyesight_type"]

    @property
    def oi(self):
        return self.__templates["oi"]

    @property
    def eyelid(self):
        return self.__templates["eyelid"]

    @property
    def lacrimal_organs(self):
        return self.__templates["lacrimal_organs"]

    @property
    def conjunctiva(self):
        return self.__templates["conjunctiva"]

    @property
    def discharge(self):
        return self.__templates["discharge"]

    @property
    def iris(self):
        return self.__templates["iris"]

    @property
    def anterior_chamber(self):
        return self.__templates["anterior_chamber"]

    @property
    def refractive_medium(self):
        return self.__templates["refractive_medium"]

    @property
    def optic_disk(self):
        return self.__templates["optic_disk"]

    @property
    def vessels(self):
        return self.__templates["vessels"]

    @property
    def macular_reflex(self):
        return self.__templates["macular_reflex"]

    @property
    def visible_periphery(self):
        return self.__templates["visible_periphery"]

    @property
    def diagnosis(self):
        return self.__templates["diagnosis"]
        
    @property
    def icd_code(self):
        return self.__templates["icd_code"]

    @property
    def recommendations(self):
        return self.__templates["recommendations"]

    @property
    def reappointment_time(self):
        return self.__templates["reappointment_time"]

    @property
    def disease_anamnesis(self):
        return self.__templates["disease_anamnesis"]
    
    @property
    def life_anamnesis(self):
        return self.__templates["life_anamnesis"]
    
    @property
    def schober_test(self):
        return self.__templates["schober_test"]
    
    @property
    def pupils(self):
        return self.__templates["pupils"]

    def add_template(self, field, template):
        self.__last_id += 1
        self.__templates[field].append([self.__last_id, template])
        self.__add_to_database(self.__last_id, field, template)
        print(self.__last_id)

    def update_template(self, id, field, template):
        for template_index in range(len(self.__templates[field])):
            if self.__templates[field][template_index][0] == id:
                self.__update_in_database(id, field, template)
                self.__templates[field][template_index][2] = template
                break

    def delete_template(self, field, template):
        for template_field in range(len(self.__templates[field])):
            if self.__templates[field][template_field][1] == template:
                self.__delete_from_database(self.__templates[field][template_field][0])
                del self.__templates[field][template_field]
                break

    def __add_to_database(self, id, field, template):
        self.__db.execute(f"INSERT INTO Templates VALUES ({id}, '{field}', '{template}')")
        self.__db.commit()

    def __update_in_database(self, id, field, template):
        self.__db.execute(f"Update Templates SET Field='{field}', Template='{template}' WHERE Id={id}")
        self.__db.commit()

    def __delete_from_database(self, id):
        self.__db.execute(f"DELETE FROM Templates WHERE Id={id}")
        self.__db.commit()


if __name__ == "__main__":
    db = Database()
    p = People(db)
    ExaminationTemplates(db)
    a = db.execute(f"SELECT * FROM Templates ORDER BY Id ASC;").fetchall()
    for x in range(len(a)):
        print(x)
        db.execute(f"UPDATE Templates SET Id={x+1} WHERE Id={a[x][0]};")
    db.commit()