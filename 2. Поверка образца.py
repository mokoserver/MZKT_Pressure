from pressurelib import *
from protocol_utils import get_protocol_info, extract_parameters
import MOKO

# Преднастройки
try:
    UN = 'moko_pressure_graph'  # Utility Name
    # Извлечение словаря с данными, введёнными пользователем через интерфейс
    data = get_protocol_info()
    params = extract_parameters(data)  # все переменные готовы
except Exception as e:
    MOKO.StageError(f"Ошибка при получении данных из утилиты: {e}")
    MOKO.HashSet('failed')
    MOKO.ScriptEnd('failed')

#Region Внешний осмотр$POV
try:
    MOKO.HashExecuteStep("Внешний осмотр$POV")
    #hash Соответствие внешнего вида
    trial_appearance = perform_visual_inspection("Соответствие внешнего вида")
    #hash Результат опробования
    trial_result = perform_operational_test("Результат опробования")
    #hash Проверка соответствия образца
    check_compliance_and_abort_if_failed(
        trial_appearance, trial_result,
        params.location, params.device_type, params.scale_max, params.accuracy, params.division, params.stamp_number
    )
except Exception as e:
    MOKO.StageError(f"Ошибка при проведении внешнего осмотра или опробования: {e}")
#Endregion

# 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁

#Region Подготовка к измерениям
try:
    Simulation = driver_choice(params.driver)  # Driver initialisation
    permissible_err = params.range * 0.01 * params.accuracy
    checkpoints = [round(x * params.point_value, 1) for x in range(int(params.scale_max / params.point_value) + 1)]
    checkpoints = final_checkpoints(checkpoints, params.accuracy)

    # Установка единиц измерения на эталонном приборе (если не симуляция)
    if not Simulation:
        set_unit_of_measure(params.driver, params.unit)


except Exception as e:
    MOKO.StageError(f"Ошибка при подготовке к измерениям: {e}")
    MOKO.HashSet('failed')
    MOKO.ScriptEnd('failed')
#Endregion

#Region Прямой ход: от MIN к MAX
try:
    # Description: класс 0.6;класс 1;класс 1.5;класс 1.6;класс 2.5;класс 4;
    MOKO.HashExecuteStep("Прямой ход: от MIN к MAX")
    # ⬆️ ⬆️ ⬆️ ⬆️ ⬆️ ⬆️ ⬆️ ⬆️ ⬆️ ⬆️ ⬆️ ⬆️ ⬆️ ⬆️
    #hash Точка 1$UP:+;+;+;+;+;+;
    #hash Точка 2$UP:+;+;+;+;+;+;
    #hash Точка 3$UP:+;+;+;+;+;+;
    #hash Точка 4$UP:+;+;+;+;+;+;
    #hash Точка 5$UP:+;+;+;+;+;+;
    #hash Точка 6$UP:+;-;-;-;-;-;
    #hash Точка 7$UP:+;-;-;-;-;-;
    #hash Точка 8$UP:+;-;-;-;-;-;

    MOKO.StageSeparator("Начинается заполнение таблицы прямого хода")
    res_up = measure_checkpoints(checkpoints, params.driver, params.unit, Simulation, reverse=False)
    MOKO.StageSuccess(f"Прямой ход завершён. Измерено {len(res_up)} точек")

except Exception as e:
    MOKO.StageError(f"Ошибка при выполнении прямого хода: {e}")
    MOKO.HashSet('failed')
    MOKO.ScriptEnd('failed')
#Endregion

#Region Выдержка под давлением
try:
    MOKO.StageSeparator("5 минут задержка между измерениями")
    #hash 5 минут
    MOKO.HashSelect("5 минут")
    MOKO.MessageSetWithImage('Пауза между измерениями',
                             'Пожалуйста, подождите 5 минут между измерениями.',
                             'images\Waiting5Minutes.png',
                             '300')
    MOKO.HashSet("passed")

except Exception as e:
    MOKO.StageError(f"Ошибка при отображении окна паузы: {e}. Выполняется обычная задержка.")
#Endregion

#Region Обратный ход: от MAX к MIN
try:
    MOKO.HashExecuteStep("Обратный ход: от MAX к MIN")
    # ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️
    #hash Точка 1$DOWN:+;+;+;+;+;+;
    #hash Точка 2$DOWN:+;+;+;+;+;+;
    #hash Точка 3$DOWN:+;+;+;+;+;+;
    #hash Точка 4$DOWN:+;+;+;+;+;+;
    #hash Точка 5$DOWN:+;+;+;+;+;+;
    #hash Точка 6$DOWN:+;-;-;-;-;-;
    #hash Точка 7$DOWN:+;-;-;-;-;-;
    #hash Точка 8$DOWN:+;-;-;-;-;-;

    MOKO.StageSeparator("Начинается заполнение таблицы обратного хода")
    res_down = measure_checkpoints(checkpoints, params.driver, params.unit, Simulation, reverse=True)
    MOKO.StageSeparator("Разворачиваем результаты обратного хода для соответствия порядку точек")
    res_down = list(reversed(res_down))
    MOKO.StageSuccess(f"Обратный ход завершён. Измерено {len(res_down)} точек")

except Exception as e:
    MOKO.StageError(f"Ошибка при выполнении обратного хода: {e}")
    MOKO.HashSet('failed')
    MOKO.ScriptEnd('failed')
#Endregion

#Region Расчет погрешности$POV
try:
    MOKO.HashExecuteStep("Расчет погрешности$POV")
    # 📊  📊  📊  📊  📊  📊  📊  📊  📊  📊  📊

    # 1. Расчет абсолютной погрешности для прямого и обратного хода, а также вариации показаний
    err_up, err_down, variation, variation_pct = calc_err_variation(checkpoints, res_up, res_down)


    # 2. Определение максимальных значений погрешности для прямого (err_up) и обратного (err_down) хода
    max_err_up, max_err_down = max_err(err_up, err_down)
    MOKO.ReportSetInfoStrings(
        ("Максимальная погрешность UP",            max_err_up,       "Максимальная погрешность для прямого хода"),
        ("Максимальная погрешность DOWN",          max_err_down, "Максимальная погрешность для обратного хода"),
    )

    # 3. Выбор наибольшей погрешности из двух ходов
    if max_err_up == '-' or max_err_down == '-':
        max_err = '-'  # Если данные отсутствуют
    else:
        max_err = max([max_err_up, max_err_down], key=abs)  # По модулю
    MOKO.ReportSetInfoStrings(
        ("Максимальная погрешность", max_err, "Максимальная погрешность"),
    )
    # 4. Определение результата поверки и заключения о годности
    result, conclusion = conclusion(max_err, permissible_err, trial_appearance, trial_result)

    # ========== СОЗДАНИЕ ОСНОВНОЙ ТАБЛИЦЫ (СВОДНОЙ) С РЕЗУЛЬТАТАМИ ИЗМЕРЕНИЙ ==========
    # Эта таблица создаётся функцией reports() и содержит только числовые данные
    main_reports(
        checkpoints,
        res_up,
        res_down,
        err_up,
        err_down,
        variation,
        variation_pct,
        params.unit,
        params.permissible_error,
        max_err,
    )

    MOKO.ReportTableCreate('Перечень приборов давления',"Тип СИ;Предел измерения;Ед. изм.;Класс точности;Заводской номер;Результат поверки;Дата поверки" )
    MOKO.ReportSetTable('Перечень приборов давления',)
    # ---- ИНИЦИАЛИЗИРУЕМ ПЕРВУЮ ТАБЛИЦУ (с информацией об образце) ----
    #results(
    #    params.location,
    #    params.device_type,
    #    params.scale_max,
    #    params.accuracy,
    #    params.division,
    #    trial_appearance,
    #    trial_result,
    #    params.stamp_number
    #)

except Exception as e:
    MOKO.StageError(f"Ошибка при расчёте погрешности: {e}")
    MOKO.HashSet('failed')
    # Устанавливаем значения по умолчанию, чтобы избежать ошибок в дальнейшем
    result = "не соответствует"
    conclusion = "не годен"
    MOKO.ReportSetString('Результат поверки', result)
    MOKO.ReportSetString('Заключение', conclusion)
    MOKO.ScriptEnd('failed')
#Endregion

#Region Формирование отчета и завершение
try:
    # Запись заключительных строк в отчёт
    MOKO.ReportSetStrings(
        ("Заключение", f'{conclusion}')
    )

    MOKO.StageSuccess("Все таблицы успешно заполнены!")

except Exception as e:
    MOKO.StageError(f"Ошибка при формировании отчета: {e}")
#EndRegion

MOKO.EndScript()