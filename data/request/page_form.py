import wtforms
from form.JsonForm import JsonForm
from wtforms.validators import DataRequired, NumberRange


class PageQueryForm(JsonForm):
    pageIndex = wtforms.IntegerField(validators=[DataRequired(message="pageIndex能为空且不能小于1"),
                                                 NumberRange(min=1, message="pageIndex必须大于%(min)d且小于%(max)d")])
    pageSize = wtforms.IntegerField(validators=[DataRequired(message="pageSize不能为空且不能小于1"),
                                                NumberRange(min=1, max=50, message="pageSize必须大于%(min)且小于%(max)")])
