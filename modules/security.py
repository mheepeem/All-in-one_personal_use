from cryptography.fernet import Fernet

def encrypt_message(message, key):
    cipher_suite = Fernet(key)
    encrypted_message = cipher_suite.encrypt(message.encode('utf-8'))
    return encrypted_message.decode('utf-8')

def decrypt_message(encrypted_message, key):
    cipher_suite = Fernet(key)
    decrypted_message = cipher_suite.decrypt(encrypted_message.encode())
    return decrypted_message.decode('utf-8')

# For something like JSON file or similar structure
def encrypt_kv_value_only(data, key):
    if isinstance(data, str): # Base case
        msg = encrypt_message(data, key)
        return msg

    elif isinstance(data, dict):
        for k,v in data.items():
            new_val = encrypt_kv_value_only(v, key)
            if new_val:
                data[k] = new_val
    elif isinstance(data, list):
        temp = []
        for i in data:
            temp.append(encrypt_kv_value_only(i, key))
        if temp != [None]:
            return temp

# For something like JSON file or similar structure
def decrypt_kv_value_only(data, key):
    if isinstance(data, str): # Base case
        msg = decrypt_message(data, key)
        return msg

    elif isinstance(data, dict):
        for k,v in data.items():
            new_val = decrypt_kv_value_only(v, key)
            if new_val:
                data[k] = new_val
    elif isinstance(data, list):
        temp = []
        for i in data:
            temp.append(decrypt_kv_value_only(i, key))
        if temp != [None]:
            return temp


