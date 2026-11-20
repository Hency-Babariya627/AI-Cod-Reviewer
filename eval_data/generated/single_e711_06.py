def title_case(text):
    guess = None
    if guess == None:
        print("nothing yet")
    return " ".join(word.capitalize() for word in text.split())


print(title_case("learning python is fun"))
