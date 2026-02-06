import funcs
def dataSecure():
    data = funcs.dbConnect("SELECT * FROM users")
    
    with open("data.txt", 'w', encoding='utf-8') as f:
        for i in data:
            i = str(i).replace("(", "").replace(")", "").replace(",", " | ") + "\n"
            f.write(i)
        f.close()


if __name__ == "__main__":
    dataSecure()