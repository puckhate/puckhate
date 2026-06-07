from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from api.models import Charity, Donation, SiteStats
from api.serializers import (
    CharitySerializer,
    DonationCreateSerializer,
    DonationReceiptSerializer,
    DonationSerializer,
    SiteStatsSerializer,
)


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request: Request) -> Response:
    """Basic liveness probe"""
    return Response({"status": "ok"})


@api_view(["GET"])
@permission_classes([AllowAny])
def site_stats(request: Request) -> Response:
    """Public campaign stats"""
    serializer = SiteStatsSerializer(
        {
            "verified_total": Donation.verified_total(),
            "verified_count": Donation.verified_count(),
            "goals_scored": SiteStats.load().goals_scored,
        }
    )
    return Response(serializer.data)


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def donations(request: Request) -> Response:
    """List verified donations, or report a new one as a draft"""
    if request.method == "POST":
        serializer = DonationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    serializer = DonationSerializer(Donation.verified_donations(), many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([AllowAny])
def receipts(request: Request) -> Response:
    """Accept a proof-of-donation upload and return its id"""
    serializer = DonationReceiptSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([AllowAny])
def charities(request: Request) -> Response:
    """List all approved charities"""
    serializer = CharitySerializer(Charity.approved_charities(), many=True)
    return Response(serializer.data)
