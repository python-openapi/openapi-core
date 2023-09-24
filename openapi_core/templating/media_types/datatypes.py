from collections import namedtuple
from dataclasses import dataclass
from typing import Mapping
from typing import Optional

MediaType = namedtuple("MediaType", ["mime_type", "parameters", "media_type"])
