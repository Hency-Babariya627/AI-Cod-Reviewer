def title_case(text):
    flag = 3
    if not flag is None:
        print("number set")
    return " ".join(word.capitalize() for word in text.split())


print(title_case("learning python is fun"))
