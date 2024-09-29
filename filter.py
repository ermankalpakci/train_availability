

import datetime
# Wagon_Types = [["2+1 Pulman (1. Mevki) (125 )", "2 Yataklı 1.Mevki  (2  Engelli koltuğu)"],
#                ["2+2 Pulman  (Ekonomi) (2  Engelli koltuğu)", "2+1 Pulman (Business) (0 )"],
#                ["2+2 Pulman  (Ekonomi) (59 )", "2+1 Pulman (Business) (4 )"],
#                ["2+2 Pulman  (Ekonomi) (126 )","2+1 Pulman (Business) (33 )", "2+2 Pulman  (Ekonomi) (2  Engelli koltuğu)", "2+1 Pulman (Business) (0 )"],
#                ["DMU 2+2 A TİPİ 1.Mevki  (190 )", "2+2 Pulman  (Ekonomi) (1  Engelli koltuğu)", "2+1 Pulmannn (Business) (0 )"]]


# Anahat = True
# Aktarma = True
# Business = True
# Disabled = True

# train_infos = {
#     "Train 1": {
#         "Departure Date": "05.07.202406:00",
#         "Duration": "1s:18dk",
#         "Arrival Date": "05.07.202407:18",
#         "Wagon Types": ["DMU 2+2 A TİPİ 1.Mevki  (190 )", "2+2 Pulman  (Ekonomi) (1  Engelli koltuğu)", "2+1 Pulmannn (Business) (0 )"],
#     },
#     "Train 2": {
#         "Departure Date": "05.07.202406:50",
#         "Duration": "1s:21dk",
#         "Arrival Date": "05.07.202408:11",
#         "Wagon Types": ["2+2 Pulman  (Ekonomi) (126 )","2+1 Pulman (Business) (33 )", "2+2 Pulman  (Ekonomi) (2  Engelli koltuğu)", "2+1 Pulman (Business) (0 )"],
#     },
#     "Train 3": {
#         "Departure Date": "05.07.202407:30",
#         "Duration": "1s:18dk",
#         "Arrival Date": "05.07.202408:48",
#         "Wagon Types": ["2+2 Pulman  (Ekonomi) (59 )", "2+1 Pulman (Business) (4 )"],
#     },
#     "Train 4": {
#         "Departure Date": "05.07.202408:35",
#         "Duration": "1s:21dk",
#         "Arrival Date": "05.07.202409:56",
#         "Wagon Types": ["2+2 Pulman  (Ekonomi) (2  Engelli koltuğu)", "2+1 Pulman (Business) (0 )"],
#     },
#     "Train 5": {
#         "Departure Date": "05.07.202409:50",
#         "Duration": "1s:18dk",
#         "Arrival Date": "05.07.202411:08",
#         "Wagon Types": ["2+1 Pulman (1. Mevki) (125 )", "2 Yataklı 1.Mevki  (2  Engelli koltuğu)"],
#     },
# }



def train_wagon_types_filter(Wagon_Types, Anahat, Aktarma, Business, Disabled):
    filtered_wagon_types = []

    for wagon in Wagon_Types:
        add_wagon = True
        wagon_length_first = len(Wagon_Types)

        if not Anahat:
            mevki_check = "".join(Wagon_Types)
            if "Mevki" in mevki_check:
                break

        if not Aktarma:
            if wagon_length_first == 3 or wagon_length_first == 4:
                break
        
        if not Disabled:
            if 'Engelli' in wagon:
                add_wagon = False

        if not Business:
            if 'Business' in wagon:
                add_wagon = False

        if wagon_length_first == 4:
            if len(wagon) < 2:
                break

        if wagon_length_first == 3:
            if len(wagon) < 2:
                break
            elif len(wagon) == 2:
                if "DMU" in wagon:
                    pass
        if add_wagon:
            filtered_wagon_types.append(wagon)

    return filtered_wagon_types, wagon_length_first


# train_info = {'Train 1': {'Departure Date': '19.09.202406:00', 'Duration': '1s:18dk', 'Arrival Date': '19.09.202407:18', 'Wagon Types': ['2+2 Pulman  (Ekonomi) (151 )', '2+1 Pulman (Business) (13 )']}, 'Train 2': {'Departure Date': '19.09.202406:50', 'Duration': '1s:21dk', 'Arrival Date': '19.09.202408:11', 'Wagon Types': ['2+2 Pulman  (Ekonomi) (105 )', '2+1 Pulman (Business) (6 )']}, 'Train 3': {'Departure Date': '19.09.202407:30', 'Duration': '1s:18dk', 'Arrival Date': '19.09.202408:48', 'Wagon Types': ['2+2 Pulman  (Ekonomi) (91 )', '2+1 Pulman (Business) (13 )']}, 'Train 4': {'Departure Date': '19.09.202408:35', 'Duration': '1s:21dk', 'Arrival Date': '19.09.202409:56', 'Wagon Types': ['2+2 Pulman  (Ekonomi) (75 )', '2+1 Pulman (Business) (9 )']}, 'Train 5': {'Departure Date': '19.09.202409:50', 'Duration': '1s:18dk', 'Arrival Date': '19.09.202411:08', 'Wagon Types': ['2+2 Pulman  (Ekonomi) (49 )', '2+1 Pulman (Business) (15 )']}, 'Train 6': {'Departure Date': '19.09.202411:00', 'Duration': '1s:21dk', 'Arrival Date': '19.09.202412:21', 'Wagon Types': ['2+2 Pulman  (Ekonomi) (87 )', '2+1 Pulman (Business) (5 )']}, 'Train 7': {'Departure Date': '19.09.202412:05', 'Duration': '1s:18dk', 'Arrival Date': '19.09.202413:23', 'Wagon Types': ['2+2 Pulman  (Ekonomi) (49 )', '2+1 Pulman (Business) (3 )']}, 'Train 8': {'Departure Date': '19.09.202413:10', 'Duration': '1s:21dk', 'Arrival Date': '19.09.202414:31', 'Wagon Types': ['2+2 Pulman  (Ekonomi) (42 )', '2+1 Pulman (Business) (14 )']}, 'Train 9': {'Departure Date': '19.09.202414:15', 'Duration': '1s:18dk', 'Arrival Date': '19.09.202415:33', 'Wagon Types': ['2+2 Pulman  (Ekonomi) (48 )', '2+1 Pulman (Business) (13 )']}, 'Train 10': {'Departure Date': '19.09.202415:10', 'Duration': '1s:21dk', 'Arrival Date': '19.09.202416:31', 'Wagon Types': ['2+2 Pulman  (Ekonomi) (96 )', '2+1 Pulman (Business) (6 )']}, 'Train 11': {'Departure Date': '19.09.202416:45', 'Duration': '1s:18dk', 'Arrival Date': '19.09.202418:03', 'Wagon Types': ['2+2 Pulman  (Ekonomi) (78 )', '2+1 Pulman (Business) (3 )']}, 'Train 12': {'Departure Date': '19.09.202416:57', 'Duration': '1s:16dk', 'Arrival Date': '19.09.202418:13', 'Wagon Types': ['2+2 Pulman  (Ekonomi) (16 )', '2+1 Pulman (Business) (3 )']}, 'Train 13': {'Departure Date': '19.09.202417:20', 'Duration': '1s:21dk', 'Arrival Date': '19.09.202418:41', 'Wagon Types': ['2+2 Pulman  (Ekonomi) (4 )', '2+1 Pulman (Business) (3 )']}, 'Train 14': {'Departure Date': '19.09.202417:50', 'Duration': '1s:21dk', 'Arrival Date': '19.09.202419:11', 'Wagon Types': ['2+2 Pulman  (Ekonomi) (223 )', '2+1 Pulman (Business) (44 )']}, 'Train 15': {'Departure Date': '19.09.202418:25', 'Duration': '1s:21dk', 'Arrival Date': '19.09.202419:46', 'Wagon Types': ['2+2 Pulman  (Ekonomi) (2  Engelli koltuğu)', '2+1 Pulman (Business) (0 )']}, 'Train 16': {'Departure Date': '19.09.202419:35', 'Duration': '1s:18dk', 'Arrival Date': '19.09.202420:53', 'Wagon Types': ['2+2 Pulman  (Ekonomi) (40 )', '2+1 Pulman (Business) (6 )']}, 'Train 17': {'Departure Date': '19.09.202420:00', 'Duration': '3s:15dk', 'Arrival Date': '19.09.202423:15', 'Wagon Types': ['2+1 Pulman (1. Mevki) (206 )', '2 Yataklı 1.Mevki  (24 )']}, 'Train 18': {'Departure Date': '19.09.202422:00', 'Duration': '3s:4dk', 'Arrival Date': '20.09.202401:04', 'Wagon Types': ['2+1 Pulman (1. Mevki) (236 )', '2 Yataklı 1.Mevki  (12 )']}}
# filtered = train_filter(train_infos, True, True, True, False, True, '05:00', '06:01')
# print(filtered)
# print(filtered_wagon_types)
# print(len(filtered_wagon_types))



def filter_trains(trains, start_time, end_time, num_passengers, all_times, Anahat, Aktarma, Business, Disabled):
    filtered_trains = {}

    if not all_times:
        # Convert user-provided times to datetime objects
        start_time = datetime.datetime.strptime(start_time, '%H:%M:%S')
        end_time = datetime.datetime.strptime(end_time, '%H:%M:%S')
    
    for train_id, info in trains.items():
        # Convert train departure time to datetime object

        departure_time = datetime.datetime.strptime(info['Departure Date'][-5:], '%H:%M')
        
        # Check if the train departure time is within the specified range
        if all_times or (start_time <= departure_time <= end_time):

            # Check if the train has enough available seats for the specified number of passengers
            total_seats_rest = 0

            wagons, wagon_length_first = train_wagon_types_filter(info['Wagon Types'], Anahat, Aktarma, Business, Disabled)
            # print(wagons)
            if wagon_length_first == 3 and wagons:
                total_seats_first_part = int(wagons[0].split('(')[-1].split()[0])
                wagons = wagons[1:]
                for wagon in wagons:
                    seats = int(wagon.split('(')[-1].split()[0])
                    total_seats_rest += seats
                if total_seats_first_part >= num_passengers and total_seats_rest >= num_passengers:
                    filtered_trains[train_id] = info

            elif wagon_length_first == 4 and wagons:
                wagon_length_current = len(wagons)
                if wagon_length_current == 3 and "Ekonomi" in wagons[0]:
                    total_seats_first_part = int(wagons[0].split('(')[-1].split()[0]) + int(wagons[1].split('(')[-1].split()[0])
                    total_seats_first_rest = int(wagons[2].split('(')[-1].split()[0])
                    if total_seats_first_part >= num_passengers and total_seats_first_rest >= num_passengers:
                        filtered_trains[train_id] = info
                elif wagon_length_current == 3 and "Business" in wagons[0]:
                    total_seats_first_part = int(wagons[0].split('(')[-1].split()[0])
                    total_seats_first_rest = int(wagons[1].split('(')[-1].split()[0]) + int(wagons[2].split('(')[-1].split()[0])
                    if total_seats_first_part >= num_passengers and total_seats_first_rest >= num_passengers:
                        filtered_trains[train_id] = info
                else:
                    total_seats_first_part = 0
                    for wagon in wagons[:int(wagon_length_current/2)]:
                        seats = int(wagon.split('(')[-1].split()[0])
                        total_seats_first_part += seats
                    total_seats_first_rest = 0
                    for wagon in wagons[int(wagon_length_current/2):]:
                        seats = int(wagon.split('(')[-1].split()[0])
                        total_seats_first_rest += seats
                    if total_seats_first_part >= num_passengers and total_seats_first_rest >= num_passengers:
                        filtered_trains[train_id] = info
            else:
                total_seats = 0
                for wagon in wagons:
                    seats = int(wagon.split('(')[-1].split()[0])
                    total_seats += seats
                if total_seats >= num_passengers:
                    filtered_trains[train_id] = info
    
    return filtered_trains

# User inputs
# start_time = '05:00'  # Start time of departure range
# end_time = '23:00'    # End time of departure range
# num_passengers = 3    # Number of passengers
# all_times = True     # Whether to include all times or not

# Get filtered trains based on user inputs
# filtered_trains = filter_trains(train_infos, start_time, end_time, num_passengers, all_times)

# Print filtered trains
# for train_id, info in filtered_trains.items():
#     print(f"{train_id}")

# Example usage
# start_time = '06:00'
# end_time = '10:00'
# num_passengers = 2
# include_anahat = False
# all_times = False
# include_disabled = True
# train_info = {'Train 1': {'Departure Date': '19.09.202406:00', 'Duration': '1s:18dk', 'Arrival Date': '19.09.202407:18', 'Wagon Types': ['2+2 Pulman  (Ekonomi) (151 )', '2+1 Pulman (Business) (13 )']}, 'Train 2': {'Departure Date': '19.09.202406:50', 'Duration': '1s:21dk', 'Arrival Date': '19.09.202408:11', 'Wagon Types': ['2+2 Pulman  (Ekonomi) (105 )', '2+1 Pulman (Business) (6 )']}, 'Train 3': {'Departure Date': '19.09.202407:30', 'Duration': '1s:18dk', 'Arrival Date': '19.09.202408:48', 'Wagon Types': ['2+2 Pulman  (Ekonomi) (91 )', '2+1 Pulman (Business) (13 )']}, 'Train 4': {'Departure Date': '19.09.202408:35', 'Duration': '1s:21dk', 'Arrival Date': '19.09.202409:56', 'Wagon Types': ['2+2 Pulman  (Ekonomi) (75 )', '2+1 Pulman (Business) (9 )']}, 'Train 5': {'Departure Date': '19.09.202409:50', 'Duration': '1s:18dk', 'Arrival Date': '19.09.202411:08', 'Wagon Types': ['2+2 Pulman  (Ekonomi) (49 )', '2+1 Pulman (Business) (15 )']}, 'Train 6': {'Departure Date': '19.09.202411:00', 'Duration': '1s:21dk', 'Arrival Date': '19.09.202412:21', 'Wagon Types': ['2+2 Pulman  (Ekonomi) (87 )', '2+1 Pulman (Business) (5 )']}, 'Train 7': {'Departure Date': '19.09.202412:05', 'Duration': '1s:18dk', 'Arrival Date': '19.09.202413:23', 'Wagon Types': ['2+2 Pulman  (Ekonomi) (49 )', '2+1 Pulman (Business) (3 )']}, 'Train 8': {'Departure Date': '19.09.202413:10', 'Duration': '1s:21dk', 'Arrival Date': '19.09.202414:31', 'Wagon Types': ['2+2 Pulman  (Ekonomi) (42 )', '2+1 Pulman (Business) (14 )']}, 'Train 9': {'Departure Date': '19.09.202414:15', 'Duration': '1s:18dk', 'Arrival Date': '19.09.202415:33', 'Wagon Types': ['2+2 Pulman  (Ekonomi) (48 )', '2+1 Pulman (Business) (13 )']}, 'Train 10': {'Departure Date': '19.09.202415:10', 'Duration': '1s:21dk', 'Arrival Date': '19.09.202416:31', 'Wagon Types': ['2+2 Pulman  (Ekonomi) (96 )', '2+1 Pulman (Business) (6 )']}, 'Train 11': {'Departure Date': '19.09.202416:45', 'Duration': '1s:18dk', 'Arrival Date': '19.09.202418:03', 'Wagon Types': ['2+2 Pulman  (Ekonomi) (78 )', '2+1 Pulman (Business) (3 )']}, 'Train 12': {'Departure Date': '19.09.202416:57', 'Duration': '1s:16dk', 'Arrival Date': '19.09.202418:13', 'Wagon Types': ['2+2 Pulman  (Ekonomi) (16 )', '2+1 Pulman (Business) (3 )']}, 'Train 13': {'Departure Date': '19.09.202417:20', 'Duration': '1s:21dk', 'Arrival Date': '19.09.202418:41', 'Wagon Types': ['2+2 Pulman  (Ekonomi) (4 )', '2+1 Pulman (Business) (3 )']}, 'Train 14': {'Departure Date': '19.09.202417:50', 'Duration': '1s:21dk', 'Arrival Date': '19.09.202419:11', 'Wagon Types': ['2+2 Pulman  (Ekonomi) (223 )', '2+1 Pulman (Business) (44 )']}, 'Train 15': {'Departure Date': '19.09.202418:25', 'Duration': '1s:21dk', 'Arrival Date': '19.09.202419:46', 'Wagon Types': ['2+2 Pulman  (Ekonomi) (2  Engelli koltuğu)', '2+1 Pulman (Business) (0 )']}, 'Train 16': {'Departure Date': '19.09.202419:35', 'Duration': '1s:18dk', 'Arrival Date': '19.09.202420:53', 'Wagon Types': ['2+2 Pulman  (Ekonomi) (40 )', '2+1 Pulman (Business) (6 )']}, 'Train 17': {'Departure Date': '19.09.202420:00', 'Duration': '3s:15dk', 'Arrival Date': '19.09.202423:15', 'Wagon Types': ['2+1 Pulman (1. Mevki) (206 )', '2 Yataklı 1.Mevki  (24 )']}, 'Train 18': {'Departure Date': '19.09.202422:00', 'Duration': '3s:4dk', 'Arrival Date': '20.09.202401:04', 'Wagon Types': ['2+1 Pulman (1. Mevki) (236 )', '2 Yataklı 1.Mevki  (12 )']}}
# filtered_trains =  filter_trains(train_infos, "06:01", "06:50", 4, True, False, True, True, False)
# for train in filtered_trains:
#     print(train)
# print(filtered_trains)
