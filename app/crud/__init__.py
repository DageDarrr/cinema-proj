def is_isogram(string: str) -> bool:
    if not string:
        return True

    my_dict = {}

    for char in string.lower():
        my_dict[char] = my_dict.get(char, 0) + 1

    for count in my_dict.values():
        if count > 1:
            return False
    return True


print(is_isogram("midlqwerty"))
