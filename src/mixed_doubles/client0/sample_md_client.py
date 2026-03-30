import asyncio
import json
import numpy as np
import logging
from pathlib import Path

from load_secrets import username, password
from dc4client.dc_client import DCClient
from dc4client.send_data import TeamModel, MatchNameModel, PositionedStonesModel

formatter = logging.Formatter(
    "%(asctime)s, %(name)s : %(levelname)s - %(message)s"
)

async def main():
    # match_idの読み込みます。
    json_path = Path(__file__).parents[1] / "match_id.json"
    with open(json_path, "r") as f:
        match_id = json.load(f)

    # 最初のエンドにおいて、team0が先攻、team1が後攻です。
    # デフォルトではmatch_team_name=team1となっており、先攻に切り替えたい場合はDCClientのコンストラクタの引数にて
    # match_team_name=MatchNameModel.team0
    # としてください
    # クライアントの初期化（ログレベルはデフォルトでINFO、保存機能はデフォルトでTrue）
    client = DCClient(match_id=match_id, username=username, password=password, match_team_name=MatchNameModel.team0, auto_save_log=True, log_dir="logs")

    # ここで、接続先のサーバのアドレスとポートを指定します。
    # デフォルトではlocalhost:5000となっています。
    # こちらは接続先に応じて変更してください。
    client.set_server_address(host="localhost", port=5000)

    # チーム設定の読み込み
    with open("md_team_config.json", "r") as f:
        data = json.load(f)
    client_data = TeamModel(**data)

    # ログ設定(不要であれば削除してください)
    logger = logging.getLogger("SampleMDClient")
    logger.setLevel(level=logging.INFO)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    logger.info(f"client_data.team_name: {client_data.team_name}")
    logger.debug(f"client_data: {client_data}")


    try:
        # チーム情報をサーバに送信します。
        # 相手のクライアントも同様にチーム情報を送信するまで待機します。
        # 送信後、自チームの名前を受け取ります(team0 または team1)。
        # 両チームが揃うと試合が開始されます。
        # 最初の置き石を設定するチームが、サーバに置き石の設定を送信したら思考時間のカウントが始まります。
        # そのため、AIの初期化などはこの前に行ってください。
        match_team_name: MatchNameModel = await client.send_team_info(client_data)

        async for state_data in client.receive_state_data():
            # ゲーム終了の判定
            if (winner_team := client.get_winner_team()) is not None:
                logger.info(f"Winner: {winner_team}")
                break

            next_shot_team = client.get_next_team()

            # AIを実装する際の処理はこちらになります。
            # 最初の置き石を設定するチームの場合、最初の状態データ受信時に置き石の情報を送信します。
            if state_data.next_shot_team is None and state_data.mixed_doubles_settings is not None and state_data.last_move is None:
                if state_data.mixed_doubles_settings.end_setup_team == match_team_name:
                    logger.info("You select the positioned stones.")
                    # 置き石のパターンを選択します。
                    # 以下のいずれかを選択してください。
                    # PositionedStonesModel.center_guard -> 現エンド: ガードを中央に置き、先攻
                    # PositionedStonesModel.center_house -> 現エンド: ハウスを中央に置き、後攻
                    # PositionedStonesModel.pp_left      -> 現エンド: パワープレイを実施し、左側に置き、後攻
                    # PositionedStonesModel.pp_right     -> 現エンド: パワープレイを実施し、右側に置き、後攻
                    positioned_stones = PositionedStonesModel.pp_left

                    # 置き石の情報をサーバに送信します。
                    await client.send_positioned_stones_info(positioned_stones)
        
            if next_shot_team == match_team_name:
                await asyncio.sleep(2)

                translational_velocity = 2.3
                angular_velocity = np.pi / 2
                shot_angle = np.pi / 2

                await client.send_shot_info(
                    translational_velocity=translational_velocity,
                    shot_angle=shot_angle,
                    angular_velocity=angular_velocity,
                )
                # なお、デジタルカーリング3で使用されていた、(vx, vy, rotation(cw または ccw))での送信も可能です。
                # vx = 0.0
                # vy = 2.33
                # rotation = "cw"
                # await client.send_shot_info_dc3(
                #     vx=vx,
                #     vy=vy,
                #     rotation=rotation,
                # )
    except Exception as e:
        client.logger.error(f"Unexpected error in main loop: {e}")
    finally:
        client.save_log_file()

if __name__ == "__main__":
    asyncio.run(main())
