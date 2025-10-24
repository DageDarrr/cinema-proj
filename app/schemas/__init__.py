def is_palindrome(text : str) -> bool:
    clean_text = text.replace(' ', '').lower()

    return clean_text == clean_text[::-1]


res = is_palindrome('А роза упала на лапу Азора')
print(res)

    