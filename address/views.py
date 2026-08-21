from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.exceptions import ValidationError

from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAdminUser, AllowAny

from drf_spectacular.utils import (
    extend_schema, 
    OpenApiResponse, 
    OpenApiExample
)

from address.models import (
    Country, 
    Region,
    SettlementType,
    Settlement,
    District,
    StreetType,
    Street,
    Address,
    BuildingType,
    Building
)


class CountryAPIView(APIView):
    SAFE_METHODS = "GET"

    def get_permissions(self):
        if self.request.method not in self.SAFE_METHODS:
            return [IsAdminUser()]
        return [AllowAny()]

    class OutputListSerializer(serializers.ModelSerializer):
        class Meta:
            model = Country
            fields = "__all__"

    @extend_schema(
        responses={
            200: OpenApiResponse(
                response=OutputListSerializer(many=True),
                description="List of countries",
            ),
        },
        examples=[
            OpenApiExample(
                name="Countries",
                value=[
                    {"id": 1, "iso_code": "RUS", "name": "Russia"},
                    {"id": 2, "iso_code": "USA", "name": "United States of America"},
                ],
                response_only=True,
                status_codes=["200"],
            )
        ],
        description="Get list of countries",
        tags=["Countries"],
    )
    def get(self, request):
        countries = Country.objects.all()
        serializer = self.OutputListSerializer(countries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    class InputCreateSerializer(serializers.ModelSerializer):
        class Meta:
            model = Country
            fields = ["iso_code", "name"]
            extra_kwargs = {
                "iso_code": {"validators": []},
                "name": {"validators": []},
            }

    @extend_schema(
        request=InputCreateSerializer(many=True),
        responses={
            201: OpenApiResponse(description="Countries created successfully"),
            400: OpenApiResponse(description="Invalid input"),
        },
        examples=[
            OpenApiExample(
                name="Create single country",
                value=[{"iso_code": "DE", "name": "Germany"}],
                request_only=True,
            ),
            OpenApiExample(
                name="Create multiple countries",
                value=[
                    {"iso_code": "DE", "name": "Germany"},
                    {"iso_code": "FR", "name": "France"},
                ],
                request_only=True,
            ),
        ],
        description="Create one or several countrys",
        tags=["Countries"],
    )
    def post(self, request):
        payload = request.data
        if isinstance(payload, dict):
            payload = [payload]

        serializer = self.InputCreateSerializer(data=payload, many=True)

        if serializer.is_valid(raise_exception=True):
            validated_data = serializer.validated_data

            existing_iso_codes = set(Country.objects.values_list("iso_code", flat=True))
            existing_names = set(Country.objects.values_list("name", flat=True))

            to_create = []
            seen_iso_codes = set()
            seen_names = set()

            for item in validated_data:
                iso = item["iso_code"]
                name = item["name"]

                if (
                    iso not in existing_iso_codes
                    and iso not in seen_iso_codes
                    and name not in existing_names
                    and name not in seen_names
                ):
                    to_create.append(Country(**item))
                    seen_iso_codes.add(iso)
                    seen_names.add(name)

            with transaction.atomic():
                Country.objects.bulk_create(to_create)
                return Response({"created_count": len(to_create)}, status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class CountryDetailAPIView(APIView):
    SAFE_METHODS = ["PATCH", "DELETE"]

    def get_permissions(self):
        if self.request.method in self.SAFE_METHODS:
            return [IsAdminUser()]
        return [AllowAny()]

    class InputUpdateSerializer(serializers.ModelSerializer):
        class Meta:
            model = Country
            fields = ["iso_code", "name"]

    @extend_schema(
        request=InputUpdateSerializer(),
        responses={
            200: OpenApiResponse(description="Country updated"),
            400: OpenApiResponse(description="Invalid input"),
            404: OpenApiResponse(description="Country not found"),
        },
        examples=[
            OpenApiExample(
                name="Update country",
                value={"iso_code": "DE", "name": "Deutschland"},
                request_only=True,
            )
        ],
        description="Update (Patch) country by its pk",
        tags=["Countries"],
    )
    @permission_classes([IsAdminUser])
    def patch(self, request, country_id):
        country = get_object_or_404(Country, id=country_id)

        serializer = self.InputUpdateSerializer(
            country, data=request.data, partial=True
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response("Country updated", status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={
            204: OpenApiResponse(description="Country deleted"),
            404: OpenApiResponse(description="Country not found"),
        },
        description="Delete country by its pk",
        tags=["Countries"],
    )
    @permission_classes([IsAdminUser])
    def delete(self, request, country_id: int):
        country = get_object_or_404(Country, pk=country_id)

        country.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class RegionAPIView(APIView):
    SAFE_METHODS = ["GET"]

    def get_permissions(self):
        if self.request.method not in self.SAFE_METHODS:
            return [IsAdminUser()]
        return [AllowAny()]

    
    class OutputListSerializer(serializers.ModelSerializer):
        class Meta:
            model = Region
            fields = ["id", "name"]

    @extend_schema(
        responses={
            200: OpenApiResponse(
                response=OutputListSerializer(many=True),
                description="Regions for a country",
            ),
            404: OpenApiResponse(description="Country not found"),
        },
        examples=[
            OpenApiExample(
                name="Get list of regions",
                value=[
                    {"id": 1, "name": "Bavaria"},
                    {"id": 2, "name": "Berlin"},
                ],
                response_only=True,
                status_codes=["200"],
            )
        ],
        tags=["Regions"],
    )
    def get(self, request, country_id:int):
        country = get_object_or_404(Country, id=country_id)

        regions = Region.objects.filter(country=country)

        output_serializer = self.OutputListSerializer(regions, many=True)
        return Response(output_serializer.data, status=status.HTTP_200_OK)


    class InputCreateSerializer(serializers.Serializer):
        country_id = serializers.IntegerField()
        regions = serializers.ListField(
            allow_empty=False,
        )

    @extend_schema(
        request=InputCreateSerializer(),
        responses={
            201: OpenApiResponse(description="Regions created"),
            404: OpenApiResponse(description="Country not found"),
        },
        examples=[
            OpenApiExample(
                name="Create regions for a country",
                value={
                    "country_id": 0,
                    "regions": [{"region_name": "region_code"}],
                },
                request_only=True,
                status_codes=["201"],
            )
        ],
        tags=["Regions"],
    )
    def post(self, request):
        serializer = self.InputCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        country_id = serializer.validated_data["country_id"]
        country = get_object_or_404(Country, id=country_id)

        regions_data = serializer.validated_data["regions"]

        country_regions_names = set(
            Region.objects.filter(country_id=country_id).values_list("name", flat=True)
        )
        country_regions_codes = set(
            Region.objects.filter(country_id=country_id).values_list("code", flat=True)
        )
        seen_names = set()
        seen_codes = set()
        to_create = []

        for region in regions_data:
            name = region["name"]
            code = region["code"]
            if (
                name not in country_regions_names and 
                code not in country_regions_codes and
                name not in seen_names and
                code not in seen_codes
                ):
                to_create.append(Region(name=name, code=code, country=country))
                seen_names.add(name)
                seen_codes.add(code)

        with transaction.atomic():
            Region.objects.bulk_create(to_create)

        return Response({"created_count": len(to_create)}, status=status.HTTP_201_CREATED)


    class InputDeleteSerializer(serializers.Serializer):
        regions_id = serializers.ListField()

    @extend_schema(
        responses={
            204: OpenApiResponse(description="Regions deleted"),
            400: OpenApiResponse(description="Invalid input"),
        },
        examples=[
            OpenApiExample(
                name="Delete regions",
                value={"regions_id": [1, 2, 3]},
                request_only=True,
            )
        ],
        description="Delete several regions by its pk",
        tags=["Regions"],
    )
    def delete(self, request):
        serializer = self.InputDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        Region.objects.filter(id__in=serializer.validated_data["regions_id"]).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RegionDetailAPIView(APIView):
    SAFE_METHODS = ["GET"]

    def get_permissions(self):
        if self.request.method not in self.SAFE_METHODS:
            return [IsAdminUser()]
        return [AllowAny()]


    class InputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Region
            fields = ["country", "name", "code"]

    @extend_schema(
        request=InputSerializer(),
        responses={
            200: OpenApiResponse(description="Region updated"),
            400: OpenApiResponse(description="Invalid input"),
            404: OpenApiResponse(description="Region not found"),
        },
        examples=[
            OpenApiExample(
                name="Update country",
                value={"country": 1, "name": "Some name"},
                request_only=True,
            )
        ],
        description="Update (Patch) region by its pk",
        tags=["Regions"],
    )
    def patch(self, request, region_id: int):
        region = get_object_or_404(Region, id=region_id)

        serializer = self.InputSerializer(region, data=request.data, partial=True)
        serializer.is_valid()
        serializer.save()
        return Response(status=status.HTTP_200_OK)


class SettlementTypesAPIView(APIView):
    SAFE_METHODS = ["GET"]

    def get_permissions(self):
        if self.request.method not in self.SAFE_METHODS:
            return [IsAdminUser()]
        return [AllowAny()]


    class OutputListSerializer(serializers.ModelSerializer):
        class Meta:
            model = Settlement
            fields = ["id", "name"]

    def get(self, request):
        settlement_types = SettlementType.objects.all()
        output_serializer = self.OutputListSerializer(settlement_types, many=True)
        return Response(output_serializer.data, status=status.HTTP_200_OK)


    class InputCreateSerializer(serializers.Serializer):
        settlement_types = serializers.ListField(
            child=serializers.CharField()
        )

    def post(self, request):
        input_serializer = self.InputCreateSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        settlement_types_data = input_serializer.validated_data["settlement_types"]

        settlements_types = set(
            SettlementType.objects.all().values_list("name", flat=True)
        )
        seen_names = set()
        to_create = []

        for name in settlement_types_data:
            if name not in settlements_types:
                to_create.append(SettlementType(name=name))
                seen_names.add(name)

        with transaction.atomic():
            SettlementType.objects.bulk_create(to_create)

        return Response({"created_count": len(to_create)}, status=status.HTTP_201_CREATED)


    class InputDeleteSerializer(serializers.Serializer):
        settlement_types_id = serializers.ListField()

    @extend_schema(
        responses={
            204: OpenApiResponse(description="Settlements deleted"),
            400: OpenApiResponse(description="Invalid input"),
        },
        examples=[
            OpenApiExample(
                name="Delete settlements",
                value={"settlements_id": [1, 2, 3]},
                request_only=True,
            )
        ],
        description="Delete several settlements by its pk",
        tags=["Settlements"],
    )
    def delete(self, request):
        serializer = self.InputDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        SettlementType.objects.filter(id__in=serializer.validated_data["settlement_types_id"]).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SettlementTypeDetailAPIView(APIView):
    SAFE_METHODS = ["GET"]

    def get_permissions(self):
        if self.request.method not in self.SAFE_METHODS:
            return [IsAdminUser()]
        return [AllowAny()]


    class InputUpdateSerializer(serializers.ModelSerializer):
        class Meta:
            model = Region
            fields = ["name"]

    @extend_schema(
        request=InputUpdateSerializer(),
        responses={
            200: OpenApiResponse(description="Settlement type updated"),
            400: OpenApiResponse(description="Invalid input"),
            404: OpenApiResponse(description="Settlement type not found"),
        },
        examples=[
            OpenApiExample(
                name="Update Settlement type",
                value={"settlement_type_id": 1, "name": "New name"},
                request_only=True,
            )
        ],
        description="Update (Patch) settlement type by its pk",
        tags=["SettlementType"],
    )
    def patch(self, request, settlement_type_id: int):
        settlement_type = get_object_or_404(SettlementType, id=settlement_type_id)

        serializer = self.InputUpdateSerializer(settlement_type, data=request.data, partial=True)
        serializer.is_valid()
        serializer.save()
        return Response(status=status.HTTP_200_OK)


class SettlementAPIView(APIView):
    SAFE_METHODS = ["GET"]

    def get_permissions(self):
        if self.request.method not in self.SAFE_METHODS:
            return [IsAdminUser()]

        return [AllowAny()]

    class OutputListSerializer(serializers.ModelSerializer):
        settlement_type = serializers.CharField(
            source="settlement_type.name",
            read_only=True,
        )

        class Meta:
            model = Settlement
            fields = ["id", "name", "settlement_type"]

    def get(self, request, region_id: int):
        region = get_object_or_404(Region, id=region_id)

        settlements = (
            Settlement.objects.filter(region=region).select_related("settlement_type").order_by("name")
        )

        output_serializer = self.OutputListSerializer(
            settlements,
            many=True,
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )
    

    class InputCreateSerializer(serializers.Serializer):
        class SettlementInputSerializer(serializers.Serializer):
            name = serializers.CharField(max_length=255)
            settlement_type = serializers.PrimaryKeyRelatedField(
                queryset=SettlementType.objects.all(),
            )
                
        settlements = SettlementInputSerializer(
            many=True,
            allow_empty=False,
        )

    def post(self, request, region_id: int):
        input_serializer = self.InputCreateSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        region = get_object_or_404(Region, id=region_id)
        settlements_data = input_serializer.validated_data["settlements"]

        existing_names = set(
            Settlement.objects.filter(region=region).values_list("name", flat=True)
        )

        seen_names = set()
        to_create = []

        for settlement_data in settlements_data:
            name = settlement_data["name"].strip()
            settlement_type = settlement_data["settlement_type"]

            if name not in existing_names and name not in seen_names:
                to_create.append(
                    Settlement(
                        name=name,
                        settlement_type=settlement_type,
                        region=region,
                    )
                )
                seen_names.add(name)

        with transaction.atomic():
            Settlement.objects.bulk_create(to_create)

        return Response({"created_count": len(to_create)}, status=status.HTTP_201_CREATED)


    class InputDeleteSerializer(serializers.Serializer):
        settlements_id = serializers.ListField(
            child=serializers.IntegerField()
        )
    
    def delete(self, request):
        serializer = self.InputDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        Settlement.objects.filter(id__in=serializer.validated_data["settlements_id"]).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SettlementDetailAPIView(APIView):
    SAFE_METHODS = ["GET"]

    def get_permissions(self):
        if self.request.method not in self.SAFE_METHODS:
            return [IsAdminUser()]
        return [AllowAny()]


    class InputUpdateSerializer(serializers.ModelSerializer):
        class Meta:
            model = SettlementType
            fields = ["name", "settlement_type"]


    def patch(self, request, settlement_id: int):
        settlement = get_object_or_404(Settlement, id=settlement_id)

        serializer = self.InputUpdateSerializer(settlement, data=request.data, partial=True)
        serializer.is_valid()
        serializer.save()
        return Response(status=status.HTTP_200_OK)

    

class DistrictAPIView(APIView):
    SAFE_METHODS = ["GET"]

    def get_permissions(self):
        if self.request.method not in self.SAFE_METHODS:
            return [IsAdminUser()]

        return [AllowAny()]

    class OutputListSerializer(serializers.ModelSerializer):
        class Meta:
            model = District
            fields = ["id", "name"]

    def get(self, request, settlement_id: int):
        settlement = get_object_or_404(Settlement, id=settlement_id)

        districts = (
            District
            .objects
            .filter(settlement=settlement)
            .order_by("name")
        )

        output_serializer = self.OutputListSerializer(districts, many=True)

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )


    class InputCreateSerializer(serializers.Serializer):
        districts = serializers.ListField(
            child=serializers.CharField()
        )

    def post(self, request, settlement_id:int):
        input_serializer = self.InputCreateSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        settlement = get_object_or_404(Settlement, id=settlement_id)
        districts_data = input_serializer.validated_data["districts"]

        existing_names = set(
            District
            .objects
            .filter(settlement=settlement)
            .values_list("name", flat=True)
        )

        seen_names = set()
        to_create = []

        for name in districts_data:
            if name not in existing_names and name not in seen_names:
                to_create.append(
                    District(
                        name=name,
                        settlement=settlement
                    )
                )
                seen_names.add(name)

        with transaction.atomic():
            District.objects.bulk_create(to_create)

        return Response({"created_count": len(to_create)}, status=status.HTTP_201_CREATED)


    class InputDeleteSerializer(serializers.Serializer):
        districts_id = serializers.ListField(
            child=serializers.IntegerField()
        )
    
    def delete(self, request, settlement_id:int):
        serializer = self.InputDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        District.objects.filter(id__in=serializer.validated_data["districts_id"]).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DistrictDetailAPIView(APIView):
    SAFE_METHODS = ["GET"]

    def get_permissions(self):
        if self.request.method not in self.SAFE_METHODS:
            return [IsAdminUser()]
        return [AllowAny()]


    class InputUpdateSerializer(serializers.ModelSerializer):
        class Meta:
            model = District
            fields = ["name", "settlement"]


    def patch(self, request, district_id: int):
        district = get_object_or_404(District, id=district_id)

        serializer = self.InputUpdateSerializer(district, data=request.data, partial=True)
        serializer.is_valid()
        serializer.save()
        return Response(status=status.HTTP_200_OK)
    

class StreetTypeAPIView(APIView):
    SAFE_METHODS = ["GET"]

    def get_permissions(self):
        if self.request.method not in self.SAFE_METHODS:
            return [IsAdminUser()]

        return [AllowAny()]

    class OutputListSerializer(serializers.ModelSerializer):
        class Meta:
            model = StreetType
            fields = ["id", "code", "name"]

    def get(self, request):
        street_types = (
            StreetType
            .objects
            .order_by("code")
        )

        output_serializer = self.OutputListSerializer(street_types, many=True)

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )


    class InputCreateSerializer(serializers.Serializer):
        class StreetTypeSerializer(serializers.Serializer):
            name = serializers.CharField()
            code = serializers.CharField()

        street_types = StreetTypeSerializer(
            many=True,
            allow_empty=False
        )

    def post(self, request):
        input_serializer = self.InputCreateSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        street_types_data = input_serializer.validated_data["street_types"]

        existing_names = set(
            StreetType
            .objects
            .values_list("name", flat=True)
        )
        existing_codes = set(
            StreetType
            .objects
            .values_list("code", flat=True)
        )
        seen_names = set()
        seen_codes = set()
        to_create = []

        for street_type in street_types_data:
            name = street_type["name"]
            code = street_type["code"]
            if (
                name not in existing_names and
                name not in seen_names and
                code not in existing_codes and
                code not in seen_codes
            ):
                to_create.append(
                    StreetType(
                        name=name,
                        code=code
                    )
                )
                seen_names.add(name)
                seen_codes.add(code)

        with transaction.atomic():
            StreetType.objects.bulk_create(to_create)

        return Response({"created_count": len(to_create)}, status=status.HTTP_201_CREATED)


    class InputDeleteSerializer(serializers.Serializer):
        street_types_id = serializers.ListField(
            child=serializers.IntegerField()
        )
    
    def delete(self, request):
        serializer = self.InputDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        StreetType.objects.filter(id__in=serializer.validated_data["street_types_id"]).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StreetTypeDetailAPIView(APIView):
    SAFE_METHODS = ["GET"]

    def get_permissions(self):
        if self.request.method not in self.SAFE_METHODS:
            return [IsAdminUser()]
        return [AllowAny()]


    class InputUpdateSerializer(serializers.ModelSerializer):
        class Meta:
            model = StreetType
            fields = ["name", "code"]


    def patch(self, request, street_type_id: int):
        street_type = get_object_or_404(StreetType, id=street_type_id)

        serializer = self.InputUpdateSerializer(street_type, data=request.data, partial=True)
        serializer.is_valid()
        serializer.save()
        return Response(status=status.HTTP_200_OK)


class StreetAPIView(APIView):
    SAFE_METHODS = ["GET"]

    def get_permissions(self):
        if self.request.method not in self.SAFE_METHODS:
            return [IsAdminUser()]

        return [AllowAny()]


    class OutputListSerializer(serializers.ModelSerializer):
        street_type = serializers.SerializerMethodField()

        class Meta:
            model = Street
            fields = ["id", "street_code", "name", "street_type"]

        def get_street_type(self, obj):
            return obj.street_type.name

    def get(self, request, district_id:int):
        district = get_object_or_404(District, id=district_id)

        streets = Street.objects.filter(district=district)
        output_serializer = self.OutputListSerializer(streets, many=True)

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )


    class InputCreateSerializer(serializers.Serializer):
        class StreetSerializer(serializers.Serializer):
            name = serializers.CharField()
            street_code = serializers.CharField()
            street_type = serializers.PrimaryKeyRelatedField(
                queryset=StreetType.objects.all()
            )

        streets = StreetSerializer(
            many=True,
            allow_empty=False
        )

    def post(self, request, district_id:int):
        input_serializer = self.InputCreateSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        district = get_object_or_404(District, id=district_id)
        streets_data = input_serializer.validated_data["streets"]

        existing_names = set(
            Street
            .objects
            .filter(district=district)
            .values_list("name", flat=True)
        )
        existing_codes = set(
            Street
            .objects
            .filter(district=district)
            .values_list("street_code", flat=True)
        )
        seen_names = set()
        seen_codes = set()
        to_create = []

        for street in streets_data:
            name = street["name"]
            street_code = street["street_code"]
            street_type = street["street_type"]
            if (
                name not in existing_names and
                name not in seen_names and
                street_code not in existing_codes and
                street_code not in seen_codes
            ):
                to_create.append(
                    Street(
                        name=name,
                        street_code=street_code,
                        street_type=street_type,
                        district=district
                    )
                )
                seen_names.add(name)
                seen_codes.add(street_code)

        with transaction.atomic():
            Street.objects.bulk_create(to_create)

        return Response({"created_count": len(to_create)}, status=status.HTTP_201_CREATED)


    class InputDeleteSerializer(serializers.Serializer):
        streets_id = serializers.ListField(
            child=serializers.IntegerField()
        )
    
    def delete(self, request, district_id:int):
        serializer = self.InputDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        Street.objects.filter(id__in=serializer.validated_data["streets_id"]).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StreetDetailAPIView(APIView):
    SAFE_METHODS = ["GET"]

    def get_permissions(self):
        if self.request.method not in self.SAFE_METHODS:
            return [IsAdminUser()]
        return [AllowAny()]


    class InputUpdateSerializer(serializers.ModelSerializer):
        class Meta:
            model = Street
            fields = ["name", "street_code", "street_type", "district"]


    def patch(self, request, street_id: int):
        street = get_object_or_404(Street, id=street_id)

        serializer = self.InputUpdateSerializer(street, data=request.data, partial=True)
        serializer.is_valid()
        serializer.save()
        return Response(status=status.HTTP_200_OK)


class AdressAPIView(APIView):
    SAFE_METHODS = ["GET"]

    def get_permissions(self):
        if self.request.method not in self.SAFE_METHODS:
            return [IsAdminUser()]

        return [AllowAny()]


    class OutputListSerializer(serializers.ModelSerializer):
        country = serializers.SerializerMethodField()
        region = serializers.SerializerMethodField()
        settlement = serializers.SerializerMethodField()
        district = serializers.SerializerMethodField()
        street = serializers.SerializerMethodField()

        class Meta:
            model = Address
            fields = [
                "id",
                "country",
                "region",
                "settlement",
                "district",
                "street",
                "house_number",
                "building_name",
                "postal_code",
                "longitude",
                "latitude",
            ]

        def get_country(self, obj):
            return obj.country.name

        def get_region(self, obj):
            return obj.region.name

        def get_settlement(self, obj):
            return obj.settlement.name

        def get_district(self, obj):
            return obj.district.name

        def get_street(self, obj):
            return obj.street.name


    class InputCreateSerializer(serializers.Serializer):
        class AddressSerializer(serializers.Serializer):
            country = serializers.PrimaryKeyRelatedField(
                queryset=Country.objects.all(),
            )
            region = serializers.PrimaryKeyRelatedField(
                queryset=Region.objects.all(),
            )
            settlement = serializers.PrimaryKeyRelatedField(
                queryset=Settlement.objects.all(),
            )
            district = serializers.PrimaryKeyRelatedField(
                queryset=District.objects.all(),
            )

            house_number = serializers.CharField(max_length=50)
            building_name = serializers.CharField(
                max_length=255,
                required=False,
                allow_blank=True,
                default="",
            )
            postal_code = serializers.CharField(max_length=20)

            longitude = serializers.DecimalField(
                max_digits=10,
                decimal_places=6,
                min_value=-180,
                max_value=180,
            )
            latitude = serializers.DecimalField(
                max_digits=9,
                decimal_places=6,
                min_value=-90,
                max_value=90,
            )

        addresses = AddressSerializer(
            many=True,
            allow_empty=False
        )

    def post(self, request, street_id: int):
        serializer = self.InputCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        street = get_object_or_404(
            Street.objects.select_related(
                "district",
                "district__settlement",
                "district__settlement__region",
                "district__settlement__region__country",
            ),
            id=street_id,
        )

        addresses_data = serializer.validated_data["addresses"]
        to_create = []

        for address_data in addresses_data:
            country = address_data["country"]
            region = address_data["region"]
            settlement = address_data["settlement"]
            district = address_data["district"]

            if region.country_id != country.id:
                continue

            if settlement.region_id != region.id:
                continue

            if district.settlement_id != settlement.id:
                continue

            if street.district_id != district.id:
                continue

            to_create.append(
                Address(
                    country=country,
                    region=region,
                    settlement=settlement,
                    district=district,
                    street=street,
                    house_number=address_data["house_number"].strip(),
                    building_name=address_data["building_name"].strip(),
                    postal_code=address_data["postal_code"].strip(),
                    longitude=address_data["longitude"],
                    latitude=address_data["latitude"],
                )
            )

        with transaction.atomic():
            Address.objects.bulk_create(to_create)

        return Response(
            {
                "created_count": len(to_create),
            },
            status=status.HTTP_201_CREATED,
        )


    class InputDeleteSerializer(serializers.Serializer):
        streets_id = serializers.ListField(
            child=serializers.IntegerField()
        )
    
    def delete(self, request, district_id:int):
        serializer = self.InputDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        Street.objects.filter(id__in=serializer.validated_data["streets_id"]).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AddressDetailAPIView(APIView):
    SAFE_METHODS = ["GET"]

    def get_permissions(self):
        if self.request.method not in self.SAFE_METHODS:
            return [IsAdminUser()]
        return [AllowAny()]


    class InputUpdateSerializer(serializers.ModelSerializer):
        class Meta:
            model = Address
            fields = [
                "country",
                "region",
                "settlement",
                "district",
                "street",
                "house_number",
                "building_name",
                "postal_code",
                "longitude",
                "latitude",
            ]

    def patch(self, request, address_id: int):
        address = get_object_or_404(Street, id=address_id)

        serializer = self.InputUpdateSerializer(address, data=request.data, partial=True)
        serializer.is_valid()
        serializer.save()
        return Response(status=status.HTTP_200_OK)

    
class BuildingTypesAPIView(APIView):
    SAFE_METHODS = ["GET"]

    def get_permissions(self):
        if self.request.method not in self.SAFE_METHODS:
            return [IsAdminUser()]
        return [AllowAny()]


    class OutputListSerializer(serializers.ModelSerializer):
        class Meta:
            model = Settlement
            fields = ["id", "name"]

    def get(self, request):
        building_types = BuildingType.objects.all()
        output_serializer = self.OutputListSerializer(building_types, many=True)
        return Response(output_serializer.data, status=status.HTTP_200_OK)


    class InputCreateSerializer(serializers.Serializer):
        building_types = serializers.ListField(
            child=serializers.CharField()
        )

    def post(self, request):
        input_serializer = self.InputCreateSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        building_types_data = input_serializer.validated_data["building_types"]

        existing_building_types = set(
            BuildingType.objects.all().values_list("name", flat=True)
        )
        seen_names = set()
        to_create = []

        for name in building_types_data:
            if name not in existing_building_types:
                to_create.append(BuildingType(name=name))
                seen_names.add(name)

        with transaction.atomic():
            BuildingType.objects.bulk_create(to_create)

        return Response({"created_count": len(to_create)}, status=status.HTTP_201_CREATED)


    class InputDeleteSerializer(serializers.Serializer):
        building_types_id = serializers.ListField()

    def delete(self, request):
        serializer = self.InputDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        BuildingType.objects.filter(id__in=serializer.validated_data["settlement_types_id"]).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BuildingTypeDetailAPIView(APIView):
    SAFE_METHODS = ["GET"]

    def get_permissions(self):
        if self.request.method not in self.SAFE_METHODS:
            return [IsAdminUser()]
        return [AllowAny()]


    class InputUpdateSerializer(serializers.ModelSerializer):
        class Meta:
            model = Region
            fields = ["name"]

    def patch(self, request, settlement_type_id: int):
        building_type = get_object_or_404(BuildingType, id=settlement_type_id)

        serializer = self.InputUpdateSerializer(building_type, data=request.data, partial=True)
        serializer.is_valid()
        serializer.save()
        return Response(status=status.HTTP_200_OK)