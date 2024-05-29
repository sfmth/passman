"""
Written for
MicroPython v1.22.1 on 2024-01-05; Raspberry Pi Pico with RP2040


---> whole file checksums are to be handled by the raid controller
"""


def open_menu():
    print()
    menu_selection = input("Menu:\n" +
        "1. Change login\n" +
        "2. Add new item\n" +
        "3. Retrieve an item\n")
    if (menu_selection == "1"):
        update_password()
    elif (menu_selection == "2"):
        add_item()
    elif (menu_selection == "3"):
        retrieve_item()
    else:
        print("select")
        open_menu()
        
def add_item():
    password = input('Input Credentials: ')
    password_coded = read_sdcard(".key")
    auth = verify_password(password, password_coded)
    if (auth == True):
        item_name = input("Name of the item: ")
        item_creds = input("Item Credentials: ")
        item_creds_enc = encrypt(item_creds, hash_(password))
        write_sdcard("item_"+item_name, item_creds_enc)
        add_checksum("item_"+item_name)
        read_file = check_checksum("item_"+item_name)
        print("Item successfully added!")
        open_menu()
    else:
        print()
        print("ERROR: Wrong Credentials")
        open_menu()

def retrieve_item():
    password = input('Input Credentials: ')
    password_coded = read_sdcard(".key")
    auth = verify_password(password, password_coded)
    if (auth == True):
        item_name = input("Name of the item: ")
        read_file = check_checksum("item_"+item_name)
        creds = decrypt(read_file, hash_(password))
        print("Credentials: ")
        print(creds)
        open_menu()
    else:
        print()
        print("ERROR: Wrong Credentials")
        open_menu()


def test_microsd():
    # Create a file and write something to it
    with open("/sd/.config", "w") as file:
        file.write(b'tests&\x07C\xfcP\xfe;d+4\xaez\t\xcbs\xc9\xe7]\xaf\xabg\xa8\x00/')

    # Open the file we just created and read from it
    with open("/sd/.config", "rb", encoding='iso-8859-15') as file:
        data = file.read()
    if data == b'tests&\x07C\xfcP\xfe;d+4\xaez\t\xcbs\xc9\xe7]\xaf\xabg\xa8\x00/':
        return 1
        write_sdcard("testing_checksum", hash_("encrypted"))
        add_checksum("testing_checksum")
        read_file = check_checksum("testing_checksum")
    else:
        print(data)
        print("ERROR: Fatal Error: microsd card is not functional")
        #time.sleep(10)
        machine.soft_reset()

def read_sdcard(filename):
    path = "/sd/" + filename
    with open(path, "rb") as file:
        data = file.read()
        return data

def write_sdcard(filename, data):
    path = "/sd/" + filename
    with open(path, "w") as file:
        file.write(data)
    
def check_hash_integrity():
    pass

def encrypt(plaintext, key):
    BLOCK_SIZE = 32
    cipher = aes(key, 1)
    pad = BLOCK_SIZE - len(plaintext) % BLOCK_SIZE
    plaintext = plaintext + " "*pad

    encrypted = cipher.encrypt(plaintext)
    return encrypted

def decrypt(encrypted, key):
    cipher = aes(key, 1)
    decrypted = cipher.decrypt(encrypted)
    return decrypted

def hash_(text):
    return hashlib.sha256(text).digest()

def check_checksum(filename):
    file = read_sdcard(filename)
    lenght = len(file)
    hash_calc = hash_(file[:lenght-32])
    hash_file = file[lenght-32:]
    if (hash_calc == hash_file):
        print("checksum is correct")
        return file[:lenght-32]
    else:
        print()
        print("ERROR: Fatal Error: File Corrupted")
        #time.sleep(10)
        machine.soft_reset()

def add_checksum(filename):
    file = read_sdcard(filename)
    hash_calc = hash_(file)
    file += hash_calc
    write_sdcard(filename, file)

def update_chechsum(filename):
    file = read_sdcard(filename)
    lenght = len(file)
    hash_calc = hash_(file[:length-32])
    file = file[:length-32] + hash_calc
    write_sdcard(filename, file)

LOOP = 69

def hash_loop(text):
    hashed = text
    for i in range(LOOP):
        hashed = hash_(hashed)
    return hashed

def encrypt_loop(plaintext, key):
    encrypted = plaintext
    for i in range(LOOP):
        key = hash_(key)
        encrypted = encrypt(encrypted, key)

    return encrypted[:32]

def decrypt_loop(encrypted, key):
    keychain = key
    decrypted = encrypted
    for i in range(LOOP):
        keychain = key
        for i in range(LOOP-i):
            keychain = hash_(keychain)
        decrypted = decrypt(decrypted, keychain)
    
    return decrypted

def verify_password(password, password_coded):
    key_init = "this_is_an_init_this_is_an_init_"
    key = encrypt(password, key_init)
    password_decrypted = decrypt_loop(password_coded, key)
    if (hash_loop(password) == password_decrypted.strip()):
        return True
    else:
        return False

def update_password():
    password_1 = input("Enter your new password: ")
    if (password_1.strip() != password_1):
        print()
        print("ERROR: Password should not contain spaces!")
        open_menu()
    
    password_2 = input("Please re-enter your password: ")
    if (password_1 == password_2):
        password = password_1
    else:
        print()
        print("ERROR: Entered passwords do not match!")
        open_menu()
    
    password_hash = hash_loop(password)
    key_init = "this_is_an_init_this_is_an_init_"
    key = encrypt(password, key_init)
    password_encrypted = encrypt_loop(password_hash, key)
    test = verify_password(password, password_encrypted)
    if test == False:
        print()
        print("ERROR: Fatal Error: Unknown internal error.")
        open_menu()
    try:
        previous_password_encrypted = read_sdcard(".key")
    except OSError as e:
        if e.errno == errno.ENOENT:
            print("No previous credentials detected, creating one .....")
    
    write_sdcard(".key", password_encrypted)
    new_password_encrypted = read_sdcard(".key")
    test = verify_password(password, new_password_encrypted)
    if test == False:
        print()
        print("ERROR: Fatal Error: Unknown internal error.")
        print("Reversing password change ..... ")
        write_sdcard(".key", previous_password_encrypted)
        open_menu()
    else:
        print("Password was successfully changed")
        open_menu()
    


print()
print("Welcome to Passman!")
print()
print("Initializing .....")
print()

import os
#print("System: " + os.uname().sysname + " " + os.uname().release)
print("Hardware: " + os.uname().machine)
print("MicroPython: " + os.uname().version)

print()
import hashlib
import sys
import time

import machine
import sdcard
import uos

CS = machine.Pin(9, machine.Pin.OUT)
spi = machine.SPI(1,baudrate=1000000,polarity=0,phase=0,bits=8,firstbit=machine.SPI.MSB,sck=machine.Pin(10),mosi=machine.Pin(11),miso=machine.Pin(8))
sd = sdcard.SDCard(spi,CS)

print("Mounting SD Card .....")
vfs = uos.VfsFat(sd)
uos.mount(vfs, "/sd")
test_microsd()

from cryptolib import aes
import uos
MODE_CTR = 6
BLOCK_SIZE = 32


#plaintext = input("Enter text to be encrypted: ")


#encrypted = encrypt_loop(plaintext, key)
#print('AES-ECB encrypted:', encrypted )
#print(encrypted[:3])
 

#decrypted = decrypt_loop(encrypted, key)
#print('AES-ECB decrypted:', decrypted.strip())


password = input('Input Credentials: ')

try:
    password_coded = read_sdcard(".key")
except OSError as e:
    if e.errno == errno.ENOENT:
        print("No previous credentials detected!")
        update_password()

auth = verify_password(password, password_coded)


#print("Input Credentials: ", end="")
#password = sys.stdin.readline()
#password = "asdasd"
#password_saved = b'&\x07C\xfcP\xfe;d+4\xaez\t\xcbs\xc9\xe7]\xaf\xabg\xa8\x00/\x1f\xa3g\x91\xca\xd1\xb37'
#print(len(password_saved))
#password_hash = hashlib.sha256(str(password)).digest()
if (auth == True):
    print()
    print("login sucessful")
    print()
    open_menu()
else:
    #time.sleep(60)
    print()
    print("ERROR: Wrong Credentials")
    machine.soft_reset()





