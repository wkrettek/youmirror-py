import pytest
from youmirror.configurer import *
from pathlib import Path

config_path = Path("./testconfig.toml")

def test_new_config():
    new_config(config_path, '.')
    assert config_path.is_file()

    from youmirror.template import template
    config = load_config(config_path)
    config_path.unlink()    # Clean up

if __name__ == "__main__":
    test_new_config()