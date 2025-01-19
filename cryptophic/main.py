import pyaes, pbkdf2, binascii, os, secrets
import os
import time
from cryptophic.aes256_crypto import encryptFile, decryptFile

# AES supports multiple key sizes: 16 (AES128), 24 (AES192), or 32 (AES256).
bufferSize = 64 * 1024
keypath = r".\key.key"
dec_secure_path = r"C:\\Users\\" + os.getlogin() + r"\\.secure\\.encfiles"


# Generating 32-byte key and return generated key
def generate_key():
    password = "s3cr3t*c0d3"
    passwordSalt = os.urandom(16)
    key = pbkdf2.PBKDF2(password, passwordSalt).read(32)
    print(binascii.hexlify(key))
    return key, binascii.hexlify(key)


# Generating 16-byte key and return generated key
def generate_token():
    password = "s3cr3t*c0d3"
    passwordSalt = os.urandom(16)
    key = pbkdf2.PBKDF2(password, passwordSalt).read(16)
    # print(binascii.hexlify(key))
    return key, binascii.hexlify(key)


def get_dec_file_path():
    return dec_secure_path


def encrypt_file(file_name):
    if not os.path.isdir(dec_secure_path):
        os.makedirs(dec_secure_path)

    with open(keypath, 'rb') as f:
        key = f.read()

    encfile = {"decfile": os.path.join(dec_secure_path, file_name), "encfile": os.path.join(".", file_name)}
    try:
        encryptFile(encfile["decfile"], encfile["encfile"], str(key), bufferSize)
        os.remove(encfile["decfile"])
    except Exception:
        print("Encrypt File Error")
        return False

    return True


def decrypt_file(file_name):
    if not os.path.isdir(dec_secure_path):
        os.makedirs(dec_secure_path)

    with open(keypath, 'rb') as f:
        key = f.read()

    decfile = {"encfile": os.path.join(".", file_name), "decfile": os.path.join("\\", file_name)}
    try:
        decryptFile(decfile["encfile"], dec_secure_path + decfile["decfile"], str(key), bufferSize)
    except Exception as e:
        print("Decrypt File Error:", e)
        return False

    return True


def encrypt_file_to(_from, _to):
    if not os.path.isdir(dec_secure_path):
        os.makedirs(dec_secure_path)

    with open(keypath, 'rb') as f:
        key = f.read()

    try:
        encryptFile(_from, _to, str(key), bufferSize)
        os.remove(_from)
    except Exception as e:
        print("Encrypt File Error:", e)
        return False

    return True


def decrypt_file_to(_from, _to):
    if not os.path.isdir(dec_secure_path):
        os.makedirs(dec_secure_path)

    with open(keypath, 'rb') as f:
        key = f.read()

    try:
        decryptFile(_from, _to, str(key), bufferSize)
    except Exception as e:
        print("Decrypt File Error:", e)
        return False

    return True


def decrypt(folder_path):
    if not os.path.isdir(dec_secure_path):
        os.makedirs(dec_secure_path)

    with open(keypath, 'rb') as f:
        key = f.read()

    decfiles = []
    try:
        for root, dirs, files in os.walk(folder_path):
            for filename in files:
                decfiles.append({"encfile": os.path.join(root, filename), "decfile": os.path.join("\\", filename)})
        for decfile in decfiles:
            try:
                decryptFile(decfile["encfile"], dec_secure_path + decfile["decfile"], str(key), bufferSize)
            except Exception as e:
                print("Decrypt Error1:", e)
                return False
    except Exception as e:
        print("Decrypt Error2:", e)
        return False

    return True


def exit_process():
    for root, dirs, files in os.walk(dec_secure_path):
        for filename in files:
            os.remove(os.path.join(root, filename))
