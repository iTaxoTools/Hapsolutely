import pytest


def app_factory(argv):
    from itaxotools.hapsolutely import config
    from itaxotools.taxi_gui.app import Application, skin

    app = Application(argv)
    app.set_config(config)
    app.set_skin(skin)
    return app


@pytest.fixture(scope="session")
def qapp_cls():
    return app_factory
