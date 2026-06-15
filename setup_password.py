"""
Run this script once to generate your hashed password.
Copy the output into your .env file as ADMIN_PASSWORD_HASH.

Usage:
    python setup_password.py
"""
from werkzeug.security import generate_password_hash
import getpass

print("=" * 50)
print("  Jaundice Tracker — Password Setup")
print("=" * 50)

password = getpass.getpass("Enter your desired password: ")
confirm  = getpass.getpass("Confirm password: ")

if password != confirm:
    print("\n❌ Passwords do not match. Try again.")
    exit(1)

hashed = generate_password_hash(password)

print("\n✅ Password hash generated successfully!")
print("\nAdd these lines to your .env file:\n")
print(f"ADMIN_USERNAME=admin")
print(f"ADMIN_PASSWORD_HASH={hashed}")
print("\n⚠️  Never commit your .env file to git!")
