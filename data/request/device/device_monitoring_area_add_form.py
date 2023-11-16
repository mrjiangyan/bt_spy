import wtforms
from form.JsonForm import JsonForm
from wtforms.validators import DataRequired, length, regexp


class DeviceMonitoringAreaForm(JsonForm):
    id = wtforms.StringField()

    areaName = wtforms.StringField(validators=[DataRequired(message='区域名称不允许为空'), length(
        min=4, max=20, message="区域名称长度必须大于%(min)d且小于%(max)d"
    ), regexp(message="区域名称不允许特殊字符不对", regex="^[\u4E00-\u9FA5A-Za-z0-9_]+$"),
                                               regexp(message="区域名称只能中文和字母", regex="^(?!.*[0-9])")])
    # 设备Id
    deviceId = wtforms.StringField(validators=[DataRequired(message='deviceId不允许为空')])
    # 颜色
    colour = wtforms.StringField(validators=[DataRequired(message='颜色不允许为空'),
                                             length(min=1, max=20, message="颜色长度必须大于%(min)且小于%(max)")])
    # 坐标数组
    effectiveArea = wtforms.StringField('effectiveArea', validators=[DataRequired(message='effectiveArea不允许为空')])
