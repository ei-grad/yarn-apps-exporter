YARN Apps Exporter
==================

Write YARN applications metrics for prometheus node\_exporter textfile collector.

Install
-------

```
sudo pip install yarn-apps-exporter
```

Check that it runs correctly:

```
sudo yarn-apps-exporter http://resource.manager.hostname:8088
cat /opt/prometheus/exporters/node_exporter_current/yarn_apps.prom
```

Add systemd service:

```
sudo tee /etc/systemd/system/yarn-apps-exporter.service << EOF
[Unit]
Description=Write YARN apps metrics for node_exporter textfile

[Service]
ExecStart=/usr/local/bin/yarn-apps-exporter http://resource.manager.hostname:8088

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl start yarn-apps-exporter
sudo systemctl enable yarn-apps-exporter
```

Replacement Patterns
--------------------

To have `HIVE-{uuid}` application name instead of many unique names:

1. Put `replacement\npattern\n` lines to patterns.txt file:

```
{uuid}
[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}
```

2. Specify `--patterns` argument:

```bash
yarn-apps-exporter http://resource.manager.hostname:8088 --patterns patterns.txt
```

You can add more patterns in the next lines.
