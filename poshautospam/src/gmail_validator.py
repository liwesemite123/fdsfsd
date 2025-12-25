import ctypes
import json
import platform
from pathlib import Path
from typing import Any


class EmailValidator:
    def __init__(self, lib_path: str | None = None) -> None:
        if lib_path is None:
            system = platform.system()
            if system == "Windows":
                lib_path = "./dll/validator.dll"
            else:
                lib_path = "./dll/validator.so"
        lib_file = Path(lib_path)
        if not lib_file.exists():
            msg = f"Library not found: {lib_path}"
            raise FileNotFoundError(msg)

        self.lib = ctypes.CDLL(str(lib_file))

        self.lib.ValidateEmailExport.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self.lib.ValidateEmailExport.restype = ctypes.c_char_p

        self.lib.FreeString.argtypes = [ctypes.c_char_p]
        self.lib.FreeString.restype = None

        self.lib.GetVersion.argtypes = []
        self.lib.GetVersion.restype = ctypes.c_char_p

    def validate(self, email: str, proxy_url: str | None = None) -> dict[str, Any]:
        email_bytes = email.encode("utf-8")
        proxy_bytes = proxy_url.encode("utf-8") if proxy_url else b""

        result_ptr = self.lib.ValidateEmailExport(email_bytes, proxy_bytes)

        result_json = ctypes.string_at(result_ptr).decode("utf-8")

        return json.loads(result_json)


    def get_version(self) -> str:
        version_ptr = self.lib.GetVersion()
        return ctypes.string_at(version_ptr).decode("utf-8")
