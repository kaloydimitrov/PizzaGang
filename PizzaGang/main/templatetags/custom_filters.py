from django import template

register = template.Library()


@register.filter
def multiply(value, arg):
    return value * arg


@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()
