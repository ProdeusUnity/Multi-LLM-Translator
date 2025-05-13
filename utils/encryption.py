import os
import base64
import hashlib
import platform
import getpass
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


# Global encryption key
_encryption_key = None


def initialize_encryption():
    """Initialize the encryption system."""
    global _encryption_key
    
    # Generate a device-specific key
    machine_id = _get_machine_id()
    username = getpass.getuser()
    
    # Create a deterministic but unique salt for this user/machine
    salt_input = f"{machine_id}:{username}:translator_app_salt"
    salt = hashlib.sha256(salt_input.encode()).digest()[:16]
    
    # Create a key derivation function
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    
    # Derive the key
    key_material = f"{machine_id}:{username}:translator_app_key"
    key = base64.urlsafe_b64encode(kdf.derive(key_material.encode()))
    
    # Create the Fernet cipher
    _encryption_key = key


def _get_machine_id():
    """Get a unique identifier for the current machine."""
    system = platform.system()
    
    if system == "Windows":
        # Use Windows registry to get machine ID
        try:
            import winreg
            registry = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
            key = winreg.OpenKey(registry, r"SOFTWARE\Microsoft\Cryptography")
            machine_guid, _ = winreg.QueryValueEx(key, "MachineGuid")
            winreg.CloseKey(key)
            return machine_guid
        except:
            # Fallback to hostname
            return platform.node()
    
    elif system == "Darwin":  # macOS
        try:
            # Try to get hardware UUID
            import subprocess
            result = subprocess.run(
                ["system_profiler", "SPHardwareDataType"],
                capture_output=True,
                text=True
            )
            for line in result.stdout.split('\n'):
                if "Hardware UUID" in line:
                    return line.split(":")[1].strip()
            # Fallback to hostname
            return platform.node()
        except:
            return platform.node()
    
    else:  # Linux and others
        try:
            # Try to get machine-id
            with open("/etc/machine-id", "r") as f:
                return f.read().strip()
        except:
            # Try to get dbus machine ID
            try:
                with open("/var/lib/dbus/machine-id", "r") as f:
                    return f.read().strip()
            except:
                # Fallback to hostname
                return platform.node()


def encrypt_data(data):
    """Encrypt data using the initialized key."""
    global _encryption_key
    
    if _encryption_key is None:
        initialize_encryption()
    
    f = Fernet(_encryption_key)
    return f.encrypt(data.encode())


def decrypt_data(data):
    """Decrypt data using the initialized key."""
    global _encryption_key
    
    if _encryption_key is None:
        initialize_encryption()
    
    f = Fernet(_encryption_key)
    return f.decrypt(data).decode()
