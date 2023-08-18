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

from typing import TextIO

import yaml
from itaxotools.haplostats import HaploStats
from itaxotools.taxi2.sequences import Sequences


def _dict_representer(dumper, data):
    return dumper.represent_mapping('tag:yaml.org,2002:map', data.items())


yaml.add_representer(dict, _dict_representer)


def _yamlify(data, title: str = None) -> str:
    if title:
        data = {title: data}
    return yaml.dump(data, default_flow_style=False)


def _separate(file: TextIO):
    print('---\n', file=file)


def write_all_stats(stats: HaploStats, file: TextIO):

    print(file=file)

    data = stats.get_haplotypes()
    print(_yamlify(data, 'Haplotype sequences'), file=file)
    _separate(file=file)

    data = stats.get_haplotypes_per_subset()
    print(_yamlify(data, 'Haplotypes per species'), file=file)
    _separate(file=file)

    data = stats.get_haplotypes_shared_between_subsets()
    print(_yamlify(data, 'Haplotypes shared between species'), file=file)
    _separate(file=file)

    data = stats.get_fields_of_recombination()
    print(_yamlify(data, 'Fields of recombination'), file=file)
    _separate(file=file)

    data = stats.get_subsets_per_field_of_recombination()
    print(_yamlify(data, 'Species count per FOR'), file=file)
    _separate(file=file)

    data = stats.get_fields_of_recombination_per_subset()
    print(_yamlify(data, 'FOR count per species'), file=file)
    _separate(file=file)

    data = stats.get_fields_of_recombination_shared_between_subsets()
    print(_yamlify(data, 'FORs shared between species'), file=file)
    _separate(file=file)

    data = stats.get_dataset_sizes()
    print(_yamlify(data, 'Dataset size'), file=file)
