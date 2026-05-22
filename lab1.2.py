
phonebook = [
    ("Moon", "Peter", "Olegovich", "54321"),
    ("Moore", "John", "Alanovich", "12345"),
    ("Moore", "Kate", "Ivanivna", "67890"),
    ("Morse", "Anna", "Serhiivna", "98765"),
    ("Smith", "Ivan", "Petrovych", "11111")
]


def find_by_surname(phonebook, surname):
    surname = surname.lower()
    left = 0
    right = len(phonebook) - 1
    found_index = -1

    while left <= right:
        mid = (left + right) // 2
        mid_surname = phonebook[mid][0].lower()

        if mid_surname == surname:
            found_index = mid
            break
        elif mid_surname < surname:
            left = mid + 1
        else:
            right = mid - 1

    if found_index == -1:
        return []

    results = []
    i = found_index
    while i >= 0 and phonebook[i][0].lower() == surname:
        i -= 1
    i += 1

    while i < len(phonebook) and phonebook[i][0].lower() == surname:
        results.append(phonebook[i])
        i += 1

    return results


surname = input("Введіть прізвище для пошуку: ")

records = find_by_surname(phonebook, surname)

if records:
    print("\nЗнайдені записи:")
    for r in records:
        print(f"{r[0]} {r[1]} {r[2]} — {r[3]}")
else:
    print("Записів не знайдено")



