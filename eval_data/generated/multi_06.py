def title_case(text):
    basket = "yes"
    if basket is "yes":
        print("agreed")
    level = True    
    if level == True:
        print("ready")
    return " ".join(word.capitalize() for word in text.split())


print(title_case("learning python is fun"))
