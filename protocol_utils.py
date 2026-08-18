# protocol_utils.py
import MOKO
UN = 'moko_pressure_mini'  # Utility Name
def get_protocol_info():
    """Парсит информацию о поверке из утилиты"""
    info = MOKO.UtilityGetParseKeyValue(UN, "info")

    MOKO.StageSeparator("- Информация поверки -")

    return {
        'AccuracyClass':            info.get('AccuracyClass',        ''),  # 01 Класс точности
        'UnitOfMeasure':            info.get('UnitOfMeasure',        ''),  # 02 Единицы измерения
        'ScaleMax':                 info.get('ScaleMax',             ''),  # 03 Предельное значение давления на шкале прибора
        'FirstPoint':               info.get('FirstPoint',           ''),  # 04 Первая поверяемая точка на шкале прибора после нуля
        'ValueofDivision':          info.get('ValueofDivision',      ''),  # 05 Цена деления
        'TypeofUnit':               info.get('TypeofUnit',           ''),  # 06 Тип образца
        'PermissibleError':         info.get('PermissibleError',     ''),  # 07 Пределы допускаемой погрешности
        'StampNumber':              info.get('StampNumber',          ''),  # 08 Номер штампа
        'Owner':                    info.get('Owner',                ''),  # 09 Владелец
        'Verifier':                 info.get('Verifier',             ''),  # 10 ФИО поверителя
        'VerificationLocation':     info.get('VerificationLocation', ''),  # 11 Место проведения поверки
        'WorkplaceNumber':          info.get('WorkplaceNumber',      ''),  # 12 Номер рабочего места
        'OrderNumber':              info.get('OrderNumber',          ''),  # 13 Номер заказа
        'Day':                      info.get('Day',                  ''),  # 14 День (дата)
        'Month':                    info.get('Month',                ''),  # 15 Месяц (дата)
        'Year':                     info.get('Year',                 ''),  # 16 Год (дата)
        'ProtocolNumber':           info.get('ProtocolNumber',       ''),  # 17 Номер протокола
        'Temperature':              info.get('Temperature',          ''),  # 18 Температура
        'Humidity':                 info.get('Humidity',             ''),  # 19 Влажность
        'AmbientPressure':          info.get('AmbientPressure',      ''),  # 20 Давление окружающей среды
        'Driver':                   info.get('Driver',               ''),  # 21 Драйвер
        'UnitNumber':               info.get('UnitNumber',           '')   # 22 Номер образца
    }


def fill_report_info(data):
    """Заполняет отчёт данными"""
    MOKO.StageSeparator("Формирование первичной информации протокола поверки")

    MOKO.ReportSetInfoStrings(
        ("AccuracyClass",              data['AccuracyClass'],              "Класс точности"),
        ("UnitOfMeasure",              data['UnitOfMeasure'],              "Единицы измерения"),
        ("ScaleMax",                   data['ScaleMax'],                   "Предельное значение давления на шкале прибора"),
        ("FirstPoint",                 data['FirstPoint'],                 "Первая поверяемая точка на шкале прибора после нуля"),
        ("ValueofDivision",            data['ValueofDivision'],            "Цена деления"),
        ("TypeofUnit",                 data['TypeofUnit'],                 "Тип образца"),
        ("PermissibleError",           data['PermissibleError'],           "Пределы допускаемой погрешности"),
        ("StampNumber",                data['StampNumber'],                "Номер штампа"),
        ("Owner",                      data['Owner'],                      "Владелец"),
        ("Verifier",                   data['Verifier'],                   "ФИО поверителя"),
        ("VerificationLocation",       data['VerificationLocation'],       "Место проведения поверки"),
        ("WorkplaceNumber",            data['WorkplaceNumber'],            "Номер рабочего места"),
        ("OrderNumber",                data['OrderNumber'],                "Номер заказа"),
        ("Day",                        data['Day'],                        "День (дата)"),
        ("Month",                      data['Month'],                      "Месяц (дата)"),
        ("Year",                       data['Year'],                       "Год (дата)"),
        ("ProtocolNumber",             data['ProtocolNumber'],             "Номер протокола"),
        ("Temperature",                data['Temperature'],                "Температура"),
        ("Humidity",                   data['Humidity'],                   "Влажность"),
        ("AmbientPressure",            data['AmbientPressure'],            "Давление окружающей среды"),
        ("Driver",                     data['Driver'],                     "Драйвер"),
        ("UnitNumber",                 data['UnitNumber'],                 "Номер образца"),
    )


def set_additional_parameters(data):
    """Устанавливает дополнительные параметры протокола"""
    MOKO.ReportSetString('MeasuringRange', f'(0-{str(data["ScaleMax"]).replace(".", ",")})')