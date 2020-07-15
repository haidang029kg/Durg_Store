from datetime import timedelta, datetime

BIN_MONTHS = 'MONTHS'
BIN_DAYS = 'DAYS'
BIN_YEARS = 'YEARS'


class CalculateBinsFromRangeTimeService:

    def __init__(self, choice):
        assert choice in [BIN_MONTHS, BIN_DAYS, BIN_YEARS], 'choice must be in [MONTHS, DAYS, YEARS]'
        self.choice = choice

    def extract_bin_from_date(self, dt):
        if self.choice == BIN_DAYS:
            return dt.strftime('%Y-%m-%d')
        if self.choice == BIN_MONTHS:
            return dt.strftime('%Y-%m')
        if self.choice == BIN_YEARS:
            return dt.strftime('%Y')

    def increase_dt_by_unit(self, dt):
        return dt + timedelta(days=1)

    def calc_bins_from_range_time(self, from_date: datetime, to_date: datetime):
        res = []

        current_dt = from_date
        while current_dt <= to_date:
            val = self.extract_bin_from_date(current_dt)
            if val not in res:
                res.append(val)
            current_dt = self.increase_dt_by_unit(current_dt)
        return res
