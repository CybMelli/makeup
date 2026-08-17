from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
import base64
from hashlib import sha256

def pad(text):
    pad_len=16-(len(text)%16)
    return text + chr(pad_len) * pad_len

def unpad(text):
    pad_len=ord(text[-1])
    return text[:-pad_len]

def encrypt_aes(plain_text,key):
    iv= get_random_bytes(16)
    cipher=AES.new(key,AES.MODE_CBC,iv)

    #pad the text and encrypt
    encrypted = cipher.encrypt(pad(plain_text).encode())

    #Return IV + encrypt 
    return base64.b64encode(iv+encrypted).decode('utf-8')

#function to decrypt aes encrypted text
def decrypted_aes (encrypted_text,key):
    try:
        encrypted_data=base64.b64decode(encrypted_text)
        iv= encrypted_data[:16]
        encrypted_message=encrypted_data[16:]
        cipher = AES.new(key,AES.MODE_CBC, iv)
        decrypted= cipher.decrypt(encrypted_message).decode('utf-8')
        return unpad(decrypted)
    except Exception:
        return None

#Main execution

if __name__ == "__main__":
    password = "mysecurepassowrd"
    key=sha256(password.encode()).digest()
    user_input= input("Enter a message to encrypt or an encrypted message to decrypt:")

decrypted_message= decrypted_aes(user_input,key)
if decrypted_message is not None:
    print("\nDecrypted message:",decrypted_message)
else:
    encrypted_message=encrypt_aes(user_input,key)
    print("\nEncrypted message:",encrypted_message)
