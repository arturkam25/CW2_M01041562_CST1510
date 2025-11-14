import bcrypt

def hash_password(pwd):
    password_bytes = pwd.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(pwd, hashed):
    return bcrypt.checkpw(pwd.encode('utf-8'), hashed.encode('utf-8'))

def register_user():
    username = input("Enter username: ")
    password = input("Enter password: ")

    hashed_password = hash_password(password)

    with open('users.txt', 'a') as f:
        f.write(f"{username},{hashed_password}\n")

    print("User registered successfully.")

def login_user(username, password):
    try:
        with open('users.txt', 'r') as f:
            users = f.readlines()
    except FileNotFoundError:
        print("User database does not exist yet.")
        return

    for line in users:
        stored_username, stored_hashed_password = line.strip().split(',')
        if stored_username == username:
            if verify_password(password, stored_hashed_password):
                print("Login successful.")
                return
            else:
                print("Incorrect password.")
                return

    print("Username not found.")

def menu():
    print("Choose an option")
    print("1. Register")
    print("2. Login")
    print("3. Exit")

def main():
    while True:
        menu()
        choice = input("Enter choice: ")
        if choice == "1":
            register_user()
        elif choice == "2":
            username = input("Enter username: ")
            password = input("Enter password: ")
            login_user(username, password)
        elif choice == "3":
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please try again.")

main()