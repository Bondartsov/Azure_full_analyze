def choose_from_list(options, prompt):
    print(prompt)
    for i, option in enumerate(options, start=1):
        print(f"{i}. {option}")
    while True:
        try:
            choice = int(input("Введите номер: "))
            if 1 <= choice <= len(options):
                return options[choice - 1]
            print("Неверный номер. Попробуйте снова.")
        except ValueError:
            print("Пожалуйста, введите число.")
