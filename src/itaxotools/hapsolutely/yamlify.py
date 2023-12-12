# -----------------------------------------------------------------------------
# Hapsolutely - Reconstruct haplotypes and produce genealogy graphs
# Copyright (C) 2023  Patmanidis Stefanos
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# -----------------------------------------------------------------------------

from __future__ import annotations

import yaml


def _dict_representer(dumper, data):
    return dumper.represent_mapping("tag:yaml.org,2002:map", data.items())


yaml.add_representer(dict, _dict_representer)


def dump(data) -> str:
    return yaml.dump(data, default_flow_style=False)


def yamlify(data, title: str = None) -> str:
    if title:
        data = {title: data}
    return dump(data)
