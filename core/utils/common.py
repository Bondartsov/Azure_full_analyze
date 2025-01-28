def choose_from_list(options, prompt):
    print(prompt)
    for i, option in enumerate(options, start=1):
        if isinstance(option, str):
            print(f"{i}. {option}")
        else:
            print(f"{i}. {option.name}")  # Выводим имя репозитория

    while True:
        try:
            choice = int(input("Введите номер: "))
            if 1 <= choice <= len(options):
                selected = options[choice - 1]
                return selected if isinstance(selected, str) else selected  # Возвращаем сам объект, а не его имя
            print("Неверный номер. Попробуйте снова.")
        except ValueError:
            print("Пожалуйста, введите число.")
