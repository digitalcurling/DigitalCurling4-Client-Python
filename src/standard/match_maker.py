import json
import aiohttp.client_exceptions
import asyncio
import logging

from load_secrets import username, password
from dc4client.send_data import ClientDataModel
from dc4client.match_maker_client import MatchMakerClient

logger = logging.getLogger("Match_Maker")
logger.setLevel(level=logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s, %(name)s : %(levelname)s - %(message)s"
)
st_handler = logging.StreamHandler()
st_handler.setFormatter(formatter)
logger.addHandler(st_handler)


class MatchMaker:
    """
    MatchMaker class to handle match making for the DigitalCurling.
    This class is responsible for sending match data to the server
    and receiving the match_id for the next match.
    """
    def __init__(self):
        pass

    # こちらを試合開始前に実行してください
    # このプログラムを実行すると、match_id.jsonに次の試合で使用するmatch_idが生成されます
    # このmatch_idを使って試合を開始します
    async def main(self, data: ClientDataModel):
        try:
            # ホスト名とポート番号、ユーザ名、パスワードを指定してMatchMakerClientのインスタンスを作成します
            match_client = MatchMakerClient(
                host="localhost", port=5000, username=username, password=password
            )
            # サーバに試合作成リクエストを送信し、match_idを取得します
            match_id = await match_client.create_match(data)
            logger.info(f"match_id: {match_id}")
            # match_idをmatch_id.jsonに保存します
            with open("match_id.json", "w") as f:
                json.dump(match_id, f)
        except aiohttp.client_exceptions.ServerDisconnectedError:
            logger.error("Server is not running. Please contact the administrator")
        except aiohttp.client_exceptions.ClientConnectorError:
            logger.error("Cannot connect to server. Is it running on localhost:5000?")
        except RuntimeError as e:
            logger.error(str(e))


if __name__ == "__main__":
    # 4人制カーリング用の設定ファイルを読み込みます
    with open("setting.json", "r") as f:
        data = json.load(f)
    # 取得した設定データをClientDataModelに変換します
    data = ClientDataModel(**data)
    match_maker = MatchMaker()
    asyncio.run(match_maker.main(data))
