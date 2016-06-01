from django.contrib import admin

from import_export import fields, resources
from import_export.admin import ExportMixin
from models import Attendance, Event, EventMetric, EventMetricOutcome


class AttendanceInline(admin.TabularInline):
    """Attendance Inline."""
    model = Attendance
    extra = 1


class EventResource(resources.ModelResource):
    event_categories = fields.Field()
    event_metrics = fields.Field()
    owner = fields.Field(column_name='owner')
    campaign = fields.Field(column_name='campaign')

    class Meta:
        model = Event
        exclude = ('id', 'categories', 'metrics',)

    def dehydrate_event_categories(self, event):
        if event.categories.all().exists():
            categories = ', '.join([x.name for x in event.categories.all()])
            return categories
        return ''

    def dehydrate_event_metrics(self, event):
        event_metrics = event.metrics.all()
        if event_metrics.exists():
            event_outcome = EventMetricOutcome.objects.filter(event=event)
            if event_outcome.exists():
                outcome = [(x.metric.name, x.expected_outcome, x.outcome)
                           for x in event_outcome]
                return str(outcome).strip('[]')
            else:
                metrics = ', '.join(x.name for x in event_metrics)
            return metrics
        return ''

    def dehydrate_owner(self, event):
        return event.owner.get_full_name()

    def dehydrate_campaign(self, event):
        if event.campaign:
            return event.campaign.name
        return ''


class EventAdmin(ExportMixin, admin.ModelAdmin):
    """Event Admin."""
    resource_class = EventResource
    inlines = [AttendanceInline]
    model = Event
    list_display = ('name', 'start', 'end', 'created_on', 'updated_on',)
    search_fields = ('name', 'country', 'region', 'venue', 'slug',
                     'campaign__name', 'owner__first_name', 'owner__last_name')
    list_filter = ('has_new_metrics', ('start', admin.DateFieldListFilter),
                   ('end', admin.DateFieldListFilter))
    readonly_fields = ['times_edited']

    def owner_display_name(self, obj):
        return obj.owner.userprofile.display_name


class AttendanceResource(resources.ModelResource):
    user_full_name = fields.Field()
    event_name = fields.Field()

    class Meta:
        model = Attendance
        export_order = ['event_name', 'user_full_name']

    def dehydrate_user_full_name(self, obj):
        return obj.user.get_full_name()

    def dehydrate_event_name(self, obj):
        return obj.event.name


class AttendanceAdmin(ExportMixin, admin.ModelAdmin):
    """Attendance Admin"""
    resource_class = AttendanceResource
    model = Attendance
    list_display = ('event', 'user', 'date_subscribed',)
    search_fields = ('event__name', 'user__first_name', 'user__last_name',)


class EventMetricAdmin(ExportMixin, admin.ModelAdmin):
    """EventMetric Admin."""
    model = EventMetric
    list_display = ('name', 'active')
    list_filter = ('active',)


class EventMetricOutcomeAdmin(ExportMixin, admin.ModelAdmin):
    """EventMetricOutcome Admin."""
    model = EventMetricOutcome
    list_display = ('event', 'metric', 'expected_outcome', 'outcome')
    search_fields = ('event__name', 'metric__name')

admin.site.register(Event, EventAdmin)
admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(EventMetric, EventMetricAdmin)
admin.site.register(EventMetricOutcome, EventMetricOutcomeAdmin)
