import pandas as pd
from models.smart_ai_model import SmartAIModel

# Шаг 1: Загрузка данных
data = pd.read_csv("historical_data.csv")  # Ваш CSV с историческими данными

# Шаг 2: Подготовка данных
look_back = 60
model = SmartAIModel(input_shape=(look_back, 4))
X, y = model.preprocess_data(data, look_back=look_back)

# Шаг 3: Разделение данных на тренировочные и тестовые выборки
split_index = int(len(X) * 0.8)
X_train, X_test = X[:split_index], X[split_index:]
y_train, y_test = y[:split_index], y[split_index:]

# Шаг 4: Обучение модели
print("Начало обучения...")
model.train(X_train, y_train, epochs=50, batch_size=32)

# Шаг 5: Сохранение модели
model.save_model("models/smart_ai_model.h5")
print("Модель успешно сохранена.")
