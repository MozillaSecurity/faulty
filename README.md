Faulty
======


jenkins.sh
---
Custom build configuration script which applies faulty.v*.diff to mozilla-inbound and generates Firefox package and FuzzManager configuration.

faulty.sh
---
UserData script to setup an instance at DigitalOcean which installs `rr`, downloads the other resources and launches the fuzzing task.

faulty-rr.sh
---
The bot which is spawned by `faulty.sh` to launch Firefox with Faulty and which collects and buckets the test-cases.

faulty.js
---
Preferences for Firefox with adjusted IPC settings.

faulty.v*.diff
---
The actual IPC fuzzing patch.
