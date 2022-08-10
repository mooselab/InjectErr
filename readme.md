# InjectErr

A simple python framework to inject errors while running HiBench workloads on Hadoop and collecting logs

### Installation

InjectErr uses poetry:

```bash
poetry shell # optional, only use it if you want to install this in a venv
poetry install
```

### Usage

First, let's understand the `injections.yml` file

```yaml
username: hadoop # Username of all the nodes
master_host: node-master # Hostname of master nodes
slave_nodes: # Hostnames of slave nodes
  - node1
  - node2
ssh_key_path: /home/wantguns/.ssh/id_ed25519 # path to SSH priv key for logging in to all the nodes

injections:
  fill_ram: # Injection name
    desc: "Fill RAM completely" # Injection Desc
    dataset_size: small # Hibench profile scale, can be [tiny, small, huge, etc] 
    workload: micro/wordcount # Hibench workload to run
    waittime: 10 # Time to wait before injecting the error
    how: | # Shell commands which perform the injection
      timeout -k 95 90 cat /dev/random > /dev/shm/fillitup
```

To run InjectErr, simply execute the installed script:

```bash
$ injecterr
```

It will read the `injections.yml` file from the current working directory,
perform the injections and then finally copy logs from all the nodes to a
local folder named `logs` and label them.
