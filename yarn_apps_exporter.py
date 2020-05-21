#!/usr/bin/env python

from collections import defaultdict
from operator import itemgetter
from time import sleep
import argparse
import json
import re
import logging
import os

try:
    from urllib.request import Request, urlopen  # Python 3
except ImportError:
    from urllib2 import Request, urlopen  # noqa, Python 2


def write_resource_usage(f, apps):
    key = itemgetter("name", "user", "queue")
    for metric, metric_type in [
        ("allocatedVCores", "gauge"),
        ("allocatedMB", "gauge"),
        ("vcoreSeconds", "counter"),
    ]:
        data = defaultdict(lambda: 0)
        for i in apps:
            data[key(i)] += i[metric]
        f.write(
            "# HELP yarn_apps_%s YARN %s per App/User/Queue\n" % (metric, metric)
        )
        f.write("# TYPE yarn_apps_%s %s\n" % (metric, metric_type))
        for (name, user, queue), value in data.items():
            f.write(
                'yarn_apps_%s{name="%s", user="%s", queue="%s"} %s\n'
                % (metric, name, user, queue, value)
            )


def write_count_by_state(f, apps):
    key = itemgetter("name", "user", "queue", "state")
    data = defaultdict(lambda: 0)
    for i in apps:
        data[key(i)] += 1
    f.write(
        "# HELP yarn_apps_by_state YARN applications count by App/User/Queue/State\n"
    )
    f.write("# TYPE yarn_apps_by_state gauge\n")
    for (name, user, queue, state), value in data.items():
        f.write(
            'yarn_apps_by_state{name="%s", user="%s", queue="%s", state="%s"} %s\n'
            % (name, user, queue, state, value)
        )


def tick(resource_manager_url, fname, patterns):

    request = Request(resource_manager_url + "/ws/v1/cluster/apps")
    request.add_header("Accept", "application/json")
    response = urlopen(request)
    apps = json.load(response)["apps"]["app"]

    for pattern, replacement in patterns:
        for app in apps:
            app["name"] = pattern.sub(replacement, app["name"])

    with open(fname + ".swp", "w") as f:
        write_resource_usage(f, [i for i in apps if i["state"] == "RUNNING"])
        write_count_by_state(f, apps)

    os.rename(fname + ".swp", fname)


def loop(args):
    if args.patterns is not None:
        with open(args.patterns) as f:
            patterns = [
                (re.compile(pattern.rstrip('\n')), replacement.rstrip('\n'))
                for replacement, pattern in zip(f, f)
            ]
    else:
        patterns = []
    while True:
        try:
            tick(args.resource_manager_url, args.output_file, patterns)
            sleep(10)
        except KeyboardInterrupt:
            break


def main():
    parser = argparse.ArgumentParser(
        description="Write YARN apps metrics for node_exporter textfile",
    )
    parser.add_argument("resource_manager_url")
    parser.add_argument(
        "--output-file",
        default="/opt/prometheus/exporters/node_exporter_current/yarn_apps.prom",
    )
    parser.add_argument("--patterns", help="file containing replacement patterns")
    args = parser.parse_args()
    loop(args)


if __name__ == "__main__":
    main()
