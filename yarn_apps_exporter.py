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


UUID_RE = re.compile("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")


def tick(resource_manager_url, fname):

    request = Request(resource_manager_url + "/ws/v1/cluster/apps?states=RUNNING")
    request.add_header("Accept", "application/json")
    response = urlopen(request)
    apps = json.load(response)["apps"]["app"]

    key = itemgetter("name", "user", "queue")

    with open(fname + ".swp", "w") as f:
        for metric, metric_type in [
            ("allocatedVCores", "gauge"),
            ("allocatedMB", "gauge"),
            ("vcoreSeconds", "counter"),
        ]:
            data = defaultdict(lambda: 0)
            for i in apps:
                i["name"] = UUID_RE.sub("{uuid}", i["name"])
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

    os.rename(fname + ".swp", fname)


def loop(args):
    while True:
        try:
            tick(
                args.resource_manager_url, args.output_file,
            )
            sleep(10)
        except KeyboardInterrupt:
            break
        except Exception:
            logging.exception("unexpected error")


def main():
    parser = argparse.ArgumentParser(
        description="Write YARN apps metrics for node_exporter textfile",
    )
    parser.add_argument("resource_manager_url")
    parser.add_argument(
        "--output-file",
        default="/opt/prometheus/exporters/node_exporter_current/yarn_apps.prom",
    )
    args = parser.parse_args()
    loop(args)


if __name__ == "__main__":
    main()
