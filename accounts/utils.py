from django.contrib.auth.hashers import make_password, check_password

def hash_pin(pin: str) -> str:
    return make_password(pin)

def verify_pin(pin: str, hashed: str) -> bool:
    return check_password(pin, hashed)