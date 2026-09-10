# protocol_utils.py
import MOKO
from types import SimpleNamespace
UN = 'moko_pressure_graph'  # Utility Name
def get_protocol_info():
    """
    Парсит информацию о поверке из утилиты.
    Возвращает словарь со всеми новыми полями (без разбивки даты).
    """
    info = MOKO.UtilityGetParseKeyValue(UN, "info")
    MOKO.StageSeparator("Информация поверки")

    return {
        # Все новые поля, как они приходят из утилиты
        'location':          info.get('location', ''),          # Место эксплуатации
        'verifier':          info.get('verifier', ''),          # Поверитель
        'standard':          info.get('standard', ''),          # Эталонные средства
        'protocol_number':   info.get('protocol_number', ''),   # Номер протокола
        'protocol_date':     info.get('protocol_date', ''),     # Дата поверки (полная строка)
        'scale_max':         info.get('scale_max', ''),         # Макс. значение давления
        'scale_min':         info.get('scale_min', ''),         # Мин. значение давления
        'point_value':       info.get('point_value', ''),       # Первая поверяемая точка
        'division':          info.get('division', ''),          # Цена деления
        'unit':              info.get('unit', ''),              # Единица измерения
        'list_accuracy':     info.get('list_accuracy', ''),     # Класс точности
        'permissible_error': info.get('permissible_error', ''), # Пределы допускаемой погрешности
        'range':             info.get('range', ''),             # Пределы допускаемой погрешности
        'device_type':       info.get('device_type', ''),       # Тип образца
        'serial_number':     info.get('serial_number', ''),     # Серийный номер
        'stamp_number':      info.get('stamp_number', ''),      # Номер клейма
        'temperature':       info.get('temperature', ''),       # Температура
        'humidity':          info.get('humidity', ''),          # Влажность
        'pressure':          info.get('pressure', ''),          # Давление окружающей среды
        'driver':            info.get('driver', ''),            # Драйвер
    }


def extract_parameters(data):
    """
    Извлекает и преобразует параметры из словаря data.
    Возвращает SimpleNamespace с атрибутами для удобного доступа через точку.
    """
    return SimpleNamespace(
        accuracy           = float(data['list_accuracy'].replace(',', '.')) if data['list_accuracy'] else 0.0,
        unit               = str(data['unit']),
        scale_max          = float(data['scale_max'].replace(',', '.')) if data['scale_max'] else 0.0,
        scale_min          = float(data['scale_min'].replace(',', '.')) if data['scale_min'] else 0.0,
        point_value        = float(data['point_value'].replace(',', '.')) if data['point_value'] else 0.0,
        permissible_error  = str(data['permissible_error']),
        range              =float(data['range'].replace(',', '.')) if data['range'] else 0.0,
        driver             = str(data['driver']),
        location           = str(data['location']),
        device_type        = str(data['device_type']),
        division           = str(data['division']),
        stamp_number       = str(data['stamp_number']),
        serial_number      = str(data['serial_number']),
        protocol_date      = str(data['protocol_date']),
    )

def fill_report_info(data):
    """
    Заполняет отчёт данными. Для совместимости с существующими скриптами
    используются старые имена закладок (например, 'PermissibleError'),
    но значения берутся из новых ключей.
    """
    MOKO.StageSeparator("Формирование первичной информации протокола поверки")

    MOKO.ReportSetInfoStrings(
        ("----- Характеристики СИ -----", "", ""),
        ("Класс точности",            data['list_accuracy'], "Класс точности по ГОСТ (из паспорта прибора)"),
        ("Единица измерения",         data['unit'], "Единицы измерения давления (МПа, кПа, кгс/см² и т.п.)"),
        ("Минимальное давление",      parse_engineering_string(data['scale_min']), "Минимальное значение шкалы (обычно 0)"),
        ("Максимальное давление",     parse_engineering_string(data['scale_max']), "Максимальное значение шкалы прибора"),

        ("Первая точка",              data['point_value'], "Первая поверяемая точка после нулевой отметки"),
        ("Цена деления",              parse_engineering_string(data['division']), "Цена деления шкалы поверяемого прибора"),
        ("Диапазон измерений",        data['range'], "Диапазон измеряемых давлений"),
        ("Допустимая погрешность",    parse_engineering_string(data['permissible_error']), "Пределы допускаемой основной погрешности по паспорту"),
        ("----- Информация об образце -----", "", ""),
        ("Тип прибора",               data['device_type'], "Тип (модель) поверяемого образца"),
        ("Серийный номер",            data['serial_number'], "Серийный (заводской) номер образца"),
        ("Номер клейма",              data['stamp_number'], "Номер клейма (штампа) поверителя"),
        ("----- Информация о поверке -----", "", ""),
        ("Место эксплуатации",        data['location'], "Место эксплуатации (или владелец) прибора"),
        ("Поверитель",                data['verifier'], "ФИО поверителя, проводившего поверку"),
        ("Номер протокола",           data['protocol_number'], "Номер протокола поверки"),
        ("Эталонные средства",        data['standard'], "Сведения об эталонных и вспомогательных средствах поверки"),
        ("Дата поверки",              data['protocol_date'], "Дата проведения поверки (полная)"),
        ("----- Условия поверки -----", "",""),
        ("Температура",               data['temperature'], "Температура окружающей среды во время поверки, °C"),
        ("Влажность",                 data['humidity'], "Относительная влажность воздуха, %"),
        ("Атмосферное давление",      data['pressure'], "Атмосферное давление (барометрическое), мм рт. ст."),
        ("----- Дополнительные данные -----", "", ""),
        ("Драйвер",                   data['driver'], "Используемый драйвер (эталонный прибор)"),
    )

def parse_engineering_string(s):
    if s is None or s == '':
        return '0,000'
    s = s.strip()
    # Определяем суффикс (последний символ, если он буква)
    # Может быть несколько букв? В основном одна.
    # Разделим на число и суффикс
    # Попробуем извлечь число в начале, остальное - суффикс
    # Регулярное выражение: ^([-+]?\d*[.,]?\d+)\s*([a-zA-Zа-яА-Я]+)?$
    import re
    match = re.match(r'^([-+]?\d*[.,]?\d+)\s*([a-zA-Zа-яА-Я]+)?$', s)
    if not match:
        # Если не удалось, просто возвращаем s (или 0,000)
        return '0,000'
    num_str = match.group(1)
    suffix = match.group(2) if match.group(2) else ''
    # Заменяем запятую на точку
    num_str = num_str.replace(',', '.')
    try:
        num = float(num_str)
    except:
        return '0,000'
    # Множители
    factors = {
        'm': 1e-3,
        'k': 1e3,
        'M': 1e6,
        'G': 1e9,
        'u': 1e-6,
        'μ': 1e-6,
        'n': 1e-9,
        'p': 1e-12,
        # добавить русские аналоги
        'м': 1e-3,  # русская м
        'к': 1e3,   # русская к (кило)
        'М': 1e6,   # русская М (мега) - но заглавная
        # 'Г' = 1e9? но обычно G
    }
    factor = factors.get(suffix.lower(), 1.0)
    result = num * factor
    # Форматируем с 3 знаками, заменяем точку на запятую
    return f"{result:.3f}".replace('.', ',')