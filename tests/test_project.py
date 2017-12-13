"""Project tests."""

from __future__ import unicode_literals


def test_project_read():
    from docknv.project_handler import project_read
    config = project_read("samples/sample01")

    assert "composefiles/sample.yml" in config.composefiles
    assert "standard" in config.schemas
    assert "portainer" in config.schemas["standard"]["services"]
