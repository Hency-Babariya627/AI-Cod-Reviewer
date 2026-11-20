def title_case(text):
    try:
        size = [1, 2]
        print(size[5])
    except:
        print("bad index")
    return " ".join(word.capitalize() for word in text.split())


print(title_case("learning python is fun"))
