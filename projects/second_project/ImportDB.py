import csv
from models.second_model.DatetimeExtractor import DatetimeExtractor
from os import listdir
from os.path import isfile, join

# flight{
#   source,
#   flight_number,
#   scheduled departure, (nel caso sia sconosciuto prendo l'actual)
#   actual departure,
#   departure gate, (ne caso sia sconosciuto -> gate fittizio UDG )
#   scheduled arrival, (nel caso sia sconosciuto prendo l'actual)
#   actual arrival,
#   arrival gate (ne caso sia sconosciuto -> gate fittizio UAG )
# }


def import_gate(gate):
    gate = gate.strip()
    gate = gate.upper()
    if gate == "-" or gate == "--" or gate == "" or gate == "?" or gate == "$" or gate == "NOT PROVIDED BY AIRLINE" or \
            gate is None:
        gate = "--"
    return gate


data_base_path = "../../datasets/flights/clean_flight/"

start_year = 2011
start_month = 12
start_day = 1

dte = DatetimeExtractor(start_year, start_month, start_day)

data_set_files = [f for f in listdir(data_base_path) if isfile(join(data_base_path, f))]
data_set_files.sort()

sources = set()
flights = set()
gates = set()

records = []

# clean dataset
for file in data_set_files:

    print("Importing: " + data_base_path+file)

    with open(data_base_path+file, "r", encoding="iso-8859-1") as f:
        reader = csv.reader(f, delimiter='\t')

        count_null_scheduled_departures = 0
        count_null_scheduled_arrivals = 0
        count_null_actual_departures = 0
        count_null_actual_arrivals = 0

        for i, row in enumerate(reader):
            try:
                source = row[0].strip().upper()
                flight = row[1].strip().upper()
                departure_gate = import_gate(row[4])  # one hot
                arrival_gate = import_gate(row[4])  # one hot
            except Exception as p:
                print(i)
                print(row)

            sources.add(source)
            flights.add(flight)
            gates.add(departure_gate)
            gates.add(arrival_gate)

            scheduled_departure = row[2]    # scheduled departure
            scheduled_departure_is_null = scheduled_departure.strip() == "" or scheduled_departure is None

            if scheduled_departure_is_null:
                count_null_scheduled_departures += 1
            else:
                try:
                    scheduled_departure = dte.get_datetime(scheduled_departure)
                except Exception as p:
                    print(row)
                    print(p)

            actual_departure = row[3]  # scheduled departure
            actual_departure_is_null = actual_departure.strip() == "" or actual_departure is None

            if actual_departure_is_null:
                count_null_actual_departures += 1
            else:
                try:
                    actual_departure = dte.get_datetime(actual_departure)
                except Exception as p:
                    print(row)
                    print(p)

            scheduled_arrival = row[5]  # scheduled arrival
            scheduled_arrival_is_null = scheduled_arrival.strip() == "" or scheduled_arrival is None

            if scheduled_arrival_is_null:
                count_null_scheduled_arrivals += 1
            else:
                try:
                    scheduled_arrival = dte.get_datetime(scheduled_arrival)
                except Exception as p:
                    print(row)
                    print(p)

            actual_arrival = row[6]  # actual arrival
            actual_arrival_is_null = actual_arrival.strip() == "" or actual_arrival is None

            if actual_arrival_is_null:
                count_null_actual_arrivals += 1
            else:
                try:
                    actual_arrival = dte.get_datetime(actual_arrival)
                except Exception as p:
                    print(row)
                    print(p)

            records.append([source, flight, scheduled_departure, actual_departure, departure_gate,
                            scheduled_arrival, actual_arrival, arrival_gate])
