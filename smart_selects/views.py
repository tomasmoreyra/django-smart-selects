import locale
import json

from django.db.models import get_model
from django.http import HttpResponse

from smart_selects.utils import unicode_sorter


def filterchain(request, app, model, field, value, manager=None):
    model_class = get_model(app, model)
    if value == '0':
        keywords = {str("%s__isnull" % field): True}
    else:
        keywords = {str(field): str(value)}
    if manager is not None and hasattr(model_class, manager):
        queryset = getattr(model_class, manager)
    else:
        queryset = model_class._default_manager

    results = queryset.filter(**keywords)

    if not getattr(model_class._meta, 'ordering', False):
        results = list(results)
        results.sort(cmp=locale.strcoll, key=lambda x: unicode_sorter(unicode(x)))

    result = []
    for item in results:
        result.append({'value': item.pk, 'display': unicode(item)})
    json_dump = json.dumps(result)
    return HttpResponse(json_dump, mimetype='application/json')


def filterchain_all(request, app, model, field, value):
    model_class = get_model(app, model)
    if value == '0':
        keywords = {str("%s__isnull" % field): True}
    else:
        keywords = {str(field): str(value)}
    results = list(model_class._default_manager.filter(**keywords))
    results.sort(cmp=locale.strcoll, key=lambda x: unicode_sorter(unicode(x)))
    final = []
    for item in results:
        final.append({'value': item.pk, 'display': unicode(item)})
    results = list(model_class._default_manager.exclude(**keywords))
    results.sort(cmp=locale.strcoll, key=lambda x: unicode_sorter(unicode(x)))
    final.append({'value': "", 'display': "---------"})

    for item in results:
        final.append({'value': item.pk, 'display': unicode(item)})
    json_dump = json.dumps(final)
    return HttpResponse(json_dump, mimetype='application/json')
