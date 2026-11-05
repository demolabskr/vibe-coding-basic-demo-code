from django import template

register = template.Library()


@register.filter
def won(value):
    """12000 -> "12,000원" """
    return f"{int(value):,}원"
