import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from data_fetcher import DataFetcher
from ai_predictor import AIPredictor
from utils.indicators import Supertrend, EMA, RSI, MACD
from utils.validation_utils import validate_data
import logging

class TradingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Crypto Trading Analysis")
        self.geometry("1200x720")
        self.configure(bg="#1e1e2f")  # Тёмный фон приложения

        # Настройка главной сетки окна
        self.grid_columnconfigure(0, weight=0)  # левая панель
        self.grid_columnconfigure(1, weight=1)  # центральная (растягивается)
        self.grid_columnconfigure(2, weight=0)  # правая панель
        self.grid_rowconfigure(0, weight=1)

        # Создание фреймов для каждой из зон
        self.input_frame = tk.Frame(self, bg="#28293e", highlightbackground="#4e4e4e", highlightthickness=2)
        self.input_frame.grid(row=0, column=0, sticky="ns")

        self.center_frame = tk.Frame(self, bg="#28293e", highlightbackground="#4e4e4e", highlightthickness=2)
        self.center_frame.grid(row=0, column=1, sticky="nsew")

        self.result_frame = tk.Frame(self, bg="#28293e", highlightbackground="#4e4e4e", highlightthickness=2)
        self.result_frame.grid(row=0, column=2, sticky="ns")

        # Заполнение зон
        self.setup_input_section()    # левая панель
        self.setup_analysis_section() # верхний центр
        self.setup_result_section()   # правая панель

    def setup_input_section(self):
        """Левая панель: Параметры анализа."""
        sub_frame = tk.Frame(self.input_frame, bg="#28293e")
        sub_frame.grid(row=0, column=0, sticky="nsew")

        tk.Label(sub_frame, text="Параметры анализа", font=("Arial", 14, "bold"),
                 bg="#28293e", fg="#ffffff").grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        tk.Label(sub_frame, text="Выберите пару:", bg="#28293e", fg="#a9b7c6").grid(row=1, column=0, padx=20, sticky="w")
        self.symbol_var = tk.StringVar(value="BTC/USDT")
        ttk.Combobox(sub_frame, values=["BTC/USDT", "ETH/USDT"], textvariable=self.symbol_var, width=15)\
            .grid(row=2, column=0, padx=20, pady=5, sticky="w")

        tk.Label(sub_frame, text="Сумма ставки:", bg="#28293e", fg="#a9b7c6").grid(row=3, column=0, padx=20, pady=(10, 0), sticky="w")
        self.capital_entry = tk.Entry(sub_frame, width=15, bg="#1e1e2f", fg="#ffffff",
                                      insertbackground="#ffffff", relief="solid", borderwidth=1)
        self.capital_entry.grid(row=4, column=0, padx=20, pady=5, sticky="w")

        # Кнопка "Запустить анализ"
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
        self.start_button.grid(row=5, column=0, padx=20, pady=(20, 0), sticky="w")

    def setup_analysis_section(self):
        """Центральная область: Процесс анализа."""
        tk.Label(self.center_frame, text="Процесс анализа", font=("Arial", 14, "bold"),
                 bg="#28293e", fg="#ffffff").grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.analysis_text = ScrolledText(
            self.center_frame,
            width=60,
            height=25,
            bg="#1e1e2f",
            fg="#a9b7c6",
            font=("Courier New", 10),
            insertbackground="#ffffff",
            relief="solid",
            borderwidth=1
        )
        self.analysis_text.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

    def setup_result_section(self):
        """Правая панель: Общая рекомендация."""
        tk.Label(self.result_frame, text="Общая рекомендация", font=("Arial", 14, "bold"),
                 bg="#28293e", fg="#ffffff").grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.result_text = ScrolledText(
            self.result_frame,
            width=40,
            height=35,
            bg="#1e1e2f",
            fg="#a9b7c6",
            font=("Courier New", 10),
            insertbackground="#ffffff",
            relief="solid",
            borderwidth=1
        )
        self.result_text.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

    def start_analysis(self):
        """Обработчик кнопки 'Запустить анализ'."""
        self.analysis_text.delete("1.0", tk.END)
        self.result_text.delete("1.0", tk.END)

        self.analysis_text.insert(tk.END, "Запуск анализа...\n\n")

        try:
            # Получаем выбранную пару
            symbol = self.symbol_var.get()
            self.analysis_text.insert(tk.END, f"Выбрана пара: {symbol}\n")

            # Загружаем исторические данные
            fetcher = DataFetcher()
            data = fetcher.fetch_historical_data(symbol, timeframe='1h', limit=200)
            if data.empty:
                self.analysis_text.insert(tk.END, "Ошибка: Не удалось загрузить данные.\n")
                return

            self.analysis_text.insert(tk.END, "Данные успешно загружены.\n")

            # Проверяем данные
            if not validate_data(data):
                self.analysis_text.insert(tk.END, "Ошибка: Данные не прошли валидацию.\n")
                return

            self.analysis_text.insert(tk.END, "Данные прошли валидацию.\n")

            # Применяем индикаторы
            self.analysis_text.insert(tk.END, "Расчет индикаторов...\n")
            trend_signal = Supertrend.get_signal(data)
            ema_signal = EMA.get_signal(data)
            rsi_signal = RSI.get_signal(data)
            macd_signal = MACD.get_signal(data)

            self.analysis_text.insert(tk.END, f"Supertrend: {trend_signal}\n")
            self.analysis_text.insert(tk.END, f"EMA: {ema_signal}\n")
            self.analysis_text.insert(tk.END, f"RSI: {rsi_signal}\n")
            self.analysis_text.insert(tk.END, f"MACD: {macd_signal}\n")

            # Прогнозируем с помощью ИИ
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
            logging.error(f"Ошибка при выполнении анализа: {e}")