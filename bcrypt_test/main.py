import bcrypt

def hash_password(pwd):
    password_bytes = pwd.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(pwd, hashed):
    password_bytes = pwd.encode('utf-8')
    hashed_bytes = hashed.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)

def register_user():
    user_name = ("Enter username: ")
    passowrd = input("Enter password: ")
    hashed_password = hash_password(passowrd)
    with open('users.txt', 'a') as f:
        f.write(f"{user_name},{hashed_password}\n")
    print("User registered successfully.")

register_user()

def login_user(username, password):
    with open('users.txt', 'r') as f:
        users = f.readlines()
    for line in liness:
        stored_username, stored_hashed_password = line.strip().split(',')
        if stored_username == username:
            if verify_password(password, stored_hashed_password):
                print("Login successful.")
                return
            else:
                print("Incorrect password.")
                return
            
    print("Username not found.")




user_name = input("Enter username: ")
password = input("Enter password: ")
login_user(user_name, password)       
#   pass


def menu():
    print('Chose an option')
    print('1. Register')
    print('2. Login')
    print('3. Exit')

def main():
    while True:
        menu()
        choice = input('Enter choice: ')
        if choice == '1':
            register_user()
        elif choice == '2':
            user_name = input("Enter username: ")
            password = input("Enter password: ")
            login_user(user_name, password)
        elif choice == '3':
            print('Exiting program.')
            break
        else:
            print('Invalid choice. Please try again.')
