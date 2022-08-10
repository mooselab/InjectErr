import os
import time

from injecterr.injections import Injection
from injecterr.config import Config

from fabric import Connection

def postrun(injection: Injection):
    """Collect logs after the error injection"""

    time_now = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime())
    remote_tarball = f"/tmp/logs_{time_now}.tar.gz"
    local_tarball = "logs.tar.gz"
    logpath = os.path.join(Config.LOGPATH, injection.name + time_now)
    os.makedirs(logpath, exist_ok=True)

    nodes = Config.SLAVE_NODES + [Config.MASTER_HOST]

    for node in nodes:
        with Connection(
                node,
                user=Config.USERNAME,
                connect_kwargs={"key_filename": Config.SSH_KEY_PATH}
            ) as c:

            # Tar the logs up and copy it to local
            with c.cd("/home/hadoop/hadoop"):
                node_logpath = os.path.join(logpath, node)
                os.makedirs(node_logpath, exist_ok=True)
                c.run(f"tar czf {remote_tarball} logs")
                c.get(f"{remote_tarball}", local=f"{node_logpath}/{local_tarball}")
