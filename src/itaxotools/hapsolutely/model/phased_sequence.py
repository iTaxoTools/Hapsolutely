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

from typing import Generic, TypeVar

from itaxotools.common.utility import AttrDict, DecoratorDict
from itaxotools.taxi_gui.model.common import Object, Property
from itaxotools.taxi_gui.types import FileInfo

FileInfoType = TypeVar('FileInfoType', bound=FileInfo)

models = DecoratorDict[FileInfo, Object]()


class PhasedSequenceModel(Object, Generic[FileInfoType]):
    info = Property(FileInfo, None)
    is_phasing_optional = Property(bool, False)

    def __init__(self, info: FileInfo, is_phasing_optional=False):
        super().__init__()
        self.info = info
        self.is_phasing_optional = is_phasing_optional
        self.name = f'Phased sequences from {info.path.name}'

    def __repr__(self):
        return f'{".".join(self._get_name_chain())}({repr(self.name)})'

    def is_valid(self):
        return True

    def as_dict(self):
        return AttrDict({p.key: p.value for p in self.properties})

    @classmethod
    def from_file_info(cls, info: FileInfoType, is_phasing_optional=False) -> PhasedSequenceModel[FileInfoType]:
        if not type(info) in models:
            raise Exception(f'No suitable {cls.__name__} for info: {info}')
        return models[type(info)](info, is_phasing_optional)


@models(FileInfo.Fasta)
class PhasedFasta(PhasedSequenceModel):
    has_subsets = Property(bool, False)
    subset_separator = Property(str, '|')
    parse_organism = Property(bool, False)

    def __init__(self, info: FileInfo.Fasta, is_phasing_optional=False):
        super().__init__(info, is_phasing_optional)
        self.has_subsets = info.has_subsets
        self.subset_separator = info.subset_separator
        self.parse_organism = info.has_subsets


@models(FileInfo.Tabfile)
class PhasedTabfile(PhasedSequenceModel):
    index_column = Property(int, -1)
    sequence_column = Property(int, -1)
    allele_column = Property(int, -1)

    def __init__(self, info: FileInfo.Tabfile, is_phasing_optional=False):
        super().__init__(info, is_phasing_optional)
        self.index_column = self._header_get(info.headers, info.header_individuals)
        self.sequence_column = self._header_get(info.headers, info.header_sequences)
        self.allele_column = self._header_get(info.headers, 'allele')

    @staticmethod
    def _header_get(headers: list[str], field: str):
        try:
            return headers.index(field)
        except ValueError:
            return -1

    def is_valid(self):
        if self.index_column < 0:
            return False
        if self.sequence_column < 0:
            return False
        if self.allele_column < 0 and not self.is_phasing_optional:
            return False
        if len(set([self.index_column, self.sequence_column, self.allele_column])) < 3:
            return False
        return True
