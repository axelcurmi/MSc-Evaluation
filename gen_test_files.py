with open("./resources/1KB.txt", "w") as stream:
    stream.write((b"A" * pow(2, 10)).decode())

with open("./resources/1MB.txt", "w") as stream:
    stream.write((b"B" * pow(2, 20)).decode())
