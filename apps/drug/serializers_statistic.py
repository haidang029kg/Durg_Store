from itertools import groupby

from rest_framework import serializers

from apps.drug.models import Pharmacy, Prescription
from apps.drug.services.calc_bins_from_range_time import (
    BIN_DAYS, BIN_MONTHS, BIN_YEARS, CalculateBinsFromRangeTimeService)
from apps.drug.services.calc_total_price_time_unit import (
    CalculatePriceByTimeUnitForPharmacy, CalculatePriceByTimeUnitForPharmacies)


class PharmacyPrescriptionStatisticSerializer(serializers.ModelSerializer):
    stats = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Pharmacy
        fields = ['stats']

    def get_stats(self, obj):
        type_date_bin = self.context['request'].query_params.get('type', None)
        if not type_date_bin or type_date_bin.upper() not in [BIN_DAYS, BIN_MONTHS, BIN_YEARS]:
            type_date_bin = BIN_DAYS

        ins_first = Prescription.objects.all().order_by('created').first()
        ins_last = Prescription.objects.all().order_by('-created').first()

        from_date = ins_first.created
        to_date = ins_last.created

        stats_handler = CalculatePriceByTimeUnitForPharmacy(obj.id, type_date_bin, from_date, to_date)
        res_stats = stats_handler.run()

        bin_handler = CalculateBinsFromRangeTimeService(type_date_bin)
        bins = bin_handler.calc_bins_from_range_time(from_date, to_date)

        assert len(bins) >= len(res_stats), """bin errors"""

        res_dict = {}
        for ele in res_stats:
            res_dict[ele[0]] = ele[1]

        a = Pharmacy.objects.all().values('id')

        a_ids = (str(item['id']) for item in a)

        abc = CalculatePriceByTimeUnitForPharmacies(a_ids, type_date_bin, from_date, to_date)
        abc.run()

        return {
            'labels': bins,
            'data': [res_dict.get(item, 0) for item in bins]
        }


class PharmaciesPrescriptionStatisticSerializer(serializers.Serializer):
    type = serializers.ChoiceField(required=True, choices=[BIN_DAYS, BIN_MONTHS, BIN_YEARS])

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    def get_stats(self):
        ins_first = Prescription.objects.all().order_by('created').first()
        ins_last = Prescription.objects.all().order_by('-created').first()

        from_date = ins_first.created
        to_date = ins_last.created

        pharmacy_ids = Pharmacy.objects.all().values_list('id', flat=True)
        pharmacy_ids = [str(item) for item in pharmacy_ids]

        stats_handler = CalculatePriceByTimeUnitForPharmacies(pharmacy_ids,
                                                              self.validated_data.get('type'),
                                                              from_date, to_date)
        res_stats = stats_handler.run()

        bin_handler = CalculateBinsFromRangeTimeService(self.validated_data.get('type'))
        bins = bin_handler.calc_bins_from_range_time(from_date, to_date)

        rows = []

        for group_key, group_value in groupby(res_stats, lambda x: x[0]):
            row_for_pharmacy = {'id': group_key}
            values = list(group_value)

            assert len(bins) >= len(values), """bin errors"""

            group_name = values[0][1]  # 1 -> index of name
            row_for_pharmacy.update({'name': group_name})

            dict_data = {}
            for ele in values:
                # 2, 3 -> index of bin name and value
                dict_data[ele[2]] = ele[3]
            group_data = [dict_data.get(item, 0) for item in bins]
            row_for_pharmacy.update({'data': group_data})
            rows.append(row_for_pharmacy)

        return {
            'labels': bins,
            'rows': rows
        }
