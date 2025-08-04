from django import template

register = template.Library()

def to_persian_number(number: str):
    persian_digits = '۰۱۲۳۴۵۶۷۸۹'
    return ''.join(persian_digits[int(d)] if d.isdigit() else d for d in str(number))


@register.filter
def persian_price(value):
    try:
        value = int(value)
        formatted = f"{value:,}"
        return to_persian_number(formatted)
    except (ValueError, TypeError):
        return value
