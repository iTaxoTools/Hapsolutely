from itaxotools.hapsolutely.tasks import convphase, haplodemo, haplostats
from itaxotools.taxi_gui import app
from itaxotools.taxi_gui.main import Main


def test_main(qapp):
    Main()


def test_convphase(qapp):
    task = app.Task.from_module(convphase)
    # task.model()
    task.view()


def test_haplodemo(qapp):
    task = app.Task.from_module(haplodemo)
    # task.model()
    task.view()


def test_haplostats(qapp):
    task = app.Task.from_module(haplostats)
    # task.model()
    task.view()
