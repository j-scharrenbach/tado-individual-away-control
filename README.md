# tado-individual-away-control

`tado-individual-away-control` allows to control the away state of your tado heating control by individual users.
It uses pings in the local network to get the state of a desired device (e.g. a smartphone).

This software is not developed by Tado itself.

### Installation

The software requires Python 3 (tested with 3.8 under MacOS and Raspbian).

To install the required pip packages run

```pip packets
python3 -m pip install -r requirements.txt
```

### Configuration

The `config.json` contains all tweakable parameters.

Some values are already set up, other ones need to be entered manually (username and password; rules).

```
{
  "username": "<your-username>",
  "password": "<your-password>",
  "away_temperature": <int, temperature to be set when away>,
  "interval": <int, interval of ping events in seconds>,
  "max_ping_cnt": <int, number of consecutive pings>,
  "client_state_history_len": <int, number of ping events to evaluate for state>,
  "min_home_success_pings": <int, minimal number of successfull pings to set state to home>,
  "print_timestamp": <true/false, print the timestamps in terminal (set to false for privacy reasons)>,
  "rules": [
    {
      "zone_id": <int, id of the zone>,
      "ips": [
        "<list of ips for the desired zone>"
      ]
    }
  ]
}
```

Each rule is defined by the zone id and a list of the devices to look for (make sure the devices have a static ip).
Multiple rules aswell as multiple devices are possible. Only if all devices are not available, the state of the zone is away.

To list all zones run
```pip packets
python3 start.py --list-zones
```

The time needed to recognize a device as away is determined by `interval * client_state_history_len`.

To run the application simply start the `start.py` with sudo rights (those are needed for the pings).

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
