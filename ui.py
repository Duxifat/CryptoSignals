def show_recommendation(results, text_widget):
    text_widget.config(state="normal")  # Разрешаем запись в текстовый блок
    text_widget.delete("1.0", "end")  # Очистка блока перед вставкой
    
    text_widget.insert("end", "Trading Analysis Results:\n\n")
    for timeframe, data in results.items():
        if timeframe == "Итоговая рекомендация":
            continue  # Пропустим итоговую рекомендацию для отдельного вывода
        recommendation = data.get("Final Recommendation", "Неопределенно")
        text_widget.insert("end", f"{timeframe}: {recommendation}\n")
    
    # Добавляем итоговую рекомендацию в конец
    final_recommendation = results.get("Итоговая рекомендация", {}).get("Final Recommendation", "Неопределенно")
    text_widget.insert("end", f"\nИтоговая рекомендация: {final_recommendation}\n")
    text_widget.config(state="disabled")  # Блокируем редактирование текста пользователем
