from django.urls import path, include
from django_filters import rest_framework

from rest_framework import routers, serializers, viewsets, generics

from artistboard.models import Artist, Event, Show, Season, Link


class ArtistSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Artist
        fields = "__all__"


class ArtistFilter(rest_framework.FilterSet):
    class Meta:
        model = Artist
        fields = ["name", "style", "info"]


class ArtistViewSet(viewsets.ModelViewSet, generics.DestroyAPIView):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    filter_backends = [rest_framework.DjangoFilterBackend]
    filterset_class = ArtistFilter


class LinkSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Link
        fields = "__all__"


class LinkViewSet(viewsets.ModelViewSet, generics.DestroyAPIView):
    queryset = Link.objects.all()
    serializer_class = LinkSerializer


class SeasonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Season
        fields = "__all__"


class SeasonViewSet(viewsets.ModelViewSet, generics.DestroyAPIView):
    queryset = Season.objects.all()
    serializer_class = SeasonSerializer


class ShowSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Show
        fields = "__all__"


class ShowViewSet(viewsets.ModelViewSet, generics.DestroyAPIView):
    queryset = Show.objects.all()
    serializer_class = ShowSerializer


class EventSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"


class EventViewSet(viewsets.ModelViewSet, generics.DestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


router = routers.DefaultRouter()
router.register(r"artists", ArtistViewSet)
router.register(r"links", LinkViewSet)
router.register(r"events", EventViewSet)
router.register(r"shows", ShowViewSet)
router.register(r"seasons", SeasonViewSet)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
