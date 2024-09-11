import json
import os
import uuid
import pickle
import time
import sys

from hyperopt import fmin, hp, STATUS_OK, Trials
import numpy as np
from reservoirpy.hyper._hypersearch import _parse_config
from sqlalchemy import create_engine

import doubletrack
import utils
from experiments import Experiments

MODELS = {
    "doubletrack": doubletrack
}


def gaussian(x, y, r):
    return np.exp(-(x**2 + y**2) / r ** 2)


def objective(args):
    tic = time.time()
    config, sim_args = args
    model = MODELS[config["model"]]
    wl_pump = sim_args.pop("wl_pump")
    sim_result = model.simulate(sim_args, wl_pump, engine=config["matlab"])
    x, y, Es, Ei, Ep = utils.get_modes(sim_result)
    modes = ["signal", "idler", "pump"]
    int_eff_area = utils.interaction_eff_area(sim_result)
    xx, yy = np.meshgrid(x, y)
    E_in = gaussian(xx, yy, config["r_in"][str(wl_pump)]).T
    E_out = gaussian(xx, yy, config["r_out"][str(wl_pump)]).T
    coupling_p = utils.coupling_efficiency(x, y, Ep, x, y, E_in)
    coupling_s = utils.coupling_efficiency(x, y, Es, x, y, E_out)
    coupling_i = utils.coupling_efficiency(x, y, Ei, x, y, E_out)
    toc = time.time()

    result = {
        "int_eff_area": int_eff_area,
        "coupling_s": coupling_s,
        "coupling_i": coupling_i,
        "coupling_p": coupling_p,
        "status": STATUS_OK,
        "start_time": tic,
        "duration": toc - tic,
    }
    for mode in modes:
        for key in ["wl", "neff"]:
            result[key + "_" + mode] = sim_result[mode][key]
    config["db"].record_experiment(sim_result["params"], result)
    result["loss"] = eval(config["loss"])

    return result


def dump(obj, filename):
    ext = os.path.splitext(filename)[-1]
    if ext not in [".pkl", '.pickle']:
        raise NotImplementedError
    else:
        with open(filename, "wb") as f:
            pickle.dump(obj, f)
 

def optimize(config):
    config = _parse_config(config)
    db_path = config.get("db", None)
    trials_path = config.get("trials", None)
    if db_path is None:
        db_path = "sqlite:///{}/{}.db".format("../data", config["exp"])
    if trials_path is None:
        trials_path = "../data/{}.trials".format(config["exp"])
    db = create_engine(db_path)
    config["db"] = Experiments(db)
    if config["continue"] and os.path.isfile(trials_path):
        print("Loading trials from {}".format(trials_path))
        with open(trials_path, "rb") as f:
            trials = pickle.load(f)
    else:
        if os.path.isfile(trials_path):
            print("Overwriting trials in {}".format(trials_path))
        else:
            print("Creating trials at {}".format(trials_path))
        trials = Trials()
    if config.get("seed") is None:
        rs = np.random.default_rng()
    else:
        rs = np.random.default_rng(config["seed"])
    matlab_eng = utils.start_matlab()
    matlab_eng.maxNumCompThreads(1)
    config["matlab"] = matlab_eng
    space = hp.choice(
        "args", [(config, config["hp_space"])]
    )
    best = fmin(
        objective,
        space=space,
        algo=config["hp_method"],
        max_evals=config["hp_max_evals"],
        trials=trials,
        trials_save_file=trials_path,
        rstate=rs
    )
    return best


if __name__ == "__main__":
    # Load config from json file
    if len(sys.argv) > 2:
        raise TypeError("Too many arguments")
    elif len(sys.argv) == 2:
        confpath = sys.argv[1]
    else:
        confpath = "hp_space.json"
    print("Loading configuration from {}".format(confpath))
    with open(confpath, "r") as f:
        config = json.load(f)
    optimize(config)
    
