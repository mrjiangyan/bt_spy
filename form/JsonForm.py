import json

from wtforms import Form
from flask import request


class JsonForm(Form):

    def __init__(self):
        data = request.get_json()
        args = request.args.to_dict()
        super(JsonForm, self).__init__(data=data, **args)

    def validate_for_api(self):
        valid = super(JsonForm, self).validate()
        if not valid:
            errors = json.loads(str(self.errors).replace("'", '"'))
            message = []
            for i in errors.values():
                message.append(i[0])
            print('，'.join(message))
            raise Exception('，'.join(message))
        return self

    # @classmethod
    # def init_and_validate(cls):
    #     wtforms_json.init()
    #     form = cls.from_json(request.get_json())
    #     valid = form.validate()
    #     if not valid:
    #         raise Exception(msg=form.errors)
    #     return form
