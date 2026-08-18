import MOKO
# Результат измерений
#Region ------------------------------$REP1
PermissibleError = MOKO.ReportGet('PermissibleError', 'string')  # Пределы допускаемой погрешности
UnitOfMeasure = MOKO.ReportGet('UnitOfMeasure', 'string')        # единицы измерения


#hash Создание протокола: MS Word;
#hash Повторить измерения
#hash Завершить
MOKO.ReportSetStrings(('PermissibleErr', f'{PermissibleError}'),
                      ('UnitofMeasure', f'{UnitOfMeasure}'),
                      ('UnitofMeasure1', f'{UnitOfMeasure}'),
                      ('UnitofMeasure2', f'{UnitOfMeasure}'),
                      ('UnitofMeasure3', f'{UnitOfMeasure}'),
                      ('UnitofMeasure4', f'{UnitOfMeasure}'))



MOKO.ReportSetStrings(('UoM1', f'{UnitOfMeasure}'),
                      ('UoM2', f'{UnitOfMeasure}'),
                      ('UoM3', f'{UnitOfMeasure}'),
                      ('UoM4', f'{UnitOfMeasure}'))


MOKO.Stage('Поверка завершена.', 'info')


variable = MOKO.Messenger("get", "Протокол измерений #repeat.png",
                                  "Сохранить текущие результаты? \n"
                                  "Отмена запустит измерения повторно.",
                          "boolean = false time = 10")

#MOKO.ExecuteStep("Создание протокола$REPORT")
#MOKO.Program('Control', 'set', 'Save project report')

if variable:
    try:
        MOKO.Export("Word")
        MOKO.StageSuccess("Word-отчет сгенерирован")
        MOKO.HashSet('passed')
    except Exception as e:
        MOKO.StageError(f"Ошибка во время генерации отчета: {e}")
        MOKO.HashSet('failed')
else:
    MOKO.ProjectRestart()



MOKO.EndScript()
