```shell
import confspawn.spawn as spwn

from pathlib import Path


def z(env, var_key):
    cf_path = Path("tests/confs/sample_config.toml")
    spwn.print_env_var(cf_path, env, var_key)
```

```shell
#!/bin/sh
poetry run python -c "from test import z; z('$1', '$2')"
```