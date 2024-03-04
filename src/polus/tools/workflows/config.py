"""Config contains project wide-configurations."""

from typing import Any

import yaml  # type: ignore[import]


def str_presenter(dumper: Any, data: Any) -> Any:  # noqa ANN401
    """Configures yaml for dumping multiline strings.

    Ref: https://stackoverflow.com/questions/8640959/how-can-i-control-what-scalar-form-pyyaml-uses-for-my-data.
    """
    if len(data.splitlines()) > 1:  # check for multiline string
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


yaml.add_representer(str, str_presenter)
yaml.representer.SafeRepresenter.add_representer(
    str,
    str_presenter,
)  # to use with safe_dum
