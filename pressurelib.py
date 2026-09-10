# Library for Pressure Tests
import MOKO
import random

UN = 'moko_pressure_graph'  # Utility Name
MULT_RES_TABLE_NAME = 'Таблица для нескольких образцов'  # Первая таблица – с информацией об образце
SUMMARY_TABLE_NAME = 'Сводная таблица измерений' # Новая таблица – только результаты измерений
RESULT_GOOD = 'годен'
RESULT_BAD = 'не годен'
MATCH_YES = 'соответствует'
MATCH_NO = 'не соответствует'
FAKE_VALUE = 0.005
def final_checkpoints(checkpoints, accuracy_class):
    """
    Формирует итоговый список контрольных точек согласно СТБ 8056-2015 (п. 8.3.1.5).
    """
    total_points = len(checkpoints)

    if accuracy_class == 0.4:
        return checkpoints

    target_points = 8 if accuracy_class == 0.6 else 5

    if total_points <= target_points:
        return checkpoints

    step = (total_points - 1) / (target_points - 1)
    indices = [round(step * i) for i in range(target_points)]
    unique_indices = sorted(list(set(indices)))

    return [checkpoints[i] for i in unique_indices]


##########################  Driver functions   ####################
def driver_choice(driver):
    if driver == 'Simulation':
        return True

    if driver in ('XP2i', 'ADT681'):
        MOKO.DriverInit(driver)
    return False


def set_unit_of_measure(driver, unitofmeasure):
    if unitofmeasure == 'МПа':
        MOKO.DriverSet(driver, 'UNITS=KPa')
    else:
        MOKO.Driver(driver, 'set', 'UNITS=' + unitofmeasure)


##########################  Функция измерения с пошаговым заполнением  ######
def measure_checkpoints(checkpoints, driver, unitofmeasure,
                        simulation, reverse=False):
    """
    Измерение давления в контрольных точках с пошаговым заполнением таблицы.

    При reverse=False: обход от 0 к максимуму (UP)
    При reverse=True: обход от максимума к 0 (DOWN)
    """
    results = []
    total = len(checkpoints)

    seq = reversed(checkpoints) if reverse else checkpoints
    suffix = "DOWN" if reverse else "UP"
    table_name = "Таблица обратного хода" if reverse else "Таблица прямого хода"

    # Инициализируем таблицу для этого направления
    if len(results) == 0:
        init_direction_table(checkpoints, unitofmeasure, table_name, reverse)

    for idx, checkpoint in enumerate(seq, start=1):
        # Установка текущей точки в интерфейсе
        MOKO.HashSelectCheck(f"Точка {idx}${suffix}")
        MOKO.UtilitySet(UN, f'show={checkpoint}')

        # Проверка дефекта
        if MOKO.UtilityGet(UN, 'defect', 'bool'):
            results.extend(['–'] * (total - len(results)))
            MOKO.HashSet('failed')
            # Записываем оставшиеся точки как прочерки
            for remaining_idx in range(len(results), total):
                add_row_to_direction_table(
                    table_name, checkpoint=checkpoints[remaining_idx if not reverse
                    else total - 1 - remaining_idx],
                    result='–',
                    unit=unitofmeasure)
            break
        else:
            MOKO.HashSet('passed')

        # Получение значения давления
        pressure_value = (
            Get_Fake_Pressure(checkpoint, FAKE_VALUE) if simulation
            else round(Get_Pressure(driver, unitofmeasure), 3)
        )
        results.append(pressure_value)

        # НЕМЕДЛЕННАЯ ЗАПИСЬ в таблицу после каждого измерения
        add_row_to_direction_table(
            table_name,
            index = idx,
            checkpoint=checkpoint,
            result=pressure_value,
            unit=unitofmeasure
        )

        MOKO.Stage(f"Измерено: {pressure_value} {unitofmeasure}")

    return results


##########################  ФУНКЦИИ для работы с таблицами  ####################

def init_direction_table(checkpoints, unit, table_name, reverse=False):
    """
    Создаёт и инициализирует таблицу для направления с заголовками.
    """
    header_columns = (
        f'№\\nп/п;'
        f'Контрольная\\nточка, {unit};'
        f'Показания\\nприбора, {unit};'
        f'Погрешность,\\n{unit}'
    )

    MOKO.ReportTableCreate(table_name, header_columns)


def add_row_to_direction_table(table_name, index, checkpoint, result, unit):
    """
    Добавляет одну строку в таблицу направления.
    """
    checkpoint_str = str(checkpoint).replace('.', ',')
    result_str = str(result).replace('.', ',')

    try:
        if result == '–':
            err_str = '–'
        else:
            err = round(result - checkpoint, 3)
            err_str = str(err).replace('.', ',')
    except (TypeError, ValueError):
        err_str = '–'

    row_data = f'{index};{checkpoint_str};{result_str};{err_str}'
    MOKO.ReportSetTable(table_name, row_data)



def add_row_to_main_table(checkpoint, res_up, res_down,
                             err_up, err_down, variation, variation_pct,
                             unit, permissible_err, max_err,
                             is_first=False, is_last=False):
    """
    Добавляет строку в сводную таблицу.
    """
    try:
        point_str = str(checkpoint).replace('.', ',')
        up_str = str(res_up).replace('.', ',')
        down_str = str(res_down).replace('.', ',')
        err_up_str = str(err_up).replace('.', ',') if err_up != '–' else '–'
        err_down_str = str(err_down).replace('.', ',') if err_down != '–' else '–'
        var_str = str(variation).replace('.', ',') if variation != '–' else '–'
        var_pct_str = str(variation_pct).replace('.', ',') if variation_pct != '–' else '–'


        row_data = f'{point_str};' \
                   f'{up_str};' \
                   f'{down_str};' \
                   f'{err_up_str};' \
                   f'{err_down_str}' \
                   f';{var_str};' \
                   f'{var_pct_str}'
        MOKO.ReportSetTable(SUMMARY_TABLE_NAME, row_data)

    except Exception as e:
        MOKO.StageError(f"Ошибка при добавлении строки в сводную таблицу: {e}")
        # Можно также установить хэш в failed, но это зависит от контекста
def add_row_to_summary_table(checkpoint, res_up, res_down,
                             err_up, err_down, variation, variation_pct,
                             unit, permissible_err, max_err,
                             is_first=False, is_last=False):
    """
    Добавляет строку в сводную таблицу.
    """
    try:
        point_str = str(checkpoint).replace('.', ',')
        up_str = str(res_up).replace('.', ',')
        down_str = str(res_down).replace('.', ',')
        err_up_str = str(err_up).replace('.', ',') if err_up != '–' else '–'
        err_down_str = str(err_down).replace('.', ',') if err_down != '–' else '–'
        var_str = str(variation).replace('.', ',') if variation != '–' else '–'
        var_pct_str = str(variation_pct).replace('.', ',') if variation_pct != '–' else '–'

        if is_first:
            extra = f'[Delta]max= {str(max_err).replace(".", ",")}{unit}'
        elif is_last:
            extra = f'[Delta]доп= ±{permissible_err}'
        else:
            extra = ' '

        row_data = f'{point_str};{up_str};{down_str};{err_up_str};' \
                   f'{err_down_str};{var_str};{var_pct_str};{extra}'
        MOKO.ReportSetTable(SUMMARY_TABLE_NAME, row_data)

    except Exception as e:
        MOKO.StageError(f"Ошибка при добавлении строки в сводную таблицу: {e}")
        # Можно также установить хэш в failed, но это зависит от контекста


##########################  Calculating absolute measurement error   #############
def calc_err_variation(checkpoints, res_up, res_down):
    # ДОБАВИЛИ variation_pct в объявление массивов
    err_up, err_down, variation, variation_pct = [], [], [], []

    for i in range(len(checkpoints)):
        # 1. Погрешность прямого хода
        try:
            val_up = round(res_up[i] - checkpoints[i], 3)
            err_up.append(val_up)
        except (TypeError, IndexError):
            err_up.append('–')
            val_up = None

        # 2. Погрешность обратного хода
        try:
            val_down = round(res_down[i] - checkpoints[i], 3)
            err_down.append(val_down)
        except (TypeError, IndexError):
            err_down.append('–')
            val_down = None

        # 3. Вариация манометра в данной точке
        try:
            val_var = round(abs(res_up[i] - res_down[i]), 3)
            variation.append(val_var)
        except (TypeError, IndexError):
            variation.append('–')
            val_var = None # Присваиваем None, чтобы шаг 4 не упал

        # 4. Вариация в процентах от текущего значения эталона
        try:
            if val_var is not None and checkpoints[i] != 0:
                val_var_pct = round((val_var / checkpoints[i]) * 100, 2)
                variation_pct.append(val_var_pct)
            else:
                variation_pct.append('–') # Для нуля на входе процент не имеет смысла
        except (TypeError, ZeroDivisionError):
            variation_pct.append('–')

    return err_up, err_down, variation, variation_pct


def conclusion(max_err, permissible_err, trial_appearance, trial_result):
    if max_err == '-' or abs(max_err) >= abs(permissible_err):
        result = MATCH_NO
    else:
        result = MATCH_YES

    MOKO.ReportSetString('Результат поверки', result)
    if max_err != '-':
        MOKO.ReportSetString('Максимальная погрешность',
                             str(max_err).replace('.', ','))

    verdict = RESULT_GOOD if (
                result == MATCH_YES and
                trial_appearance == MATCH_YES and
                trial_result == MATCH_YES) else RESULT_BAD
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


##########################  ФОРМИРОВАНИЕ ОТЧЕТА  ####################

def results(workplace, typeofunit, scalemax,
            accuracyclass, valueofdivision,
            trial_appearance, trial_result, stampnumber):
    """
    Создаёт таблицу «Таблица для нескольких образцов» и записывает в неё
    информацию об образце, внешнем осмотре и опробовании.
    (Без изменений – оставляем как есть)
    """
    header_columns = (
        'Показания эталона, ед. изм.;'
        'Показания поверяемого прибора\\nед. изм. при повышении давления;'
        'Показания поверяемого прибора\\nед. изм. при понижении давления;'
        'Абсолютная погрешность,\\nед. изм. при повышении;'
        'Показания поверяемого прибора\\nед. изм. при понижении;'
        'Вариация ед. изм.;'
        'Результаты погрешности.\\nЗаключение'
    )

    MOKO.ReportTableCreate(MULT_RES_TABLE_NAME, header_columns)

    header_sample = (
        f'Место эксплуатации {workplace};'
        f'Тип {typeofunit};'
        f'Диапазон (0-{str(scalemax).replace(".", ",")});'
        f'Класс точности {str(accuracyclass).replace(",", ".")};'
        f'Ц.д. {valueofdivision};  ; '
    )
    MOKO.ReportSetTable(MULT_RES_TABLE_NAME, header_sample)

    header_inspection = (
        f'Внешний осмотр {trial_appearance};'
        f'Опробование {trial_result};'
        f'Номер клейма {stampnumber};'
        f' ; ; Подпись; '
    )
    MOKO.ReportSetTable(MULT_RES_TABLE_NAME, header_inspection)


def create_multi_summary_table():
    """
    Создаёт новую таблицу «Сводная таблица измерений» только с заголовками.
    """
    header_columns = (
        'Показания эталона, ед. изм.;'
        'Показания поверяемого прибора\\nед. изм. при повышении давления;'
        'Показания поверяемого прибора\\nед. изм. при понижении давления;'
        'Абсолютная погрешность,\\nед. изм. при повышении;'
        'Показания поверяемого прибора\\nед. изм. при понижении;'
        'Вариация ед. изм.;'
        'Результаты погрешности.\\nЗаключение'
    )
    MOKO.ReportTableCreate(SUMMARY_TABLE_NAME, header_columns)


def main_reports(checkpoints, res_up, res_down,
            err_up, err_down, variation,variation_pct,
            unit, permissible_err, max_err):
    """
    Создаёт сводную таблицу измерений и заполняет её результатами.
    """
    # Сначала создаём таблицу с заголовками
    header_columns = (
            f'Показания эталона,\n{unit};'
            f'Показания прибора,\n{unit} при повышении;'
            f'Показания прибора,\n{unit} при понижении;'
            f'Абс. погрешность,\n{unit} при повышении;'
            f'Абс. погрешность,\n{unit} при понижении;'
            f'Вариация, {unit};'
            f'Вариация, %;'
    )
    MOKO.ReportTableCreate(SUMMARY_TABLE_NAME, header_columns, 15)
    # Затем заполняем строками
    for i in range(len(checkpoints)):
        add_row_to_main_table(
            checkpoint=checkpoints[i],
            res_up=res_up[i],
            res_down=res_down[i],
            err_up=err_up[i],
            err_down=err_down[i],
            variation=variation[i],
            variation_pct=variation_pct[i],
            unit=unit,
            permissible_err=permissible_err,
            max_err=max_err,
            is_first=(i == 0),
            is_last=(i == len(checkpoints) - 1)
        )



##########################  ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ  ####################

def Get_Pressure(driver, UnitOfMeasure):
    pressure = float(MOKO.Driver(driver, 'get', 'PRESSURE', 'string'))
    if UnitOfMeasure == 'МПа':
        pressure = float(pressure) * 0.001
    return pressure


def Get_Fake_Pressure(pressure, pressure_range):
    fake_pressure = round(random.uniform(pressure - pressure_range,
                                         pressure + pressure_range), 3)
    return fake_pressure


######################### Внешний осмотр ################################
def perform_visual_inspection(step_string="Соответствие внешнего вида"):
    """
    Проводит внешний осмотр образца.
    """
    MOKO.HashSelect(step_string)
    trial_appearance = MATCH_YES if MOKO.MessageGetBool(
        'Образец #images\ExternalInspection.png',
        'Пожалуйста, проведите внешний осмотр образца. '
        'Соответствует ли внешний вид образца установленным нормам?'
    ) else MATCH_NO

    if trial_appearance == MATCH_YES:
        MOKO.HashSet('passed')
    else:
        MOKO.HashSet('failed')

    MOKO.ReportSetString('Результат внешнего осмотра', trial_appearance)
    return trial_appearance


def perform_operational_test(step_string="Результат опробования"):
    """
    Проводит опробование образца.
    """
    MOKO.HashSelect(step_string)
    trial_result = MATCH_YES if MOKO.MessageGetBool(
        'Опробование #images\Testing.png',
        'Пожалуйста, проведите опробование образца (герметичность, работоспособность и т.п.).\n'
        'Соответствует ли образец требованиям по опробованию?'
    ) else MATCH_NO

    if trial_result == MATCH_YES:
        MOKO.HashSet('passed')
    else:
        MOKO.HashSet('failed')

    MOKO.ReportSetString('Результат опробования', trial_result)
    return trial_result


def check_compliance_and_abort_if_failed(trial_appearance, trial_result, workplace,
                                         typeofunit, scalemax, accuracyclass,
                                         valueofdivision, stampnumber):
    """
    Проверяет результаты внешнего осмотра и опробования.
    """
    if trial_appearance == MATCH_NO or trial_result == MATCH_NO:
        MOKO.StageSeparator("Образец не соответствует требованиям внешнего осмотра или опробования")
        MOKO.StageError("Измерения не проводятся. Образец признан негодным.")

        MOKO.ReportSetString('Результат поверки', MATCH_NO)
        MOKO.ReportSetString('Заключение', RESULT_BAD)
        MOKO.ReportSetString('Результат внешнего осмотра', trial_appearance)
        MOKO.ReportSetString('Результат опробования', trial_result)

        results(workplace, typeofunit, scalemax,
                accuracyclass, valueofdivision,
                trial_appearance, trial_result, stampnumber)

        MOKO.HashSet('failed')
        MOKO.ScriptEnd('failed')
# Endregion