import time
from multiprocessing import Process

import yaml
from fabric import Connection

from injecterr.injections import Injection
from injecterr.config import Config
from injecterr.pre import prerun
from injecterr.post import postrun
from injecterr.how import How

def parse_injections(service_file):
    """Parses the injections.yaml file and returns a list of injections"""

    injections: list[Injection] = []

    with open(service_file) as f:
        parsed = yaml.safe_load(f)

        Config.USERNAME = parsed["username"]
        Config.MASTER_HOST = parsed["master_host"]
        Config.SLAVE_NODES = parsed["slave_nodes"]
        Config.SSH_KEY_PATH = parsed["ssh_key_path"]

        for iname, idata in parsed["injections"].items():
            injections.append(
                Injection(
                    name=iname, 
                    desc=idata["desc"], 
                    workload=idata["workload"], 
                    dataset_size=idata["dataset_size"], 
                    how=[How(h["host"], h["waittime"], h["run"]) for h in idata["how"]]
                )
            )

    return injections

def start_workload(injection: Injection):
    with Connection(
            Config.MASTER_HOST,
            user=Config.USERNAME,
            connect_kwargs={"key_filename": Config.SSH_KEY_PATH}
        ) as c:

        # start workload
        with c.prefix("source ~/.profile"):
            with c.cd("/home/hadoop/hibench"):
                c.run(f"./bin/workloads/{injection.workload}/hadoop/run.sh", warn=True)


def perform_injection(how: How):
    """Performs injections"""

    time.sleep(how.waittime)

    with Connection(
            how.host,
            user=Config.USERNAME,
            connect_kwargs={"key_filename": Config.SSH_KEY_PATH}
        ) as c:

        with c.prefix("source ~/.profile"):
            for command in how.run:
                c.run(command, warn=True)


def parallely_execute(tasks):
    """Parallely executes functions passed in the list"""

    running_tasks = [Process(target=t[0], args=(t[1],)) for t in tasks]
    for running_task in running_tasks:
        running_task.start()
    for running_task in running_tasks:
        running_task.join()


def main():
    # parse injections
    injections = parse_injections("injections.yml")

    # perform injections
    for injection in injections:

        # Populate parallel tasks:
        tasks = [[ start_workload, injection ]]
        for h in injection.how:
            tasks.append([ perform_injection, h ])

        prerun(injection)
        parallely_execute(tasks)
        postrun(injection)


if __name__ == '__main__':
    main()
