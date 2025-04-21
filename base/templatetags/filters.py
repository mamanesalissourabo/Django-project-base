from django import template

register = template.Library()

@register.filter
def truncate_chars(value, max_length):
    """
    Tronque une chaîne de caractères à une longueur maximale et ajoute des points de suspension.
    """
    if len(value) > max_length:
        return value[:max_length] + "..."
    return value