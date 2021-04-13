import docker


def test_apoc_plugin_installed():
    """Test that APOC plugin is installed."""
    client = docker.from_env()
    db_container = client.containers.get('db')
    res = db_container.exec_run(
        cmd="test -f /var/lib/neo4j/plugins/apoc.jar",
        tty=True
    )
    assert res[0] == 0
