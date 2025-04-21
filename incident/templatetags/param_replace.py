from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    request = context['request']
    if not request:
        return ''
    
    params = request.GET.copy()
    
    # Gestion spéciale du tri (inverse si on clique sur la même colonne)
    if 'sort' in kwargs and 'sort' in params:
        if kwargs['sort'] == params['sort']:
            kwargs['sort'] = f"-{kwargs['sort']}"
        elif kwargs['sort'] == params['sort'].lstrip('-'):
            kwargs['sort'] = kwargs['sort'].lstrip('-')
    
    for key, value in kwargs.items():
        params[key] = value
    return params.urlencode()
