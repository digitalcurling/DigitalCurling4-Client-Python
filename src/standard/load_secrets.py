import os
from dotenv import load_dotenv

# AI作成者一人一人に固有のユーザネーム、パスワードを設定して頂きます。
load_dotenv()

username = os.getenv("MATCH_USER_NAME")
password = os.getenv("PASS_WORD")

if __name__ == "__main__":
    print(f"Username: {username}")
    print(f"Password: {password}")