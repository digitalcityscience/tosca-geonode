from django.contrib import admin
from django import forms
from geonode.geoserver.helpers import gs_catalog
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.db.models import Avg  # Add this import
from django.contrib.gis import admin as geoadmin
import csv
import json
from cpt.models import CategoryType, Category, Campaign,GeoserverLayers,Rating,Form


"""
parametrelerin ne oldugu ile ilgili kuuck infoyu admin panelde gostermek icin ne yapmali

"""

# Registering the CategoryType model
@admin.register(CategoryType)
class CategoryTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

# Registering the Category model
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_id', 'name', 'category_type')
    search_fields = ('name', 'category_type__name')
    list_filter = ('category_type',)

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = (
        'campaign_id', 'campaign_name', 'campaign_url_name', 'campaing_title', 
        'campaing_short_description', 'campaing_detailed_description', 
        'start_date', 'end_date', 'rate_enabled', 'category_type', 
        'form_enabled', 'allow_drawings'
    )
    search_fields = ('campaign_name', 'campaign_url_name', 'category_type__name')
    list_filter = ('category_type', 'start_date', 'end_date')
    
    filter_horizontal = ('geoserver_layers',)  # Enable the dual-pane selection UI for layers

    def get_form(self, request, obj=None, **kwargs):
        # Update the GeoserverLayers whenever the form is loaded
        GeoserverLayers.update_layers()
        return super().get_form(request, obj, **kwargs)


class FormProxy(Form):
    #extend the Form model to include the campaign name
    class Meta:
        proxy = True
        verbose_name = 'Feedback Details'
        verbose_name_plural = 'Feedback Details'

class FormAdmin(geoadmin.OSMGeoAdmin):
    list_display = ('campaign', 'feedback_text', 'feedback_category', 'feedback_geometry', 'created_at')
    search_fields = ('campaign__campaign_name', 'feedback_text', 'feedback_category')
    list_filter = ('campaign', 'created_at', 'feedback_category', 'campaign__category_type')  # Add category_type filter here

admin.site.register(FormProxy, FormAdmin)


class CampaignFeedbackProxy(Campaign):
    class Meta:
        proxy = True
        verbose_name = 'Feedback Export'
        verbose_name_plural = 'Feedback Exports'


class CampaignFeedbackExportAdmin(admin.ModelAdmin):
    list_display = ('campaign_name', 'total_feedback', 'mean_rating')
    actions = ['export_feedback_to_csv', 'export_feedback_to_geojson']
    search_fields  = ('campaign_name',) 
    # Display the total number of feedback entries for each campaign
    def total_feedback(self, obj):
        return Form.objects.filter(campaign=obj).count()

    total_feedback.short_description = 'Total Feedback'
    def mean_rating(self, obj):
        # Calculate the average rating for the campaign
        mean_rating = Rating.objects.filter(campaign=obj).aggregate(Avg('rating'))['rating__avg']
        if mean_rating is not None:
            return round(mean_rating, 2)  # Round to 2 decimal places
        return 'No Ratings'

    mean_rating.short_description = 'Mean Rating'
    # Action to export merged feedback from multiple campaigns to CSV
    def export_feedback_to_csv(self, request, queryset):
        # Ensure at least one campaign is selected
        if queryset.count() == 0:
            self.message_user(request, "Please select at least one campaign to export.", level='error')
            return None

        # Merge feedback from all selected campaigns
        feedbacks = Form.objects.filter(campaign__in=queryset)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="merged_feedback.csv"'

        writer = csv.writer(response)
        writer.writerow(['Campaign Name', 'Feedback Text', 'Category', 'Feedback Location', 'Created At'])

        for form in feedbacks:
            writer.writerow([
                form.campaign.campaign_name,
                form.feedback_text,
                form.feedback_category,
                form.feedback_location,
                form.created_at
            ])

        return response

    export_feedback_to_csv.short_description = 'Export merged feedback to CSV'

    # Action to export merged feedback from multiple campaigns to GeoJSON
    def export_feedback_to_geojson(self, request, queryset):
        # Ensure at least one campaign is selected
        if queryset.count() == 0:
            self.message_user(request, "Please select at least one campaign to export.", level='error')
            return None

        # Merge feedback from all selected campaigns
        feedbacks = Form.objects.filter(campaign__in=queryset)

        geojson_data = {
            "type": "FeatureCollection",
            "features": []
        }

        for form in feedbacks:
            feature = {
                "type": "Feature",
                "geometry": json.loads(form.feedback_location.geojson),  # Convert geometry to GeoJSON
                "properties": {
                    "campaign_name": form.campaign.campaign_name,
                    "feedback_text": form.feedback_text,
                    "feedback_category": form.feedback_category,
                    "created_at": form.created_at.isoformat(),
                }
            }
            geojson_data["features"].append(feature)

        response = HttpResponse(json.dumps(geojson_data), content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="merged_feedback.geojson"'

        return response

    export_feedback_to_geojson.short_description = 'Export merged feedback to GeoJSON'

# Register the proxy model with the custom admin
admin.site.register(CampaignFeedbackProxy, CampaignFeedbackExportAdmin)
admin.site.site_title = "TOSCA Dashboard"
admin.site.site_header = "TOSCA Dashboard"