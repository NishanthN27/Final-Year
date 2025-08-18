# src/interview_system/auth/password_utils.py

import bcrypt

def hash_password(password: str) -> str:
    """
    Hashes a plain-text password using bcrypt.
    
    Args:
        password: The plain-text password to hash.
        
    Returns:
        A string containing the hashed password.
    """
    # Generate a salt and hash the password
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against a stored bcrypt hash.
    
    Args:
        plain_password: The plain-text password from a login attempt.
        hashed_password: The stored hashed password from the database.
        
    Returns:
        True if the passwords match, False otherwise.
    """
    password_bytes = plain_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_password_bytes)