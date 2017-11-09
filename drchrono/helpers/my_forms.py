from datetime import date

from django import forms
from django.forms import widgets

from drchrono.models import Profile


class DateSelectorWidget(widgets.MultiWidget):
    def __init__(self, attrs=None):
        # create choices for days, months, years
        # example below, the rest snipped for brevity.
        years = [(year, year) for year in (2011, 2012, 2013)]
        days = [(day, day) for day in (1, 11, 13)]
        months = [(month, month) for month in (1, 8, 11)]
        _widgets = (
            widgets.Select(attrs=attrs, choices=days),
            widgets.Select(attrs=attrs, choices=months),
            widgets.Select(attrs=attrs, choices=years),
        )
        super(DateSelectorWidget, self).__init__(_widgets, attrs)

    def decompress(self, value):
        if value:
            return [value.day, value.month, value.year]
        return [None, None, None]

    def value_from_datadict(self, data, files, name):
        datelist = [
            widget.value_from_datadict(data, files, name + '_%s' % i)
            for i, widget in enumerate(self.widgets)]
        try:
            D = date(
                day=int(datelist[0]),
                month=int(datelist[1]),
                year=int(datelist[2]),
            )
        except ValueError:
            return ''
        else:
            return str(D)


class CheckInForm(forms.Form):
    first_name = forms.CharField(label='First name', required=False)
    last_name = forms.CharField(label='Last name', required=False)
    ssn = forms.CharField(max_length=15, required=False, help_text='format: xxx-xx-xxxx')


DATE_TIME_CHOICES = [(1, '8:00'), (2, '9:00'), (3, '10:00'), (4, '11:00'), (5, '12:00'),
                     (6, '13:00'), (7, '14:00'), (8, '15:00'), ]


class DateTimeForm(forms.Form):
    time = forms.ChoiceField(choices=DATE_TIME_CHOICES, widget=forms.RadioSelect)
    alarm_time = forms.IntegerField(min_value=-12, max_value=0, label='Alarm Offset(hours)', initial=-1)
    time3 = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)
    time2 = forms.MultipleChoiceField(widget=DateSelectorWidget)
    time3.choices = DATE_TIME_CHOICES


class IdentityForm(forms.Form):
    identity = forms.ChoiceField(choices=[('doctor', 'As doctor'), ('patient', 'As patient')], widget=forms.RadioSelect)


# class LoginForm(forms.Form):
#     username = forms.CharField(widget=forms)
#     password = forms.CharField(widget=forms.PasswordInput)


class UpdateForm(forms.Form):
    address = forms.CharField(required=False)
    cell_phone = forms.CharField(max_length=10, required=False)
    city = forms.CharField(required=False)
    date_of_birth = forms.DateField(widget=forms.TextInput(attrs={
        'class': 'datepicker',
        'readonly': 'true'
    }))


class AvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('avatar',)
