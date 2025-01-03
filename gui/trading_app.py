import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox
from data_fetcher import DataFetcher
from ai_predictor import AIPredictor
from utils.indicators import Supertrend, EMA, RSI, MACD
from utils.validation_utils import validate_data
from utils.logging_utils import setup_logging, TextWindowHandler
from datetime import datetime, timezone
import logging
import threading
import asyncio
import sys

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

        # Настройка логирования в текстовое окно
        self.setup_logging_to_text_window()

        # Обновление статуса ИИ при запуске
        self.update_ai_status()

        # Запуск часов
        self.update_clock()

    def setup_logging_to_text_window(self):
        """Настраивает логирование в текстовое окно."""
        text_handler = TextWindowHandler(self.analysis_text)
        text_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.addHandler(text_handler)

    def validate_number(self, P):
        """Валидация: разрешает ввод только чисел."""
        if P == "":
            return True
        try:
            float(P)
            return True
        except ValueError:
            return False

    def setup_input_section(self):
        """Левая панель: Параметры анализа."""
        sub_frame = tk.Frame(self.input_frame, bg="#28293e")
        sub_frame.grid(row=0, column=0, sticky="nsew")

        # Заголовок
        tk.Label(sub_frame, text="Параметры анализа", font=("Arial", 14, "bold"),
                 bg="#28293e", fg="#ffffff", anchor="center").grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        # Выбор пары
        tk.Label(sub_frame, text="Выберите пару:", bg="#28293e", fg="#a9b7c6", anchor="center").grid(row=1, column=0, padx=20, sticky="ew")
        self.symbol_var = tk.StringVar(value="BTCUSDT")
        self.symbols = [
            "BTCUSDT", "ETHUSDT", "XRPUSDT", "SOLUSDT", 
            "DOGEUSDT", "TAIUSDT", "ADAUSDT", "SUIUSDT", 
            "VIRTUALUSDT"
        ]
        ttk.Combobox(sub_frame, values=self.symbols, textvariable=self.symbol_var, width=15).grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        # Сумма ставки
        tk.Label(sub_frame, text="Сумма ставки:", bg="#28293e", fg="#a9b7c6", anchor="center").grid(row=3, column=0, padx=20, pady=(10, 0), sticky="ew")
        self.capital_entry = tk.Entry(sub_frame, width=15, bg="#1e1e2f", fg="#ffffff",
                                      insertbackground="#ffffff", relief="solid", borderwidth=1,
                                      validate="key", validatecommand=(self.register(self.validate_number), "%P"))
        self.capital_entry.grid(row=4, column=0, padx=20, pady=5, sticky="ew")

        # Плечо
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
            command=self.start_train_ai_on_all_pairs,
            relief="flat",
            activebackground="#45a049"
        )
        self.train_all_button.grid(row=9, column=0, padx=20, pady=(20, 0), sticky="ew")

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

    def start_train_ai_on_all_pairs(self):
        """Запускает обучение ИИ в отдельном потоке."""
        self.analysis_text.delete("1.0", tk.END)  # Очистка окна
        threading.Thread(target=self.run_async_train, daemon=True).start()

    def run_async_train(self):
        """Запускает асинхронное обучение."""
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(self.train_ai_on_all_pairs())

    async def train_ai_on_all_pairs(self):
        """Обработчик кнопки 'Обучить ИИ на всех парах'."""
        logging.info("Запуск обучения ИИ на всех парах...")
        try:
            predictor = AIPredictor()
            await predictor.train_ai_on_all_timeframes(self.symbols)
            self.update_ai_status()
            logging.info("Обучение ИИ на всех парах завершено.")
        except Exception as e:
            logging.error(f"Ошибка при обучении ИИ: {e}")
            messagebox.showerror("Ошибка", f"Ошибка при обучении ИИ: {e}")

    def setup_analysis_section(self):
        """Центральная область: Процесс анализа."""
        tk.Label(self.center_frame, text="Процесс анализа", font=("Arial", 14, "bold"),
                 bg="#28293e", fg="#ffffff", anchor="center").grid(row=0, column=0, padx=10, pady=10, sticky="ew")

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

        self.center_frame.grid_columnconfigure(0, weight=1)
        self.center_frame.grid_rowconfigure(1, weight=1)

    def setup_result_section(self):
        """Правая панель: Общая рекомендация."""
        tk.Label(self.result_frame, text="Общая рекомендация", font=("Arial", 14, "bold"),
                 bg="#28293e", fg="#ffffff", anchor="center").grid(row=0, column=0, padx=10, pady=10, sticky="ew")

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

        self.result_frame.grid_columnconfigure(0, weight=1)
        self.result_frame.grid_rowconfigure(1, weight=1)

    def calculate_trade_parameters(self, data, trend_signal, ema_signal, rsi_signal, macd_signal, predictions):
        """
        Рассчитывает параметры сделки: цену входа, тейк-профит, стоп-лосс и вероятность успеха.
        :param data: Исторические данные.
        :param trend_signal: Сигнал Supertrend.
        :param ema_signal: Сигнал EMA.
        :param rsi_signal: Сигнал RSI.
        :param macd_signal: Сигнал MACD.
        :param predictions: Прогнозы ИИ.
        :return: Словарь с параметрами сделки.
        """
        try:
            # Текущая цена закрытия
            current_price = data['close'].iloc[-1]

            # Расчет цены входа
            entry_price = current_price

            # Расчет тейк-профита и стоп-лосса на основе волатильности (ATR)
            atr = data['high'].iloc[-1] - data['low'].iloc[-1]  # Простой ATR
            take_profit = entry_price + atr * 1.5  # Тейк-профит: 1.5 * ATR
            stop_loss = entry_price - atr * 1.0    # Стоп-лосс: 1.0 * ATR

            # Расчет вероятности успеха
            success_probability = 0.7  # Базовая вероятность (можно улучшить на основе данных)

            # Корректировка параметров на основе сигналов
            if trend_signal == "Покупать":
                take_profit = entry_price + atr * 2.0  # Увеличиваем тейк-профит для бычьего тренда
                stop_loss = entry_price - atr * 0.8    # Уменьшаем стоп-лосс
                success_probability += 0.1
            elif trend_signal == "Продавать":
                take_profit = entry_price - atr * 2.0  # Увеличиваем тейк-профит для медвежьего тренда
                stop_loss = entry_price + atr * 0.8    # Уменьшаем стоп-лосс
                success_probability += 0.1

            if rsi_signal == "Перепроданность":
                success_probability += 0.05
            elif rsi_signal == "Перекупленность":
                success_probability -= 0.05

            if macd_signal == "Покупать":
                success_probability += 0.05
            elif macd_signal == "Продавать":
                success_probability -= 0.05

            # Ограничение вероятности в пределах 0.5 - 0.95
            success_probability = max(0.5, min(0.95, success_probability))

            return {
                "entry_price": round(entry_price, 2),
                "take_profit": round(take_profit, 2),
                "stop_loss": round(stop_loss, 2),
                "success_probability": round(success_probability * 100, 2)  # В процентах
            }
        except Exception as e:
            logging.error(f"Ошибка при расчете параметров сделки: {e}")
            return {
                "entry_price": None,
                "take_profit": None,
                "stop_loss": None,
                "success_probability": None
            }

    def generate_recommendation(self, trend_signal, ema_signal, rsi_signal, macd_signal, predictions):
        """Генерирует общую рекомендацию и параметры сделки."""
        buy_signals = 0
        sell_signals = 0

        if trend_signal == "Покупать":
            buy_signals += 1
        elif trend_signal == "Продавать":
            sell_signals += 1

        if ema_signal == "Покупать":
            buy_signals += 1
        elif ema_signal == "Продавать":
            sell_signals += 1

        if rsi_signal == "Перепроданность":
            buy_signals += 1
        elif rsi_signal == "Перекупленность":
            sell_signals += 1

        if macd_signal == "Покупать":
            buy_signals += 1
        elif macd_signal == "Продавать":
            sell_signals += 1

        if predictions is not None and predictions[-1] > 0:
            buy_signals += 1
        elif predictions is not None and predictions[-1] < 0:
            sell_signals += 1

        if buy_signals > sell_signals:
            recommendation = "Покупать"
        elif sell_signals > buy_signals:
            recommendation = "Продавать"
        else:
            recommendation = "Держать"

        # Расчет параметров сделки
        trade_parameters = self.calculate_trade_parameters(data, trend_signal, ema_signal, rsi_signal, macd_signal, predictions)

        return {
            "recommendation": recommendation,
            "entry_price": trade_parameters["entry_price"],
            "take_profit": trade_parameters["take_profit"],
            "stop_loss": trade_parameters["stop_loss"],
            "success_probability": trade_parameters["success_probability"]
        }

    def start_analysis(self):
        """Обработчик кнопки 'Запустить анализ'."""
        self.analysis_text.delete("1.0", tk.END)  # Очистка окна
        logging.info("Запуск анализа...")

        try:
            symbol = self.symbol_var.get()
            logging.info(f"Выбрана пара: {symbol}")

            capital = self.capital_entry.get()
            leverage = self.leverage_entry.get()
            logging.info(f"Сумма ставки: {capital}")
            logging.info(f"Плечо: {leverage}")

            # Шаг 1: Загрузка данных
            logging.info("Шаг 1: Загрузка исторических данных...")
            fetcher = DataFetcher()
            data = fetcher.fetch_historical_data(symbol, timeframe='1h', limit=200)
            if data.empty:
                logging.error("Ошибка: Не удалось загрузить данные.")
                messagebox.showerror("Ошибка", "Не удалось загрузить данные. Проверьте интернет-соединение.")
                return

            logging.info("Данные успешно загружены.")

            # Шаг 2: Валидация данных
            logging.info("Шаг 2: Валидация данных...")
            if not validate_data(data):
                logging.error("Ошибка: Данные не прошли валидацию.")
                messagebox.showerror("Ошибка", "Данные не прошли валидацию.")
                return

            logging.info("Данные прошли валидацию.")

            # Шаг 3: Расчет индикаторов
            logging.info("Шаг 3: Расчет индикаторов...")
            trend_signal = Supertrend.get_signal(data)
            ema_signal = EMA.get_signal(data)
            rsi_signal = RSI.get_signal(data)
            macd_signal = MACD.get_signal(data)

            logging.info(f"Supertrend: {trend_signal}")
            logging.info(f"EMA: {ema_signal}")
            logging.info(f"RSI: {rsi_signal}")
            logging.info(f"MACD: {macd_signal}")

            # Шаг 4: Прогнозирование с помощью ИИ
            logging.info("Шаг 4: Прогнозирование с помощью ИИ...")
            predictor = AIPredictor()
            predictions = predictor.predict_price_movement(data)
            if predictions is not None:
                logging.info(f"Прогноз: {predictions[-1]}")
            else:
                logging.error("Ошибка: Не удалось выполнить прогноз.")
                messagebox.showerror("Ошибка", "Не удалось выполнить прогноз.")

            # Шаг 5: Формирование рекомендации
            logging.info("Шаг 5: Формирование рекомендации...")
            recommendation = self.generate_recommendation(trend_signal, ema_signal, rsi_signal, macd_signal, predictions)
            self.result_text.insert(tk.END, f"Рекомендация: {recommendation['recommendation']}\n")
            self.result_text.insert(tk.END, f"Цена входа: {recommendation['entry_price']}\n")
            self.result_text.insert(tk.END, f"Тейк-профит: {recommendation['take_profit']}\n")
            self.result_text.insert(tk.END, f"Стоп-лосс: {recommendation['stop_loss']}\n")
            self.result_text.insert(tk.END, f"Вероятность успеха: {recommendation['success_probability']}%\n")

            logging.info("Анализ завершен.")

        except Exception as e:
            logging.error(f"Ошибка: {str(e)}")
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

if __name__ == "__main__":
    app = TradingApp()
    app.mainloop()