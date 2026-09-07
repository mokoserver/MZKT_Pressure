import MOKO
# Результат измерений
#Region ------------------------------$REP1
# ============================================================
# ПОЛУЧЕНИЕ ДАННЫХ ИЗ ОТЧЕТА
# ============================================================
try:
    # Получаем необходимые данные из отчета для подстановки в протокол
    Result = MOKO.ReportGet('Результат поверки', 'string')           # Результат поверки
    Conclusion = MOKO.ReportGet('Заключение', 'string')              # Заключение
except Exception as e:
    MOKO.StageError(f"Ошибка при получении данных из отчета: {e}")
    MOKO.HashSet('failed')
    MOKO.ScriptEnd('failed')


#hash Создание протокола: MS Word;
#hash Повторить измерения
#hash Завершить


# ============================================================
# СОЗДАНИЕ ПРОТОКОЛА
# ============================================================
try:
    MOKO.HashSelect('Создание протокола')
    MOKO.StageSeparator("Формирование протокола поверки")
    # Создаем протокол в формате Word
    MOKO.Export("Word")
    MOKO.StageSuccess("Протокол поверки успешно создан в формате MS Word")
    MOKO.HashSet('passed')

    # Если нужно создать PDF - раскомментировать
    # MOKO.Export("PDF")
    # MOKO.StageSuccess("Протокол поверки успешно создан в формате PDF")

except Exception as e:
    MOKO.StageError(f"Ошибка при создании протокола: {e}")
    MOKO.HashSet('failed')
    MOKO.ScriptEnd('failed')
# ============================================================

# ============================================================
# ВОПРОС О ПОВТОРЕ ИЗМЕРЕНИЙ
# ============================================================
try:
    MOKO.HashSelect('Повторить измерения')
    MOKO.StageSeparator("Завершение работы")

    # hash Повторить измерения
    # hash Завершить

    # Формируем информационное сообщение с результатами
    status_message = "Протокол успешно создан!\n\n"
    status_message += f"Результат поверки: {Result if Result else 'не определен'}\n"
    status_message += f"Заключение: {Conclusion if Conclusion else 'не определено'}\n\n"
    status_message += "Желаете ли вы выполнить измерения повторно?\n"
    status_message += "• 'Да' - перезапустить проект и начать заново\n"
    status_message += "• 'Нет' - завершить работу"

    # Показываем диалог с вопросом о повторных измерениях
    repeat = MOKO.MessageGetBool(
        'Повторить измерения? #images\GoodProtocol.png',
        status_message,
        boolean=False,  # По умолчанию "Нет"
        timeout=30  # Авто-закрытие через 30 секунд (выберется "Нет")
    )

    if repeat:
        MOKO.StageInfo("Повторные измерения: перезапуск проекта")
        MOKO.StageSeparator("Перезапуск проекта...")
        MOKO.HashSet('passed')
        # Перезапускаем проект
        MOKO.ProjectRestart()
    else:
        MOKO.StageSuccess("Поверка завершена. Протокол сохранён.")
        MOKO.HashSet('passed')
        # Завершаем скрипт с успехом
        MOKO.ScriptEnd('passed')

except Exception as e:
    MOKO.StageError(f"Ошибка при отображении диалога повторных измерений: {e}")
    MOKO.HashSet('failed')
    MOKO.ScriptEnd('failed')
# ============================================================


MOKO.HashSelect('Завершить')
MOKO.HashSet('passed')
MOKO.EndScript()
