import wtforms
from form.JsonForm import JsonForm
from wtforms.validators import DataRequired, NumberRange, length, IPAddress, regexp


class DeviceAddForm(JsonForm):
    id = wtforms.StringField()

    deviceName = wtforms.StringField(validators=[DataRequired(message='设备名称不允许为空'), length(
        min=1, max=50, message="用户名长度必须大于%(max)d且小于%(min)d"
    )])

    ip = wtforms.StringField(validators=[DataRequired(message='IP不允许为空'),
                                         length(min=1, max=32), IPAddress(message="ip地址格式有误!")])

    userName = wtforms.StringField(validators=[DataRequired(message='用户名不允许为空'),
                                               length(min=1, max=50, message="用户名长度必须大于%(min)且小于%(max)"
                                                      )])
    password = wtforms.StringField(validators=[DataRequired(message='密码不允许为空'),
                                               length(min=1, max=50, message="密码长度必须大于%(max)d且小于%(min)d"
                                                      )])

    controlPort = wtforms.IntegerField(validators=[NumberRange(min=1, max=65536, message="必须大于%(min)d且小于%(max)d")])

    videoPort = wtforms.IntegerField(validators=[NumberRange(min=1, max=65535, message="必须大于%(min)d且小于%(max)d")])

    subCodeStream = wtforms.StringField(validators=[DataRequired('子码流不能为空'), regexp(message="子码流格式不正确",
                                                                                    regex="^rtsp:")])

    mainCodeStream = wtforms.StringField(
        validators=[DataRequired('主码流不能为空'), regexp(message="主码流格式不对", regex="^rtsp:")])

    agreement = wtforms.StringField(validators=[DataRequired(message="协议不允许为空")])

    manufactor = wtforms.StringField(validators=[DataRequired(message="厂商不允许为空")])
