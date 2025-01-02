import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from data_fetcher import DataFetcher
from ai_predictor import AIPredictor
from utils.indicators import Supertrend, EMA, RSI, MACD
from utils.validation_utils import validate_data
from utils.logging_utils import (
    log_data_fetching,
    log_data_fetching_error,
    log_data_validation,
    log_user_action,
    log_critical_error
)
from datetime import datetime, timezone

class TradingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Crypto Trading Analysis")
        self.geometry("1200x720")
        self.configure(bg="#1e1e2f")

        # Настройка главной сетки окна
        self.grid_columnconfigure(0, weight=0)  # левая панель (фиксированная ширина)
        self.grid_columnconfigure(1, weight=1)  # центральная панель (растягивается)
        self.grid_columnconfigure(2, weight=1)  # правая панель (растягивается)
        self.grid_rowconfigure(0, weight=1)     # единственная строка (растягивается)

        # Создание фреймов для каждой из зон
        self.input_frame = tk.Frame(self, bg="#28293e", highlightbackground="#4e4e4e", highlightthickness=2)
        self.input_frame.grid(row=0, column=0, sticky="ns")

        self.center_frame = tk.Frame(self, bg="#28293e", highlightbackground="#4e4e4e", highlightthickness=2)
        self.center_frame.grid(row=0, column=1, sticky="nsew")

        self.result_frame = tk.Frame(self, bg="#28293e", highlightbackground="#4e4e4e", highlightthickness=2)
        self.result_frame.grid(row=0, column=2, sticky="nsew")

        # Заполнение зон
        self.setup_input_section()    # левая панель
        self.setup_analysis_section() # центральный блок
        self.setup_result_section()   # правая панель

        # Обновление статуса ИИ при запуске
        self.update_ai_status()

        # Запуск часов
        self.update_clock()

    def validate_number(self, P):
        """Валидация: разрешает ввод только чисел."""
        if P == "":
            return True  # Разрешаем пустую строку
        try:
            float(P)  # Пробуем преобразовать в число
            return True
        except ValueError:
            return False

    def setup_input_section(self):
        """Левая панель: Параметры анализа."""
        sub_frame = tk.Frame(self.input_frame, bg="#28293e")
        sub_frame.grid(row=0, column=0, sticky="nsew")

        # Заголовок (центрирован)
        tk.Label(sub_frame, text="Параметры анализа", font=("Arial", 14, "bold"),
                 bg="#28293e", fg="#ffffff", anchor="center").grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        # Элементы (центрированы)
        tk.Label(sub_frame, text="Выберите пару:", bg="#28293e", fg="#a9b7c6", anchor="center").grid(row=1, column=0, padx=20, sticky="ew")
        self.symbol_var = tk.StringVar(value="BTC/USDT")
        self.symbols = [
            "BTC/USDT", "ETH/USDT", "XRP/USDT", "SOL/USDT", 
            "DOGE/USDT", "TAI/USDT", "PHA/USDT", "SUI/USDT", 
            "1000PEPE/USDT"
        ]
        ttk.Combobox(sub_frame, values=self.symbols, textvariable=self.symbol_var, width=15).grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        tk.Label(sub_frame, text="Сумма ставки:", bg="#28293e", fg="#a9b7c6", anchor="center").grid(row=3, column=0, padx=20, pady=(10, 0), sticky="ew")
        self.capital_entry = tk.Entry(sub_frame, width=15, bg="#1e1e2f", fg="#ffffff",
                                      insertbackground="#ffffff", relief="solid", borderwidth=1,
                                      validate="key", validatecommand=(self.register(self.validate_number), "%P"))
        self.capital_entry.grid(row=4, column=0, padx=20, pady=5, sticky="ew")

        tk.Label(sub_frame, text="Укажи плечо", bg="#28293e", fg="#a9b7c6", anchor="center").grid(row=5, column=0, padx=20, pady=(10, 0), sticky="ew")
        self.leverage_entry = tk.Entry(sub_frame, width=15, bg="#1e1e2f", fg="#ffffff",
                                       insertbackground="#ffffff", relief="solid", borderwidth=1,
                                       validate="key", validatecommand=(self.register(self.validate_number), "%P"))
        self.leverage_entry.grid(row=6, column=0, padx=20, pady=5, sticky="ew")

        # Статус ИИ
        self.ai_status_label = tk.Label(sub_frame, text="Статус ИИ: Не обучена", bg="#28293e", fg="#a9b7c6", anchor="center")
        self.ai_status_label.grid(row=7, column=0, padx=20, pady=(10, 0), sticky="ew")

        # Рекомендация по обучению
        self.ai_recommendation_label = tk.Label(sub_frame, text="Рекомендация: Обучить ИИ", bg="#28293e", fg="#a9b7c6", anchor="center")
        self.ai_recommendation_label.grid(row=8, column=0, padx=20, pady=(10, 0), sticky="ew")

        # Кнопка "Обучить ИИ на всех парах"
        self.train_all_button = tk.Button(
            sub_frame,
            text="Обучить ИИ на всех парах",
            bg="#4caf50",
            fg="#ffffff",
            font=("Arial", 10, "bold"),
            command=self.train_ai_on_all_pairs,
            relief="flat",
            activebackground="#45a049"
        )
        self.train_all_button.grid(row=9, column=0, padx=20, pady=(20, 0), sticky="ew")

        self.start_button = tk.Button(
            sub_frame,
            text="Запустить анализ",
            bg="#4caf50",
            fg="#ffffff",
            font=("Arial", 10, "bold"),
            command=self.start_analysis,
            relief="flat",
            activebackground="#45a049"
        )
        self.start_button.grid(row=10, column=0, padx=20, pady=(20, 0), sticky="ew")

        # Часы (местное время и UTC)
        self.local_time_label = tk.Label(
            sub_frame,
            text="Местное время: ",
            bg="#28293e",
            fg="#a9b7c6",
            font=("Arial", 10)
        )
        self.local_time_label.grid(row=11, column=0, padx=20, pady=(20, 5), sticky="ew")

        self.utc_time_label = tk.Label(
            sub_frame,
            text="Время UTC: ",
            bg="#28293e",
            fg="#a9b7c6",
            font=("Arial", 10)
        )
        self.utc_time_label.grid(row=12, column=0, padx=20, pady=(0, 20), sticky="ew")

    def update_clock(self):
        """Обновляет время каждую секунду."""
        local_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        utc_time = datetime.now(timezone.utc).strftime("%d-%m-%Y %H:%M:%S")

        self.local_time_label.config(text=f"Местное время: {local_time}")
        self.utc_time_label.config(text=f"Время UTC: {utc_time}")

        self.after(1000, self.update_clock)

    def update_ai_status(self):
        """Обновляет статус ИИ и рекомендацию."""
        predictor = AIPredictor()
        status, last_trained = predictor.get_ai_status()
        self.ai_status_label.config(text=f"Статус ИИ: {status}")
        if last_trained:
            self.ai_status_label.config(text=f"Статус ИИ: {status} (обучена {last_trained})")
        recommendation = predictor.get_training_recommendation()
        self.ai_recommendation_label.config(text=f"Рекомендация: {recommendation}")

    def train_ai_on_all_pairs(self):
        """Обработчик кнопки 'Обучить ИИ на всех парах'."""
        self.analysis_text.insert(tk.END, "Запуск обучения ИИ на всех парах...\n")
        try:
            predictor = AIPredictor()
            predictor.train_ai_on_all_pairs(self.symbols)
            self.update_ai_status()
            self.analysis_text.insert(tk.END, "Обучение ИИ на всех парах завершено.\n")
        except Exception as e:
            self.analysis_text.insert(tk.END, f"Ошибка при обучении ИИ: {e}\n")
            log_critical_error(f"Ошибка при обучении ИИ: {e}")

    def setup_analysis_section(self):
        """Центральная область: Процесс анализа."""
        # Заголовок (центрирован)
        tk.Label(self.center_frame, text="Процесс анализа", font=("Arial", 14, "bold"),
                 bg="#28293e", fg="#ffffff", anchor="center").grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Текстовое поле (занимает 30% высоты блока)
        self.analysis_text = ScrolledText(
            self.center_frame,
            bg="#1e1e2f",
            fg="#a9b7c6",
            font=("Courier New", 10),
            insertbackground="#ffffff",
            relief="solid",
            borderwidth=1
        )
        self.analysis_text.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

        # Настройка сетки для растягивания
        self.center_frame.grid_columnconfigure(0, weight=1)
        self.center_frame.grid_rowconfigure(1, weight=1)  # Текстовое поле (30%)
        self.center_frame.grid_rowconfigure(2, weight=2)  # Оставшаяся часть (70%)

    def setup_result_section(self):
        """Правая панель: Общая рекомендация."""
        # Заголовок (центрирован)
        tk.Label(self.result_frame, text="Общая рекомендация", font=("Arial", 14, "bold"),
                 bg="#28293e", fg="#ffffff", anchor="center").grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Текстовое поле (занимает 30% высоты блока)
        self.result_text = ScrolledText(
            self.result_frame,
            bg="#1e1e2f",
            fg="#a9b7c6",
            font=("Courier New", 10),
            insertbackground="#ffffff",
            relief="solid",
            borderwidth=1
        )
        self.result_text.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

        # Настройка сетки для растягивания
        self.result_frame.grid_columnconfigure(0, weight=1)
        self.result_frame.grid_rowconfigure(1, weight=1)  # Текстовое поле (30%)
        self.result_frame.grid_rowconfigure(2, weight=2)  # Оставшаяся часть (70%)

    def start_analysis(self):
        """Обработчик кнопки 'Запустить анализ'."""
        self.analysis_text.delete("1.0", tk.END)
        self.result_text.delete("1.0", tk.END)

        self.analysis_text.insert(tk.END, "Запуск анализа...\n\n")

        try:
            symbol = self.symbol_var.get()
            self.analysis_text.insert(tk.END, f"Выбрана пара: {symbol}\n")

            capital = self.capital_entry.get()
            leverage = self.leverage_entry.get()
            self.analysis_text.insert(tk.END, f"Сумма ставки: {capital}\n")
            self.analysis_text.insert(tk.END, f"Плечо: {leverage}\n")

            fetcher = DataFetcher()
            data = fetcher.fetch_historical_data(symbol, timeframe='1h', limit=200)
            if data.empty:
                self.analysis_text.insert(tk.END, "Ошибка: Не удалось загрузить данные.\n")
                log_data_fetching_error(symbol, '1h', "Data is empty")
                return

            log_data_fetching(symbol, '1h')
            self.analysis_text.insert(tk.END, "Данные успешно загружены.\n")

            if not validate_data(data):
                self.analysis_text.insert(tk.END, "Ошибка: Данные не прошли валидацию.\n")
                log_data_validation(success=False)
                return

            log_data_validation(success=True)
            self.analysis_text.insert(tk.END, "Данные прошли валидацию.\n")

            self.analysis_text.insert(tk.END, "Расчет индикаторов...\n")
            trend_signal = Supertrend.get_signal(data)
            ema_signal = EMA.get_signal(data)
            rsi_signal = RSI.get_signal(data)
            macd_signal = MACD.get_signal(data)

            self.analysis_text.insert(tk.END, f"Supertrend: {trend_signal}\n")
            self.analysis_text.insert(tk.END, f"EMA: {ema_signal}\n")
            self.analysis_text.insert(tk.END, f"RSI: {rsi_signal}\n")
            self.analysis_text.insert(tk.END, f"MACD: {macd_signal}\n")

            self.analysis_text.insert(tk.END, "Прогнозирование с помощью ИИ...\n")
            predictor = AIPredictor()
            predictions = predictor.predict_price_movement(data)
            if predictions is not None:
                self.analysis_text.insert(tk.END, f"Прогноз: {predictions[-1]}\n")
            else:
                self.analysis_text.insert(tk.END, "Ошибка: Не удалось выполнить прогноз.\n")

            self.analysis_text.insert(tk.END, "Анализ завершен.\n")

        except Exception as e:
            self.analysis_text.insert(tk.END, f"Ошибка: {str(e)}\n")
            log_critical_error(f"Ошибка при выполнении анализа: {e}")

if __name__ == "__main__":
    app = TradingApp()
    app.mainloop()