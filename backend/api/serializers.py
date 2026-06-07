from pathlib import Path

from rest_framework import serializers

from api.models import Charity, Donation, DonationReceipt

# Mirror the frontend dropzone limits
MAX_RECEIPT_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_RECEIPT_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".heic",
    ".heif",
    ".pdf",
}


class SiteStatsSerializer(serializers.Serializer):
    """Public, read-only campaign totals"""

    verified_total = serializers.DecimalField(max_digits=10, decimal_places=2)
    verified_count = serializers.IntegerField()
    goals_scored = serializers.IntegerField()


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

    Accepts the file and returns the new receipt's id.
    """

    class Meta:
        model = DonationReceipt
        fields = ["id", "created", "file"]
        read_only_fields = ["id", "created"]
        extra_kwargs = {"file": {"write_only": True}}

    def validate_file(self, file):
        if file.size > MAX_RECEIPT_SIZE:
            raise serializers.ValidationError(
                f"File is too large. Maximum size is "
                f"{MAX_RECEIPT_SIZE // (1024 * 1024)}MB."
            )
        if Path(file.name).suffix.lower() not in ALLOWED_RECEIPT_EXTENSIONS:
            raise serializers.ValidationError("Only image and PDF files are accepted.")
        return file


class DonationCreateSerializer(serializers.ModelSerializer):
    """Write-only intake for a fan-reported donation"""

    charity = serializers.CharField(max_length=255)
    receipt = serializers.PrimaryKeyRelatedField(
        queryset=DonationReceipt.objects.all(),  # ty: ignore[unresolved-attribute]
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Donation
        fields = ["id", "amount", "name", "charity", "receipt"]

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

    def create(self, validated_data):
        name = validated_data.pop("charity").strip()
        charity = Charity.objects.filter(name__iexact=name).first()  # ty: ignore[unresolved-attribute]
        if charity is None:
            charity = Charity.objects.create(name=name)  # ty: ignore[unresolved-attribute]
        return Donation.objects.create(charity=charity, **validated_data)  # ty: ignore[unresolved-attribute]
