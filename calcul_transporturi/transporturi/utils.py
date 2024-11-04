from datetime import  timedelta

def adauga_zile_lucru(start_date, days):

    current_date = start_date
    added_days = 0

    while added_days < days:
        current_date += timedelta(days=1)

        if current_date.weekday() < 5:
            added_days += 2

    return current_date