"""Forms for Python Trader app."""
from wtforms import SelectField,StringField,HiddenField
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired


class ApplyStrategyForm(FlaskForm):
    """Form for applying strategies to stocks."""
    strategy_id=SelectField("Choose a Strategy",coerce=int)
