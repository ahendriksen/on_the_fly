from pathlib import Path
import sys
import os
from datetime import datetime


def print_run(ex, path):
    run = ex.current_run
    id = run._id
    if id is None:
        id = "no_id"

    path = Path(path)
    if path.is_dir():
        path = path / f"README_{id}"

    # Info dictionaries
    host_info = run.host_info
    # {'hostname': 'sipsey.ci.cwi.nl',
    #  'os': ['Linux',
    #   'Linux-4.20.6-100.fc28.x86_64-x86_64-with-fedora-28-Twenty_Eight'],
    #  'python_version': '3.6.8',
    #  'cpu': 'Intel(R) Core(TM) i7-7700K CPU @ 4.20GHz',
    #  'gpus': {'gpus': [{'model': 'GeForce GTX 1070',
    #     'total_memory': 8119,
    #     'persistence_mode': False}],
    #   'driver_version': '415.27'},
    #  'ENV': {}}
    experiment_info = run.experiment_info
    # {'name': 'Test sacred',
    #  'base_dir': '/export/scratch1/hendriks/projects/fact_fiction/fact_fiction',
    #  'sources': [('test_sacred.py', '166e98a4abc1c62cb95e85383010bcbe')],
    #  'dependencies': ['ipython==7.4.0', 'numpy==1.15.4', 'sacred==0.7.4'],
    #  'repositories': [],
    #  'mainfile': 'test_sacred.py'}

    meta_info = run.meta_info
    # {'command': 'main',
    #  'options': {'--sql': None,
    #   '--name': None,
    #   '--beat_interval': None,
    #   '--capture': None,
    #   '--priority': None,
    #   '--mongo_db': None,
    #   '--loglevel': None,
    #   '--debug': False,
    #   '--pdb': False,
    #   '--enforce_clean': False,
    #   '--unobserved': False,
    #   '--tiny_db': None,
    #   '--force': False,
    #   '--print_config': False,
    #   '--comment': None,
    #   '--file_storage': None,
    #   '--queue': False,
    #   '--help': False,
    #   'with': True,
    #   'UPDATE': ['param1=10'],
    #   'help': False,
    #   'COMMAND': None}}

    updated_parameters = meta_info.get("options", {}).get("UPDATE", [])

    name = experiment_info.get("name", "")
    command = meta_info.get("command", "")

    command_line = " ".join(sys.argv)
    cwd = os.getcwd()
    hostname = host_info.get("hostname", "")

    with open(path, "w") as f:
        now = datetime.now()
        print("--------------------------------------------------", file=f)
        print(f"-- experiment   ({now:%Y-%m-%d %H:%M:%S})", file=f)
        print("--------------------------------------------------", file=f)

        print(f"{name} - {command} ({id})", file=f)
        for u in updated_parameters:
            print(f"    {u}", file=f)
        print("", file=f)

        print("--------------------------------------------------", file=f)
        print(f"-- command line", file=f)
        print("--------------------------------------------------", file=f)
        print(f"{hostname} {cwd}", file=f)
        print(f"$ {command_line}", file=f)

        print("", file=f)
        info_dicts = [
            ("configuration", run.config),
            ("host_info", host_info),
            ("experiment_info", experiment_info),
            ("meta_info", meta_info),
        ]

        for name, d in info_dicts:
            print("", file=f)
            print("--------------------------------------------------", file=f)
            print(f"-- {name}", file=f)
            print("--------------------------------------------------", file=f)
            for k, v in d.items():
                print(f"{k:<20} : {v}", file=f)
