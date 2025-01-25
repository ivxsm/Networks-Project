import hashlib as hashlib
def main():
    with open('text.txt', 'rb') as file:
        print(hashlib.file_digest(file, 'md5').hexdigest())

if __name__ == "__main__":
    main()
    