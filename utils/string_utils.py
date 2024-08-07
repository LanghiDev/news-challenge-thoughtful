def count_phrases_in_title_and_desc(phrase: str, title: str, description: str):
    phrase_words = phrase.lower().strip().split(' ')
    counter: int = sum(title.count(w) for w in phrase_words)
    counter += sum(description.count(w) for w in phrase_words)
    return counter


def has_money_in_title_and_desc(title: str, description: str):
    # possible formats -> ['$11.1', '$111,111.11', '11 dollars', '11 USD']
    title_words: list[str] = title.lower().split(' ')
    if search_money_in_words(title_words):
        return True

    description_words: list[str] = description.lower().split(' ')
    if search_money_in_words(description_words):
        return True

    return False


def search_money_in_words(words: list):
    money_found_maybe: bool = False
    for word in words:
        if money_found_maybe and (word.find('$') >= 0 or word.find('dollar') >= 0 or word.find('usd')) >= 0:
            return True
        else:
            money_found_maybe = False

        if any(letter for letter in word if letter.isnumeric()):  # if detects that has a number, could be money
            if any(letter for letter in word if letter == '$'):  # if detects '$' character, it's a money
                return True
            money_found_maybe = True  # if didn't detects '$', can detects 'dollar' or 'usd' in next word
    return False
