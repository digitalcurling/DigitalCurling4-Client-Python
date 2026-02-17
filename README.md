# DigitalCurling4 Client Template

This is a client template compatible with DigitalCurling4.
(For compatibility, DigitalCurling3 throw data can also be used)

## Language
- [English(default)](https://github.com/digitalcurling/DigitalCurling4-Client-Python/blob/main/README.md)
- [Japanese](https://github.com/digitalcurling/DigitalCurling4-Client-Python/blob/main/README.ja.md)

## Install requirements.txt
```bash
pip install -r requirements.txt
```

## How to use
### Prepare user data
To play a match, each user must be registered on the server.
Example:

```
MATCH_USER_NAME="user"
PASS_WORD="password"
```
By default, a file named .env.sample is included. Rename it to .env and set your own username and password registered on the server in this file.

## Make Match

### Match Setting File
In the "setting.json" file or "md_setting.json" file, describe the information required for the match, such as standard_end_count, time_limits, the simulator to be used, and the applied_rule.

Please set game_mode to either **standard** or **mix_doubles**.

- If standard is selected: 
A 4-player match will start. 
In this case, please select one of the following for applied_rule:
    - fgz_rule
    - no_tick_rule

- If mixed_doubles is selected: 
A match compatible with Mixed Doubles will start. In this case, please select following for applied_rule.
    - modified_fgz_rule
Please note that for mixed doubles, enter a number between 0 and 5 in the **positioned_stones_pattern** field. This determines the placement of the stones at each end.
![](./figure/positioned_stone.png)

(Currently, "fcv1" is the only simulator available, so matches cannot be played on other simulators.)

## Match Making
After completing the settings in setting.json, enter the following command.
```bash
python match_maker.py
```
The above command should be entered when you want to start a new match.

The match_id will now be stored in match_id.json.

### Connect client to server
You can configure the players who will play in that match in “team_config.json” and “md_team_config.json”. In addition, when playing with the same settings as in the tournament, you can set
```md
"use_default_config": true
``` 
If you want to create a unique team,

```md
"use_default_config": false
``` 

After the above settings are in place, connect the client to the server by entering the following command

```bash
cd client0
python sample.client.py
```

Then open another terminal,
```bash
cd client1
python sample.client.py
```

I think you can check the connection with these command.

## Match flow
### Four-player curling
The protocol for four-player curling is ![here](./figure/protocol.png).

1. Instantiate the client  
    ```Python
    client = DCClient(match_id=match_id, username=username, password=password, match_team_name=MatchNameModel.team0)
    ```
    match_id is received from the server when a match is created.
    username and password are required to identify the client. In production each participant should set their own username and password. For now you can use the preconfigured values in the project [.env](./.env).

    First, send your team information to the server. See [team_config.json](./team_config.json) for an example.

2. Set server host and port
    Use the set_server_address function inside DCClient to set the server host and port:
    ```Python
    client.set_server_address(host="localhost", port=5000)
    ```

3. Send team information
    Send your team information to the server using the **send_team_info** function.
    At this time, you will receive from the server which team plays first/second in the first end.
    (First -> team0, Second -> team1)

4. Start the match
    Receive state data from the server. If the next shot team matches your team name (team0 or team1), send a shot to the server using **send_shot_info**.

    You can also send shot data in the same format as Digital Curling 3rd generation using **send_shot_info_dc3**.
    Arguments:
    - vx
    - vy
    - rotation ("cw" or "ccw")

5. End of the match
When **winner_team** in the state data becomes team0 or team1, the match is finished.

### Mixed Doubles
The protocol for mixed doubles is as follows ![here](./figure/md_protocol.png).

1. Instantiate the client
    ```Python
    client = DCClient(match_id=match_id, username=username, password=password, match_team_name=MatchNameModel.team0)
    ```
    match_id is received from the server when a match is created.
    username and password are required to identify the client. In production each participant should set their own username and password.

    First, send your team information to the server.
    See [md_team_config.json](./md_team_config.json) for an example. (Only the team data differs from four-player curling.)

2. Set server host and port (same as four-player curling)
    Use the set_server_address function inside DCClient to set the server host and port:
    ```Python
    client.set_server_address(host="localhost", port=5000)
    ```

3. Send team information (same as four-player curling)
    Send your team information to the server using **send_team_info**.
    At this time, you will receive from the server which team plays first/second in the first end.
    (First -> team0, Second -> team1)

4. Start the match
    At match start, the server sends a state where **next_shot_team** is None. At the beginning of each end, you must choose the positioned stones.

    Use the following to choose the positioned stones pattern (and optional power play):
    ```Python
    class PositionedStonesModel(str, enum.Enum):
        center_guard = "center_guard"
        center_house = "center_house"
        pp_left = "pp_left"
        pp_right = "pp_right"
    ```

    Power play can be used only once per team per match. After the second attempt, **center_guard** is automatically selected.
    - PositionedStonesModel.center_guard -> Positioned stones at guard, take first throw
    - PositionedStonesModel.center_house -> Positioned stones in house, take second throw
    - PositionedStonesModel.pp_left -> Power play: positioned stones on the left, take second throw
    - PositionedStonesModel.pp_right -> Power play: positioned stones on the right, take second throw

    After that, receive state data from the server. If the next shot team matches your team name (team0 or team1), send a shot to the server using **send_shot_info**.

    You can also send shot data in the same format as Digital Curling 3rd generation using **send_shot_info_dc3**.

5. End of the match (same as four-player curling)
When **winner_team** in the state data becomes team0 or team1, the match is finished.
