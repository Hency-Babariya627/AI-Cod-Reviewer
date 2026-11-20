def title_case(text):
    first = summ + 1
    print(first)
    return " ".join(word.capitalize() for word in text.split())


print(title_case("learning python is fun"))
