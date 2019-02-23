from datetime import datetime, timedelta


# timestamp: the timestamp of the alert
# description: the description of the alert
# indices: the list of entry indices related to the alert
# count: the number of times the alert was triggered
# last_seen: the timestamp of the last time the alert was triggered
class Alert:

    def __init__(self, a_type, timestamp, description, index, count, last_seen):
        self.a_type = a_type
        self.timestamp = timestamp
        self.description = description
        self.indices = [index]
        self.count = count
        self.last_seen = last_seen

    def merge(self, new_alert):
        self.__update_indices(new_alert.indices)
        self.__update_count()
        self.__update_last_seen(new_alert.timestamp)

    def get_max_delta(self, max_delta):
        datetime_t = self.get_timestamp_in_dt()
        return datetime_t - timedelta(seconds=max_delta)

    def get_timestamp_in_dt(self):
        timestamp = self.timestamp.split('.')[0]
        return datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S')

    def to_dict(self):
        data = {
            'a_type': self.a_type,
            'timestamp': self.timestamp,
            'description': self.description,
            'indices': self.indices,
            'count': self.count,
            'last_seen': self.last_seen,
        }

        return data

    def __update_indices(self, new_index):
        self.indices.extend(new_index)

    def __update_count(self):
        self.count += 1

    def __update_last_seen(self, new_last_seen):
        self.last_seen = new_last_seen

    @staticmethod
    def from_dict(jason):
        a_type = jason['a_type']

        if a_type == 'Enum':
            return EnumAlert(jason['timestamp'], jason['description'],
                             jason['indices'], jason['count'],
                             jason['last_seen'], jason['enums'])
        elif a_type == 'Integrity':
            return IntegrityAlert(jason['timestamp'], jason['description'],
                                  jason['indices'], jason['count'],
                                  jason['last_seen'])
        elif a_type == 'Secrets':
            return SecretsAlert(jason['timestamp'], jason['description'],
                                jason['indices'], jason['count'],
                                jason['last_seen'])
        elif a_type == 'RCE':
            return RCEAlert(jason['timestamp'], jason['description'],
                            jason['indices'], jason['count'],
                            jason['last_seen'], jason['commands'])
        else:
            return Alert(jason['a_type'], jason['timestamp'],
                         jason['description'], jason['indices'],
                         jason['count'], jason['last_seen'])


class EnumAlert(Alert):
    def __init__(self, timestamp, description, index, count, last_seen,
                 enums):
        super().__init__('Enum', timestamp, description, index, count,
                         last_seen)

        self.enums = [enums]

    def merge(self, new_alert):
        super().merge(new_alert)

        self.__update_commands(new_alert.enums)

    def to_dict(self):
        data = super().to_dict()
        data['enums'] = self.enums
        return data

    def __update_commands(self, new_enums):
        self.enums.extend(new_enums)


class IntegrityAlert(Alert):
    def __init__(self, timestamp, description, index, count, last_seen):
        super().__init__('Integrity', timestamp, description, index, count,
                         last_seen)


class SecretsAlert(Alert):
    def __init__(self, timestamp, description, index, count, last_seen):
        super().__init__('Secrets', timestamp, description, index, count,
                         last_seen)


class RCEAlert(Alert):
    def __init__(self, timestamp, description, index, count, last_seen,
                 command):
        super().__init__('RCE', timestamp, description, index, count,
                         last_seen)

        self.commands = [command]

    def merge(self, new_alert):
        super().merge(new_alert)

        self.__update_commands(new_alert.commands)

    def to_dict(self):
        data = super().to_dict()
        data['commands'] = self.commands
        return data

    def __update_commands(self, new_commands):
        self.commands.extend(new_commands)
