import hashlib
import itertools
import string
import requests
from bs4 import BeautifulSoup
import os

def hash_password(password, hash_type):
    if hash_type == "md5":
        return hashlib.md5(password.encode()).hexdigest()
    elif hash_type == "sha1":
        return hashlib.sha1(password.encode()).hexdigest()
    elif hash_type == "sha256":
        return hashlib.sha256(password.encode()).hexdigest()
    else:
        raise ValueError("Unsupported hash type")

def dictionary_attack(hash_to_crack, hash_type, dictionary_file):
    if not os.path.exists(dictionary_file):
        print(f"Dictionary file {dictionary_file} does not exist.")
        return None

    with open(dictionary_file, "r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            password = line.strip()
            hashed_password = hash_password(password, hash_type)
            if hashed_password == hash_to_crack:
                return password
    return None

def brute_force_attack(hash_to_crack, hash_type, max_length, verbose=False):
    chars = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
    for length in range(1, max_length + 1):
        for password in itertools.product(chars, repeat=length):
            password = ''.join(password)
            hashed_password = hash_password(password, hash_type)
            if hashed_password == hash_to_crack:
                return password
            if verbose and length == 1 and ''.join(password).endswith('z'):
                print(f"Still working, checked up to length {length} with last character 'z'")
    return None

def perform_login(url, username, password, username_field, password_field):
    session = requests.Session()
    response = session.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Assuming a simple form with username and password fields
    form = soup.find('form')
    if not form:
        print("Login form not found on the page.")
        return False

    # Assuming the form uses POST method and has input fields for username and password
    action_url = form.get('action')
    if not action_url.startswith('http'):
        action_url = url.rstrip('/') + '/' + action_url.lstrip('/')

    payload = {
        username_field: username,
        password_field: password
    }

    login_response = session.post(action_url, data=payload)
    if "Login failed" not in login_response.text:
        return True
    return False

def main():
    hash_type = input("Enter the hash type (md5, sha1, sha256): ").lower()
    hash_to_crack = input("Enter the hash to crack: ")

    attack_type = input("Choose attack type (dictionary/brute-force): ").lower()

    if attack_type == "dictionary":
        dictionary_file = "hashed_password_dictionary.txt"
        result = dictionary_attack(hash_to_crack, hash_type, dictionary_file)
    elif attack_type == "brute-force":
        max_length = int(input("Enter the maximum length for brute-force attack: "))
        result = brute_force_attack(hash_to_crack, hash_type, max_length)
    else:
        print("Invalid attack type.")
        return

    if result:
        print(f"Password found: {result}")
    else:
        print("Password not found. Please try brute-force instead.")

if __name__ == "__main__":
    main()