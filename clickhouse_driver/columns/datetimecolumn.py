from calendar import timegm
from datetime import datetime, timezone
from time import mktime

from .base import FormatColumn

timezones = { 'Zulu': timezone.utc, 'UTC': timezone.utc }

class DateTimeColumn(FormatColumn):
    ch_type = 'DateTime'
    py_types = (datetime, int)
    format = 'I'

    def __init__(self, timezone=None, **kwargs):
        self.timezone = timezone
        super(DateTimeColumn, self).__init__(**kwargs)

    def after_read_item(self, value):
        dt = datetime.fromtimestamp(value, self.timezone)
        return dt.replace(tzinfo=None)

    def before_write_item(self, value):
        if isinstance(value, int):
            # support supplying raw integers to avoid
            # costly timezone conversions when using datetime
            return value

        if self.timezone:
            # Set server's timezone for offset-naive datetime.
            if value.tzinfo is None:
                value = value.replace(tzinfo=self.timezone)

            value = value.astimezone(timezone.utc)
            return int(timegm(value.timetuple()))

        else:
            # If datetime is offset-aware use it's timezone.
            if value.tzinfo is not None:
                value = value.astimezone(timezone.utc)
                return int(timegm(value.timetuple()))

            return int(mktime(value.timetuple()))


def create_datetime_column(spec, column_options):
    context = column_options['context']

    tz_name = timezone = None

    # Use column's timezone if it's specified.
    if spec[-1] == ')':
        tz_name = spec[10:-2]
    else:
        if not context.settings.get('use_client_time_zone', False):
            tz_name = context.server_info.timezone

    if tz_name:
        timezone = timezones[tz_name]

    return DateTimeColumn(timezone=timezone, **column_options)

def set_timezone(name, tz):
    timezones[name] = tz
