import hashlib

import config


class Sha1Utils:
    def __init__(self,
                 nonce=None,
                 secretId=None,
                 ):
        if nonce is None and secretId is None:
            self.nonce = 'nonce=' + config.NONCE
            self.secretId = 'secretId=' + config.SECRET_ID

    def get_interface_sign(self, timeStamp):
        encryption_list = [self.nonce, self.secretId]
        timeStamps = 'timeStamp=' + timeStamp
        encryption_list.append(timeStamps)
        temp = '&'.join(encryption_list)
        return hashlib.sha1(temp.encode("utf8")).hexdigest()
