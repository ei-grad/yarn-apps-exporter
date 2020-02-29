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
