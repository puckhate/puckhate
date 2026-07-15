import logging
from decimal import ROUND_HALF_UP, Decimal

from rest_framework import serializers

from django.db import IntegrityError

from api.banned_words import contains_banned_word
from api.models import Charity, Donation, DonationReceipt, SiteStats
from api.validators import (
    ERROR_FILE_TOO_LARGE,
    ERROR_FILE_TYPE_INVALID,
    has_allowed_file_extension,
    has_allowed_file_header,
    has_allowed_file_size,
)

logger = logging.getLogger(__name__)


class SiteStatsSerializer(serializers.Serializer):
    """Public, read-only campaign totals"""

    verified_total = serializers.DecimalField(max_digits=10, decimal_places=2)
    verified_count = serializers.IntegerField()
    goals_scored = serializers.IntegerField()
    ca_exchange_rate = serializers.DecimalField(max_digits=10, decimal_places=4)


class ExchangeRateSerializer(serializers.Serializer):
    """Public, read-only current exchange rate"""

    ca_exchange_rate = serializers.DecimalField(max_digits=10, decimal_places=4)


class DonationSerializer(serializers.ModelSerializer):
    """Public, read-only view of a single verified donation"""

    name = serializers.CharField(source="get_name_display", read_only=True)
    charity = serializers.CharField(source="charity.name", read_only=True)

    class Meta:
        model = Donation
        fields = ["id", "created", "amount", "name", "charity"]


class CharitySerializer(serializers.ModelSerializer):
    """Public, read-only view of an approved charity"""

    class Meta:
        model = Charity
        fields = ["id", "name", "url"]


class DonationReceiptSerializer(serializers.ModelSerializer):
    """Write-only intake of a proof-of-donation upload.

    Accepts the file and returns the new receipt's claim token.
    """

    class Meta:
        model = DonationReceipt
        fields = ["token", "created", "file"]
        read_only_fields = ["token", "created"]
        extra_kwargs = {"file": {"write_only": True}}

    def validate_file(self, file):
        if not has_allowed_file_size(file.size):
            raise serializers.ValidationError(ERROR_FILE_TOO_LARGE)
        if not has_allowed_file_extension(file.name):
            raise serializers.ValidationError(ERROR_FILE_TYPE_INVALID)
        head = file.read(32)
        file.seek(0)
        if not has_allowed_file_header(head):
            raise serializers.ValidationError(ERROR_FILE_TYPE_INVALID)
        return file


class DonationCreateSerializer(serializers.ModelSerializer):
    """Write-only intake for a fan-reported donation"""

    charity = serializers.CharField(max_length=255)
    currency = serializers.ChoiceField(
        choices=["USD", "CAD"],
        default="USD",
    )
    receipt = serializers.SlugRelatedField(
        slug_field="token",
        queryset=DonationReceipt.objects.all(),  # ty: ignore[unresolved-attribute]
        required=False,
        allow_null=True,
    )

    # Set True by validate() when a banned word is present in the name or charity fileds
    banned_word_present = False

    class Meta:
        model = Donation
        fields = ["id", "amount", "currency", "name", "charity", "receipt"]

    def validate(self, attrs):
        """Flag submissions containing a banned word

        Do not raise an exception, the user should not know they were banned
        """
        for field in ("name", "charity"):
            matched = contains_banned_word(attrs.get(field, ""))
            if matched:
                logger.info(
                    "Donation discarded by banned-word filter (matched: %r)", matched
                )
                self.banned_word_present = True
                break
        return attrs

    def validate_amount(self, amount):
        if amount <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return amount

    def validate_receipt(self, receipt):
        # refuse receipt already claimed by another donation.
        if (
            receipt is not None
            and Donation.objects.filter(  # ty: ignore[unresolved-attribute]
                receipt=receipt
            ).exists()
        ):
            raise serializers.ValidationError("This receipt has already been used.")
        return receipt

    def save(self, **kwargs):
        # If the banned word sentinel is set, return None instead of an instance.
        if self.banned_word_present:
            return None
        return super().save(**kwargs)

    def create(self, validated_data):
        # All amounts are stored in USD. Convert to USD using the current rate
        currency = validated_data.pop("currency", "USD")
        rate = Decimal("1.0000")
        if currency == "CAD":
            rate = SiteStats.load().ca_exchange_rate
            # The field validator keeps this positive, but guard at the point of
            # use too: a zero/negative rate would otherwise 500 (division) or
            # store a negative amount that corrupts the totals.
            if rate <= 0:
                raise serializers.ValidationError(
                    {"currency": ["Currency conversion is temporarily unavailable."]}
                )
            validated_data["amount"] = (validated_data["amount"] / rate).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        validated_data["effective_exchange_rate"] = rate
        name = validated_data.pop("charity").strip()
        charity = Charity.objects.filter(name__iexact=name).first()  # ty: ignore[unresolved-attribute]
        if charity is None:
            charity = Charity.objects.create(name=name)  # ty: ignore[unresolved-attribute]
        try:
            return Donation.objects.create(charity=charity, **validated_data)  # ty: ignore[unresolved-attribute]
        except IntegrityError:
            # Two donations raced to claim the same receipt
            raise serializers.ValidationError(
                {"receipt": ["This receipt has already been used."]}
            )
