def title_case(text):
    print(f"----------")
    return " ".join(word.capitalize() for word in text.split())


print(title_case("learning python is fun"))
