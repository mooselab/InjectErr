import time
from multiprocessing import Process

import yaml
from fabric import Connection

from injecterr.injections import Injection
from injecterr.config import Config
from injecterr.pre import prerun
from injecterr.post import postrun

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
                    waittime=idata["waittime"], 
                    how=idata["how"].split('\n')
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


def perform_injection(injection: Injection):
    """Performs injections"""

    time.sleep(injection.waittime)

    with Connection(
            Config.MASTER_HOST,
            user=Config.USERNAME,
            connect_kwargs={"key_filename": Config.SSH_KEY_PATH}
        ) as c:
        for command in injection.how:
            c.run(command, warn=True)


def parallely_execute(tasks):
    """Parallely executes functions passed in the dict"""

    running_tasks = [Process(target=func, args=(args,)) for func, args in tasks.items()]
    for running_task in running_tasks:
        running_task.start()
    for running_task in running_tasks:
        running_task.join()


def main():
    # parse injections
    injections = parse_injections("injections.yml")

    # perform injections
    for injection in injections:
        prerun(injection)
        parallely_execute({ 
          start_workload: injection, 
          perform_injection: injection
        })
        postrun(injection)


if __name__ == '__main__':
    main()
