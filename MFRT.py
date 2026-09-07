"""
MFRT.py - Библиотека для форматирования чисел MOKO
====================================================

Эта библиотека предоставляет расширенные возможности для форматирования и преобразования чисел
между стандартными типами Python (float, int, str) и строковым представлением, использующим
SI-префиксы (например, '1.2k', '500m', '10G').

Она предназначена для выполнения сложных преобразований, включая:
- Парсинг чисел с префиксами и разделителями.
- Форматирование чисел с заданной точностью и префиксом.
- Расширенные опции округления (математическое, в большую или меньшую сторону).

Примеры использования:
--------------------

**1. Преобразование строки с префиксом в число:**
```python
import MFRT

frequency_str = "1.25k"
frequency_float = MFRT.ConvertStringToFloat(frequency_str)
# frequency_float будет равен 1250.0
```

**2. Преобразование числа в строку с префиксом:**
```python
import MFRT

voltage = 0.05
# Преобразуем в строку с префиксом 'm' (милли) и 2 знаками после запятой
voltage_str = MFRT.ConvertFloatToString(voltage, prefix='m', resolution=2, delimiter=',')
# voltage_str будет равен "50,00m"
```
"""
import decimal
import math
from decimal import Decimal

# region ### Public API Functions / Публичные функции API ###

# region --- ConvertStringToFloat / Преобразовать строку в float ---
def ConvertStringToFloat(value: str):
    """
    Преобразует строку с SI-префиксом в число с плавающей точкой (float).

    Args:
        value (str): Входная строка с числом (например, "1.25k").

    Returns:
        float: Преобразованное число.
    """
    if not isinstance(value, str):
        return float(value)
    library_object = MFRTLibrary(value=value, resolution=0)
    return library_object.get_prefix_in_value()
# endregion

# region --- ConvertFloatToString / Преобразовать float в строку ---
def ConvertFloatToString(value: (float, str, int),
                         reference_number: str = None,
                         resolution: int = 0,
                         delimiter: str = None,
                         prefix: str = None,
                         round_type: str = "NORMAL",
                         round_number: int = 0,
                         type_value_result: str = "String",
                         enable_rounding: bool = False,
                         abs_number: bool = False):
    """
    Преобразует число в строку с SI-префиксом и заданным форматированием.

    Это мощная функция с множеством настроек для форматирования, округления и
    представления числа по шаблону.

    Args:
        value: Входное число для преобразования.
        reference_number (str, optional): Строка-шаблон для форматирования.
        resolution (int, optional): Количество знаков после запятой.
        delimiter (str, optional): Символ-разделитель для дробной части.
        prefix (str, optional): Желаемый SI-префикс для вывода.
        round_type (str, optional): Метод округления ("NORMAL", "UP", "DOWN"). Defaults to "NORMAL".
        round_number (int, optional): Количество знаков для округления.
        type_value_result (str, optional): Тип возвращаемого значения ("String", "Float", "Decimal", "Integer"). Defaults to "String".
        enable_rounding (bool, optional): Включает режим округления. Defaults to False.
        abs_number (bool, optional): Использовать абсолютное значение числа. Defaults to False.

    Returns:
        Преобразованное значение в указанном формате.
    """
    library_object = MFRTLibrary(
        value=value,
        reference_number=reference_number,
        resolution=resolution,
        delimiter=delimiter,
        prefix=prefix,
        round_type=round_type,
        round_number=round_number,
        type_value_result=type_value_result,
        enable_rounding=enable_rounding,
        abs_number=abs_number)
    value = library_object.translate_value()
    try:
        match library_object.type_value_result:
            case "String":
                return str(value)
            case "Integer":
                return int(value)
            case "Decimal":
                return Decimal(value)
            case "Float":
                return float(value)
            case _:
                return str(value)
    except ValueError:
        return str(value)
# endregion

# endregion

# region ### Core Formatting Class / Основной класс форматирования ###
class MFRTLibrary:
    # region --- Constants & Initialization / Константы и инициализация ---

    # -- Константы --
    round_types_list = ["NORMAL", "UP", "DOWN"]
    type_values_allowed_list = ["String", "Float", "Decimal", "Integer"]
    list_prefix_english = ['P', 'T', 'G', 'M', 'k', '-', 'm', 'u', 'n', 'p', 'f']
    list_prefix_russian = ['П', 'Т', 'Г', 'М', 'к', '-', 'м', 'мк', 'н', 'п', 'ф']

    # -- __init__ --
    def __init__(self, value: (float, str, int), reference_number: str = None, resolution: int = None,
                 delimiter: str = None, prefix: str = None, round_type: str = round_types_list[0],
                 round_number: int = 0, type_value_result: str = type_values_allowed_list[0],
                 enable_rounding: bool = False, abs_number: bool = False):
        """Инициализирует ядро форматера со всеми необходимыми параметрами."""
        self.__value = value
        self.__reference_number = reference_number
        self.__resolution = resolution if resolution > 0 else 0
        self.__delimiter = delimiter
        self.__prefix = prefix
        self.__prefix_value = None
        self.type_value_result = (type_value_result if type_value_result in self.type_values_allowed_list
                                  else self.type_values_allowed_list[0])
        self.__get_prefix, self.__check = False, False
        self.__enable_rounding = enable_rounding
        self.__round_number = round_number
        self.__abs_number = abs_number
        self.__round_type = round_type if round_type in self.round_types_list else self.round_types_list[0]
        self.__translate_value = self.__reference_number if self.__reference_number else self.__value
    # endregion

    # region --- Public Methods / Публичные методы ---

    # -- get_prefix_in_value --
    def get_prefix_in_value(self):
        """
        Конвертирует число из строки с префиксом в нормальную форму (float).
        Также может быть использован для извлечения префикса из строки.

        Returns:
            float: Число, если функция вызывалась для преобразования.
            str: Префикс числа, в противном случае.
        """
        if self.__translate_value[-2:] in self.list_prefix_english + self.list_prefix_russian:
            ind = 2
        elif self.__translate_value[-1:] in self.list_prefix_english + self.list_prefix_russian:
            ind = 1
        else:
            ind = 0
        self.__prefix_value = self.__translate_value[-ind:] if ind != 0 else '-'
        self.__get_delimiter_value(ind=ind)
        try:
            self.__translate_value = Decimal(self.__translate_value)
        except decimal.InvalidOperation:
            return self.__value
        if self.__get_prefix:
            self.__get_prefix = False
            return self.__prefix_value
        self.__translate_value = self.__translate_value * self.__create_translation_constant()
        return float(f'{self.__translate_value:.14f}')

    # -- translate_value --
    def translate_value(self):
        """
        Основная функция, выполняющая преобразование числа из float или int в строку с SI-префиксом.

        Returns:
            Преобразованное значение для вывода.
        """
        if not self.__reference_number and not self.__resolution and not self.__delimiter and not self.__prefix:
            if isinstance(self.__value, (int | float)):
                self.__value = round(self.__rounded_value(value=Decimal(self.__value)))
            return str(self.__value)
        if isinstance(self.__value, (float, int)):
            if isinstance(self.__value, int):
                self.__value = f'{Decimal(self.__value):.14f}'.split('.')[0]
            else:
                self.__value = Decimal(self.__value)
                if 'e' in str(self.__value) and not self.__resolution and not self.__reference_number:
                    self.__resolution = int(str(self.__value)[-2:])
                elif not self.__resolution and not self.__reference_number:
                    self.__resolution = len(str(self.__value).split('.')[1])
                self.__value = f'{Decimal(self.__value):.14f}'
                self.__value = self.__value.split('.')[0] + '.' + self.__value.split('.')[1]
        elif isinstance(self.__value, str) and not self.__reference_number and not self.__resolution:
            delimiter_value = next((x for x in self.__value[1:] if not x.isdigit() and not x.isalpha()), None)
            if delimiter_value:
                self.__resolution = len(self.__value.split(delimiter_value)[1])
            else:
                self.__resolution = 0
        if not self.__reference_number:
            self.__check = True
            if self.__check_prefix_in_value():
                try:
                    Decimal(self.__value)
                except ValueError:
                    self.__translate_value = self.__value
                    self.__value = self.get_prefix_in_value()
                return self.__check_zeros_after_point_in_string()
            return self.__value
        else:
            if not self.__prefix:
                self.__get_prefix = True
                self.__prefix = self.get_prefix_in_value()
            else:
                self.__check = True
                if not self.__check_prefix_in_value():
                    return self.__value
            if not self.__check_prefix_in_value():
                return self.__value
            return self.__translate_variable_reference_number_and_prefix()
    # endregion

    # region --- Internal Helper Methods / Внутренние вспомогательные методы ---

    # -- __create_translation_constant --
    def __create_translation_constant(self):
        """
        Создает множитель (float) на основе SI-префикса для увеличения или уменьшения числа.

        Returns:
            Decimal: Множитель для преобразования.
        """
        if self.__prefix_value in self.list_prefix_english and self.__prefix_value != '-':
            list_prefix = self.list_prefix_english
        elif self.__prefix_value in self.list_prefix_russian and self.__prefix_value != '-':
            list_prefix = self.list_prefix_russian
        else:
            return Decimal(1.0)
        index = list_prefix.index(self.__prefix_value)
        len_lst_prefix = len(list_prefix)
        const_resolution = (len_lst_prefix // 2 - index) * 3
        return Decimal(round(10 ** const_resolution, (len(list_prefix) - 1) // 2 * 3))

    # -- __translate_variable_not_reference_number --
    def __translate_variable_not_reference_number(self):
        """
        Преобразует значение в выходной формат, когда не задан шаблон (reference_number).

        Returns:
            Преобразованное число.
        """
        if self.__resolution:
            self.__delimiter = next((x for x in self.__value[1: len(self.__value)] if not x.isdigit()), None)
            self.__get_prefix = True
            self.__translate_value = self.__value
            self.__prefix = self.get_prefix_in_value()
            if self.__delimiter:
                self.__value = self.__value.replace(self.__delimiter, '.')
                self.__value = self.__value[:-len(self.__prefix)] if self.__prefix != '-' else self.__value
            self.__value = f'{Decimal(self.__value):.14f}'.split('.')
            return (self.__value[0] + f"{self.__delimiter if self.__delimiter else '.'}" +
                    self.__value[1][:self.__resolution])
        else:
            return self.__rounded_value(self.__value)

    # -- __translate_variable_reference_number_and_prefix --
    def __translate_variable_reference_number_and_prefix(self):
        """
        Преобразует значение в выходной формат, когда задан шаблон (reference_number).

        Returns:
            Преобразованное число.
        """
        if self.__prefix:
            self.__translate_value = self.__value
            self.__value = self.get_prefix_in_value()
            delimiter_reference_number = next((x for x in self.__reference_number[1: -(len(self.__prefix))]
                                               if not x.isdigit()), None)
            if not self.__delimiter and not delimiter_reference_number:
                return self.__check_zeros_after_point_in_string()
            self.__delimiter = self.__delimiter if self.__delimiter else delimiter_reference_number
            if not self.__resolution:
                if self.__prefix != "-" and delimiter_reference_number:
                    self.__resolution = len(self.__reference_number.split(delimiter_reference_number)[1]) - len(
                        self.__prefix)
                elif delimiter_reference_number:
                    self.__resolution = len(self.__reference_number.split(delimiter_reference_number)[1])
                else:
                    self.__resolution = 0
            return self.__check_zeros_after_point_in_string()
        self.__value = self.__rounded_value(self.__value)
        return self.__translate_variable_not_reference_number()

    # -- __check_zeros_after_point_in_string --
    def __check_zeros_after_point_in_string(self):
        """
        Финальное форматирование числа из float в строку с нужной точностью и префиксом.

        Returns:
            Преобразованное значение для вывода.
        """
        if self.__prefix:
            self.__prefix_value = self.__prefix
        translation_cost = self.__create_translation_constant()
        translation_value = self.__rounded_value(Decimal(Decimal(self.__value) / Decimal(translation_cost)))
        formatted_translation_value = f'{Decimal(translation_value):.14f}'.split('.')
        if not self.__prefix:
            self.__prefix = ''
        else:
            self.__prefix = '' if self.__prefix in '-' or not self.__prefix_value else self.__prefix
        if not self.__delimiter or not self.__resolution:
            if self.__resolution:
                return (formatted_translation_value[0] + '.' + formatted_translation_value[1][:self.__resolution] +
                        self.__prefix)
            return formatted_translation_value[0] + self.__prefix
        if len(formatted_translation_value[1]) < self.__resolution:
            self.__resolution = len(formatted_translation_value[1])
        return (formatted_translation_value[0] + self.__delimiter + formatted_translation_value[1][:self.__resolution] +
                self.__prefix)

    # -- __check_prefix_in_value --
    def __check_prefix_in_value(self):
        """Проверяет корректность заданного префикса."""
        if self.__check:
            self.__check = False
            if (self.__prefix not in self.list_prefix_english + self.list_prefix_russian) and self.__prefix:
                return False
            return True
        if self.__prefix in self.list_prefix_english:
            self.__list_prefix = self.list_prefix_english
        else:
            self.__list_prefix = self.list_prefix_russian
        return True

    # -- __get_delimiter_value --
    def __get_delimiter_value(self, ind: int = None):
        """Определяет и заменяет разделитель в строке на точку."""
        delimiter_value = next(
            (x for x in self.__translate_value[1: -(len(self.__prefix_value))] if not x.isdigit()), None)
        self.__translate_value = self.__translate_value[:-ind] if ind != 0 else self.__translate_value
        if delimiter_value:
            self.__translate_value = self.__translate_value.replace(delimiter_value, '.')

    # -- __rounded_value --
    def __rounded_value(self, value: Decimal):
        """Выполняет округление числа в соответствии с заданными параметрами."""
        value = abs(value) if self.__abs_number else value
        if self.__enable_rounding:
            value += Decimal(0.0000000000000000000001)
            if self.__round_number:
                if self.__round_type == self.round_types_list[0]:
                    value = Decimal(round(value, self.__round_number))
                elif self.__round_type == self.round_types_list[1]:
                    value = Decimal(
                        math.ceil(value * 10 ** Decimal(self.__round_number)) / Decimal(10 ** self.__round_number))
                elif self.__round_type == self.round_types_list[2]:
                    value = Decimal(
                        math.floor(value * 10 ** Decimal(self.__round_number)) / Decimal(10 ** self.__round_number))
            else:
                if self.__round_type == self.round_types_list[0]:
                    value = Decimal(round(value))
                elif self.__round_type == self.round_types_list[1]:
                    value = Decimal(math.ceil(value))
                elif self.__round_type == self.round_types_list[2]:
                    value = Decimal(math.floor(value))
        return value
    # endregion
# endregion
