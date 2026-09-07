import MOKO
from protocol_utils import get_protocol_info, fill_report_info

# ========== ЗАГОЛОВОК СКРИПТА ==========
MOKO.StageSeparatorWithTitle("Скрипт ввода информации об образце и климатических условий")
UN = 'moko_pressure_graph'  # Utility Name



#Region ------------------------------$REG1
try:
    MOKO.HashExecuteStep('Регистрация образца')
except Exception as e:
    MOKO.StageError(f"Ошибка при выполнении шага 'Регистрация образца': {e}")
    MOKO.HashSet('failed')
    MOKO.ScriptEnd('failed')


# ========== ВВОД ДАННЫХ ==========
try:
    #hash Ввод данных
    MOKO.HashSelect('Ввод данных')
    MOKO.StageSeparator("Ввод информации об образце и климатических условиях")
    MOKO.UtilitySet(UN, 'info')
    MOKO.HashSet('passed')
except Exception as e:
    MOKO.StageError(f"Ошибка при вводе данных (UtilitySet): {e}")
    MOKO.HashSet('failed')
    MOKO.ScriptEnd('failed')

# ========== ПОЛУЧЕНИЕ ДАННЫХ ==========
try:
    #hash Получение данных
    MOKO.HashSelect('Получение данных')
    data = get_protocol_info()
    MOKO.HashSet('passed')
except Exception as e:
    MOKO.StageError(f"Ошибка при получении данных из утилиты: {e}")
    MOKO.HashSet('failed')
    MOKO.ScriptEnd('failed')

# ========== ФОРМИРОВАНИЕ ОТЧЕТА ==========
try:
    #hash Формирование отчета
    MOKO.HashSelect('Формирование отчета')
    MOKO.StageSeparator("Чтение введенных данных в переменные скрипта")
    fill_report_info(data)
    MOKO.StageSeparator("Все данные успешно внесены в протокол")
    MOKO.HashSet('passed')
except Exception as e:
    MOKO.StageError(f"Ошибка при формировании отчета (fill_report_info): {e}")
    MOKO.HashSet('failed')
    MOKO.ScriptEnd('failed')

#EndRegion

#Region ------------------------------$REG2
#EndRegion

MOKO.ScriptEnd()
