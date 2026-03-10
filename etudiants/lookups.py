from ajax_select import register, LookupChannel
from .models import EtablissementDorigine

@register('tags')
class TagsLookup(LookupChannel):

    model = EtablissementDorigine

    def get_query(self, q, request):
        return self.model.objects.filter(nom__icontains=q).order_by('nom')[:100]

    def format_item_display(self, item):
        return u"<span class='tag'>%s</span>" % item.nom