"""View module for handling requests about park areas"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from kennywoodapi.models import Customer, Attraction, Itinerary
from .attraction import AttractionSerializer


class ItinerarySerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for park areas

    Arguments:
        serializers
    """
    class Meta:
        model = Itinerary
        url = serializers.HyperlinkedIdentityField(
            view_name='itinerary',
            lookup_field='id'
        )
        fields = ('id', 'url', 'attraction', 'starttime')
        depth = 2


class ItineraryView(ViewSet):
    """Itinerary for Kennywood Amusement Park customers"""

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized Itinerary instance
        """
        newarea = Itinerary()
        attraction = Attraction.objects.get(pk=request.data["attraction_id"])
        customer = Customer.objects.get(user=request.auth.user)

        newarea.attraction = attraction
        newarea.customer = customer
        newarea.starttime = request.data["starttime"]
        newarea.save()

        serializer = ItinerarySerializer(newarea, context={'request': request})

        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single park area

        Returns:
            Response -- JSON serialized park area instance
        """
        try:
            area = Itinerary.objects.get(pk=pk)
            serializer = ItinerarySerializer(area, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """Handle PUT requests for an individual itinerary item

        Returns:
            Response -- Empty body with 204 status code
        """
        itinerary = Itinerary.objects.get(pk=pk)
        itinerary.starttime = request.data["starttime"]
        itinerary.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single park are

        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            itinerary = Itinerary.objects.get(pk=pk)
            itinerary.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Itinerary.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """Handle GET requests to itinerary resource

        Returns:
            Response -- JSON serialized list of customer itineraries
        """
        customer = Customer.objects.get(user=request.auth.user)
        itineraries = Itinerary.objects.filter(customer=customer)
        serializer = ItinerarySerializer(
            itineraries, many=True, context={'request': request})
        return Response(serializer.data)
