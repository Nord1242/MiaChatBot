import threading
from collections import namedtuple
from dataclasses import dataclass
from datetime import datetime
from queue import Queue, Empty
from time import sleep
from typing import Union, List

from influxdb_client import InfluxDBClient, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# "сырые" объекты, которые прилетают из хэндлеров или мидлварей
RawUpdatePre = namedtuple("RawUpdatePre", ["is_handled"])
NamedEventPre = namedtuple("NamedEventPre", ["event"])
UniqueUserPre = namedtuple("UniqueUserPre", [])


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


# # Объект сбора онлайна
# @dataclass
# class UserOnline:
#     timestamp: datetime
#     updates_in_batch: int


@dataclass
class UniqueUser:
    timestamp: datetime
    updates_in_batch: int


@dataclass
class AllUniqueUser:
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

        handled_count = 0
        unhandled_count = 0
        day_unique_user_count = 0
        all_unique_user_count = 0
        named_events = {}
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
                        day_unique_user_count += 1
                        all_unique_user_count += 1
                except Empty:
                    # Наличие N элементов в очереди не гарантирует, что все N можно забрать
                    break
            print(day_unique_user_count)
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
            self.write_unique_user(
                UniqueUser(
                    timestamp=datetime.utcnow(),
                    updates_in_batch=day_unique_user_count
                ))
            self.all_write_unique_user(
                UniqueUser(
                    timestamp=datetime.utcnow(),
                    updates_in_batch=all_unique_user_count
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
            if datetime.utcnow().strftime("%H:%M") == "22:35":
                day_unique_user_count = 0
            sleep(3)
        print("InfluxAnalyticsClient stopped")

    def __write_generic(self, bucket: str, tags: List[str], obj: Union[RawUpdate, NamedEvent, UniqueUser]):
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

    def write_unique_user(self, unique_user: UniqueUser):
        self.__write_generic(bucket="day_unique_user", tags=["unique_user"], obj=unique_user)

    def all_write_unique_user(self, unique_user: UniqueUser):
        self.__write_generic(bucket="all_unique_user", tags=["unique_user"], obj=unique_user)

