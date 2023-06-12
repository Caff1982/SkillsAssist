from app import app


# Define custom Jinja filters
def datetime_format(date, str_format='%Y-%m-%d %H:%M'):
    """Converts a datetime object to a custom string format.

    Args:
        date (datetime): A datetime object.
        str_format (str, optional): The desired format, default is
                                    '%Y-%m-%d %H:%M'.

    Returns:
        str: A string representing the date in the desired format.
    """
    return date.strftime(str_format)


def percent(value):
    """
    Converts a decimal to a percentage.

    Args:
        value (float): A decimal value between 0 and 1.
    
    Returns:
        str: A string representing the decimal as a percentage.
    """
    return f'{value:.0%}'


# Register the filters with Jinja
app.jinja_env.filters['datetime_format'] = datetime_format
app.jinja_env.filters['percent'] = percent
