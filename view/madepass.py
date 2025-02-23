import secrets
import string

class SecurePasswordGenerator:
    def __init__(self, length=12, use_digits=True, use_special_chars=True):
        self.length = length
        self.use_digits = use_digits
        self.use_special_chars = use_special_chars

    def generate_password(self):
        characters = string.ascii_letters  # Includes uppercase and lowercase letters
        
        if self.use_digits:
            characters += string.digits
        
        if self.use_special_chars:
            characters += string.punctuation
        
        password = ''.join(secrets.choice(characters) for _ in range(self.length))
        return password
