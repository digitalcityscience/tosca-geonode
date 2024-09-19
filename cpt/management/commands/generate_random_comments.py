import random
import math
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from django.utils import timezone
from cpt.models import Form, Campaign

class Command(BaseCommand):
    help = "Generate random Form instances with points within 60 km of a base point"

    def add_arguments(self, parser):
        # Command argument for the base point (longitude, latitude)
        parser.add_argument('base_lon', type=float, help="Base longitude coordinate")
        parser.add_argument('base_lat', type=float, help="Base latitude coordinate")
        parser.add_argument('campaign_id', type=int, help="ID of the campaign to associate the forms with")
        parser.add_argument('num_points', type=int, help="Number of random points to generate")

    def handle(self, *args, **options):
        base_lon = options['base_lon']
        base_lat = options['base_lat']
        campaign_id = options['campaign_id']
        num_points = options['num_points']

        try:
            campaign = Campaign.objects.get(campaign_id=campaign_id)  # Use campaign_id here
        except Campaign.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Campaign with ID {campaign_id} does not exist."))
            return

        # Generate random points and create forms
        for _ in range(num_points):
            point = self.generate_random_point(base_lon, base_lat, 60000)  # 60 km radius
            self.create_form(campaign, point)

        self.stdout.write(self.style.SUCCESS(f"Successfully created {num_points} random forms."))

    def generate_random_point(self, base_lon, base_lat, radius_meters):
        """
        Generate a random point within a specified radius around a base point (longitude, latitude).
        :param base_lon: Base longitude
        :param base_lat: Base latitude
        :param radius_meters: Radius around the base point in meters
        :return: Point object representing the random geographic point
        """
        # Convert radius from meters to degrees (approximation)
        radius_degrees = radius_meters / 111320  # Rough approximation for degrees in latitude/longitude

        # Generate random angle and distance within the radius
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(0, radius_degrees)

        # Calculate new coordinates
        delta_lon = distance * math.cos(angle) / math.cos(math.radians(base_lat))
        delta_lat = distance * math.sin(angle)

        new_lon = base_lon + delta_lon
        new_lat = base_lat + delta_lat

        return Point(new_lon, new_lat, srid=4326)

    def create_form(self, campaign, point):
        """
        Create a Form instance with the given campaign and geographic point.
        :param campaign: Campaign object
        :param point: GEOSGeometry Point object
        """
        form = Form.objects.create(
            campaign=campaign,
            feedback_location=point,
            feedback_text='Randomly generated feedback',
            feedback_category='general',
            created_at=timezone.now(),
        )
        form.save()
