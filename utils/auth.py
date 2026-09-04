"""
User Authentication & Encrypted State Management
Each user gets an encrypted profile directory with their data.
"""
import os
import json
import hashlib
import secrets
from pathlib import Path
from cryptography.fernet import Fernet
from datetime import datetime

# Base directory for all user data
DATA_DIR = Path(__file__).parent.parent / ".userdata"
DATA_DIR.mkdir(exist_ok=True)

# Master key for encryption (stored in app, derived from a salt)
# In production, this would be a proper KMS. For now, we use a fixed salt.
_SALT = b"airbud-salt-2026"
_MASTER_KEY = hashlib.sha256(_SALT).digest()[:32]
# Generate a proper Fernet key (32 bytes URL-safe base64)
FERNET_KEY = Fernet.generate_key()


def _get_user_dir(username: str) -> Path:
    """Get the user's data directory."""
    user_dir = DATA_DIR / username
    user_dir.mkdir(exist_ok=True)
    return user_dir


def _get_user_store_path(username: str) -> Path:
    """Get the path to the user's encrypted state file."""
    return _get_user_dir(username) / "state.enc"


def _get_user_uploads_dir(username: str) -> Path:
    """Get the user's uploads directory."""
    uploads_dir = _get_user_dir(username) / "uploads"
    uploads_dir.mkdir(exist_ok=True)
    return uploads_dir


def hash_password(password: str, salt: str = None) -> tuple:
    """Hash a password with a random salt. Returns (hashed_password, salt)."""
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
    return hashed.hex(), salt


def verify_password(password: str, hashed: str, salt: str) -> bool:
    """Verify a password against a stored hash."""
    expected, _ = hash_password(password, salt)
    return expected == hashed


def create_user(username: str, full_name: str, password: str, email: str = "") -> dict:
    """
    Create a new user account.
    Returns user profile dict.
    """
    if list(DATA_DIR.glob(username)):
        raise ValueError(f"Username '{username}' already exists.")

    user_dir = _get_user_dir(username)
    hashed, salt = hash_password(password)

    profile = {
        "username": username,
        "full_name": full_name,
        "email": email,
        "password_hash": hashed,
        "password_salt": salt,
        "created_at": datetime.now().isoformat(),
        "last_login": datetime.now().isoformat(),
    }

    # Save profile (not encrypted — contains no sensitive data beyond hash)
    profile_path = user_dir / "profile.json"
    profile_path.write_text(json.dumps(profile, indent=2))

    # Initialize empty encrypted state
    save_user_state(username, {})

    return profile


def login_user(username: str, password: str) -> dict:
    """
    Authenticate a user. Returns profile dict on success.
    Raises ValueError on failure.
    """
    profile_path = DATA_DIR / username / "profile.json"
    if not profile_path.exists():
        raise ValueError("Invalid username or password.")

    profile = json.loads(profile_path.read_text())

    if not verify_password(password, profile["password_hash"], profile["password_salt"]):
        raise ValueError("Invalid username or password.")

    # Update last login
    profile["last_login"] = datetime.now().isoformat()
    profile_path.write_text(json.dumps(profile, indent=2))

    return profile


def list_users() -> list:
    """List all registered usernames."""
    users = []
    for user_dir in DATA_DIR.iterdir():
        if user_dir.is_dir() and (user_dir / "profile.json").exists():
            profile = json.loads((user_dir / "profile.json").read_text())
            users.append({
                "username": profile["username"],
                "full_name": profile["full_name"],
                "created_at": profile["created_at"],
            })
    return users


def encrypt_data(data: dict) -> bytes:
    """Encrypt a dict as bytes."""
    fernet = Fernet(FERNET_KEY)
    return fernet.encrypt(json.dumps(data).encode())


def decrypt_data(data_bytes: bytes) -> dict:
    """Decrypt bytes back to a dict."""
    fernet = Fernet(FERNET_KEY)
    return json.loads(fernet.decrypt(data_bytes).decode())


def save_user_state(username: str, state: dict):
    """Save encrypted user state."""
    store_path = _get_user_store_path(username)
    encrypted = encrypt_data(state)
    store_path.write_bytes(encrypted)


def load_user_state(username: str) -> dict:
    """Load encrypted user state. Returns empty dict if not found."""
    store_path = _get_user_store_path(username)
    if not store_path.exists():
        return {}
    try:
        return decrypt_data(store_path.read_bytes())
    except Exception:
        return {}


def save_user_file(username: str, filename: str, file_bytes: bytes) -> str:
    """Save a user's uploaded file. Returns the file path."""
    uploads_dir = _get_user_uploads_dir(username)
    filepath = uploads_dir / filename
    filepath.write_bytes(file_bytes)
    return str(filepath)


def get_user_files(username: str) -> list:
    """List all files in user's uploads directory."""
    uploads_dir = _get_user_uploads_dir(username)
    if not uploads_dir.exists():
        return []
    files = []
    for f in uploads_dir.iterdir():
        if f.is_file():
            files.append({
                "filename": f.name,
                "filepath": str(f),
                "size": f.stat().st_size,
                "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
            })
    return files
