nums = []

def append_test():
    global nums

    for i in range(1000000):
        nums.append(i)

def main():
    for i in range(100):
        print(i)
        append_test()

if __name__ == "__main__":
    main()
