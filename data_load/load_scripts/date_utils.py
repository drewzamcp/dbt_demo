#!/usr/bin/env python3
from datetime import date, timedelta, datetime
from typing import List
from dateutil.relativedelta import relativedelta


def last_month() -> date:
    end_date = date.today()
    first_day = end_date.replace(day=1)
    prev_mon_end: date = first_day - relativedelta(days=1)
    return prev_mon_end


def previous_month(input_date: date) -> date:
    first_day = input_date.replace(day=1)
    return first_day - relativedelta(days=1)


def last_3_mon() -> List:
    end_month = last_month()
    last_3_months = []

    for month_count in range(3):
        x = end_month - relativedelta(months=month_count)
        last_3_months.append(x)

    return last_3_months


def last_6_mon() -> List:
    last_6_months = []

    for month_count in range(6):
        x = last_month() - relativedelta(months=month_count)
        last_6_months.append(x)

    return last_6_months


def last_12_months(date_param: date) -> List:
    months_list = []
    end_date = last_of_month(date_param)

    for month_count in range(12):
        _ = end_date - relativedelta(months=month_count)
        months_list.append(_)

    return months_list


def last_month_format(any_date: date):
    d_day = any_date.replace(day=1)
    return (d_day + relativedelta(months=1)) + relativedelta(days=-1)


def rep_periods(report_date: date):  # <- from selected end_date in get_performance()
    rp_current_month = last_month_format(report_date)
    rp_prev_month = rp_current_month.replace(day=1) - relativedelta(days=1)
    _rp_last_quarter = last_month_format(rp_current_month - relativedelta(months=3))
    rp_last_quarter = last_month_format(_rp_last_quarter)
    rp_bi_annual = last_month_format(rp_current_month - relativedelta(months=6))
    rp_annual = last_month_format(rp_current_month - relativedelta(years=1))

    return [
        rp_current_month.isoformat(),
        rp_prev_month.isoformat(),
        rp_last_quarter.isoformat(),
        rp_bi_annual.isoformat(),
        rp_annual.isoformat(),
    ]


def last_of_month(param_date: date):
    current_month = param_date.month
    new_month = current_month + 1 if current_month < 12 else 1

    if new_month is None or new_month == 1:
        return param_date.replace(day=31)
    next_date = param_date.replace(month=new_month)
    next_mon_start = next_date.replace(day=1)

    return next_mon_start + timedelta(days=-1)


def file_stamp() -> str:
    return datetime.now()\
        .isoformat(timespec='microseconds')\
        .replace(":", '')\
        .replace('.', "")\
        .replace('-', '')


if __name__ == "__main__":
    print(last_month())
    print(previous_month(last_month()))
    print(last_3_mon())
    print(last_6_mon())
    print(last_month_format(last_month()))
    print(last_of_month(date.today()))
    print(rep_periods(date.today()))
    print(file_stamp())
