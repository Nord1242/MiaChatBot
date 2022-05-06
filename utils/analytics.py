import threading
from collections import namedtuple
from dataclasses import dataclass
from datetime import datetime, timedelta, time
from dateutil.relativedelta import relativedelta
from queue import Queue, Empty
from time import sleep
from typing import Union, List

from influxdb_client import InfluxDBClient, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# "сырые" объекты, которые прилетают из хэндлеров или мидлварей
RawUpdatePre = namedtuple("RawUpdatePre", ["is_handled"])
NamedEventPre = namedtuple("NamedEventPre", ["event"])
UniqueUserPre = namedtuple("UniqueUserPre", ["channel"])
UserOnlinePre = namedtuple("UserOnlinePre", ["user_id"])


# Объект апдейта для логирования по типу обработан/не обработан
@dataclass
class RawUpdate:
    timestamp: datetime
    is_handled: int
    updates_in_batch: int


# Объект именованного события (произвольная строка)
@dataclass
class NamedEvent:
    timestamp: datetime
    event: str
    updates_in_batch: int


# Объект сбора онлайна
@dataclass
class UserOnline:
    timestamp: datetime
    updates_in_batch: int


@dataclass
class UniqueUser:
    channel: str
    timestamp: datetime
    updates_in_batch: int


class InfluxAnalyticsClient(threading.Thread):

    def __init__(self, url: str, token: str, org: str, objects_queue: Queue):
        super().__init__()
        # Очередь, из которой будут забираться события разных типов
        self.objects_queue = objects_queue
        # Флаг, при выставлении которого тред должен быть завершён
        self.stop_flag = threading.Event()
        # Объект клиента для работы с InfluxDB и "писатель" для него
        self.influx_client = InfluxDBClient(url=url, token=token, org=org)
        self.writer = self.influx_client.write_api(write_options=SYNCHRONOUS)

    def health_check(self) -> bool:
        return self.influx_client.ping()

    def run(self):
        """
        Основной рабочий цикл

        Для начала, проверяется текущая длина очереди. Пусть, к примеру, эта длина N
        Далее в цикле забирается не более N элементов (по факту может вернуться x < N)
        и определяется их тип. Затем эти элементы приводятся к датаклассам, которые передаются
        библиотеке для работы с InfluxDB и отправки в СУБД.

        При выставлении флага {stopflag} на очередной итерации цикл прекращает обработку
        """
        users_list = {}
        named_events = {}
        unique_user = {}

        next_day = datetime.utcnow() + timedelta(days=1)
        next_day = datetime.combine(next_day, time.min)
        online_count = len(users_list)

        handled_count = 0
        unhandled_count = 0

        while not self.stop_flag.is_set():
            for index in range(self.objects_queue.qsize()):
                try:
                    new_object = self.objects_queue.get(block=False)
                    if isinstance(new_object, RawUpdatePre):
                        if new_object.is_handled:
                            handled_count += 1
                        else:
                            unhandled_count += 1
                    elif isinstance(new_object, NamedEventPre):
                        named_events.setdefault(new_object.event, 0)
                        named_events[new_object.event] += 1
                    elif isinstance(new_object, UniqueUserPre):
                        unique_user.setdefault(new_object.channel, 0)
                        unique_user[new_object.channel] += 1
                    elif isinstance(new_object, UserOnlinePre):
                        if new_object.user_id not in users_list:
                            users_list.setdefault(new_object.user_id, datetime.utcnow() + timedelta(minutes=30))
                        else:
                            users_list[new_object.user_id] = datetime.utcnow() + timedelta(minutes=30)

                except Empty:
                    # Наличие N элементов в очереди не гарантирует, что все N можно забрать
                    break
            # Отправка при наличии обработанных апдейтов
            if handled_count > 0:
                self.write_update(
                    RawUpdate(
                        timestamp=datetime.utcnow(),
                        is_handled=1,
                        updates_in_batch=handled_count
                    )
                )
                handled_count = 0
            self.write_user_online(
                UserOnline(
                    timestamp=datetime.utcnow(),
                    updates_in_batch=online_count
                )
            )
            # Отправка уникальных пользователей с канала
            for channel, users in unique_user.items():
                self.write_unique_user(UniqueUser(
                    timestamp=datetime.utcnow(),
                    channel=channel,
                    updates_in_batch=users
                ))
            # Отправка именованных событий
            for key, value in named_events.items():
                if value > 0:
                    self.write_event(
                        NamedEvent(
                            timestamp=datetime.utcnow(),
                            event=key,
                            updates_in_batch=value
                        )
                    )
                named_events[key] = 0
            # Сбор онлайна
            if datetime.utcnow() >= next_day:
                for channel, users in unique_user.items():
                    unique_user[channel] = 0
                next_day = datetime.utcnow() + timedelta(days=1)
                next_day = datetime.combine(next_day, time.min)
            # for user_id, time in users_list.items():
            #     if time <= datetime.utcnow():
            #         users_list.pop(user_id)
            users_list = {user_id: act_time for user_id, act_time in users_list.items() if
                          act_time >= datetime.utcnow()}
            online_count = len(users_list)
            sleep(3)
        print("InfluxAnalyticsClient stopped")

    def __write_generic(self, bucket: str, tags: List[str], obj: Union[RawUpdate, NamedEvent, UniqueUser]):
        # UserOnline
        """
        Отправка произвольного события в InfluxDB

        :param bucket: имя "таблицы" (оно же имя "базы данных")
        :param tags: массив названий полей, являющихся тегами
        :param obj: сам объект, который надо отправить
        """
        self.writer.write(
            bucket=bucket,
            record=obj,
            record_measurement_name=bucket,
            record_time_key="timestamp",
            record_tag_keys=tags,
            record_field_keys=["updates_in_batch"],
            write_precision=WritePrecision.S
        )

    def write_update(self, update: RawUpdate):
        self.__write_generic(bucket="updates", tags=["is_handled"], obj=update)

    def write_event(self, event: NamedEvent):
        self.__write_generic(bucket="events", tags=["event"], obj=event)

    def write_user_online(self, event: UserOnline):
        self.__write_generic(bucket="user_online", tags=["online"], obj=event)

    def write_unique_user(self, unique_user: UniqueUser):
        self.__write_generic(bucket="unique_user", tags=["channel"], obj=unique_user)
