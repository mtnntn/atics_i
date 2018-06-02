from datetime import datetime


class DatetimeExtractor(object):

    def __init__(self, start_year, start_month, start_day):
        self.month = start_month
        self.year = start_year
        self.day = start_day

    def get_datetime(self, diocane):  # la stringa si chiama diocane per ovvi motivi!

        if diocane == "Not Available":
            return None

        # 1:20pDec 1
        try:
            time_month, day = diocane.split(" ")
            hours, minutes_ampm_month = time_month.split(":")
            minutes = minutes_ampm_month[:2]
            am_pm = "AM" if minutes_ampm_month[2:3] == "a" else "PM"
            month = minutes_ampm_month[3:]
            tm = ":".join([hours, minutes])
            tm = zero_padding_str(tm, ":")
            day = zero_padding_str(day, " ")

            raw_str_data = str(self.year) + " " + " ".join([tm, am_pm, month, day])
            return datetime.strptime(raw_str_data, "%Y %I:%M %p %b %d")
        except Exception as p:
            pass

        # Dec 01 - 10:20pm - Dec 01 - Not Available
        try:
            month_day, tm = diocane.split(" - ")
            pattern = "%Y %b %d - %I:%M%p"
            raw_str_data = diocane

            if tm.find("pm") == -1 and tm.find("am") == -1:
                pattern = "%Y %b %d"
                raw_str_data = month_day

            raw_str_data = str(self.year) + " " + raw_str_data

            return datetime.strptime(raw_str_data, pattern)
        except Exception as p:
            pass

        # 2011-12-01 10:20 PM - 2011-12-01 4:27 PM (Estimated runway)
        try:
            raw_str_data = diocane
            split_date = raw_str_data.split(" ")[:3]

            tm = split_date[1].split(":")  # handle zero padding for hours.
            if len(tm[0]) == 1:
                tm[0] = str(0) + str(tm[0])
                split_date[1] = ":".join(tm)

            raw_str_data = " ".join(split_date)

            return datetime.strptime(raw_str_data, "%Y-%m-%d %I:%M %p")
        except Exception as p:
            pass

        # 2011-12-01 18:45
        try:
            return datetime.strptime(diocane.strip(), "%Y-%m-%d %H:%M")
        except Exception as p:
            pass

        # 2011-12-01 Thu  08:45
        try:
            return datetime.strptime(diocane.strip(), "%Y-%m-%d %a  %H:%M")
        except Exception as p:
            pass

        # 10:20 PM, Dec 01
        try:
            raw_str_data = str(self.year) + " " + diocane.strip()
            return datetime.strptime(raw_str_data, "%Y %I:%M %p, %b %d")
        except Exception as p:
            pass

        # 3:56 PMDec 01
        try:
            raw_str_data = str(self.year) + " " + diocane.strip()
            return datetime.strptime(raw_str_data, "%Y %I:%M %p%b %d")
        except Exception as p:
            pass

        # 10:20 PM  Thu 01-Dec-2011
        try:
            return datetime.strptime(diocane.strip(), "%I:%M %p  %a %d-%b-%Y")
        except Exception as p:
            pass

        # 2011-12-01 10:20PM CST  -  2011-12-01 04:22PM PST  -  2011-12-01 08:30AM EST
        try:
            split_date = diocane.strip().split(" ")
            raw_str_data = " ".join(split_date[:len(split_date)-1])
            return datetime.strptime(raw_str_data, "%Y-%m-%d %I:%M%p")
        except Exception as p:
            pass

        # 12/1/11 10:30 PM (-06:00)
        try:
            split_date = diocane.split(" ")

            split_date[0] = zero_padding_str(split_date[0], "/")  # handle zero padding for hours.

            raw_str_data = " ".join(split_date[:len(split_date)-1])

            return datetime.strptime(raw_str_data, "%m/%d/%y %I:%M %p")

        except Exception as p:
            pass

        # 12/01/2011 01:55 PM
        try:
            return datetime.strptime(diocane.strip(), "%m/%d/%Y %I:%M %p")
        except Exception as p:
            pass

        # Fri, Dec 2 12:50 AM   - Tue, Dec 13 7:19 PM        rerouted
        try:
            raw_str_data = str(self.year) + " " + diocane.strip()
            split_date = raw_str_data.split(" ")
            split_date = split_date[:6]

            split_date[3] = zero_padding_str(split_date[3], " ")
            split_date[4] = zero_padding_str(split_date[4], ":")

            raw_str_data = " ".join(split_date)

            return datetime.strptime(raw_str_data, "%Y %a, %b %d %I:%M %p")
        except Exception as p:
            pass

        # Thu., Dec.01, 2011 8:30 a.m.
        try:
            raw_str_data = diocane.strip()
            split_date = raw_str_data.split(" ")

            split_date[len(split_date)-2] = zero_padding_str(split_date[len(split_date)-2], ":")
            split_date[len(split_date)-1] = "AM" if split_date[len(split_date)-1] == "a.m." else "PM"

            raw_str_data = " ".join(split_date)

            return datetime.strptime(raw_str_data, "%a., %b.%d, %Y %I:%M %p")
        except Exception as p:
            pass

        # 2011-12-01 06:00:00
        try:
            return datetime.strptime(diocane.strip(), "%Y-%m-%d %I:%M%S")
        except Exception as p:
            pass

        # 12/1/2011 8:55PM CST
        try:
            dt, tm, zn = diocane.strip().split(" ")
            dt = zero_padding_str(dt, "/")
            tm = zero_padding_str(tm, ":")
            raw_str_data = " ".join([dt, tm])
            return datetime.strptime(raw_str_data, "%m/%d/%Y %I:%M%p")
        except Exception as p:
            pass

        # 2011-12-01 11/30 4:16 PM #-> ignoring 11/30
        try:
            dt, boh, hours, am_pm = diocane.strip().split(" ")
            hours = zero_padding_str(hours, ":")
            raw_str_data = " ".join([dt, hours, am_pm])
            return datetime.strptime(raw_str_data, "%Y-%m-%d %I:%M %p")
        except Exception as p:
            pass

        # 2:20P 12-01-11
        try:
            hours_am_pm, date_str = diocane.strip().split(" ")
            am_pm = "AM" if hours_am_pm[len(hours_am_pm)-1:] == "A" else "PM"
            hours = zero_padding_str(hours_am_pm[:len(hours_am_pm)-1], ":")

            raw_str_data = " ".join([date_str, hours, am_pm])

            return datetime.strptime(raw_str_data, "%m-%d-%y %I:%M %p")
        except Exception as p:
            pass

        # 2011-12-10  2:46P
        try:
            split_data = diocane.strip().split(" ")
            split_data = [x for x in split_data if x != ""]
            date_str, hours_am_pm = split_data
            am_pm = "AM" if hours_am_pm[len(hours_am_pm) - 1:] == "A" else "PM"
            hours = zero_padding_str(hours_am_pm[:len(hours_am_pm) - 1], ":")
            raw_str_data = " ".join([date_str, hours, am_pm])
            return datetime.strptime(raw_str_data, "%Y-%m-%d %I:%M %p")
        except Exception as p:
            pass

        # December 8, 2011               01:55 PM
        try:
            split_date = diocane.strip().split(" ")
            split_date = [el for el in split_date if el != ""]

            split_date[1] = split_date[1][:len(split_date[1]) - 1]   # remove ,
            split_date[1] = zero_padding_str(split_date[1], " ")
            raw_str_data = " ".join(split_date)

            return datetime.strptime(raw_str_data, "%B %d %Y %I:%M %p")
        except Exception as p:
            pass

        # December 8, 2011
        try:
            split_date = diocane.strip().split(" ")
            split_date[1] = split_date[1][:len(split_date[1])-1]
            split_date[1] = zero_padding_str(split_date[1], " ")    # remove ,
            raw_str_data = " ".join(split_date)
            return datetime.strptime(raw_str_data, "%B %d %Y")
        except Exception as p:
            pass

        # 3:25 PM, Dec 10&nbsp(Estimated)
        try:
            cut_at = diocane.find("&")
            raw_str_data = diocane[:cut_at]
            split_data = raw_str_data.split(" ")
            split_data[0] = zero_padding_str(split_data[0], ":")
            split_data.append(str(self.year))
            raw_str_data = " ".join(split_data)
            return datetime.strptime(raw_str_data, "%I:%M %p, %b %d %Y")
        except Exception as p:
            pass

        # Dec 10 - 9:17pm*
        try:
            raw_str_date = diocane[:len(diocane) - 1]
            raw_str_date = str(self.year) + " " + raw_str_date
            return datetime.strptime(raw_str_date, "%Y %b %d - %I:%M%p")
        except Exception as p:
            pass

        # 04:14 PM  Sat 10-Dec-2011 (Runway)
        try:
            raw_str_date = [x for x in diocane.split(" ") if x != ""]
            raw_str_date = " ".join(raw_str_date[:len(raw_str_date) - 1])
            return datetime.strptime(raw_str_date, "%I:%M %p %a %d-%b-%Y")
        except Exception as p:
            pass

        # 2011-12-10 Cancelled
        # 2011-12-17 result unknown (?) (track log &amp; graph)
        try:
            cut_at = diocane.find("Cancelled")  # cut at 0 would be simpler but would not preserve other cases
            if cut_at == -1:
                cut_at = diocane.find("result")

            raw_str_date = diocane[:cut_at].strip()
            return datetime.strptime(raw_str_date, "%Y-%m-%d")
        except Exception as p:
            pass

        # Thu, Dec 29 Cancelled
        try:
            split_data = diocane.split(" ")
            raw_str_data = " ".join(split_data[:len(split_data) - 1])
            raw_str_data = str(self.year) + " " + raw_str_data
            return datetime.strptime(raw_str_data, "%Y %a, %b %d")
        except Exception as p:
            pass

        raise Exception("Impossibile importare Data: " + diocane)

    def get_datetime_minutes(self, raw_str_datetime):
        start_date = datetime(year=self.year, month=self.month, day=1)
        current_date = self.get_datetime(raw_str_datetime)
        delta = current_date - start_date
        delta_minutes = round(delta.total_seconds() / 60, 3)
        return delta_minutes


def zero_padding(num):
    num = str(num)
    if len(num) <= 1:
        return "0"+num
    return num


def zero_padding_str(string, separator):
    split_data = string.split(separator)
    split_data = [zero_padding(x) for x in split_data]
    return separator.join(split_data)
