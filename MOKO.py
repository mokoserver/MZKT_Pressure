'''
Библиотека MOKO.py
==================

Эта библиотека представляет собой Python-клиент для взаимодействия с программой MOKO SE.
Она позволяет управлять различными компонентами, плагинами и устройствами, подключенными к MOKO SE,
путем отправки HTTP-запросов на локальный сервер.

Ключевые возможности:
---------------------
- **Управление устройствами:** Взаимодействие с драйверами (`Driver`) и портами (`Port`).
- **Автоматизация GUI:** Управление элементами интерфейса внешних приложений (`Autoit`).
- **Взаимодействие с пользователем:** Отображение информационных окон и диалогов (`Message`).
- **Логирование и отчеты:** Отправка сообщений в лог (`Stage`) и управление отчетами (`Report`).
- **Управление системой:** Выполнение команд (`CMD`), работа с плагинами (`Plugin`) и утилитами (`Utility`).
- **Синхронизация:** Контроль за состоянием выполнения проекта (`check_project_state`).

Принцип работы:
---------------
Библиотека функционирует как API-обертка, отправляя POST-запросы в формате JSON на
HTTP-сервер, запущенный MOKO SE по адресу `http://localhost:55001`.

Зависимости:
-------------
- `requests`
- `json`

История версий:
---------------
- 26.02.2021: Библиотека переименована в MOKO.py.
- 23.06.2021 (v1.5): Изменен формат POST-запросов для драйверов.
- 24.01.2022: Внесены исправления для корректной работы команд start/pause/stop.
- 22.08.2022: Обновлена функция парсинга и проведена рефакторинг.
- 09.09.2022: Параметр 'type' заменен на 'mode' в JSON-запросах (обратная совместимость нарушена).
- 25.03.2026: Добавление регионов и комментариев в новом формате (обратная совместимость нарушена).
- 26.03.2026: Подготовка к исключению библиотеки MOSK (обратная совместимость нарушена).
- 30.03.2026: Добавлены сокращения для Stage (StageError, StageInfo и т.д.).
- 30.03.2026: Добавлены функции  Tree & Hash, Time, Report
- 05.04.2026: Добавлена функции  мессенджера MAX
- 07.04.2026: Испаравлено _request = requests.Session()
- 05.05.2026: Серверный путь исправлен с MOKOSE на SE
- 20.05.2026: Добавлено DriverSet и DriverGet
'''

import time
import requests
import json
import sys
import os
from typing import Literal, overload, Any, Union, Optional
from functools import partial


# region ### URLs for SE API / URL-адреса для SE API ###
_request = requests.Session()

_BASE_URL = "http://localhost:55001/SE"

# --- Status ---
_UrlProjectStateRead: str = f"{_BASE_URL}/status/projectstate"

# --- Stage ---
_UrlStageWrite: str = f"{_BASE_URL}/stage/stagewrite"

# --- System Components ---
_UrlAutoitWrite: str = f"{_BASE_URL}/system/autoitwrite"
_UrlAutoitRead: str = f"{_BASE_URL}/system/autoitread"

_UrlDriverWrite: str = f"{_BASE_URL}/system/driverwrite"
_UrlDriverRead: str = f"{_BASE_URL}/system/driverread"

_UrlPluginWrite: str = f"{_BASE_URL}/system/pluginwrite"
_UrlPluginRead: str = f"{_BASE_URL}/system/pluginread"

_UrlMessageWrite: str = f"{_BASE_URL}/system/messagewrite"
_UrlMessageRead: str = f"{_BASE_URL}/system/messageread"

_UrlReportWrite: str = f"{_BASE_URL}/system/reportwrite"
_UrlReportRead: str = f"{_BASE_URL}/system/reportread"

_UrlProgramWrite: str = f"{_BASE_URL}/system/programwrite"
_UrlProgramRead: str = f"{_BASE_URL}/system/programread"

_UrlUtilityWrite: str = f"{_BASE_URL}/system/utilitywrite"
_UrlUtilityRead: str = f"{_BASE_URL}/system/utilityread"

_UrlTelegramWrite: str = f"{_BASE_URL}/system/telegramwrite"
_UrlTelegramRead: str = f"{_BASE_URL}/system/telegramread"

_UrlMaxWrite: str = f"{_BASE_URL}/system/maxwrite"
_UrlMaxRead: str = f"{_BASE_URL}/system/maxread"

_UrlCmdWrite: str = f"{_BASE_URL}/system/cmdwrite"
_UrlCmdRead: str = f"{_BASE_URL}/system/cmdread"

_UrlPortWrite: str = f"{_BASE_URL}/system/portwrite"
_UrlPortRead: str = f"{_BASE_URL}/system/portread"
# endregion

###############################################################
### SE API Functions / Функции SE API #########################
###############################################################

#  ---------------------- CMD --------------------------------------

# region --- CMD() / Командная строка ---
def CMD(mode: Literal['set', 'get'],
        command: str) -> Any:
    """
    Выполняет команду в командной строке (CMD) через MOKO SE.

    Args:
        mode (str): Режим выполнения команды. Возможные значения: ???.
        command (str): Команда для выполнения.

    Returns:
        str: Результат выполнения команды, возвращенный сервером. Формат: ???.
    """
    check_project_state()
    url_write: str = _UrlCmdWrite
    url_read: str = _UrlCmdRead
    command_to_send: str = f'{{"mode":"{str(mode)}", "command":"{str(command)}"}}'
    send_request(url_write, command_to_send)
    cmd_data: str = check_status("cmd", mode, url_read)
    return cmd_data
# endregion

#  ---------------------- Port -------------------------------------

# region --- Port() / Порт ---
def Port(
    name: str,
    mode: Literal['init', 'interface', 'write', 'read','clear'],
    command: str = '',
    valuetype: Literal['string', 'int', 'float', 'bool', 'arrayint', 'arrayfloat', 'arrayboolean', 'arraystring'] = 'string'
) -> Any:
    """
    Управляет портами и устройствами, настроенными в MOKO SE.

    Позволяет инициализировать, настраивать, отправлять и получать данные с устройств,
    подключенных через различные интерфейсы (COM, LPT, и т.д.), используя их логическое имя.

    Args:
        name (str): Логическое имя порта/устройства, заданное в MOKO SE.
        mode (str): Режим работы. Основные значения: 'init', 'interface', 'write', 'read'.
        command (str, optional): Команда или данные для отправки в порт (используется в режиме 'write'). Defaults to ''.
        valuetype (str, optional): Ожидаемый тип данных при чтении (используется в режиме 'read'). Defaults to 'string'.

    Returns:
        str: Результат операции. Например:
             - Для 'init' и 'interface': 'ok' в случае успеха, 'error' в случаи не подключения.
             - Для 'write': 'ok' в случае успеха, 'error' в случаи ошибки.
             - Для 'read': прочитанные данные.
             - В случае ошибки может возвращать 'error'.
    """
    check_project_state()
    url_write: str = _UrlPortWrite
    url_read: str = _UrlPortRead
    command_to_send: str = f'{{"name":"{str(name)}","mode":"{str(mode)}","command":"{str(command)}"}}'
    send_request(url_write, command_to_send)
    port_data: str = check_status("port", mode, url_read)
    return parse_data(port_data, mode, valuetype)
# endregion

#  ---------------------- Autoit  ----------------------------------

# region --- Autoit() / Автоматизация GUI ---
def Autoit(title: str,
           classname: str,
           method: Literal['ControlClick', 'ControlGetText', 'ControlSetText'],
           attributes: str = 'void') -> Any:
    """
    Взаимодействует с элементами GUI внешних приложений, используя технологию AutoIt.

    Позволяет автоматизировать действия в окнах, например, чтение текста из полей или нажатие кнопок.

    Args:
        title (str): Заголовок окна целевого приложения.
        classname (str): Имя класса элемента управления в окне (например, 'Edit1').
        method (str): Метод для выполнения над элементом (например, 'ControlGetText').
        attributes (str, optional): Дополнительные атрибуты для команды. Defaults to 'void'.

    Returns:
        str: Результат выполнения команды (например, полученный текст).
    """
    check_project_state()
    url_write: str = _UrlAutoitWrite
    url_read: str = _UrlAutoitRead
    command_to_send: str = f'{{"title":"{str(title)}", "classname":"{str(classname)}","method":"{str(method)}","attributes":"{str(attributes)}"}}'
    send_request(url_write, command_to_send)
    autoit_data: str = check_status("autoit", method, url_read)
    return autoit_data
# endregion

#  ---------------------- Stage  -----------------------------------
# region --- StageType = Literal ---
StageType = Literal[
    'info', 'success', 'fail', 'empty', 'error', 'warning',
    'telegram', 'max', 'message', 'utility', 'autoit', 'cmd',
    'port', 'driver', 'plugin', 'report', 'project', 'script'
]
# endregion

# region --- Stage() / Логирование этапов ---
def Stage(message: str = '',
          type: StageType = "info") -> None:
    """
    Отправляет и отображает сообщение в окне "Stage" в MOKO SE.

    Используется для логирования и информирования пользователя во время выполнения скрипта.

    Args:
        message (str): Текст сообщения для вывода.
        type (str, optional): Тип сообщения. Влияет на его отображение.
                              Возможные значения: 'Info', 'Error', 'Plugin', 'Driver', 'Report', 'Warning'.
                              Defaults to 'info'.
    """
    type = type.lower()
    check_project_state()
    url_write: str = _UrlStageWrite
    command_to_send: str = f'{{"string" :"{str(message)}", "type":"{str(type)}"}}'
    send_request(url_write, command_to_send)
# endregion

# region --- Stage...() - Shortcuts / Сокращения для Stage --- <-- ИЗМЕНЕНИЕ 3: Новый регион
# Информационные
StageInfo = partial(Stage, type='info')
StageSuccess = partial(Stage, type='success')
StageFail = partial(Stage, type='fail')
StageEmpty = partial(Stage, type='empty')
StageError = partial(Stage, type='error')
StageWarning = partial(Stage, type='warning')
# Имитирующие
StageTelegram = partial(Stage, type='telegram')
StageMax = partial(Stage, type='max')
StageMessage = partial(Stage, type='message')
StageUtility = partial(Stage, type='utility')
StageAutoit = partial(Stage, type='autoit')
StageCmd = partial(Stage, type='cmd')
StagePort = partial(Stage, type='port')
StageDriver = partial(Stage, type='driver')
StagePlugin = partial(Stage, type='plugin')
StageReport = partial(Stage, type='report')
# Системные
StageProject = partial(Stage, type='project')
StageScript = partial(Stage, type='script')
# endregion

# region --- StageSeparator() / Декоративный разделитель в лог ---
def StageSeparator(
        word: str = '',
        width: int = 240,
        fillchar: str = '-',
        align: Literal['center', 'left', 'right'] = 'center',
        stage_type: StageType = 'info',
        char_width_factor: float = 1.585  # 👈 КОЭФФИЦИЕНТ: насколько буква шире черточки
) -> None:
    """
    Выводит в Stage декоративный разделитель.

    Args:
        word (str): Слово для вставки в разделитель.
        width (int): Желаемая общая ширина (в символах fillchar). По умолчанию 240.
        fillchar (str): Символ-заполнитель.
        align (str): Выравнивание слова.
        stage_type (str): Тип сообщения Stage.
        char_width_factor (float): Коэффициент ширины букв относительно fillchar.
                                   Например: 1.3 означает, что буква в 1.3 раза шире '-'
                                   Подберите экспериментально для вашего шрифта.
    """
    if not word:
        # Пустое слово → сплошная линия
        line = fillchar * width
    else:
        # Длина слова может быть больше ширины – обрежем
        if len(word) > width:
            word = word[:width - 3] + '...'

        # 👇 ГЛАВНАЯ ЛОГИКА: считаем, сколько места "съедают" буквы
        # Каждая буква занимает место: 1 (как fillchar) * char_width_factor
        # Но fillchar занимает 1 место, поэтому буква "съедает" дополнительно (char_width_factor - 1)
        extra_space = int(len(word) * (char_width_factor - 1))

        # Уменьшаем ширину на "съеденное" место
        adjusted_width = width - extra_space

        # Минимальная ширина - чтобы не было отрицательной
        if adjusted_width < len(word) + 2:
            adjusted_width = len(word) + 2

        if align == 'center':
            # Слово с пробелами по бокам
            word_with_spaces = f" {word} "
            if len(word_with_spaces) > adjusted_width:
                word_with_spaces = word
            line = f"{word_with_spaces:{fillchar}^{adjusted_width}}"
        elif align == 'left':
            line = f"{word:{fillchar}<{adjusted_width}}"
        else:  # right
            line = f"{word:{fillchar}>{adjusted_width}}"

    Stage(line, stage_type)

# endregion

# region --- StageSeparatorWithTitle() /  Декоративный разделитель в лог с разделителем---
def StageSeparatorWithTitle(title: str = ""):
    """
    Выводит разделитель, строку заголовка и ещё один разделитель.
    Если заголовок пустой, выводит только один разделитель (как MOKO.StageSeparator без аргументов).
    """
    StageSeparator()
    if title:
        StageSeparator(title)
        StageSeparator()
# endregion

#  ---------------------- Driver  ----------------------------------

# region --- Driver() / Драйвер ---
def Driver(name: str,
           mode: Literal['set', 'get','init','check','close'],
           command: str = 'void',
           valuetype: Literal['string', 'int', 'float', 'bool', 'arrayint', 'arrayfloat', 'arrayboolean', 'arraystring'] = 'string') -> Any:
    """
    Управляет драйверами устройств через MOKO SE.

    Args:
        name (str): Имя драйвера.
        mode (str): Режим работы с драйвером ('get', 'set', 'init', 'close').
        command (str, optional): Команда для драйвера. Defaults to 'void'.
        valuetype (str, optional): Ожидаемый тип данных при чтении (только для mode='get'). Defaults to 'string'.

    Returns:
        Зависит от режима:
        - 'set', 'init', 'close': None
        - 'get': Данные, полученные от драйвера, преобразованные к типу `valuetype`.
    """
    check_project_state()
    URLWrite: str = _UrlDriverWrite
    URLRead: str = _UrlDriverRead
    command_to_send: str = f'{{"name":"{str(name)}","mode":"{str(mode)}","command":"{str(command)}"}}'
    send_request(URLWrite, command_to_send)
    drvdata: str = check_status("driver", mode, URLRead)
    return parse_data(drvdata, mode, valuetype)
# endregion

# region --- DriverInit() / Инициализация драйвера ---
def DriverInit(name: str) -> None:
    """
    Инициализирует драйвер (упрощённая обёртка для Driver с mode='init').

    Args:
        name (str): Имя драйвера.
        command (str, optional): Команда для драйвера. Defaults to 'void'.

    Returns:
        None
    """
    Driver(name, mode='init', command='void')
# endregion

# region --- DriverSet() / Установка команды драйверу ---
def DriverSet(name: str, command: str = 'void') -> None:
    """
    Устанавливает команду драйверу (упрощённая обёртка для Driver с mode='set').

    Args:
        name (str): Имя драйвера.
        command (str, optional): Команда для драйвера. Defaults to 'void'.

    Returns:
        None
    """
    Driver(name, mode='set', command=command)
# endregion

# region --- DriverGet() / Получение данных от драйвера ---
def DriverGet(name: str,
              command: str = 'void',
              valuetype: Literal['string', 'int', 'float', 'bool',
                                 'arrayint', 'arrayfloat', 'arrayboolean', 'arraystring'] = 'string') -> Any:
    """
    Получает данные от драйвера (упрощённая обёртка для Driver с mode='get').

    Args:
        name (str): Имя драйвера.
        command (str, optional): Команда для драйвера. Defaults to 'void'.
        valuetype (str, optional): Ожидаемый тип данных. Defaults to 'string'.

    Returns:
        Данные от драйвера, преобразованные к типу valuetype.
    """
    return Driver(name, mode='get', command=command, valuetype=valuetype)
# endregion

#  ---------------------- Plugin  ----------------------------------

# region --- Plugin() / Плагин ---
def Plugin(name: str,
           mode: Literal['set', 'get','init','check','close'],
           command: str = 'void',
           valuetype: Literal['string', 'int', 'float', 'bool', 'arrayint', 'arrayfloat', 'arrayboolean', 'arraystring'] = 'string') -> Any:
    """
    Управляет плагинами в MOKO SE.

    Args:
        name (str): Имя плагина.
        mode (str): Режим работы с плагином ('get', 'set', 'init').
        command (str, optional): Команда для плагина. Defaults to 'void'.
        valuetype (str, optional): Ожидаемый тип данных при чтении (только для mode='get'). Defaults to 'void'.

    Returns:
        Зависит от режима:
        - 'set', 'init': None
        - 'get': Данные, полученные от плагина, преобразованные к типу `valuetype`.
    """
    check_project_state()
    URLWrite: str = _UrlPluginWrite
    URLRead: str = _UrlPluginRead
    command_to_send: str = f'{{"name":"{str(name)}","mode":"{str(mode)}","command":"{str(command)}"}}'
    send_request(URLWrite, command_to_send)
    plgdata: str = check_status("plugin", mode, URLRead)
    return parse_data(plgdata, mode, valuetype)
# endregion

# region --- PluginInit() / Инициализация плагина ---
def PluginInit(name: str, command: str = 'void') -> None:
    """
    Инициализирует плагин (упрощённая обёртка для Plugin с mode='init').

    Args:
        name (str): Имя плагина.
        command (str, optional): Команда для плагина. Defaults to 'void'.

    Returns:
        None
    """
    Plugin(name, mode='init', command=command)
# endregion

# region --- PluginSet() / Установка команды плагину ---
def PluginSet(name: str, command: str = 'void') -> None:
    """
    Устанавливает команду плагину (упрощённая обёртка для Plugin с mode='set').

    Args:
        name (str): Имя плагина.
        command (str, optional): Команда для плагина. Defaults to 'void'.

    Returns:
        None
    """
    Plugin(name, mode='set', command=command)
# endregion

# region --- PluginGet() / Получение данных от плагина ---
def PluginGet(name: str,
              command: str = 'void',
              valuetype: Literal['string', 'int', 'float', 'bool',
                                 'arrayint', 'arrayfloat', 'arrayboolean', 'arraystring'] = 'string') -> Any:
    """
    Получает данные от плагина (упрощённая обёртка для Plugin с mode='get').

    Args:
        name (str): Имя плагина.
        command (str, optional): Команда для плагина. Defaults to 'void'.
        valuetype (str, optional): Ожидаемый тип данных. Defaults to 'string'.

    Returns:
        Данные от плагина, преобразованные к типу valuetype.
    """
    return Plugin(name, mode='get', command=command, valuetype=valuetype)
# endregion

# region --- PluginClose() / Закрытие плагина ---
def PluginClose(name: str) -> None:
    """
    Закрывает плагин (упрощённая обёртка для Plugin с mode='close').

    Args:
        name (str): Имя плагина.
        command (str, optional): Команда для плагина. Defaults to 'void'.

    Returns:
        None
    """
    Plugin(name, mode='close')
# endregion

#  ---------------------- Plugin Graph  -----------------------------

# region --- GRAPH_NAME / Имя по умолчанию ---
GRAPH_NAME: str = "Graph"
# endregion

# region --- GraphInit() / Инициализация Графика ---
def GraphInit() -> None:
    """
    Инициализирует плагин MOKO Graph.
    Этот метод должен быть вызван перед использованием любых других функций из этой библиотеки.
    """
    PluginInit(GRAPH_NAME)
# endregion

# region --- GraphClose() / Закрытие Графика ---
def GraphClose() -> None:
    """
    Закрывает плагин MOKO Graph.
    """
    PluginClose(GRAPH_NAME)
# endregion

#  ---------------------- Plugin Graph Line  -------------------------
# region --- GraphLineAdd() / Управление Линиями / Команды Установки (Действия) ---
def GraphLineAdd(name: str,
            ArrOy: list,
            ArrOx: list,
            LineWidth: str = "3",
            Color: str = "000000",
            Visible: str = "True") -> None:
    """
    Добавляет новую линию на график.

    Args:
        name (str): Имя линии (будет отображаться в легенде).
        ArrOy (list): Список значений по оси Y.
        ArrOx (list): Список значений по оси X.
        LineWidth (str, optional): Толщина линии. Defaults to "3".
        Color (str, optional): Цвет линии в HEX-формате (например, "0000FF" для синего). Defaults to "000000".
        Visible (str, optional): Видимость линии ("True" или "False"). Defaults to "True".
    """
    PluginSet(GRAPH_NAME,f"Add Line={name};{ArrOy};{ArrOx};{LineWidth};{Color};{Visible}")
    PluginSet(GRAPH_NAME,"Write Graph")
# endregion

# region --- GraphLineChange() / Команды Установки (Действия) ---
def GraphLineChange(numLine: str,
               name: str,
               ArrOy: list,
               ArrOx: list,
               LineWidth: str = "3",
               Color: str = "000000",
               Visible: str = "True") -> None:
    """
    Изменяет существующую линию на графике.

    Args:
        numLine (str): Порядковый номер (начиная с 0) или имя линии для изменения.
        name (str): Новое имя линии.
        ArrOy (list): Новый список значений по оси Y.
        ArrOx (list): Новый список значений по оси X.
        LineWidth (str, optional): Новая толщина линии. Defaults to "3".
        Color (str, optional): Новый цвет линии в HEX-формате. Defaults to "000000".
        Visible (str, optional): Новая видимость линии. Defaults to "True".
    """
    PluginSet(GRAPH_NAME,f"Change Line={numLine};{name};{ArrOy};{ArrOx};{LineWidth};{Color};{Visible}")
# endregion

# region --- GraphLineDelete() / Команды Установки (Действия) ---
def GraphLineDelete(numLine: list | str | int) -> None:
    """
    Удаляет одну или несколько линий с графика.

    Args:
        numLine: Может быть:
                 - "All": для удаления всех линий.
                 - int: номер одной линии для удаления.
                 - list: список номеров или имен линий для удаления.
    """
    PluginSet(GRAPH_NAME,f"Delete Line={numLine}")
# endregion

# region --- GraphLineHide() / Команды Установки (Действия) ---
def GraphLineHide(numLine: list | str | int) -> None:
    """
    Скрывает одну или несколько линий на графике.

    Args:
        numLine: "All", номер линии (int) или список номеров/имен (list).
    """
    PluginSet(GRAPH_NAME, f"Hide Line={numLine}")
# endregion

# region --- GraphLineShow() / Команды Установки (Действия) ---
def GraphLineShow(numLine: list | str | int) -> None:
    """
    Показывает одну или несколько ранее скрытых линий.

    Args:
        numLine: "All", номер линии (int) или список номеров/имен (list).
    """
    PluginSet(GRAPH_NAME,f"Show Line={numLine}")
# endregion

# region --- GraphLineShowOnly() / Команды Установки (Действия) ---
def GraphLineShowOnly(numLine: list | str | int) -> None:
    """
    Показывает только выбранные линии, скрывая все остальные.

    Args:
        numLine: Номер линии (int) или список номеров/имен (list) для отображения.
    """
    PluginSet(GRAPH_NAME,f"Show Line=Only;{numLine}")
# endregion

#  ---------------------- Plugin Graph Settings  -------------------------

# region --- GraphSettingsAdd() / Настройки Графика и Осей / ранее AddGraphSett() ---
def GraphSettingsAdd(Value_OyOx: list, Name_Oy: str, Name_Ox: str, Autoscale: str = "Yes") -> None:
    """
    Устанавливает основные параметры графика и осей.

    Args:
        Value_OyOx (list): Список из 4 значений [Ymin, Ymax, Xmin, Xmax].
        Name_Oy (str): Название оси Y.
        Name_Ox (str): Название оси X.
        Autoscale (str, optional): Режим автомасштабирования ("Yes", "No", "OnlyOy", "OnlyOx"). Defaults to "Yes".
    """
    PluginSet(GRAPH_NAME,f"Add Graph Settings={Value_OyOx};{Name_Oy};{Name_Ox};{Autoscale}")
# endregion

# region --- GraphAutoscale() / Настройки Графика и Осей ---
def GraphAutoscale(mode: str = "Yes") -> None:
    """
    Управляет режимом автомасштабирования графика.

    Args:
        mode (str, optional): Режим ("Yes", "No", "OnlyOy", "OnlyOx"). Defaults to "Yes".
    """
    PluginSet(GRAPH_NAME,f"Autoscale={mode}")
# endregion

# region --- GraphLegend() / Настройки Графика и Осей ---
def GraphLegend() -> None:
    """
    Переключает видимость легенды графика (показать/скрыть).
    """
    PluginSet(GRAPH_NAME,"Legend")
# endregion

# region --- GraphReWrite() / Перерисовывает график / ранее GraphWrite() ---
def GraphReWrite() -> None:
    """
    Принудительно перерисовывает график, отображая все последние изменения.
    """
    PluginSet(GRAPH_NAME,"Write Graph")
# endregion

# region --- GraphClear() / Очищает область графика ---
def GraphClear() -> None:
    """
    Полностью очищает область графика, удаляя все линии и настройки.
    """
    PluginSet(GRAPH_NAME,"Clear Graph")
# endregion

#  ---------------------- Plugin Graph Screenshot  -------------------------

# region --- GraphScreenshotWindow() / Команды Скриншотов ---
def GraphScreenshotWindow() -> None:
    """
    Делает скриншот всего окна плагина "MOKO Graph".
    Файл сохраняется в стандартную директорию плагина.
    """
    PluginSet(GRAPH_NAME,"Screenshot Window")
# endregion

# region --- GraphScreenshot() / Команды Скриншотов ---
def GraphScreenshot() -> None:
    """
    Делает скриншот только области самого графика.
    Файл сохраняется в стандартную директорию плагина.
    """
    PluginSet(GRAPH_NAME,"Screenshot Graph")
# endregion

# region --- GraphGetScreenshotWindow() / Получить Скриншот Окна / Команды Получения Данных ---
def GraphGetScreenshotWindow() -> str:
    """
    Делает скриншот всего окна плагина и возвращает его в формате Base64.

    Returns:
        str: Строка с изображением в кодировке Base64.
    """
    return PluginGet(GRAPH_NAME,"ScreenshotWindow", 'string')
# endregion

# region --- GraphGetScreenshot() / Получить Скриншот Графика / Команды Получения Данных---
def GraphGetScreenshot() -> str:
    """
    Делает скриншот области графика и возвращает его в формате Base64.

    Returns:
        str: Строка с изображением в кодировке Base64.
    """
    screen = PluginGet(GRAPH_NAME,"ScreenshotGraph", 'string')
    return screen
# endregion

#  ---------------------- Message  ---------------------------------

# region --- Message() / Сообщения ---
def Message(mode: Literal['set', 'get'],
              head: str = '',
              body: str = '',
              valuetype: str = 'void',
              delaytime: str = 'void') -> Any:
    """
    Отображает всплывающее окно (мессенджер) в MOKO SE для взаимодействия с пользователем.

    Args:
        mode (str): Режим окна ('get' для ввода данных, 'set' для отображения информации).
        head (str, optional): Заголовок окна. Defaults to ''.
        body (str, optional): Основной текст сообщения. Defaults to ''.
        valuetype (str, optional): Ожидаемый тип данных при вводе (только для mode='get'). Defaults to 'void'.
        delaytime (str, optional): Время (в секундах), на которое окно задержится на экране. Defaults to 'void'.

    Returns:
        Зависит от режима:
        - 'set': None
        - 'get': Данные, введенные пользователем.
    """
    check_project_state()
    URLWrite: str = _UrlMessageWrite
    URLRead: str = _UrlMessageRead
    if (delaytime == 'void'):
        command_to_send: str = f'{{"mode":"{str(mode)}","head":"{str(head)}","body":"{str(body)}","value":"{str(valuetype)}"}}'
    else:
        command_to_send: str = f'{{"mode":"{str(mode)}","head":"{str(head)}","body":"{str(body)}","time":"{str(delaytime)}"}}'
    send_request(URLWrite, command_to_send)
    msgdata: str = check_status("message", mode, URLRead)
    return parse_data(msgdata, mode, valuetype)


# --- Обратная совместимость со старыми скриптами ---
Messenger = Message
# endregion

# region --- MessageSet() / Установка сообщения ---
def MessageSet(head: str,
               body: str,
               delaytime: Optional[Union[int, float, str]] = None) -> None:
    """
    Показать информационное сообщение.

    Args:
        Заголовок окна. Может содержать специальные директивы и пути к картинкам:
              - "#@warning"  – иконка предупреждения
              - "#@error"    – иконка ошибки
              - "#@info"     – иконка информации
              - "#C:\MOKO SE\Data\Extra images\MOKO SE.png" – абсолютный путь
              - "#FLUKE5520A_AGILENT34401A.png" – имя файла из папки Data/Extra images
              - "#folder\image.png" – относительный путь внутри Data/Extra images
              Примеры:
                  "Заголовок#@warning"
                  "Результат#C:\MOKO SE\Data\Extra images\MOKO SE.png"
                  "Статус#FLUKE5520A_AGILENT34401A.png"
                  "График#folder\FLUKE5520A_AGILENT34401A.png"
        body: Текст сообщения.
        delaytime: Время авто-закрытия в секундах (число или строка, например 5, "9", "0").
                   None или "void" — поле "time" не отправляется (окно висит до закрытия).
                   Любое другое значение (включая "0") отправляется как строка в поле "time".
    """
    # Если delaytime не указан или явно 'void' — не добавляем time в JSON
    if delaytime is None or delaytime == 'void':
        delaytime = None
    else:
        # Преобразуем любое значение в строку для JSON (числа тоже станут строками)
        delaytime = str(delaytime)

    # Вызов базовой Message (которая ожидает delaytime=None или строку)
    # Убедитесь, что ваша базовая Message добавляет поле "time" только если delaytime не None
    Message('set', head=head, body=body, delaytime=delaytime)
# endregion

# region --- MessageSetWithImage() / Сообщение с картинкой ---
def MessageSetWithImage(head: str,
                        body: str,
                        image_path: str,
                        delaytime: Optional[Union[int, float, str]] = None) -> None:
    """
    Показать сообщение с пользовательской картинкой.

    Args:
        head: Заголовок окна (без символа #, он добавится автоматически вместе с image_path).
              Можно комбинировать с директивами (#@warning, #@error, #@info), но тогда директива
              должна быть указана в самом head, а image_path будет добавлен через ещё один #.
              Рекомендуется либо использовать картинку, либо директиву, не смешивая.
        body: Текст сообщения.
                image_path: Путь к изображению. Может быть:
                    - абсолютным: "C:\MOKO SE\Data\Extra images\MOKO SE.png"
                    - относительным (относительно Data/Extra images): "folder\FLUKE5520A_AGILENT34401A.png"
                    - просто именем файла: "FLUKE5520A_AGILENT34401A.png"
                    Поддерживаются PNG, JPG, BMP и др.
        delaytime: Время авто-закрытия (число или строка, например 5, "9", "0").
    """
    full_head = f"{head}#{image_path}"
    MessageSet(full_head, body, delaytime=delaytime)
# endregion

# MessageGetBool
# MessageGetChoice
# MessageGetPath

# region --- MessageGet() / Получение ввода от пользователя ---
def MessageGet(head: str,
               body: str = '',
               valuetype: str = 'void') -> Any:
    """
    Отображает диалоговое окно для ввода данных пользователем.

    Args:
        head (str): Заголовок окна. Можно использовать директивы:
                    '#@warning', '#@error', '#@info' или путь к картинке после '#'.
        body (str, optional): Текст сообщения или подсказка. Defaults to ''.
        valuetype (str, optional): Ожидаемый тип возвращаемого значения.
                                   Поддерживаются: 'void', 'string', 'boolean', 'choice', 'path'.
                                   Defaults to 'string'.

    Returns:
        Any: Введённое пользователем значение, преобразованное к типу `valuetype` = 'string' .
    """
    return Message(mode='get', head=head, body=body, valuetype=valuetype)
# endregion

# region --- MessageGetString() / Упрощённые варианты MessageGetString ---
def MessageGetString(head: str, body: str = '') -> str:
    """Возвращает строку, введённую пользователем."""
    return MessageGet(head, body, valuetype='string')
# endregion

# region --- MessageGetBool() / Упрощённые варианты MessageGetBool ---
def MessageGetBool(head: str,
                   body: str = '',
                   boolean: bool = False,
                   timeout: Optional[Union[int, float]] = None) -> bool:
    """
    Отображает диалог Да/Нет и возвращает bool.

    Args:
        head: Заголовок окна.
        body: Текст сообщения.
        default: Значение по умолчанию (True = Да, False = Нет).
        timeout: Время авто-закрытия в секундах (None = бесконечно).
    """
    # Формируем строку valuetype, как в примерах пользователя:
    # "boolean = false", "boolean = true time = 6" и т.д.
    valuetype = f"boolean = {str(boolean).lower()}"
    if timeout is not None:
        valuetype += f" time = {timeout}"

    # Вызываем стандартную Message (delaytime='void', т.к. таймаут уже внутри valuetype)
    result = Message(mode='get', head=head, body=body,valuetype=valuetype, delaytime='void')

    return result
# endregion

# region --- MessageGetPath() / Упрощённые варианты MessageGetPath ---
def MessageGetPath(head: str, body: str = '', initial_path: str = '') -> str:
    """
    Отображает диалог выбора папки или файла (через MOKO SE).

    Args:
        head (str): Заголовок окна.
        body (str): Текст сообщения (подсказка). По умолчанию ''.
        initial_path (str): Начальный путь (например "C:" или "D:\\Folder").
                            Если не указан, используется просто "path".

    Returns:
        str: Выбранный пользователем путь.
    """
    if initial_path:
        valuetype = f"path = {initial_path}"
    else:
        valuetype = "path"

    # Вызываем базовую функцию Message без delaytime (по умолчанию 'void')
    return Message(mode='get', head=head, body=body, valuetype=valuetype)
# endregion

#  ---------------------- Report  ----------------------------------

# region --- Report() / Отчет ---
def Report(name: str,
           mode: Literal['info', 'set','get','clear','delete','save'],
           kind: Literal['string', 'table', 'picture', 'strings'] = 'string',
           data: str = '',
           valuetype: Literal['string', 'int', 'float', 'bool', 'arrayint', 'arrayfloat', 'arrayboolean', 'arraystring'] = 'string') -> Any:
    """
    Работает с данными в отчете MOKO SE.

    Args:
        name (str): Имя отчета или закладки в документе Word.
        mode (str): Режим работы ('get', 'set', ???).
        kind (str, optional): Тип записываемых данных ('string', 'table', 'picture'). Defaults to 'string'.
        data (str, optional): Данные для записи в отчет. Defaults to ''.
        valuetype (str, optional): Ожидаемый тип данных при чтении (только для mode='get'). Defaults to 'void'.

    Returns:
        Зависит от режима:
        - 'set': None
        - 'get': Данные, полученные из отчета.
    """
    check_project_state()
    URLWrite: str = _UrlReportWrite
    URLRead: str = _UrlReportRead
    command_to_send: str = f'{{"name":"{str(name)}","mode":"{str(mode)}", "kind":"{str(kind)}", "data":"{str(data)}"}}'
    send_request(URLWrite, command_to_send)
    repdata: str = check_status("report", mode, URLRead)
    return parse_data(repdata, mode, valuetype)
# endregion

# region --- ReportSetString() / Упрощённая запись в отчёт строки ---
def ReportSetString(name: str, data: str) -> None:
    """
    Записывает строковые данные в указанный отчёт (или закладку Word).

    Args:
        name (str): Имя отчёта или закладки в документе Word.
        data (str): Строка, которая будет записана.
    """
    Report(name, mode='set', kind='string', data=data)
# endregion

# region --- ReportSetTable() / Упрощённая запись в отчёт таблицу ---
def ReportSetTable(name: str, data: str) -> None:
    """
    Записывает табличные данные в указанный отчёт.

    Формат данных `data` должен соответствовать требованиям MOKO SE:
    - Строки разделены точкой с запятой ';'
    - Колонки внутри строки – тоже ';'
    - Для задания ширины колонки используется '#<ширина>' после заголовка.
    Пример: "Имя#100;Значение#50;Результат#80"

    Args:
        name (str): Имя отчёта или закладки.
        data (str): Данные таблицы в виде строки.
    """
    Report(name, mode='set', kind='table', data=data)
# endregion

# region --- ReportSetPicture() / Упрощённая запись в отчёт картинку ---
def ReportSetPicture(name: str, data: str) -> None:
    """
    Вставляет изображение в отчёт.

    Args:
        name (str): Имя отчёта или закладки.
        data (str): Путь к файлу изображения (абсолютный или относительный)
                    или другие данные, поддерживаемые MOKO SE для вставки картинок.
    """
    Report(name, mode='set', kind='picture', data=data)


# Синоним для удобства (оба имени ведут к одной функции)
ReportSetImage = ReportSetPicture
# endregion

# region --- ReportInfoStrings / (матричная запись отчёта) ---
def ReportInfoStrings(*pairs):
    """
    Инициализация отчёта: задаёт заголовки полей.
    Кратко: ReportInfoStrings(("Поле1","Заголовок1"), ("Поле2","Заголовок2"))
    Пример:
        ReportInfoStrings(
            ("ProtocolNumber", "Протокол поверки."),
            ("AppNumber", "Заводской №.")
        )
    """
    names = ";".join(p[0] for p in pairs)
    headers = ";".join(p[1] for p in pairs)
    Report(names, 'info', 'strings', headers)
# endregion

# region --- ReportSetStrings / (матричная запись отчёта) ---
def ReportSetStrings(*pairs):
    """
    Запись значений в отчёт (порядок полей должен совпадать с ReportSetStrings).
    Кратко: ReportSetStrings(("Поле1", значение1), ("Поле2", значение2))
    Пример:
        ReportSetStrings(
            ("ProtocolNumber", protocol_number),
            ("AppNumber", app_number)
        )
    """
    names = ";".join(p[0] for p in pairs)
    data = ";".join(str(p[1]) for p in pairs)
    Report(names, 'set', 'strings', data)
# endregion

# region --- ReportSetInfoStrings / (матричная запись отчёта) ---
def ReportSetInfoStrings(*triples):
    """
    Регистрирует поля отчёта и заполняет их значениями за один вызов.

    Аргументы:
        *triples: произвольное количество троек вида (key, value, description)
    """
    # Разделяем тройки на два списка: для Info (ключ, описание) и для Set (ключ, значение)
    info_pairs = []
    set_pairs = []
    for key, value, desc in triples:
        info_pairs.append((key, desc))
        set_pairs.append((key, value))

    # Регистрация описаний
    try:
        ReportInfoStrings(*info_pairs)
    except Exception as e:
        StageError(f"Ошибка при регистрации полей отчёта: {e}")

    # Заполнение значениями
    try:
        ReportSetStrings(*set_pairs)
    except Exception as e:
        StageError(f"Ошибка при записи значений в отчёт: {e}")
# endregion


# region --- ReportGet() / Получение данных из отчёта ---
def ReportGet(name: str,
              valuetype: Literal['string', 'int', 'float', 'bool',
                                 'arrayint', 'arrayfloat', 'arrayboolean', 'arraystring'] = 'string') -> Any:
    """
    Получает данные из отчёта MOKO SE.

    Args:
        name (str): Имя отчёта или закладки в документе Word.
        valuetype (str, optional): Ожидаемый тип возвращаемого значения. По умолчанию 'string'.

    Returns:
        Any: Данные из отчёта, преобразованные к типу `valuetype`.
    """
    return Report(name, mode='get', kind='string', data='', valuetype=valuetype)
# endregion

# region --- ReportTableCreate() / Упрощенный вызов Report для создания таблиц. ---
def ReportTableCreate(title: str, columns: str, base_width: int = 15) -> None:
    """
    Упрощенный вызов Report для создания таблиц.
    Автоматически рассчитывает ширину колонок (#XX) на основе длины самой длинной строки.
    Формула: base_width + (символы - 1) * 6.

    Поддерживает многострочные заголовки через \\n (ширина считается по самой длинной строке).
    Пробелы справа сохраняются для ручного увеличения ширины.
    Пробелы слева перед \\n автоматически удаляются при сборке финальной строки.

    Args:
        title (str): Заголовок таблицы.
        columns (str): Названия колонок через точку с запятой.
                       Пример: "ID\\n точки;Канал \\n какойто;Мощность      "
        base_width (int): Базовая ширина для колонки из 1 символа. По умолчанию 15.
    """
    column_list = columns.split(';')
    formatted_columns = []

    for col in column_list:
        # Убираем пробелы только СЛЕВА у всей колонки (если они были после ;)
        col = col.lstrip()

        max_len = 0
        cleaned_lines = []  # Сюда будем собирать строки без левых пробелов

        # Разбиваем колонку на отдельные строки по символу переноса
        lines = col.split('\n')

        for line in lines:
            # Убираем пробелы слева у каждой строки, но сохраняем справа
            clean_line = line.lstrip()
            cleaned_lines.append(clean_line)  # Сохраняем очищенную версию для финальной строки

            # Считаем длину этой конкретной строки
            line_len = len(clean_line)

            # Запоминаем максимальную длину среди всех строк колонки
            if line_len > max_len:
                max_len = line_len

        # Применяем формулу с переменной base_width
        width = base_width + (max_len - 1) * 6

        # Склеиваем очищенные строки обратно через \n (пробелы перед \n исчезнут)
        final_col = "\n".join(cleaned_lines)

        # Добавляем рассчитанную ширину
        formatted_columns.append(f"{final_col}#{width}")

    # Собираем всё обратно в одну строку через точку с запятой
    final_string = ";".join(formatted_columns)

    # Вызываем оригинальную функцию Report
    Report(title, 'info', 'table', final_string)

    return
# endregion ****************************************************

# region --- ReportSave() / Сохраняет переменную в ее формате. ---
def ReportSave(name: str) -> None:
    """
    Сохраняет переменную в ее формате.

    Args:
        name: имя переменной.
    """
    Report(name, 'save')
    return
# endregion ---------------------------------------------------------

# region --- ReportClear() / Очищает переменную в ее формате. ---
def ReportClear(name: str) -> None:
    """
    Очищает переменную в ее формате.

    Args:
        name: имя переменной.
    """
    Report(name, 'clear')
    return
# endregion ---------------------------------------------------------

# region --- ReportDelete() / Удалить переменную в ее формате. ---
def ReportDelete(name: str) -> None:
    """
    Удалить переменную в ее формате.

    Args:
        name: имя переменной.
    """
    Report(name, 'delete')
    return
# endregion ---------------------------------------------------------

# region --- ReportTimeAdd / Управляет таблицей со временем выполнения скрипта. ---
def ReportTimeAdd(action: Literal["init", "add", "set"] = "init", lang: Literal["RU", "EN"] = "EN") -> None:
    """
    Управляет таблицей со временем выполнения скрипта.

    Args:
        action (Literal["init", "add", "set"]):
            - 'init': Создает таблицу с заголовками.
            - 'add' или 'set': Добавляет строку с данными о выполнении.
        lang (Literal["RU", "EN"]): Язык заголовков и ID таблицы. По умолчанию 'EN'.
    """
    # Задаем заголовок и ID таблицы в зависимости от языка
    if lang == "RU":
        table_title = "Время выполнения скрипта"
        headers = (
            "Название скрипта#350;"
            "Время запуска#120;"
            "Время окончания#120;"
            "Время исполнения#150"
        )
    else:  # EN (по умолчанию)
        table_title = "Script Execution Time"
        headers = (
            "Script Name#350;"
            "Start Time#120;"
            "End Time#120;"
            "Execution Time#150"
        )

    if action == "init":
        # Используем table_title как визуальный заголовок
        Report(table_title, "info", "table", headers)

    elif action in ("add", "set"):
        # Получаем имя файла и универсально отрезаем любое расширение
        script_name, _ = os.path.splitext(os.path.basename(sys.argv[0]))

        row_data = (
            f"{script_name};"
            f"{TimeGet('ScriptStart')};"
            f"{TimeGet('CurrentDateAndTime')};"
            f"{TimeGet('ScriptExecution')}"
        )
        # Используем тот же table_title как ID для обновления таблицы
        Report(table_title, "set", "table", row_data)
# endregion

#  ---------------------- Utility  ---------------------------------

# region --- Utility() / Утилита ---
def Utility(name: str,
            mode: Literal['set', 'get'],
            command: str = 'void',
            valuetype: Literal['string', 'int', 'float', 'bool', 'arrayint', 'arrayfloat', 'arrayboolean', 'arraystring'] = 'string') -> Any:
    """
    Управляет утилитами в MOKO SE.

    Args:
        name (str): Имя утилиты.
        mode (str): Режим работы ('get', 'set', ???).
        command (str, optional): Команда для утилиты. Defaults to 'void'.
        valuetype (str, optional): Ожидаемый тип данных при чтении (только для mode='get'). Defaults to 'void'.

    Returns:
        Зависит от режима:
        - 'set': None
        - 'get': Данные, полученные от утилиты.
    """
    check_project_state()
    URLWrite: str = _UrlUtilityWrite
    URLRead: str = _UrlUtilityRead
    command_to_send: str = f'{{"name" :"{str(name)}", "mode":"{str(mode)}", "command":"{str(command)}"}}'
    send_request(URLWrite, command_to_send)
    utldata: str = check_status("utility", mode, URLRead)
    return parse_data(utldata, mode, valuetype)
# endregion

# region --- UtilitySet() / Установка команды утилите ---
def UtilitySet(name: str, command: str = 'void') -> None:
    """
    Устанавливает команду утилите (упрощённая обёртка для Utility с mode='set').

    Args:
        name (str): Имя утилиты.
        command (str, optional): Команда для утилиты. Defaults to 'void'.

    Returns:
        None
    """
    Utility(name, mode='set', command=command)
# endregion

# region --- UtilityGet() / Получение данных от утилиты ---
def UtilityGet(name: str,
               command: str = 'void',
               valuetype: Literal['string', 'int', 'float', 'bool',
                                  'arrayint', 'arrayfloat', 'arrayboolean', 'arraystring'] = 'string') -> Any:
    """
    Получает данные от утилиты (упрощённая обёртка для Utility с mode='get').

    Args:
        name (str): Имя утилиты.
        command (str, optional): Команда для утилиты. Defaults to 'void'.
        valuetype (str, optional): Ожидаемый тип данных. Defaults to 'string'.

    Returns:
        Данные от утилиты, преобразованные к типу valuetype.
    """
    return Utility(name, mode='get', command=command, valuetype=valuetype)
# endregion

# region --- UtilityGetParseKeyValue() / Получение данных от утилиты List ---
def UtilityGetParseKeyValue(utility_name: str, command: str = "info") -> dict:
    """
    Получает данные от утилиты MOKO и преобразует в словарь.
    Поддерживает как список строк, так и строку с разделителями ';'.
    Комментарии (после '#') удаляются из значений.
    """
    raw_data = None
    try:
        raw_data = Utility(utility_name, "get", command, "arraystring")

        # Приводим raw_data к списку строк
        if isinstance(raw_data, list):
            items = raw_data
        elif isinstance(raw_data, str):
            items = raw_data.split(';')
        else:
            raise ValueError(f"Utility вернула неожиданный тип: {type(raw_data)}")

        data = {}
        for item in items:
            if not item:
                continue
            if ':' in item:
                key, value = item.split(':', 1)
                # Очищаем ключ
                key = key.strip()
                # Очищаем значение: убираем пробелы и отрезаем комментарий (всё после '#')
                value = value.strip()
                if '#' in value:
                    value = value.split('#', 1)[0].strip()
                data[key] = value
            else:
                StageError(f"Некорректный элемент: '{item}' (нет ':')")
        return data
    except Exception as e:
        StageError(f"Ошибка парсинга: {e}")
        return {}
# endregion

#  ---------------------- Messengers (Telegram, Max) ---------------

# region --- Telegram() / Мессенджер Телеграм ---
def Telegram(role: Literal['alpha', 'beta', 'gamma', 'delta', 'xi', 'id'] = 'alpha',
             mode: Literal['set','get'] = 'set',
             command: str = '',
             valuetype: Literal['void'] = 'void') -> Any:
    """
    Работает с Telegram ботом MOKO SE.

    Args:
        role (str): Принадлежность к группе для отправки сообщений ('alpha', 'beta', 'gamma', 'delta' - разработчик).
        mode (str): Режим работы ('get', 'set').
        command (str): Команда для выполнения.
        valuetype (str, optional): Ожидаемый тип данных при чтении (только для mode='get'). Defaults to 'void'.

    Returns:
        Зависит от режима:
        - 'set': None
        - 'get': Данные, полученные от Telegram.
    """
    check_project_state()
    URLWrite: str = _UrlTelegramWrite
    URLRead: str = _UrlTelegramRead
    command_to_send: str = f'{{"role":"{str(role)}","mode":"{str(mode)}","command":"{str(command)}"}}'
    send_request(URLWrite, command_to_send)
    tgmdata: str = check_status("telegram", mode, URLRead)
    return parse_data(tgmdata, mode, valuetype)
# endregion

# region --- Max() / Мессенджер MAX ---
def Max(role: Literal['alpha', 'beta', 'gamma', 'delta', 'xi', 'id'] = 'alpha',
             mode: Literal['set','get'] = 'set',
             command: str = '',
             valuetype: Literal['void'] = 'void') -> Any:
    """
    Работает с MAX ботом MOKO SE.

    Args:
        role (str): Принадлежность к группе для отправки сообщений ('alpha', 'beta', 'gamma', 'delta' - разработчик).
        mode (str): Режим работы ('get', 'set').
        command (str): Команда для выполнения.
        valuetype (str, optional): Ожидаемый тип данных при чтении (только для mode='get'). Defaults to 'void'.

    Returns:
        Зависит от режима:
        - 'set': None
        - 'get': Данные, полученные от Max.
    """
    check_project_state()
    URLWrite: str = _UrlMaxWrite
    URLRead: str = _UrlMaxRead
    command_to_send: str = f'{{"role":"{str(role)}","mode":"{str(mode)}","command":"{str(command)}"}}'
    send_request(URLWrite, command_to_send)
    maxdata: str = check_status("max", mode, URLRead)
    return parse_data(maxdata, mode, valuetype)
# endregion

#  ---------------------- Program / Программа ---------------------

# region -------   Collection Literal Program / Коллекция литералов для Program
# ==========================================
# 1. ОПИСЫВАЕМ КОМАНДЫ (Type Aliases)
# Это сделает код ниже чистым и читаемым
# ==========================================

# Для tree (есть и set, и get)
TreeGetStaticCmd = Literal['hash =',
                     'script', 'ScriptStatus',
                     'project', 'ProjectStatus']
TreeGetCmd = TreeGetStaticCmd  | str
TreeSetStaticCmd = Literal['select = ', 'info = ', 'chosen = done', 'chosen = failed', 'chosen = passed',
                                                   'chosen = canceled','chosen = frozen',
                                                    'chosen = empty','chosen = reset']
TreeSetCmd = TreeSetStaticCmd | str

# Для control (есть и set, и get)
ControlSetStaticCmd = Literal[# ------- main -------
                        'Minimized', 'OpenProject', 'SaveProject',
                        # ------- Panel Control -------
                        'Start', 'Pause', 'Stop', 'Reset','EditExecution', 'ProjectHistory', 'PersonalProjects',
                        # ------- Project -------
                        'SaveProjectReport', 'SaveTempProjectReport', 'SaveProjectReportAs','LoadProjectReport',
                        # ------- Word / Pdf-------
                        'SaveWordReport', 'SaveWordReportAs', 'SavePdfReport','SavePdfReportAs',
                        # ------- Stage -------
                        'StageClear','SaveStageReport',
                        # ------- Help Links -------
                        'License', 'Documentation','YouTube','Telegram','GitHub','AboutCompany',
                        # ------- Edit Report -------
                        'EditData','AddAllReports','AddNameReports','SaveAllReportsToAFolder',
                        # ------- Report Settings --------
                        'UseCustomReportName = true', 'UseCustomReportName = false','UseCustomPathName = true','UseCustomPathName = false',
                        'UserReportName =','UserPathName = ',
                        # ------- Language -------
                        'Language']
ControlGetCmd = Literal['Version', 'screenshot']

ControlSetCmd = ControlSetStaticCmd | str

# Для script (допустим, ТОЛЬКО set)
ScriptSetStaticCmd = Literal['Script = done', 'Script = failed', 'Script = passed','Script = start','Script = canceled']
ScriptSetCmd = ScriptSetStaticCmd | str

# Для project (есть set)
ProjectSetCmd = Literal['start', 'done', 'pause', 'stop', 'reset']

# Для Time (есть  get)
TimeGetCmd = Literal[# ________ Current _________
                        'Current', 'CurrentDateAndTime', 'CurrentDate', 'CurrentTime',
                        # ________ Project _________
                        'ProjectStart', 'ProjectStartDateAndTime', 'ProjectStartDate', 'ProjectStartTime',
                        'ProjectExecution', 'TotalExecution',
                        'ProjectIdle', 'ProjectStop', 'TotalIdle', 'TotalStop',
                        'ProjectError', 'TotalError',
                        # ________  Script _________
                        "ScriptStart", "ScriptStartDateAndTime",
                        "ScriptStartDate", "ScriptStartTime",
                        "ScriptExecution", "ScriptIdle", "ScriptStop",
                        "ScriptError"]
# endregion

# region  -------   Overload Program / Перезагрузка контекста функций Program ---

# ==========================================
# 2. ПЕРЕГРУЗКИ ФУНКЦИИ (@overload)
# Строго связываем: Имя -> Режим -> Команды
# ==========================================
# --- TREE SET---
@overload
def Program(
    name: Literal['tree'],
    mode: Literal['set'],
    command: TreeSetCmd # Используем SET команду
) -> str: ...

# --- TREE GET---
@overload
def Program(
    name: Literal['tree'],
    mode: Literal['get'],
    command: TreeGetCmd, # Используем GET команду
    valuetype: Literal['string'] = 'string'
) -> str: ...

# --- CONTROL SET---
@overload
def Program(
    name: Literal['control'],
    mode: Literal['set'],
    command: ControlSetCmd
) -> str: ...

# --- CONTROL GET---
@overload
def Program(
    name: Literal['control'],
    mode: Literal['get'], # Исправлен комментарий и режим
    command: ControlGetCmd,
    valuetype: Literal['string'] = 'string'
) -> str: ...

# --- SCRIPT SET---
@overload
def Program(
    name: Literal['script'],
    mode: Literal['set'], # Если name='script', mode может быть ТОЛЬКО 'set'
    command: ScriptSetCmd
) -> str: ...

# --- PROJECT SET---
@overload
def Program(
    name: Literal['project'],
    mode: Literal['set'],
    command: ProjectSetCmd
) -> str: ...

# --- TIME GET---
@overload
def Program(
    name: Literal['time'],
    mode: Literal['get'], # Только 'get'
    command: TimeGetCmd,
    valuetype: Literal['string'] = 'string'
) -> str: ...
# endregion

# region ------     Program() / Программа ---

# ==========================================
# 3. ОСНОВНАЯ РЕАЛИЗАЦИЯ (Ваша логика)
# ==========================================
def Program(
            name: str = 'control',
            mode: str = 'set',
            command: str = '',
            valuetype: str = 'void'
) -> str:
    """
    Центральная функция управления внутренней логикой и интерфейсом MOKO SE.
    Работает как маршрутизатор: конкретное действие определяется комбинацией параметров `name`, `mode` и `command`.

    Поддерживаемые подсистемы (параметр `name`):
      - 'tree': Управление деревом проекта (выделение хэшей, установка статусов, получение ScriptStatus).
      - 'control': Программное управление GUI MOKO SE (нажатие кнопок Start/Stop, вызов меню сохранения отчетов).
      - 'script': Установка финального статуса выполнения текущего скрипта (например, 'Script = passed').
      - 'project': Глобальное управление состоянием проекта ('start', 'stop', 'pause').
      - 'time': Запрос системных таймеров и метрик времени ('Current', 'ProjectExecution', 'ScriptError' и др.).

    Args:
        name (str): Имя подсистемы, к которой обращается команда.
        mode (str): Режим работы. 'set' (отправить команду/изменить состояние)
                    или 'get' (запросить данные). Допустимые режимы зависят от выбранной подсистемы.
        command (str): Текст команды. Формат строго зависит от `name` и `mode`.
                       Примеры: 'select = <hash>', 'ScriptStatus', 'Start', 'CurrentDate'.
        valuetype (str, optional): Ожидаемый тип данных при mode='get'.
                                   Поддерживаются: 'string', 'int', 'float', 'bool', 'array...'.
                                   При mode='set' игнорируется. Defaults to 'void'.

    Returns:
        str | int | float | bool | list | None:
            - При mode='get' возвращает данные от сервера, приведенные к типу `valuetype`.
            - При mode='set' всегда возвращает None.

    Notes:
        Функция имеет встроенную защиту от рассинхрона: если проект в MOKO SE поставлен
        на паузу, выполнение Python-скрипта в этой функции заморозится до снятия паузы.
        Если проект остановлен, скрипт принудительно завершится (sys.exit).
    """
    check_project_state()
    URLWrite: str = _UrlProgramWrite
    URLRead: str = _UrlProgramRead
    command_to_send: str = f'{{"name":"{str(name)}","mode":"{str(mode)}","command":"{str(command)}"}}'
    send_request(URLWrite, command_to_send)
    progdata: str = check_status("program", mode, URLRead)
    return parse_data(progdata, mode, valuetype)
# endregion

#  ---------------------- Script / Скрипт  -------------------------

# region --- ScriptResult / Получает результат выполнения текущего скрипта из дерева MOKO SE. --
def ScriptResult() -> str:
    """
    Получает результат выполнения текущего скрипта из дерева MOKO SE.

    Returns:
        str: Статус выполнения ('passed', 'failed', 'done').
    """
    return Program('tree', 'get', 'ScriptStatus', 'string')
# endregion

# region --- ScriptEnd() / Завершает выполнение текущего скрипта. *******
def ScriptEnd(command: str = None) -> None:
    """
    Завершает выполнение текущего скрипта.

    Обязательная функция, которая должна вызываться в конце каждого скрипта,
    чтобы уведомить MOKO SE о его завершении.

    Args:
        command (str, optional): Команда, отправляемая серверу при завершении.
                                 Возможные значения:
                                 - 'done': Выполнено (желтый нейтральный цвет).
                                 - 'passed': Пройдено (зеленый цвет).
                                 - 'failed': Не пройдено (красный цвет).

                                 Также поддерживаются синонимы:
                                 - 'good' -> преобразуется в 'passed'
                                 - 'bad' -> преобразуется в 'failed'

                                 Если параметр не передан, автоматически получает
                                 статус из ScriptResult().
                                 Если передано неподдерживаемое значение,
                                 устанавливается статус 'failed'.
                                 Defaults to None.
    """
    if command is None:
        command = ScriptResult()

    # Нормализация значений
    command_lower = str(command).lower()

    # Преобразование синонимов
    if command_lower in {'good', 'passed'}:
        command = 'passed'
    elif command_lower in {'bad', 'failed'}:
        command = 'failed'
    elif command_lower == 'done':
        command = 'done'
    else:
        # Если ничего не подошло, пишем failed
        command = 'failed'

    Program('script', 'set', command)
    sys.exit()

# --- Обратная совместимость со старыми скриптами ---
EndScript = ScriptEnd
# endregion *****************************************

#  ---------------------- Project / Проект  ------------------------

# region --- ProjectResult / Получает результат выполнения всего проекта из дерева MOKO SE. --
def ProjectResult() -> str:
    """
    Получает результат выполнения всего проекта из дерева MOKO SE.

    Returns:
        str: Статус выполнения проекта ('passed', 'failed', 'done').
    """
    return Program('tree', 'get', 'ProjectStatus', 'string')
# endregion

# region --- ProjectRestart() / Перезапускает текущий проект с нуля. *******
def ProjectRestart() -> None:
    """
    Перезапускает текущий проект с нуля.

    Выполняет полный цикл перезапуска проекта в MOKO SE, состоящий из трёх этапов:
    1. Очищает текущую стадию выполнения (StageClear).
    2. Сбрасывает все накопленные результаты и состояние проекта (Reset).
    3. Завершает текущий скрипт с нейтральным статусом (Done).

    Функция не принимает аргументов и не возвращает значения.

    Использование:
        Вызовите эту функцию в любой точке скрипта, когда необходимо
        полностью перезапустить проект и начать выполнение заново.
        После вызова скрипт завершается, и MOKO SE инициирует
        новый цикл запуска.

    Пример:
        >>> ProjectRestart()
    """
    Program('control', 'set', 'StageClear')
    Program('control', 'set', 'reset')
    Program('script', 'set', 'done')
    sys.exit()
# endregion *****************************************

#  ---------------------- Hash & Tree  / Дерево и Хэши  ------------

# region --- HashSet / Устанавливает результат выполнения в дереве (Hash). --
def HashSet(command: Literal['done', 'passed', 'failed'] = 'done') -> None:
    """
    Устанавливает результат выполнения в дереве (Hash).

    Args:
        command (str, optional): Статус для установки.
                                 Возможные значения:
                                 - 'done': Выполнено (желтый нейтральный цвет).
                                 - 'passed': Пройдено (зеленый цвет).
                                 - 'failed': Не пройдено (красный цвет).
                                 Defaults to 'done'.
    """
    Program('tree', 'set', f'chosen = {command}')
# endregion

# region --- HashSelect / Выбирает хэш(Hash) в дереве. --
def HashSelect(hash: str) -> None:
    """
    Выбирает хэш в дереве.

    Args:
        hash (str): Хэш для выбора.
    """
    Program('tree', 'set', 'select = ' + hash)
    return
# endregion

# region --- HashExecuteStep / Выполняет шаг: выбирает его в дереве и выводит название в Stage. --
def HashExecuteStep(step_string: str) -> None:
    """
    Выполняет шаг: выбирает его в дереве и выводит название в Stage.

    Ожидает строку в формате 'Название шага$HASH_ID'.
    Если символ '$' отсутствует, вся строка передается как хэш.

    Args:
        step_string (str): Строка с описанием шага и хэшем.
    """
    # Удаляем пробелы в начале и в конце строки во избежание ошибок
    step_string = step_string.strip()

    # Разделяем строку по символу '$' максимум 1 раз
    parts = step_string.split('$', 1)

    if len(parts) == 2:
        step_name = parts[0]
        step_id = parts[1]

        # Выбираем хэш в дереве (склеиваем обратно название и ID)
        HashSelect(f"{step_name}${step_id}")
        # Выводим информационное сообщение о начале шага
        StageSeparator(f"{step_name}")
    else:
        # Если символа $ в строке нет, используем всю строку как хэш
        HashSelect(step_string)
        # Выводим строку в Stage как есть
        StageSeparator(step_string)

    return
# endregion

# region --- HashSelectCheck / Выбирает хэш в дереве и проверяет, является ли он пустым. --
def HashSelectCheck(hash: str) -> bool:
    """
    Выбирает хэш в дереве и проверяет, является ли он пустым.

    Args:
        hash (str): Хэш для выбора и проверки.

    Returns:
        bool: True, если статус хэша 'empty', иначе False.
    """
    Program('tree', 'set', f'select = {hash}')
    status = Program('tree', 'get', f'hash = {hash}', 'string')

    if status == 'empty':
        return True
    return False
# endregion

# region --- HashTreeInfo / Устанавливает информационную заметку ---
def HashTreeInfo(info_text: str) -> None:
    """
    Устанавливает информационную заметку в поле "информация для выполнения"("Execution info").

    Данная заметка отображается под деревом MOKO SE и может содержать
    любую текстовую информацию о ходе выполнения, результатах измерения и т.д.

    Args:
        info_text (str): Текст информационной заметки.

    Example:
        >>> HashTreeInfo("Измерение напряжения: 5.2 В")
        >>> HashTreeInfo("Ошибка: превышен лимит времени")
    """
    Program('tree', 'set', f'info = {info_text}')

TreeInfo = HashTreeInfo
# endregion

#  ---------------------- Time / Время -----------------------------

# region --- TimeParameter / Литералы времени MOKO SE
TimeParameter = Literal[
    # Текущая дата и время
    "Current", "CurrentDateAndTime",
    # Текущая дата
    "CurrentDate",
    # Текущее время
    "CurrentTime",

    # Дата и время запуска проекта
    "ProjectStart", "ProjectStartDateAndTime",
    # Дата запуска проекта
    "ProjectStartDate", "ProjectStartTime",
    # Время выполнения проекта
    "ProjectExecution", "TotalExecution",
    # Время когда проект не выполнялся
    "ProjectStop", "TotalStop",
    "ProjectIdle", "TotalIdle",
    # Общее время ошибок в проекте
    "ProjectError", "TotalError",

    # Дата и время запуска скрипта
    "ScriptStart", "ScriptStartDateAndTime",
    # Дата запуска скрипта
    "ScriptStartDate", "ScriptStartTime",

    # Время выполнения скрипта
    "ScriptExecution",
    # Время когда скрипт не выполнялся
    "ScriptStop", "ScriptIdle",
    # Время ошибок в скрипте 00:00:00
    "ScriptError"
]
# endregion

# region --- TimeGet / Получает параметры времени через системную функцию MOKO.Program.
def TimeGet(command: TimeParameter = "Current"):
    """
    Получает параметры времени через системную функцию MOKO.Program.

    Args:
        command (TimeParameter, optional): Запрашиваемый параметр времени.
                                           По умолчанию 'Current'.

    Returns:
        Результат выполнения MOKO.Program.
    """
    return Program('time', 'get', command)
# endregion

# region --- TimeFormatDate() / Преобразует дату из формата ДД.ММ.ГГГГ в формат "ДД месяц ГГГГ"
def TimeFormatDate(date_str: str, lang: str = "EN") -> str:
    """
    Преобразует дату из формата ДД.ММ.ГГГГ в формат "ДД месяц ГГГГ".
    Поддерживаемые языки: 'RU' (русский), 'EN' (английский, значение по умолчанию).
    При любой ошибке возвращает исходную строку и вызывает MOKO.StageError (если доступен).
    """
    if not date_str or '.' not in date_str:
        return date_str

    try:
        parts = date_str.split('.')
        if len(parts) != 3:
            raise ValueError(f"Invalid date format, expected DD.MM.YYYY, got: {date_str}")

        day, month_num, year = parts[0], parts[1], parts[2]

        # Проверяем, что месяц – число от 01 до 12
        month_int = int(month_num)
        if not (1 <= month_int <= 12):
            raise ValueError(f"Month must be between 01 and 12, got: {month_num}")

        # Названия месяцев в нужном языке
        months_ru = {
            1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля',
            5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа',
            9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'
        }
        months_en = {
            1: 'January', 2: 'February', 3: 'March', 4: 'April',
            5: 'May', 6: 'June', 7: 'July', 8: 'August',
            9: 'September', 10: 'October', 11: 'November', 12: 'December'
        }

        if lang.upper() == 'RU':
            month_name = months_ru[month_int]
        else:  # EN по умолчанию
            month_name = months_en[month_int]

        return f"{day} {month_name} {year}"

    except Exception as e:
        try:
            StageError(f"Error formatting date '{date_str}': {e}")
        except NameError:
            print(f"Error: {e}")
        return date_str  # возвращаем исходную строку как fallback
# endregion


#  ---------------------- MOKO / общие команды -----------------------------
# region --- Export() / Сохраняет отчет в указанном формате. ---
def Export(report_format: Literal["Word", "PDF", "Word as", "Pdf as"] = "Word") -> None:
    """
    Сохраняет отчет в указанном формате.

    Args:
        report_format (Literal): Формат сохранения отчета.
                                 Допустимые значения: 'Word', 'PDF', 'Word as', 'Pdf as'.
                                 По умолчанию 'Word'.
    """
    # Точно сопоставляем ввод программиста с тем, что понимает сервер
    server_commands = {
        "Word": "SaveWordReport",
        "PDF": "SavePdfReport",
        "Word as": "SaveWordReportAs",
        "Pdf as": "SavePdfReportAs"
    }

    # Достаем нужную команду из словаря
    command = server_commands[report_format]

    # Вызываем команду
    Program('control', 'set', command)
    return
# endregion ---------------------------------------------------------

# region --- Screenshot() / Возвращает скриншот в Base64. ---
def Screenshot() -> Any:
    """
    Возвращает скриншот в формате Base64.
    """
    # Вызываем команду
    return Program('control', 'get', 'screenshot', 'string')
# endregion ---------------------------------------------------------

###############################################################
###############################################################
###############################################################

# region ### Internal Helper Functions / Внутренние вспомогательные функции ###

# region --- check_project_state / Проверка состояния проекта ---
def check_project_state() -> None:
    """
    Проверяет состояние проекта в MOKO SE и синхронизирует выполнение скрипта.

    - Если состояние 'run', продолжает выполнение.
    - Если состояние 'pause', приостанавливает скрипт до смены состояния.
    - Если состояние 'stop', немедленно завершает скрипт.
    """
    URLPSRead: str = _UrlProjectStateRead
    projectstate: str = ''
    while (projectstate.lower() != 'run'):
        serverstate = _request.get(URLPSRead)
        JSONprojectstate = json.loads(serverstate.content)
        projectstate: str = JSONprojectstate.get('projectstate')
        if (projectstate.lower() == 'stop'):
            sys.exit()
        if projectstate.lower() == 'pause':
            time.sleep(0.05)
# endregion

# region --- check_status / Проверка статуса ---
def check_status(system: str, mode: str, URLRead: str) -> str:
    """
    Ожидает готовности компонента MOKO SE и получает от него данные.

    Функция циклически опрашивает URLRead, пока статус компонента не станет 'ready'.
    Имеет 10 попыток, после чего возвращает пустую строку.

    Args:
        system (str): Имя системы/компонента (например, 'driver', 'plugin').
        mode (str): Режим, в котором была вызвана команда ('get', 'set', и т.д.).
        URLRead (str): URL для чтения статуса и данных.

    Returns:
        str: Строка с данными от компонента или пустая строка в случае ошибки.
    """
    data: str = ""
    badresponse: int = 0
    status: str = "none"
    while ((status.lower() != 'ready') and (badresponse < 10)):
        response = _request.get(URLRead)
        if (response.status_code != 200):
            Stage(f"ERROR IN PYTHON LIBRARY! BAD RESPONSE CODE! {str(response.status_code)}", 'error')
            badresponse += 1
        else:
            y = json.loads(response.content)
            status: str = y.get(f'{system}status')
            if mode.lower() in ('get', 'check', 'init'):
                data: str = y.get(f'{system}data')
        if system in ['message', 'driver', 'plugin', 'utility']:
            time.sleep(0.05)
    if is_bad_response(badresponse): return ""
    return data
# endregion

# region --- parse_data / Разбор данных ---
def parse_data(data: str = '', mode: str = '', valuetype: str = 'void') -> Any:
    """
    Преобразует строковые данные от сервера в нужный тип Python.

    Поддерживает базовые типы (int, float, bool, str) и их массивы (arrayint, ...).

    Args:
        data (str): Входная строка данных от сервера.
        mode (str): Режим, в котором была вызвана команда. Парсинг выполняется только для 'get', 'check', 'init'.
        valuetype (str, optional): Целевой тип данных. Defaults to 'void'.

    Returns:
        Преобразованные данные или None, если парсинг не требуется или невозможен.
    """
    if mode.lower() not in ["get", "check", "init"]: return None
    splitter: str = ";"
    if is_semicolon_error(data, splitter, valuetype): return None
    data: str = check_data(data, splitter)
    if valuetype.lower() == 'arrayboolean':
        return to_list(bool, data, splitter)
    elif valuetype.lower() == 'arrayfloat':
        return to_list(float, data, splitter)
    elif valuetype.lower() == 'arrayint':
        return to_list(int, data, splitter)
    elif valuetype.lower() == 'arraystring':
        return to_list(str, data, splitter)
    elif "bool" in valuetype.lower():
        data: str = data.split(splitter)[0]
        return True if data.lower() == "true" else False
    elif valuetype.lower() == 'float':
        data: str = data.split(splitter)[0]
        # Удаляем пробелы и проверяем
        data = data.strip()
        if not data:
            return 0.0
        # Заменяем запятую на точку
        data = data.replace(",", ".")
        # Удаляем все лишние символы кроме цифр, точки и минуса
        import re
        data = re.sub(r'[^\d.\-]', '', data)
        try:
            return float(data)
        except ValueError:
            return 0.0
    elif valuetype.lower() == 'int':
        data: str = data.split(splitter)[0]
        data: str = data.split(".")[0]
        return int(data.split(",")[0])
    else:  # Используется в качестве valuetype = 'string'
        return data.split(splitter)[0]
# endregion

# region --- check_data / Проверка данных ---
def check_data(data: str, splitter: str = ";") -> str:
    """
    Удаляет лишний символ-разделитель (';') в конце строки, если он есть.

    Args:
        data (str): Входная строка.
        splitter (str, optional): Символ-разделитель. Defaults to ";".

    Returns:
        str: Очищенная строка.
    """
    if data.rfind(splitter) == len(data)-1:
        data: str = data[:-1]
    return data
# endregion

# region --- to_list / Преобразовать в список ---
def to_list(func, data: str, splitter: str = ";") -> Any:
    """
    Разделяет строку на список и преобразует каждый элемент к заданному типу.

    Args:
        func: Функция преобразования типа (int, float, bool, str).
        data (str): Входная строка с данными, разделенными `splitter`.
        splitter (str, optional): Символ-разделитель. Defaults to ";".

    Returns:
        list: Список с преобразованными значениями.
    """
    split_data: list = data.split(splitter)
    result: list = []
    for spl in split_data:
        if func is bool:
            result.append(True if spl.lower() == "true" else False)
        elif func is int:
            spl: str = spl.split(".")[0]
            result.append(func(spl.split(",")[0]))
        elif func is float:
            result.append(func(spl.replace(",", ".")))
        else:
            result.append(func(spl))
    return result
# endregion

# region --- is_semicolon_error / Ошибка с точкой с запятой ---
def is_semicolon_error(data: str, splitter: str, valuetype: str) -> bool:
    """
    Проверяет наличие двойного разделителя (';;') в конце строки.

    Это считается ошибкой формата данных. При обнаружении выводит ошибку в Stage.

    Args:
        data (str): Входная строка.
        splitter (str): Символ-разделитель.
        valuetype (str): Тип значения, для которого производится проверка.

    Returns:
        bool: True, если ошибка найдена, иначе False.
    """
    if data[-2:] == f"{2*splitter}":
        Stage(f'ERROR IN PYTHON LIBRARY!', 'error')
        Stage(f'INPUT DATA CONTAINS MORE THAN 1 \'\'{splitter}\'\' AT THE END!', 'error')
        Stage(f'DATA: {data}     =>     VALUETYPE: {valuetype.upper()}', 'error')
        return True
    return False
# endregion

# region --- is_bad_response / Проверка плохого ответа ---
def is_bad_response(badresponse: int) -> bool:
    """
    Проверяет, не превышено ли количество неудачных ответов от сервера.

    Args:
        badresponse (int): Счетчик неудачных ответов.

    Returns:
        bool: True, если количество ошибок >= 10, иначе False.
    """
    if (badresponse >= 10):
        StageError("ERROR IN PYTHON LIBRARY! FUNCTION EXIT BECAUSE OF BAD RESPONSES", 'error')
        return True
    return False
# endregion

# region --- send_request / Отправка запроса ---
def send_request(URLWrite: str, request: str) -> None:
    """
    Отправляет POST-запрос на указанный URL с данными в формате JSON.

    Args:
        URLWrite (str): URL для отправки запроса.
        request (str): Тело запроса в виде строки JSON.
    """
    headers: dict = {'Content-Type': 'application/json; charset=utf-8'}
    response = _request.post(URLWrite, headers=headers, data=request.encode('utf-8'))
# endregion

# endregion