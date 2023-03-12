import utils.json_utils as json_utils

class ApiBase(object):
    def to_dict(self):
        return json_utils.class2dict(self)


class ApiResp(ApiBase):
    def __init__(self, code=0, data={}, message=''):
        self.code = code
        self.message = message
        self.data = data
