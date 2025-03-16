from datetime import datetime, timedelta
from user import TrainSearch

def extractTrainDetails(train_data):
    results = []

    for leg in train_data.get('trainLegs', []):
        for train_availability in leg.get('trainAvailabilities', []):
            group_details = {
                'trains': []
            }

            for train in train_availability.get('trains', []):
                train_departure_id = train.get('departureStationId')
                segments = train.get('trainSegments', [])

                departure_time = None

                for segment in segments:
                    if segment.get('departureStationId') == train_departure_id:
                        departure_time = segment.get('departureTime')

                # Fallback to first/last segment if no match found
                if not departure_time and segments:
                    departure_time = segments[0].get('departureTime', '')

                train_info = {
                    'commercial_name': train.get('commercialName', ''),
                    'type': train.get('type', ''),
                    'departure_time': departure_time,
                    'cabin_classes': [
                        {
                            'name': cabin_class.get('cabinClass', {}).get('name', ''),
                            'availability_count': cabin_class.get('availabilityCount', 0)
                        }
                        for cabin_class in train.get('cabinClassAvailabilities', [])
                    ]
                }
                group_details['trains'].append(train_info)
            results.append(group_details)
    return results


def availability_decider(user: TrainSearch, train_data):
    available_trains = []

    all_cabin_options = ["BUSİNESS", "TEKERLEKLİ SANDALYE", "LOCA", "YATAKLI"]
    user_bool_options = user.options[-4:]
    
    selected_options = [option for option, flag in zip(all_cabin_options, user_bool_options) if flag]
    selected_options.append("EKONOMİ") 
    for train_group in train_data:
        add_train = True
        if user.options[0]:
            for t in train_group:
                if not all(s['type'] == 'YHT' for s in train_group[t]):
                    add_train = False
        
        if not user.options[1] and len(train_group["trains"]) > 1:
            add_train = False

        if not user.time_flag:
            departure = datetime.fromisoformat(train_group["trains"][0]["departure_time"]) + timedelta(hours=-21)

            user_date = (datetime.fromisoformat(train_group["trains"][0]["departure_time"]) + timedelta(hours=-21)).date()  
            start_time = datetime.strptime(user.start_time, "%H:%M:%S").time() 
            end_time = datetime.strptime(user.end_time, "%H:%M:%S").time() 

            start_datetime = datetime.combine(user_date, start_time)
            end_datetime = datetime.combine(user_date, end_time)

            
            if not (start_datetime <= departure <= end_datetime):
                add_train = False

        for train in train_group["trains"]:
            counter = 0
            for cabin in train["cabin_classes"]:
                if cabin['name'] in selected_options:
                    counter += cabin['availability_count']
            if (counter < user.number_of_passengers):
                add_train = False

        if add_train:
            available_trains.append(train_group)

    return available_trains
