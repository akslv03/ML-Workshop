from datetime import datetime

class User:
    """
    Класс для представления пользователя в системе.

    Attributes:
        user_id (int): Уникальный идентификатор пользователя
        username (str): Имя пользователя
        email (str): Email пользователя
        role (str): Роль в системе (по умолчанию 'client')
        __password (str): Пароль пользователя
        balance (float): Вычисляемое свойство (property). Возвращает текущий баланс в кредитах, 
                            рассчитанный на основе истории транзакций пользователя.
    """
    def __init__(self, user_id: int, username: str, email: str, password: str, role: str = "client"):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.role = role

        self.__password = password

        self._validate_email()
        self._validate_password()

    def _validate_email(self):
        """Проверяет корректность email."""
        pass

    def _validate_password(self):
        """Проверяет минимальную длину пароля."""
        pass

    def check_password(self, input_password: str):
        """Проверяет пароль при авторизации пользователя."""
        pass

    @property
    def balance(self):
        """
        Вычисляет и возвращает итоговую сумму кредитов 
        на основе истории транзакций (сумма пополнений минус сумма списаний).
        """
        pass

    def top_up_balance(self, amount: float):
        """
        Пополнение баланса.
        Создает новую запись CreditTransaction в истории аккаунтинга.
        """
        pass

    def deduct_balance(self, amount: float):
        """
        Списание средств.
        Проверяет текущий вычисленный баланс и создает DebitTransaction.
        """
        pass


class MLmodel:
    """
    Класс для представления ML-модели для генерации описаний.

    Attributes:
        model_id (int): Уникальный идентификатор модели
        model_name (str): Название модели
        description (str): Текстовое описание возможностей модели.
        cost_per_prediction (float): Стоимость одной генерации описания
    """
    def __init__(self, model_id: int, model_name: str, description: str, cost_per_prediction: float):
        self.model_id = model_id
        self.model_name = model_name
        self.description = description
        self.cost_per_prediction = cost_per_prediction

    def predict(self, image_url: str, manual_text: str | None = None):
        """
        Выполняет генерацию описания по входным данным. Принимает на вход фотографию этикетки + название товара 
        текстом (если потребуется), и возвращает готовое описание.
        """
        pass

class MLtask:
    """
    Класс для представления задачи на генерацию описания для одного товара.

    Attributes:
        task_id (int): Уникальный номер задачи
        user (User): Объект пользователя, который создал задачу
        model (MLmodel): Объект ML-модели, которая будет выполнять задачу
        image_url (str): Ссылка на фотографию этикетки/коробки
        manual_text (str | None): Текст, введенный вручную при отсутствии названия товара на этикетке
        status (str): Текущий статус выполнения ('created', 'in_progress', 'completed')
        result_text (str): Итоговое сгенерированное описание товара
    """
    def __init__(self, task_id: int, user: User, model: MLmodel, image_url: str, manual_text: str | None = None):
        self.task_id = task_id
        self.user = user
        self.model = model
        self.image_url = image_url
        self.manual_text = manual_text
        self.status = "created"
        self.result_text = ""

    def validate_inputs(self):
        """Проверяет корректность переданных входных данных перед запуском."""
        pass

    def run_task(self):
        """Запускает обработку задачи моделью, передает данные в модель и обновляет статус."""
        pass

class Transaction:
    """
    Базовый класс для всех транзакций в системе.

    Attributes:
        transaction_id (int): Уникальный идентификатор транзакции
        _amount (float): Сумма транзакции
        user (User): Пользователь, совершающий транзакцию
        created_at (datetime): Дата и время проведения транзакции
    """
    def __init__(self, transaction_id: int, amount: float, user: User):
        self.transaction_id = transaction_id
        self.user = user
        self.created_at = datetime.now()
        self._amount = amount
    
    def apply(self):
        """Применяет транзакцию к балансу пользователя."""
        raise NotImplementedError
    
class DebitTransaction(Transaction):
    """
    Класс транзакции списания баланса за выполнение ML-задачи.

    Attributes:
        task (MLTask): ML-задача, за которую происходит списание
    """
    def __init__(self, transaction_id: int, amount: float, user: User, task: MLtask):
        super().__init__(transaction_id, amount, user)
        self.task = task

    def apply(self):
        """Cписание средств с баланса пользователя."""
        pass

class CreditTransaction(Transaction):
    """
    Класс транзакции пополнения баланса (зачисление средств)
    """

    def apply(self):
        """Пополнение баланса пользователя."""
        pass

