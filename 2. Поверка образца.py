from pressurelib import *
from protocol_utils import get_protocol_info, set_additional_parameters
import MOKO

UN = 'moko_pressure_mini'  # Utility Name
# Извлечение словаря с данными, введёнными пользователем через интерфейс
data = get_protocol_info()

# Устанавливаем дополнительные параметры MeasuringRange
set_additional_parameters(data)

# Получаем данные с приведением к нужным типам
AccuracyClass     = float(data['AccuracyClass']) if data['AccuracyClass'] else 0.0   # класс точности
UnitOfMeasure     = str(data['UnitOfMeasure'])                                        # единицы измерения
ScaleMax          = float(data['ScaleMax']) if data['ScaleMax'] else 0.0             # предельное значение давления
FirstPoint        = float(data['FirstPoint']) if data['FirstPoint'] else 0.0         # первая поверяемая точка
PermissibleError  = str(data['PermissibleError'])                                    # пределы допускаемой погрешности
Driver            = str(data['Driver'])                                              # драйвер
WorkplaceNumber   = str(data['WorkplaceNumber'])                                     # номер рабочего места
TypeofUnit        = str(data['TypeofUnit'])                                          # тип образца
ValueofDivision   = str(data['ValueofDivision'])                                     # цена деления
StampNumber       = str(data['StampNumber'])                                         # номер штампа

#Region Внешний осмотр$shdjfhsdf
MOKO.HashExecuteStep("Внешний осмотр$shdjfhsdf")
# 🔎 🔎 🔎 🔎 🔎 🔎 🔎 🔎 🔎 🔎 🔎 🔎 🔎 🔎

# hash Соответствие внешнего вида
MOKO.HashSelect('Соответствие внешнего вида')
appearance = "соответствует" if MOKO.MessageGetBool('Образец #@warning',
                                                    'Пожалуйста, проведите внешний осмотр образца. '
                                                    'Соответствует ли внешний вид образца установленным нормам?') else "не соответствует"

if appearance == "соответствует": MOKO.HashSet('passed')
else: MOKO.HashSet('failed')

Simulation = driver_choice(Driver)  # Driver initialisation
permissible_err = ScaleMax * 0.01 * AccuracyClass
#meas_error = ScaleMax * AccuracyClass / 100
checkpoints = [round(x * FirstPoint, 1) for x in range(int(ScaleMax / FirstPoint) + 1)]  # calculating checkpoints for measurement
checkpoints = final_checkpoints(checkpoints)

# Установка единиц измерения на эталонном приборе (если не симуляция)
if not Simulation:
    set_unit_of_measure(Driver, UnitOfMeasure)

#Endregion
# 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁

#Region Прямой ход: от MIN к MAX
#Description: класс 0.6;класс 1;класс 1.5;класс 1.6;класс 2.5;класс 4;
MOKO.StageSeparator("Прямой ход: от нуля до максимального значения")
# ⬆️ ⬆️ ⬆️ ⬆️ ⬆️ ⬆️ ⬆️ ⬆️ ⬆️ ⬆️ ⬆️ ⬆️ ⬆️ ⬆️
#hash Точка 1$UP:+;+;+;+;+;+;
#hash Точка 2$UP:+;+;+;+;+;+;
#hash Точка 3$UP:+;+;+;+;+;+;
#hash Точка 4$UP:+;+;+;+;+;+;
#hash Точка 5$UP:+;+;+;+;+;+;
#hash Точка 6$UP:+;-;-;-;-;-;
#hash Точка 7$UP:+;-;-;-;-;-;
#hash Точка 8$UP:+;-;-;-;-;-;
res_up = measure_checkpoints(checkpoints, Driver, UnitOfMeasure, Simulation)  # reverse=False по умолчанию
#Endregion
# 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁

#Region Выдержка под давлением
MOKO.StageSeparator("5 минут задержка между измерениями")
# ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛ ⌛

#hash 5 минут
MOKO.MessageSetWithImage('Пауза между измерениями',
                'Пожалуйста, подождите 5 минут между измерениями.',
                '@time',
                '300')
#Endregion
# 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁


#Region Обратный ход: от MAX к MIN
MOKO.StageSeparator("Обратный ход: от максимума до нуля")
# ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️ ⬇️
#hash Точка 1$DOWN:+;+;+;+;+;+;
#hash Точка 2$DOWN:+;+;+;+;+;+;
#hash Точка 3$DOWN:+;+;+;+;+;+;
#hash Точка 4$DOWN:+;+;+;+;+;+;
#hash Точка 5$DOWN:+;+;+;+;+;+;
#hash Точка 6$DOWN:+;-;-;-;-;-;
#hash Точка 7$DOWN:+;-;-;-;-;-;
#hash Точка 8$DOWN:+;-;-;-;-;-;
res_down = measure_checkpoints(checkpoints, Driver, UnitOfMeasure, Simulation, reverse=True)
# Разворачиваем результаты обратного хода для соответствия порядку точек
MOKO.StageSeparator("Разворачиваем результаты обратного хода для соответствия порядку точек")
res_down = list(reversed(res_down))
#Endregion
# 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁


# Region ----- Расчет погрешности ------
MOKO.StageSeparator("Расчет погрешности")
# 📊  📊  📊  📊  📊  📊  📊  📊  📊  📊  📊

# 1. Расчет абсолютной погрешности для прямого и обратного хода, а также вариации показаний
err_up, err_down, variation = calc_err_variation(checkpoints, res_up, res_down)

# 2. Определение максимальных значений погрешности для прямого (err_up) и обратного (err_down) хода
max_err_up, max_err_down = max_err(err_up, err_down)

# 3. Выбор наибольшей погрешности из двух ходов
if max_err_up == '-' or max_err_down == '-':
    max_err = '-'  # Если данные отсутствуют
else:
    max_err = max([max_err_up, max_err_down], key=abs)  # По модулю

# 4. Определение результата поверки и заключения о годности
result, conclusion = conclusion(max_err, permissible_err, appearance)
# endregion
# 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁 🏁


results(WorkplaceNumber, TypeofUnit, ScaleMax, AccuracyClass, ValueofDivision, appearance, result, StampNumber)
# Reports
reports(checkpoints, res_up, res_down, err_up, err_down, variation, UnitOfMeasure, PermissibleError, max_err)


MOKO.ReportSetStrings(("Appearance", f'{appearance}'),
                      ("Conclusion", f'{conclusion}'))
MOKO.ReportSetTable('Res_table1',  ' ' + ';' + ' ' + ';' + ' ' + ';' + ' ' + ';' + ' ' + ';' + ' ' + ';' + ' ')

MOKO.EndScript()
