from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectMultipleField
from wtforms.fields.simple import SubmitField
from wtforms.validators import Optional
from wtforms.widgets.core import CheckboxInput, ListWidget


class ConfigureAnalysisSettingsForm(FlaskForm):
    submit = SubmitField("Configure Analyser Settings")


class ConfigurePeopleForm(FlaskForm):
    submit = SubmitField("Configure People To Be Included")


class IncludeExcludePeopleForm(FlaskForm):
    names = SelectMultipleField(
        'Names',
        validators=[Optional()],
        coerce=int,
        widget=ListWidget(html_tag='ul', prefix_label=False),
        option_widget=CheckboxInput()
    )

    submit = SubmitField("Exclude")
