import abc
from typing import Any, Dict


class BaseStorage(abc.ABC):
    """Абстрактное хранилище состояния.

    Позволяет сохранять и получать состояние.
    Способ хранения состояния может варьироваться в зависимости
    от итоговой реализации. Например, можно хранить информацию
    в базе данных или в распределённом файловом хранилище.
    """

    @abc.abstractmethod
    def save_state(self, state: Dict[str, Any]) -> None:
        """Сохранить состояние в хранилище."""

    @abc.abstractmethod
    def retrieve_state(self) -> Dict[str, Any]:
        """Получить состояние из хранилища."""


import json
from typing import Any, Dict

class JsonFileStorage(BaseStorage):
    """Реализация хранилища, использующего локальный файл.

    Формат хранения: JSON
    """
    
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    def save_state(self, state: Dict[str, Any]) -> None:
        """Сохранить состояние в хранилище."""
        with open(self.file_path, 'w') as file:
            json.dump(state, file)

    def retrieve_state(self) -> Dict[str, Any]:
        """Получить состояние из хранилища."""
        try:
            with open(self.file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}

import redis
from typing import Any, Dict
import json

class RedisStorage(BaseStorage):
    """Реализация хранилища, использующего Redis."""
    
    def __init__(self, redis_client: redis.Redis, key: str = 'app_state') -> None:
        """Инициализация хранилища.

        Args:
            redis_client: Объект соединения с Redis.
            key: Ключ, под которым будет храниться состояние в Redis.
        """
        self._redis = redis_client
        self._key = key

    def save_state(self, state: Dict[str, Any]) -> None:
        """Сохранить состояние в хранилище."""
        self._redis.set(self._key, json.dumps(state))

    def retrieve_state(self) -> Dict[str, Any]:
        """Получить состояние из хранилища."""
        state = self._redis.get(self._key)
        if state is None:
            return {}
        return json.loads(state)

class State:
    """Класс для работы с состояниями."""

    def __init__(self, storage: BaseStorage) -> None:
        self.storage = storage
        self.current_state = self.storage.retrieve_state()

    def set_state(self, key: str, value: Any) -> None:
        """Установить состояние для определённого ключа."""
        self.current_state[key] = value
        self.storage.save_state(self.current_state)

    def get_state(self, key: str) -> Any:
        """Получить состояние по определённому ключу."""
        return self.current_state.get(key)

        
def backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10):
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка. Использует наивный экспоненциальный рост времени повтора (factor) до граничного времени ожидания (border_sleep_time)
        
    Формула:
        t = start_sleep_time * (factor ^ n), если t < border_sleep_time
        t = border_sleep_time, иначе
    :param start_sleep_time: начальное время ожидания
    :param factor: во сколько раз нужно увеличивать время ожидания на каждой итерации
    :param border_sleep_time: максимальное время ожидания
    :return: результат выполнения функции
    """
    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            # jitter,таймауты 
            inner=None
        return inner
    return func_wrapper
    
def check_state(system='json'):
    if system=='json':
        storage = JsonFileStorage('state.json')
    else:
        import redis

        # Создаем соединение с Redis
        redis_client = redis.Redis(host='localhost', port=6379, db=0)

        # Используем RedisStorage для хранения состояния
        storage = RedisStorage(redis_client)
    
    state = State(storage)

    # Установим новое состояние
    state.set_state('user', {'name': 'Maxim', 'age': 30})

    # Получим установленное состояние
    user_state = state.get_state('user')
    print(user_state)  # Вывод: {'name': 'Maxim', 'age': 30}
    
if __name__ == "__main__":
    check_state(system='json')
    