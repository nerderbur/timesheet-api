import jwt
from bson.objectid import ObjectId

def verify_token(token):
    try:
        jwt.decode(token, 'secret')
    except:
        raise

    return

def serial(dct):
    for k in dct:
        if isinstance(dct[k], ObjectId):
            dct[k] = str(dct[k])   # 试过 dct[k] = str(dct[k]) 不行
    return dct