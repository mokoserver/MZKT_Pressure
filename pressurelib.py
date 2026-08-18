# Library for Pressure Tests
import MOKO
import random

UN = 'moko_pressure_mini'  # Utility Name

def final_checkpoints(checkpoints):
    if len(checkpoints) == 9:
        del checkpoints[2:9:2]  # Удаляем 2, 4, 6, 8 → Остаются: 0, 1, 3, 5, 7 (5 точек)
    elif len(checkpoints) == 8:
        del checkpoints[2:7:2]  # Удаляем индексы 2, 4, 6 → Остаются: 0, 1, 3, 5, 7 (5 точек)
    elif len(checkpoints) == 7:
        del checkpoints[2:5:2]  # Удаляем индексы 2, 4 → Остаются: 0, 1, 3, 5, 6 (5 точек)
    elif len(checkpoints) == 6:
        del checkpoints[3]      # Удаляем индекс 3 → Остаются: 0, 1, 2, 4, 5 (5 точек)
    return checkpoints


##########################  Here will be functions for working with Drivers   ####################
# driver initialisation
def driver_choice(driver):
    if driver == 'Simulation':
        return True

    if driver in ('XP2i', 'ADT681'):
        MOKO.DriverInit(driver)
    return False


def set_unit_of_measure(driver, unitofmeasure):
    if unitofmeasure == 'МПа': MOKO.DriverSet(driver, 'UNITS=KPa')  # XP2i не измеряет в МПа
    else: MOKO.Driver(driver, 'set', 'UNITS=' + unitofmeasure)


##########################  Here will be functions for working with Utility   ####################
def measure_checkpoints(checkpoints, driver, unitofmeasure, simulation, reverse=False):
    """
    Измерение давления в контрольных точках.

    При reverse=False: обход от 0 к максимуму (UP)
    При reverse=True: обход от максимума к 0 (DOWN)
    При обнаружении дефекта оставшиеся точки заполняются '–'
    """
    results = []
    total = len(checkpoints)

    # Выбор направления обхода и суффикса для интерфейса
    seq = reversed(checkpoints) if reverse else checkpoints
    suffix = "DOWN" if reverse else "UP"

    for idx, checkpoint in enumerate(seq, start=1):
        # Установка текущей точки в интерфейсе
        MOKO.HashSelectCheck(f"Точка {idx}${suffix}")
        MOKO.UtilitySet(UN, f'show={checkpoint}')

        # Проверка дефекта
        if MOKO.UtilityGet(UN, 'defect', 'bool'):
            # Заполняем оставшиеся точки прочерками
            results.extend(['–'] * (total - len(results)))
            MOKO.HashSet('failed')
            break
        else:
            MOKO.HashSet('passed')
        # Получение значения давления
        results.append(
            Get_Fake_Pressure(checkpoint, 0.15) if simulation
            else round(Get_Pressure(driver, unitofmeasure), 3)
        )

    return results


##########################  Calculating absolute measurement error and variation   ####################
def calc_err_variation(checkpoints, res_up, res_down):
    err_up, err_down, variation = [], [], []
    for i in range(len(checkpoints)):
        try:
            err_up.append(round((res_up[i] - checkpoints[i]), 3))
        except TypeError:
            for x in range(len(checkpoints) - len(err_up)):
                err_up.append('–')
                break
    checkpoints = list(reversed(checkpoints))
    res_down = list(reversed(res_down))
    for i in range(len(checkpoints)):
        try:
            err_down.append(round((res_down[i] - checkpoints[::1][i]), 3))
        except TypeError:
            for x in range(len(checkpoints) - len(err_down)):
                err_down.append('–')
                break
    err_down = list(reversed(err_down))
    for i in range(len(checkpoints)):
        try:
            variation.append(round(err_up[i] - err_down[i], 3))
        except TypeError:
            for x in range(len(checkpoints) - len(variation)):
                variation.append('–')
            break
    return err_up, err_down, variation


def conclusion(max_err, permissible_err, appearance):
    # Определяем результат поверки
    if max_err == '-' or abs(max_err) >= abs(permissible_err):
        result = 'не соответствует'
    else:
        result = 'соответствует'

    # Записываем в отчёт
    MOKO.ReportSetString('Result', result)
    if max_err != '-':
        MOKO.ReportSetString('MaxErr', str(max_err).replace('.', ','))

    # Определяем заключение
    verdict = 'годен' if result == 'соответствует' and appearance == 'соответствует' else 'не годен'

    return result, verdict


def max_err(err_up, err_down):
    max_err_up_l = []
    max_err_down_l = []
    for x in err_up:
        if x != '–':
            max_err_up_l.append(x)
    for x in err_down:
        if x != '–':
            max_err_down_l.append(x)
    if len(max_err_up_l) > 0:
        max_err_up = max(max_err_up_l, key=abs)
    else:
        max_err_up = '-'
    if len(max_err_down_l) > 0:
        max_err_down = max(max_err_down_l, key=abs)
    else:
        max_err_down = '-'
    return max_err_up, max_err_down


#workplacenumber, typeofunit, scalemax, accuracyclass, valueofdivision, appearance, result, stampnumber
def results(*args):
    MOKO.Report('Res_table1', 'info', 'table', '#200;#200;#200;#200;#200;#150;#150')

    # Информация об образце (шапка таблицы)
    header_sample = (
        f'Номер рабочего места {args[0]};'
        f'Тип {args[1]};'
        f'Диапазон (0-{str(args[2]).replace(".", ",")});'
        f'Класс точности {str(args[3]).replace(",", ".")};'
        f'Ц.д. {args[4]};  ; '
    )

    # Результаты внешнего осмотра
    header_inspection = (
        f'Внешний осмотр {args[5]};'
        f'Опробование {args[6]};'
        f'Номер клейма {args[7]};'
        f' ; ; Подпись; '
    )

    # Заголовки колонок с результатами измерений
    header_columns = (
        'Показания эталона, ед. изм.;'
        'Показания поверяемого прибора\\nед. изм. при повышении давления;'
        'Показания поверяемого прибора\\nед. изм. при понижении давления;'
        'Абсолютная погрешность,\\nед. изм. при повышении;'
        'Показания поверяемого прибора\\nед. изм. при понижении;'
        'Вариация ед. изм.;'
        'Результаты погрешности.\\nЗаключение'
    )

    # Запись всех заголовков в таблицу
    MOKO.ReportSetTable('Res_table1', header_sample)
    MOKO.ReportSetTable('Res_table1', header_inspection)
    MOKO.ReportSetTable('Res_table1', header_columns)
    return


def reports(*args):
    # Формируем основную таблицу с результатами
    table_data = ''
    for i in range(len(args[0])):
        # Форматируем числа (замена точки на запятую)
        point_values = [str(args[j][i]).replace('.', ',') for j in range(6)]

        # Определяем дополнительную информацию для первой и последней строки
        if i == 0:  # Первая строка - добавляем максимальную погрешность
            extra = f'[Delta]max= {str(args[8]).replace(".", ",")}{args[6]}'
        elif i == len(args[0]) - 1:  # Последняя строка - добавляем допускаемую погрешность
            extra = f'[Delta]доп= ±{args[7]}'
        else:  # Обычные строки - пустое поле
            extra = ' '

        # Собираем строку
        table_data += ';'.join(point_values) + ';' + extra + '\\r'

    # Записываем в отчёт
    MOKO.Report('Res_table1', 'set', 'table', table_data)

    # Формируем упрощённую таблицу (без дополнительных полей)
    simple_data = ''
    for i in range(len(args[0])):
        point_values = [str(args[j][i]).replace('.', ',') for j in range(6)]
        simple_data += ';'.join(point_values) + '\\r'

    MOKO.Report('Res_table', 'set', 'table', simple_data)


def Get_Pressure(driver, UnitOfMeasure):
    pressure = float(MOKO.Driver(driver, 'get', 'PRESSURE', 'string'))
    if UnitOfMeasure == 'МПа':
        pressure = float(pressure) * 0.001
    return pressure


def Get_Fake_Pressure(pressure, pressure_range):
    fake_pressure = round(random.uniform(pressure - pressure_range, pressure + pressure_range), 3)
    return fake_pressure

