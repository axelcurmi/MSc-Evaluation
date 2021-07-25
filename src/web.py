from time import time, sleep

import threading

import requests
import sshtunnel

class SSHTunnel(threading.Thread):
    def __init__(self, config, add_secube_metrics = None):
        self.should_stop = threading.Event()
        self.config = config
        self.add_secube_metrics = add_secube_metrics

        threading.Thread.__init__(self)
        self.setDaemon(True)
    
    def run(self):
        server = sshtunnel.SSHTunnelForwarder(
            self.config["ssh"]["host"],
            ssh_username=self.config["ssh"]["username"],
            ssh_password=self.config["ssh"]["password"],
            remote_bind_address=(
                self.config["web_remote"]["host"],
                self.config["web_remote"]["port"]),
            local_bind_address=(
                self.config["web_local"]["host"],
                self.config["web_local"]["port"])
        )

        server.start()
        while not self.should_stop.is_set():
            pass
        if self.add_secube_metrics:
            self.add_secube_metrics(server._transport.pysecube.get_metrics())
        server.stop()

def run(**kwargs):
    config = kwargs["config"]
    experiment = kwargs["experiment"]
    with_secube = "with_secube" in kwargs and kwargs["with_secube"]

    save_timing = None if "save_timing" not in kwargs \
        else kwargs["save_timing"]
    add_secube_metrics = None if "add_secube_metrics" not in kwargs \
        else kwargs["add_secube_metrics"]

    ssh_tunnel = SSHTunnel(config,
        add_secube_metrics if with_secube and add_secube_metrics\
        else None)

    ssh_tunnel.start() # Start the SSH tunnel

    start_time = time()

    for _ in range(experiment["load_count"]):
        response = requests.get("http://{}:{}/{}".format(
            config["web_local"]["host"],
            config["web_local"]["port"],
            experiment["page"]
        ))
        assert(len(response.content) > 0)

    end_time = time()
    ssh_tunnel.should_stop.set() # Stop the SSH tunnel
    
    if with_secube:
        sleep(0.5)

    if save_timing:
        save_timing([start_time, end_time, end_time - start_time])
