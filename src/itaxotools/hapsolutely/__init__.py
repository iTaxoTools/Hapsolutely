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

"""GUI entry point"""


def find_task():
    from itaxotools.taxi_gui.app import model

    from .tasks.haplostats.model import Model as Hapsolutely

    index = model.items.find_task(Hapsolutely)
    item = model.items.data(index, role=model.items.ItemRole)
    return item.object


def run():
    """
    Show the Taxi2 window and enter the main event loop.
    Imports are done locally to optimize multiprocessing.
    """

    from argparse import ArgumentParser
    from pathlib import Path

    from itaxotools.taxi_gui.app import Application, skin
    from itaxotools.taxi_gui.main import Main

    from . import config

    app = Application()
    app.set_config(config)
    app.set_skin(skin)

    parser = ArgumentParser(description="Hapsolutely")
    parser.add_argument("input", nargs="?", type=str, help="Path to input file")
    args = parser.parse_args()

    main = Main()
    main.widgets.header.toolLogo.setFixedWidth(208)
    main.resize(780, 500)
    main.show()

    if args.input:
        model = find_task()
        model.open(Path(args.input))

    app.exec()
