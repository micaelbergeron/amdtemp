#!/usr/bin/env python
import os
import sys
import anyconfig
import re
import time
import importlib
import pdb

from select import poll, POLLIN
from statsd import StatsClient

def import_class(klass):
    (module, klass) = klass.rsplit('.', 1)
    module = importlib.import_module(module)
    return getattr(module, klass)

sample_cfg = """
verbose=false

[statsd]
host="127.0.0.1"
port=8127
prefix="amdtemp.gpu"

[metrics.card0.temp]
path="/sys/class/drm/card0/device/hwmon/hwmon2/temp1_input"

[metrics.card0.pwm]
path="/sys/class/drm/card0/device/hwmon/hwmon2/pwm1"

[metrics.card0.memory]
path="/sys/class/drm/card0/device/pp_dpm_mclk"
parser="amdtemp.parsers.RegexParser"

[metrics.card0.memory.parser_options]
regex='(?P<power_state>\d):\s(?P<current_clck>\d+)[KMG]?hz\s\*'

[metrics.card0.core]
path="/sys/class/drm/card0/device/pp_dpm_sclk"
parser="amdtemp.parsers.RegexParser"

[metrics.card0.core.parser_options]
regex='(?P<power_state>\d):\s(?P<current_clck>\d+)[KMG]?hz\s\*'
"""

VERBOSE=False

class Metric:
    def __init__(self, name, path, parser="amdtemp.parsers.IntParser", parser_options={}):
        self.name = name
        self.path = path
        self.parser = import_class(parser)(name, **parser_options)

    def poll(self):
        with open(self.path, "r") as f:
            raw = f.read()
            if VERBOSE: print("Raw input (%s): %s" % (self.name, raw))
            return self.parser.parse(raw)

    def __str__(self):
        return "Metric (%s), located at %s." % (name, path)


def record(client, fields):
    if (VERBOSE):
        [print("%s: %d" % (metric, value)) for metric, value in fields.items()]

    for metric, value in fields.items():
        client.gauge(metric, value)


def monitor(config):
    statsd_client = StatsClient(**config['statsd'])
    sources = get_sources_list(config)
    while(True):
        with statsd_client.pipeline() as batch:
            for metrics in sources.values():
                if VERBOSE: print("Recording...")
                for m in metrics:
                    fields = m.poll()
                    if VERBOSE: print(fields)
                    record(batch, fields)
        time.sleep(1)

def get_sources_list(config):
    sources = dict()
    for source, metric in config['metrics'].items():
        prefix = lambda name: '.'.join((source, name))
        sources[source] = [Metric(prefix(metric), **config) for metric, config in metric.items()]
    return sources


usage = """
AMDTemp
This program uses the amdgpu sysfs interface to collect gpu information and send
over a statsd server.

Usage: amdtemp <configfile>

A sample config will be output when called without arguments.
"""

def main():
    if len(sys.argv) == 1:
        print(sample_cfg)
        exit(0)

    if re.match(r"(-h|--help|--usage)", sys.argv[1]):
        print(usage)
        exit(1)

    config = anyconfig.load(sys.argv[1])
    VERBOSE = config.get('verbose', False)
    if (VERBOSE): print(config)
    # import pdb; pdb.set_trace()
    monitor(config)
