import os
from pathlib import Path

# Load a simple .envold file without external dependencies
def load_env_file(path=".envold"):
    env_path = Path(path)
    if not env_path.exists():
        return

    for line in env_path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        name, value = stripped.split("=", 1)
        name = name.strip()
        value = value.strip()
        if (
            len(value) >= 2
            and ((value[0] == '"' and value[-1] == '"')
                 or (value[0] == "'" and value[-1] == "'"))
        ):
            value = value[1:-1]
        if name and name not in os.environ:
            os.environ[name] = value

load_env_file()


def get_env(name, default=None):
    value = os.getenv(name, default)
    return value


def parse_comma_list(env_name, default=""):
    value = get_env(env_name, default)
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


DEFAULT_LOGIN = get_env("MT5_LOGIN", "433533897")
DEFAULT_PASSWORD = get_env("MT5_PASSWORD", "Sarbo1998@")
DEFAULT_SERVER = get_env("MT5_SERVER", "Exness-MT5Trial7")

FIB_GEN_SYMBOLS = parse_comma_list(
    "FIB_GEN_SYMBOLS",
    "EURUSDm,GBPUSDm,USDCHFm,EURGBPm,EURCHFm,GBPCHFm"
)

FIB_JPY_SYMBOLS = parse_comma_list(
    "FIB_JPY_SYMBOLS",
    "USDJPYm,GBPJPYm,CHFJPYm,EURJPYm"
)

TIMEFRAMES = parse_comma_list("TIMEFRAMES", "5m,15m,1h,1d")

FIB_KEYS = ["Fib1", "Fib2", "Fib3", "Fib4", "Fib5"]

FIB_GEN_API_URL       = get_env("FIB_GEN_API_URL",       "http://74.208.190.247:8001/signal")
FIB_JPY_API_URL       = get_env("FIB_JPY_API_URL",       "http://74.208.190.247:8002/signal")
RSI_GEN_API_URL       = get_env("RSI_GEN_API_URL",       "http://74.208.190.247:8003")
RSI_JPY_API_URL       = get_env("RSI_JPY_API_URL",       "http://74.208.190.247:8004")
BOLLINGER_GEN_API_URL = get_env("BOLLINGER_GEN_API_URL", "http://74.208.190.247:8005/bollinger")
BOLLINGER_JPY_API_URL = get_env("BOLLINGER_JPY_API_URL", "http://74.208.190.247:8006/bollinger")
MA_GEN_API_URL        = get_env("MA_GEN_API_URL",        "http://74.208.190.247:8007/signals")
MA_JPY_API_URL        = get_env("MA_JPY_API_URL",        "http://74.208.190.247:8008/signals")
COMBINED_API_URL      = get_env("COMBINED_API_URL",      "http://74.208.190.247:8000")
