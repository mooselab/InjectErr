from injecterr.injections import Injection
from injecterr.config import Config

from fabric import Connection, ThreadingGroup

def prerun(injection: Injection):
    """Setup Hibench and Hadoop before injecting errors"""

    # Stop the cluster, format namenode and delete previous logs from master
    with Connection(
            Config.MASTER_HOST,
            user=Config.USERNAME,
            connect_kwargs={"key_filename": Config.SSH_KEY_PATH}
        ) as c:

        with c.prefix("source ~/.profile"):
            c.run("stop-all.sh")
            c.run("yes | hdfs namenode -format")
            c.run("rm -rf /home/hadoop/hadoop/logs/*")

    # Delete the datanodes and previous logs from slaves
    # CHECK: JIRA HDFS-107
    with ThreadingGroup(
            *Config.SLAVE_NODES, 
            user=Config.USERNAME,
            connect_kwargs={"key_filename": Config.SSH_KEY_PATH}
        ) as tg:

        tg.run("rm -rf /home/hadoop/dfs/dataNode/*")
        tg.run("rm -rf /home/hadoop/hadoop/logs/*")

    # Start the cluster and prepare the workload
    with Connection(
            Config.MASTER_HOST,
            user=Config.USERNAME,
            connect_kwargs={"key_filename": Config.SSH_KEY_PATH}
        ) as c:

        # delete previous logs 
        with c.prefix("source ~/.profile"):
            c.run("start-all.sh")

            # configure hibench
            with c.cd("/home/hadoop/hibench"):
                # set dataset_size
                c.run(fr"sed -iE 's/^hibench\.scale\.profile.*$/hibench\.scale\.profile {injection.dataset_size}/' conf/hibench.conf")

                # prepare workload
                c.run(f"./bin/workloads/{injection.workload}/prepare/prepare.sh", warn=True)

