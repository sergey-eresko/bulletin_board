from django.contrib import admin
import datetime

from .models import AdvUser, SuperRubric, SubRubric
from .forms import SubRubricForm
from .utilities import send_activation_notification
from .models import Bb, AdditionalImage, Comment


def send_activation_notifications(modeladmin, request, queryset):
    for rec in queryset:
        if not rec.is_activated:
            send_activation_notification(rec)
    modeladmin.message_user(request, 'Requirements letters sent')
    send_activation_notifications.short_description = \
        'Requirements letters send'


class NonactivedFilter(admin.SimpleListFilter):
    title = 'Activated'
    parameter_name = 'acstate'

    def lookups(self, request, model_admin):
        return(
            ('activated', 'Activated'),
            ('threedays', 'Not activated for 3 days'),
            ('week', 'Not activated for a week'),
            ('not_activated', 'Not activated')
        )

    def queryset(self, request, queryset):
        val = self.value()
        if val == 'activated':
            return queryset.filter(is_active=True, is_activated=True)
        elif val == 'threedays':
            d = datetime.date.today() - datetime.timedelta(days=3)
            return queryset.filter(is_active=False, is_activated=False, date_joined__date__lt=d)
        elif val == 'week':
            d = datetime.date.today() - datetime.timedelta(weeks=1)
            return queryset.filter(is_active=False, is_activated=False, date_joined__date__lt=d)
        elif val == 'not_activated':
            return queryset.filter(is_active=False, is_activated=False)


class AdvUserAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_activated', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = (NonactivedFilter, )
    fields = (
        ('username', 'email'),
        ('first_name', 'last_name'),
        ('send_messages', 'is_active', 'is_activated'),
        ('is_staff', 'is_superuser'),
        'groups', 'user_permissions',
        ('last_login', 'date_joined')
    )
    readonly_fields = ('last_login', 'date_joined')
    actions = (send_activation_notifications, )


class SubRubricInline(admin.TabularInline):
    model = SubRubric


class SuperRubricAdmin(admin.ModelAdmin):
    exclude = ('super_rubric',)
    inlines = (SubRubricInline,)


class SubRubricAdmin(admin.ModelAdmin):
    form = SubRubricForm


class AdditionalImageInline(admin.TabularInline):
    model = AdditionalImage


class CommentAdmin(admin.ModelAdmin):
    model = Comment
    list_display = ('__str__', 'bb')


class CommentInline(admin.TabularInline):
    model = Comment


class BbAdmin(admin.ModelAdmin):
    list_display = ('rubric', 'title', 'content', 'author', 'created_at')
    fields = (
        ('rubric', 'author'),
        'title', 'content', 'price',
        'contacts', 'image', 'is_active'
    )
    inlines = (AdditionalImageInline, CommentInline)


admin.site.register(AdvUser, AdvUserAdmin)
admin.site.register(SuperRubric, SuperRubricAdmin)
admin.site.register(SubRubric, SubRubricAdmin)
admin.site.register(Bb, BbAdmin)
admin.site.register(Comment, CommentAdmin)
