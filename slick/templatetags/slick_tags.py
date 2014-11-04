import re

from django import template
from django.conf import settings
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from django.core.urlresolvers import reverse

site = admin.site

register = template.Library()


@register.assignment_tag(takes_context=True)
def is_active_path(context, name, by_path=False, on_subpath=False):
    """ Return the string 'active' current request.path is same as name
    
    Keyword aruguments:
    request  -- Django request object
    name     -- name of the url or the actual path
    by_path  -- True if name contains a url instead of url name
    on_subpath  -- True if active applies to items on the subpath
    """
    request = context["request"]

    if by_path:
        path = name
    else:
        path = reverse(name)

    if request.path == path or (on_subpath and request.path.startswith(path)):
        return True
 
    return False


@register.assignment_tag(takes_context=True)
def get_app_list(context):
    request = context["request"]
    app_dict = {}
    user = request.user
    for model, model_admin in site._registry.items():
        app_label = model._meta.app_label
        has_module_perms = user.has_module_perms(app_label)
        
        if has_module_perms:
            perms = model_admin.get_model_perms(request)
            
            if True in perms.values():
                model_dict = {
                    'name': capfirst(model._meta.verbose_name_plural),
                    'admin_url': mark_safe('/admin/%s/%s/' % (app_label, model.__name__.lower())),
                    'perms': perms,
                    'description': model_admin.description if hasattr(model_admin, 'description') else None
                }

                if app_label in app_dict:
                    app_dict[app_label]['models'].append(model_dict)
                else:
                    app_dict[app_label] = {
                        'name': app_label.title(),
                        'app_url': app_label + '/',
                        'admin_url': mark_safe('/admin/%s/' % (app_label)),
                        'has_module_perms': has_module_perms,
                        'models': [model_dict],
                    }
                    
    app_list = app_dict.values()
    app_list.sort(lambda x, y: cmp(x['name'], y['name']))
    return app_list