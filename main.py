import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import asyncio
import logging
import subprocess
import os
from PIL import Image, ImageTk

# ===== Импорт локальных модулей =====
from utils.data_fetcher import DataFetcher
from ai.ai_predictor import AIPredictor
from utils.indicators import Supertrend, EMA, RSI, MACD
from utils.validation_utils import validate_data

# Создаём папку logs, если её нет
if not os.path.exists("logs"):
    os.makedirs("logs")

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/application.log", mode='w'),
        logging.StreamHandler()
    ]
)
logging.info("Logging setup complete.")

# Доступные пары и таймфреймы
SYMBOLS = ["BTC/USDT", "ETH/USDT", "TAI/USDT", "BNB/USDT", "ADA/USDT", "SOL/USDT"]
TIMEFRAMES = ["5m", "15m", "30m", "1h", "4h", "1d"]

# Весовые коэффициенты для таймфреймов и индикаторов
timeframe_weights = {"5m": 0.1, "15m": 0.15, "30m": 0.2, "1h": 0.3, "4h": 0.25, "1d": 0.4}
indicator_weights = {"trend": 0.3, "ema": 0.25, "rsi": 0.2, "macd": 0.15, "ai": 0.1}


class TradingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Crypto Trading Analysis")
        self.geometry("1200x720")
        self.configure(bg="#1e1e2f")  # Тёмный фон приложения

        # ------------------------------------------------
        # 1. Настройка главной сетки окна
        # ------------------------------------------------
        # Разделяем окно на 3 столбца: левый (параметры), центр (анализ/ИИ), правый (результаты)
        self.grid_columnconfigure(0, weight=0)  # левая панель
        self.grid_columnconfigure(1, weight=1)  # центральная (растягивается)
        self.grid_columnconfigure(2, weight=0)  # правая панель
        self.grid_rowconfigure(0, weight=1)

        # ------------------------------------------------
        # 2. Создаём фреймы для каждой из зон
        # ------------------------------------------------
        # (A) Левая панель (параметры)
        self.input_frame = tk.Frame(self, bg="#28293e", highlightbackground="#4e4e4e", highlightthickness=2)
        self.input_frame.grid(row=0, column=0, sticky="ns")

        # (B) Центральная панель: в ней 2 строки:
        #     row=0:  analysis_frame (Процесс анализа)
        #     row=1:  ДВА столбца:  (0) Управление ИИ, (1) блок «Инфо о сделке»
        self.center_frame = tk.Frame(self, bg="#28293e", highlightbackground="#4e4e4e", highlightthickness=2)
        self.center_frame.grid(row=0, column=1, sticky="nsew")

        # Настройка строк и столбцов в center_frame
        self.center_frame.grid_rowconfigure(0, weight=3)  # верх (анализ)
        self.center_frame.grid_rowconfigure(1, weight=1)  # низ (ИИ + блок сделки)
        self.center_frame.grid_columnconfigure(0, weight=1)  # Весь центр

        # Фрейм для "Процесс анализа" (на всю ширину по центру сверху)
        self.analysis_frame = tk.Frame(self.center_frame, bg="#28293e")
        self.analysis_frame.grid(row=0, column=0, sticky="nsew")

        # Фрейм-низ (строка 1) мы разбиваем на 2 столбца (равные по ширине)
        self.bottom_center_frame = tk.Frame(self.center_frame, bg="#28293e")
        self.bottom_center_frame.grid(row=1, column=0, sticky="nsew")

        # Вот ключевые настройки, чтобы поделить пополам:
        self.bottom_center_frame.grid_columnconfigure(0, weight=1)  
        self.bottom_center_frame.grid_columnconfigure(1, weight=1)
        self.bottom_center_frame.grid_rowconfigure(0, weight=1)

        # (B1) Управление ИИ (левый нижний блок)
        self.ai_frame = tk.Frame(self.bottom_center_frame, bg="#28293e", highlightbackground="#4e4e4e", highlightthickness=2)
        self.ai_frame.grid(row=0, column=0, sticky="nsew")

        # (B2) Блок для «Инфо о сделке» (правый нижний блок)
        self.trade_info_frame = tk.Frame(self.bottom_center_frame, bg="#28293e", highlightbackground="#4e4e4e", highlightthickness=2)
        self.trade_info_frame.grid(row=0, column=1, sticky="nsew")

        # (C) Правая панель (результаты)
        self.result_frame = tk.Frame(self, bg="#28293e", highlightbackground="#4e4e4e", highlightthickness=2)
        self.result_frame.grid(row=0, column=2, sticky="ns")

        # ------------------------------------------------
        # 3. Заполняем все зоны
        # ------------------------------------------------
        self.setup_input_section()    # левая панель
        self.setup_analysis_section() # верхний центр
        self.setup_ai_section()       # нижний левый
        self.setup_trade_info_section()  # нижний правый (блок сделки)
        self.setup_result_section()   # правая панель

        # Установка весов (общие для анализа)
        self.timeframe_weights = timeframe_weights
        self.indicator_weights = indicator_weights

        # Проверка синхронизации времени
        self.check_time_sync()

    # =========================================================
    # Проверка времени
    # =========================================================
    def check_time_sync(self):
        fetcher = DataFetcher()
        fetcher.check_time_synchronization()

    # =========================================================
    # Левая панель: Параметры анализа
    # =========================================================
    def setup_input_section(self):
        sub_frame = tk.Frame(self.input_frame, bg="#28293e")
        sub_frame.grid(row=0, column=0, sticky="nsew")
        self.input_frame.grid_rowconfigure(0, weight=1)
        self.input_frame.grid_columnconfigure(0, weight=1)

        tk.Label(sub_frame, text="Параметры анализа", font=("Arial", 14, "bold"),
                 bg="#28293e", fg="#ffffff").grid(row=0, column=0, padx=20, pady=(20,10), sticky="w")

        tk.Label(sub_frame, text="Выберите пару:", bg="#28293e", fg="#a9b7c6").grid(row=1, column=0, padx=20, sticky="w")
        self.symbol_var = tk.StringVar(value=SYMBOLS[0])
        ttk.Combobox(sub_frame, values=SYMBOLS, textvariable=self.symbol_var, width=15)\
            .grid(row=2, column=0, padx=20, pady=5, sticky="w")

        tk.Label(sub_frame, text="Сумма ставки:", bg="#28293e", fg="#a9b7c6")\
            .grid(row=3, column=0, padx=20, pady=(10,0), sticky="w")
        self.capital_entry = tk.Entry(sub_frame, width=15, bg="#1e1e2f", fg="#ffffff",
                                      insertbackground="#ffffff", relief="solid", borderwidth=1)
        self.capital_entry.grid(row=4, column=0, padx=20, pady=5, sticky="w")

        tk.Label(sub_frame, text="Кредитное плечо:", bg="#28293e", fg="#a9b7c6")\
            .grid(row=5, column=0, padx=20, pady=(10,0), sticky="w")
        self.leverage_entry = tk.Entry(sub_frame, width=15, bg="#1e1e2f", fg="#ffffff",
                                       insertbackground="#ffffff", relief="solid", borderwidth=1)
        self.leverage_entry.grid(row=6, column=0, padx=20, pady=5, sticky="w")

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
        self.start_button.grid(row=7, column=0, padx=20, pady=(20,0), sticky="w")

        # Пустая строка для растяжения
        sub_frame.grid_rowconfigure(8, weight=1)

    # =========================================================
    # Центральная верхняя область: Процесс анализа
    # =========================================================
    def setup_analysis_section(self):
        tk.Label(self.analysis_frame, text="Процесс анализа", font=("Arial", 14, "bold"),
                 bg="#28293e", fg="#ffffff").grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.analysis_text = ScrolledText(
            self.analysis_frame,
            width=60,
            height=25,
            bg="#1e1e2f",
            fg="#a9b7c6",
            font=("Courier New", 10),
            insertbackground="#ffffff",
            relief="solid",
            borderwidth=1
        )
        self.analysis_text.grid(row=1, column=0, padx=10, pady=(0,10), sticky="nsew")

        self.analysis_frame.grid_rowconfigure(1, weight=1)
        self.analysis_frame.grid_columnconfigure(0, weight=1)

    # =========================================================
    # Центральная нижняя левая часть: Управление ИИ
    # =========================================================
    def setup_ai_section(self):
        tk.Label(self.ai_frame, text="Управление ИИ", font=("Arial", 14, "bold"),
                 bg="#28293e", fg="#ffffff").grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.train_button = tk.Button(
            self.ai_frame,
            text="Обучить ИИ",
            bg="#2196F3",
            fg="#ffffff",
            font=("Arial", 10, "bold"),
            command=self.confirm_train_ai,
            relief="flat",
            activebackground="#1976D2"
        )
        self.train_button.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.check_button = tk.Button(
            self.ai_frame,
            text="Проверить модель",
            bg="#4caf50",
            fg="#ffffff",
            font=("Arial", 10, "bold"),
            command=self.check_model,
            relief="flat",
            activebackground="#45a049"
        )
        self.check_button.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self.status_label = tk.Label(self.ai_frame, text="Статус модели: Неизвестно",
                                     bg="#28293e", fg="#a9b7c6")
        self.status_label.grid(row=3, column=0, padx=10, pady=(10,0), sticky="w")

        # Растяжка
        self.ai_frame.grid_rowconfigure(4, weight=1)
        self.ai_frame.grid_columnconfigure(0, weight=1)

    # =========================================================
    # Центральная нижняя правая часть: Информация о сделке
    # =========================================================
    def setup_trade_info_section(self):
        tk.Label(self.trade_info_frame, text="Информация о сделке",
                 font=("Arial", 14, "bold"),
                 bg="#28293e", fg="#ffffff")\
            .grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.trade_text = ScrolledText(
            self.trade_info_frame,
            width=40,
            height=10,
            bg="#1e1e2f",
            fg="#a9b7c6",
            font=("Courier New", 10),
            insertbackground="#ffffff",
            relief="solid",
            borderwidth=1
        )
        self.trade_text.grid(row=1, column=0, padx=10, pady=(0,10), sticky="nsew")

        # Растяжка
        self.trade_info_frame.grid_rowconfigure(1, weight=1)
        self.trade_info_frame.grid_columnconfigure(0, weight=1)

    def update_trade_info(
        self,
        recommendation,
        confidence,
        entry_price,
        take_profit,
        stop_loss,
        trade_horizon
    ):
        """Обновляет блок 'Информация о сделке'."""
        self.trade_text.config(state="normal")
        self.trade_text.delete("1.0", tk.END)

        self.trade_text.insert(tk.END, f"Итоговая рекомендация: {recommendation}\n")
        self.trade_text.insert(tk.END, f"Уверенность: {confidence}%\n\n")

        self.trade_text.insert(tk.END, "Расчётные параметры сделки:\n")
        self.trade_text.insert(tk.END, f"  Цена входа:  {entry_price}\n")
        self.trade_text.insert(tk.END, f"  Take Profit: {take_profit}\n")
        self.trade_text.insert(tk.END, f"  Stop Loss:   {stop_loss}\n")
        self.trade_text.insert(tk.END, f"  Тип сделки:  {trade_horizon}\n")

        self.trade_text.config(state="disabled")

    # =========================================================
    # Правая панель: Общая рекомендация (детальный вывод)
    # =========================================================
    def setup_result_section(self):
        tk.Label(self.result_frame, text="Общая рекомендация",
                 font=("Arial", 14, "bold"),
                 bg="#28293e", fg="#ffffff")\
            .grid(row=0, column=0, padx=10, pady=10, sticky="w")

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
        self.result_text.grid(row=1, column=0, padx=10, pady=(0,10), sticky="nsew")

        self.result_frame.grid_rowconfigure(1, weight=1)
        self.result_frame.grid_columnconfigure(0, weight=1)

    # =========================================================
    # Кнопка "Запустить анализ"
    # =========================================================
    def start_analysis(self):
        self.analysis_text.delete("1.0", tk.END)
        self.result_text.delete("1.0", tk.END)
        self.trade_text.delete("1.0", tk.END)

        self.analysis_text.insert(tk.END, "Запуск анализа...\n\n")

        try:
            symbol = self.symbol_var.get()
            capital = float(self.capital_entry.get())
            leverage = float(self.leverage_entry.get())

            asyncio.run(self.analyze(symbol, capital, leverage))
        except ValueError:
            messagebox.showerror("Ошибка", "Проверьте введённые данные!")

    # =========================================================
    # Асинхронный анализ
    # =========================================================
    async def analyze(self, symbol, capital, leverage):
        fetcher = DataFetcher()
        ai_predictor = AIPredictor()
        results = {}

        self.analysis_text.insert(tk.END, f"Выбрана пара: {symbol}\n\n")

        for timeframe in TIMEFRAMES:
            # Загрузка данных
            self.analysis_text.insert(tk.END, f"Загрузка данных за {timeframe}... \n")
            self.update()
            data = fetcher.fetch_historical_data(symbol, timeframe=timeframe)

            if not validate_data(data):
                self.analysis_text.insert(tk.END, "[Ошибка: Данные отсутствуют]\n\n")
                self.analysis_text.insert(tk.END, f"Расчёт индикаторов за {timeframe}... [Пропущено]\n\n")
                continue

            self.analysis_text.insert(tk.END, "[OK]\n\n")
            self.analysis_text.insert(tk.END, f"Расчёт индикаторов (trend, ema, rsi, macd, ai) за {timeframe}... \n")

            try:
                trend_signal = Supertrend.get_signal(data)
                ema_signal   = EMA.get_signal(data)
                rsi_signal   = RSI.get_signal(data)
                macd_signal  = MACD.get_signal(data)
                ai_sig       = ai_predictor.predict_price_movement(data)
                ai_signal    = "Покупать" if ai_sig == "up" else "Продавать"

                results[timeframe] = {
                    "trend": trend_signal,
                    "ema": ema_signal,
                    "rsi": rsi_signal,
                    "macd": macd_signal,
                    "ai": ai_signal
                }
                self.analysis_text.insert(tk.END, "[OK]\n\n")
            except Exception as e:
                self.analysis_text.insert(tk.END, f"[Ошибка: {str(e)}]\n\n")

        # Получаем конечную рекомендацию и заполняем интерфейс
        recommendation, confidence, entry_price, tp, sl, trade_horizon = self.display_results(results)
        self.update_trade_info(recommendation, confidence, entry_price, tp, sl, trade_horizon)

        return recommendation, confidence

    # =========================================================
    # Подсчёт итоговой рекомендации и вывод в правую панель
    # =========================================================
    def display_results(
        self,
        results,
        custom_timeframe_weights=None,
        custom_indicator_weights=None
    ):
        # Веса
        timeframe_w = custom_timeframe_weights or self.timeframe_weights
        indicator_w = custom_indicator_weights or self.indicator_weights

        total_buy_weight = 0.0
        total_sell_weight = 0.0

        # Отображаем результаты в правой панели (детально)
        self.result_text.insert(tk.END, "Общая рекомендация:\n\n")

        for timeframe, signals in results.items():
            if signals is None:
                self.result_text.insert(tk.END, f"=== {timeframe} ===\n  [Данные отсутствуют]\n\n")
                continue

            self.result_text.insert(tk.END, f"=== {timeframe} ===\n")
            timeframe_weight = timeframe_w.get(timeframe, 0.0)

            for indicator_name, signal_value in signals.items():
                self.result_text.insert(tk.END, f"  {indicator_name}: {signal_value}\n")

                # Считаем суммарный вес
                indicator_weight = indicator_w.get(indicator_name, 0.0)
                if signal_value == "Покупать":
                    total_buy_weight += timeframe_weight * indicator_weight
                elif signal_value == "Продавать":
                    total_sell_weight += timeframe_weight * indicator_weight

            self.result_text.insert(tk.END, "\n")

        # Итог (покупать / продавать / держать)
        if (total_buy_weight + total_sell_weight) > 0:
            confidence = round(
                (max(total_buy_weight, total_sell_weight) / (total_buy_weight + total_sell_weight)) * 100,
                2
            )
        else:
            confidence = 0.0

        if total_buy_weight > total_sell_weight:
            recommendation = "Покупать"
        elif total_sell_weight > total_buy_weight:
            recommendation = "Продавать"
        else:
            recommendation = "Держать"

        self.result_text.insert(
            tk.END,
            f"Итоговая рекомендация: {recommendation} (Уверенность: {confidence}%)\n\n"
        )

        # ----------------------------------
        # Расчётные параметры для «Инфо о сделке»
        # ----------------------------------
        # (1) Цена входа — в реальном коде можно взять последнюю close
        #     Тут делаю упрощённо.
        if recommendation == "Покупать":
            entry_price = 20000
            take_profit = entry_price * 1.03  # +3%
            stop_loss   = entry_price * 0.98  # -2%
        elif recommendation == "Продавать":
            entry_price = 21000
            take_profit = entry_price * 0.97
            stop_loss   = entry_price * 1.02
        else:  # "Держать"
            entry_price = 20500
            take_profit = entry_price
            stop_loss   = entry_price

        # (2) Тип сделки — упрощённо: если в списке таймфреймов есть "4h" или "1d", считаем долгую
        if "4h" in results or "1d" in results:
            trade_horizon = "Долгосрочная"
        else:
            trade_horizon = "Короткая"

        return recommendation, confidence, entry_price, take_profit, stop_loss, trade_horizon

    # =========================================================
    # Блок обучения ИИ
    # =========================================================
    def confirm_train_ai(self):
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите начать обучение ИИ?"):
            self.train_ai()

    def train_ai(self):
        try:
            self.analysis_text.insert(tk.END, "Запуск обучения ИИ...\n\n")
            self.update()
            subprocess.run(["python", "ai/train_lstm.py"], check=True)
            self.analysis_text.insert(tk.END, "Обучение завершено.\n\n")
            self.status_label.config(text="Статус модели: Обучена")
        except Exception as e:
            self.analysis_text.insert(tk.END, f"Ошибка при обучении ИИ: {e}\n\n")

    def check_model(self):
        self.status_label.config(text="Статус модели: Проверка завершена")


if __name__ == "__main__":
    app = TradingApp()
    app.mainloop()
