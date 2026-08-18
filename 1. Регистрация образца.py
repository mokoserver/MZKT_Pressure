import MOKO
from protocol_utils import get_protocol_info, fill_report_info
UN = 'moko_pressure_mini'  # Utility Name

#Region ------------------------------$REG1
MOKO.HashExecuteStep('Регистрация образца')

# ========== ЗАГОЛОВОК СКРИПТА ==========
MOKO.StageSeparatorWithTitle("Скрипт ввода информации об образце и климатических условий")

# ========== ВВОД ДАННЫХ ==========
#hash Ввод данных
MOKO.HashSelect('Ввод данных')
MOKO.StageSeparator("Ввод информации об образце и климатических условиях")
MOKO.UtilitySet(UN, 'info')
MOKO.HashSet('passed')

# ========== ПОЛУЧЕНИЕ ДАННЫХ ==========
#hash Получение данных
MOKO.HashSelect('Получение данных')
# Извлечение словаря с данными, введёнными пользователем через интерфейс
data = get_protocol_info()
MOKO.HashSet('passed')

# ========== ФОРМИРОВАНИЕ ОТЧЕТА ==========
#hash Формирование отчета
MOKO.HashSelect('Формирование отчета')
MOKO.StageSeparator("Чтение введенных данных в переменные скрипта")
fill_report_info(data)
MOKO.StageSeparator("Все данные успешно внесены в протокол")
MOKO.HashSet('passed')  # Устанавливаем флаг успешного выполнения шага

#EndRegion

#Region ------------------------------$REG2
#EndRegion

MOKO.ScriptEnd()
