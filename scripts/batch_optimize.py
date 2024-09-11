import copy
import json
import sys

from joblib import Parallel, delayed
import numpy as np

from optimize import optimize


if __name__ == "__main__":
    if len(sys.argv) > 2:
        raise TypeError("Too many arguments")
    elif len(sys.argv) == 2:
        confpath = sys.argv[1]
    else:
        confpath = "hp_space.json"
    print("Loading search space template from {}".format(confpath))
    with open(confpath, "r") as f:
        default_config = json.load(f)
    dns = np.arange(-0.001, -0.01, -0.001)
    dns = np.r_[dns, -0.01]
    
    configs = []
    for dn in dns:
        config = copy.deepcopy(default_config)
        config["hp_space"]["dn_track"][1:] = [round(dn, 3)]
        configs.append(config)
    n_jobs = min(len(configs), 6)
    Parallel(n_jobs=n_jobs)(delayed(optimize)(config) for config in configs)
