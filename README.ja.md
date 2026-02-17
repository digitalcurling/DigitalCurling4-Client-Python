# DigitalCurling4クライアントテンプレート

これは、DigitalCurling4に対応したクライアントテンプレートとなっています。
(互換性として、DigitalCurling3の投球データも使用可能です)

## 言語
- [英語（デフォルト)](https://github.com/digitalcurling/DigitalCurling4-Client-Python/blob/main/README.md)
- [日本語](https://github.com/digitalcurling/DigitalCurling4-Client-Python/blob/main/README.ja.md)

## requirements.txt のインストール
```bash
pip install -r requirements.txt
```

## 使い方
本リポジトリには、テンプレートとして4人制のカーリングとミックスダブルスの2つを用意してあります。./templatesの中にそれぞれに対応したプログラムがありあす。

### ユーザーデータの準備
試合を行うためには、各ユーザーがサーバー側に登録されている必要があります。 例:

```
MATCH_USER_NAME="user"
PASS_WORD="password"
```
デフォルトで.env.sampleというファイルが入っておりますが、そちらを.envファイルに変えた上、サーバに登録したユーザネーム・パスワードをこちらに設定してください。

## 試合の作成
### 試合設定ファイル
"setting.json" ファイルまたは"md_setting.json" ファイルに、standard_end_count（標準エンド数）、time_limits（制限時間）、使用する simulator（シミュレータ）、applied_rule（適用ルール）など、試合に必要な情報を記述してください。 

game_mode には **standard** または **mix_doubles** を入れてください。
- standardを選択した場合
4人制での対戦が開始されます。この場合は、**applied_rule**には
    - fgz_rule
    - no_tick_rule
のいずれかを選択してください。
- mixed_doublesを選択した場合
ミックスダブルスに対応した対戦が開始されます。この場合は**applied_rule**には
    - modified_fgz_rule
    を選択してください
なお、ミックスダブルスの際には、**positioned_stones_pattern**に0~5の数値を入れてください。こちらは、各エンドにおける置き石のストーン配置を決定するものです。
![](./figure/positioned_stone.png)

(現在、利用可能なシミュレータは "fcv1" のみですので、他のシミュレータでは対戦できません。)

## 試合作成
setting.json の設定が完了したら、以下のコマンドを入力してください。

```Bash
python match_maker.py
```
上記のコマンドは、新しい試合を開始したいときに入力してください。

これで match_id.json に match_id が保存されます。

### クライアントをサーバーに接続
試合でプレイするプレイヤーの設定は、"team_config.json" および "md_team_config.json" で行えます。 また、大会と同じ設定でプレイする場合は、以下のように設定してください。

```Markdown
"use_default_config": true
```
独自のチームを作成したい場合は、以下のようにします。

```Markdown
"use_default_config": flase
```
上記の設定が完了したら、以下のコマンドを入力してクライアントをサーバーに接続してください。

```Bash
cd client0
python sample.client.py
```
その後、別のターミナルを開き、以下を実行します。

```Bash
cd client1
python sample.client.py
```
これらのコマンドで接続を確認できると思います。

## 試合の流れ
### 4人制カーリング
4人制のカーリングの場合のプロトコルは![こちら](./figure/protocol.png)

1. クライアントをインスタンス化
    ```Python
    client = DCClient(match_id=match_id, username=username, password=password, match_team_name=MatchNameModel.team0)
    ```
    match_id は試合作成時にサーバから受け取ります。
    usernameとpasswordはクライアントを特定するために、設定する必要があります。
    本番環境では、参加者にusernameとpasswordを設定して参加して頂く必要があります。

    まず初めにチーム情報をサーバへ送信します。
    チーム情報の例として[team_config.json](./team_config.json)をご確認ください。

2. 通信先のホスト名・ポート番号の設定
    **DCClient**内にある**set_server_address**関数を利用して、サーバのホスト名・ポート番号を設定してください。
    ```Python
    client.set_server_address(host="localhost", port=5000)
    ```

3. チーム情報の送信
    **send_team_info**関数を用いてチーム情報を、サーバへ送信します。
    この際に、最初のエンドにおける先攻後攻をサーバから受け取ります。
    (先攻 -> team0, 後攻 -> team1)

4. 試合開始
    サーバから盤面データを受け取り、次のショットチームがあなたのチーム名(team0 または team1)と一致した場合、**send_shot_info**関数を利用して投球情報をサーバへ送信してください。

    なお、第三世代のデジタルカーリングの投球情報のままでも送信できるよう**send_shot_info_dc3**関数を用意してあります。
    引数は
    - vx
    - vy
    - rotation("cw" または"ccw"を入れてください)

5. 試合終了
    盤面データ内にある**winner_team**にteam0 または team1 が入ったら試合終了です。

### ミックスダブルス
ミックスダブルスの場合のプロトコルは![こちら](./figure/md_protocol.png)

1. クライアントをインスタンス化
    ```Python
    client = DCClient(match_id=match_id, username=username, password=password, match_team_name=MatchNameModel.team0)
    ```
    match_id は試合作成時にサーバから受け取ります。
    usernameとpasswordはクライアントを特定するために、設定する必要があります。

    まず初めにチーム情報をサーバへ送信します。
    チーム情報の例として**[md_team_config.json](./md_team_config.json)**をご確認ください。ここのチームデータだけ4人制カーリングと異なります。

2. 通信先のホスト名・ポート番号の設定 (4人制カーリングと同様)
    **DCClient**内にある**set_server_address**関数を利用して、サーバのホスト名・ポート番号を設定してください。
    ```Python
    client.set_server_address(host="localhost", port=5000)
    ```
3. チーム情報の送信 (4人制カーリングと同様)
    **send_team_info**関数を用いてチーム情報を、サーバへ送信します。
    この際に、最初のエンドにおける先攻後攻をサーバから受け取ります。
    (先攻 -> team0, 後攻 -> team1)

4. 試合開始
    試合開始のタイミングで、サーバから**next_shot_team**にNoneが入った状態の盤面データが送られます。各エンドの最初は置き石を設定して頂きます。
    この際に、
    ```Python
    class PositionedStonesModel(str, enum.Enum):
        center_guard = "center_guard"
        center_house = "center_house"
        pp_left = "pp_left"
        pp_right = "pp_right"
    ```
    を使用して、置き石の置く場所・パワープレイの選択をします。(パワープレイは1試合1チームにつき1回までです。2回目以降は自動で以下のcenter_guardが選択されます)
    - PositionedStoneModel.center_guard -> 置き石をガードに設置し、先攻を取る
    - PositionedStoneModel.center_house -> 置き石をハウス内に設置し、後攻を取る
    - PositionedStoneModel.pp_left -> パワープレイ。置き石をハウス左側に設置し、後攻を取る
    - PositionedStoneModel.pp_right -> パワープレイ。置き石をガード右側に設置し、後攻を取る

    その後はサーバから盤面データを受け取り、次のショットチームがあなたのチーム名(team0 または team1)と一致した場合、**send_shot_info**関数を利用して投球情報をサーバへ送信してください。

    なお、第三世代のデジタルカーリングの投球情報のままでも送信できるよう**send_shot_info_dc3**関数を用意してあります。

5. 試合終了 (4人制カーリングと同様)
    盤面データ内にある**winner_team**にteam0 または team1 が入ったら試合終了です。