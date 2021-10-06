# tado-individual-away-control

`tado-individual-away-control` allows to control the away state of your tado heating control by individual users.
It uses the tado api to get the home state of a desired device (e.g. a smartphone).

This software is not developed by Tado itself.

### Installation

The software requires Python 3 (tested with 3.8 under MacOS and Raspbian).

To install the required pip packages run

```pip packets
python3 -m pip install -r requirements.txt
```

To setup `tado-individual-away-control` as a systemd service (and automatically start at boot) place the files to the supposed folder and execute the `setup-service.sh` script. Beforehand the configuration step below needs to be done (otherwise the service will crash)!
To get the state of the service run `sudo systemctl status tado-control`, to restart the service run `sudo systemctl restart tado-control`.
Tested on RasperryPi 3 B (Raspbian GNU/Linux 10 (buster)).

### Configuration

The `config.json` contains all tweakable parameters. Before first run, the config-sample.json needs to be adapted to your personal tado setup and renamed to config.json!

Some values are already set up, other ones need to be entered manually (username and password; rules).

```
{
  "username": "<your-username>",
  "password": "<your-password>",
  "away_temperature": <int, temperature to be set when in away mode>,
  "allow_deep_sleep": <true/false, allow/disallow deep sleep>,
  "deep_sleep_after_hours": <float, time in hours after which deep sleep gets enabled>,
  "deep_sleep_temperature": <int, temperature to be set when in deep sleep mode>,
  "interval": <int, interval in seconds>,
  "default_stale_state": <"HOME" or "AWAY", value to consider the device as if it is stale>,
  "print_timestamp": <true/false, print the timestamps in terminal (set to false for privacy reasons)>,
  "rules": [
    {
      "zone_id": <int, id of the zone OR list<int>, zone ids OR "default">,
      "device": [
        "<list of names of the devices to listen for this zone(s)>"
      ]
    }
  ]
}
```

Each rule is defined by the zone id and a list of the devices to look for. The script receives the home state of each device in the defined interval and sets the zones accordingly.

The `zone_id` field can be a single zone id, a list of zone ids (e.g. `[1, 2, 3]`) or the string `"default"`, which applies to all zones no rule is defined for.
Keep in mind: There can only be one rule per zone, otherwise the application will terminate.

Multiple rules aswell as multiple devices are possible. Only if all devices are not available, the state of the zone is away.
The `deep sleep mode` is acitvated, when a zone is set to away mode for `deep_sleep_after_hours` number of hours. Then the temperature is set to `deep_sleep_temperature`.

To list all zones run
```
python3 start.py --list-zones
```

To list all devices run
```
python3 start.py --list-zones
```

To run the application simply start the `start.py`.

### Privacy notes

The software does not log any user behaviour or profiles. Only the last (`client_state_history_len`) results are stored in the applications memory.
Set `print_timestamp`to false to remove the time information of the output of the state changes.

### License

```
Copyright 2020 Jannik Scharrenbach.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
