from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
    throttle_classes,
)
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from api.models import Charity, Donation, SiteStats
from api.serializers import (
    CharitySerializer,
    DonationCreateSerializer,
    DonationReceiptSerializer,
    DonationSerializer,
    ExchangeRateSerializer,
    SiteStatsSerializer,
)
from api.throttling import DonationReportThrottle, ReceiptUploadThrottle
from api.validators import ERROR_FILE_TOO_LARGE, MAX_RECEIPT_REQUEST_SIZE


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request: Request) -> Response:
    """Basic liveness probe"""
    return Response({"status": "ok"})


@api_view(["GET"])
@permission_classes([AllowAny])
def site_stats(request: Request) -> Response:
    """Public campaign stats"""
    stats = SiteStats.load()
    largest_donation = (
        Donation.objects.filter(verified__isnull=False).order_by("-amount").first()  # ty: ignore[unresolved-attribute]
    )
    charities_donated_to = (
        Charity.objects.filter(  # ty: ignore[unresolved-attribute]
            donations__verified__isnull=False
        )
        .distinct()
        .count()
    )
    serializer = SiteStatsSerializer(
        {
            "verified_total": Donation.verified_total(),
            "verified_count": Donation.verified_count(),
            "largest_donation": largest_donation.amount if largest_donation else None,
            "charities_donated_to": charities_donated_to,
            "goals_scored": stats.goals_scored,
            "ca_exchange_rate": stats.ca_exchange_rate,
        }
    )
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def exchange_rate(request: Request) -> Response:
    """Current exchange rate"""
    serializer = ExchangeRateSerializer(
        {"ca_exchange_rate": SiteStats.load().ca_exchange_rate}
    )
    return Response(serializer.data)


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
@throttle_classes([DonationReportThrottle])
def donations(request: Request) -> Response:
    """List verified donations, or report a new one as a draft"""
    if request.method == "POST":
        serializer = DonationCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        if serializer.save() is None:
            # A banned word was found: the serializer silently dropped the
            # submission. Feign success with an empty body.
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    serializer = DonationSerializer(Donation.verified_donations(), many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([ReceiptUploadThrottle])
def receipts(request: Request) -> Response:
    """Accept a proof-of-donation upload and return its claim token"""
    # Reject oversized bodies up front, before Django streams the whole upload
    # to a temp file (the serializer's size check only runs after that).
    content_length = request.META.get("CONTENT_LENGTH")
    if content_length:
        try:
            too_large = int(content_length) > MAX_RECEIPT_REQUEST_SIZE
        except ValueError:
            too_large = False
        if too_large:
            return Response(
                {"file": [ERROR_FILE_TOO_LARGE]},
                status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            )
    serializer = DonationReceiptSerializer(
        data=request.data, context={"request": request}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([AllowAny])
def charities(request: Request) -> Response:
    """List all approved charities"""
    serializer = CharitySerializer(Charity.approved_charities(), many=True)
    return Response(serializer.data)
