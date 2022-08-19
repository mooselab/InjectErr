from injecterr.how import How

class Injection:
    def __init__(self, name, desc, workload, dataset_size, how: list[How]):
        self.name = name
        self.desc = desc
        self.workload = workload
        self.dataset_size = dataset_size
        self.how: list[How] = how
        
