import pandas as pd

import database.auth as auth
import database.model as model
import hashlib


def authorize(name, password):
    password = hashlib.md5(bytes(password,'utf-8')).hexdigest()
    df = auth.get_user(name)
    if len(df) > 0:
        if df.iloc[-1]['password'] == password and df.iloc[-1]['state'] == model.USER_STATE_ENABLED:
            auth.overdue_tokens(name)
            token_df = auth.create_token(name)
            return token_df
    return None


def validate_token(token):
    df = auth.find_token(token)
    return df


if __name__ == '__main__':
    #e10adc3949ba59abbe56e057f20f883e
    print(hashlib.md5(bytes('123456','utf-8')).hexdigest())
