import os
import requests
import re
import time
from flask import Flask

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8353596700:AAGGBzOlnQZepaq0lnXys4KlQNKozJpXq7A")
CHAT_ID = os.environ.get("CHAT_ID", "5316017487")

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'HTML'}
        requests.post(url, data=payload, timeout=10)
        return True
    except:
        return False

@app.route('/')
def home():
    return """
    <h1>🔍 Black Russia Debug</h1>
    <p><a href="/debug">🛠️ Проанализировать страницу FunPay</a></p>
    <p>После нажатия проверьте Telegram</p>
    """

@app.route('/debug')
def debug():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        url = "https://funpay.com/chips/186/"
        
        response = requests.get(url, headers=headers, timeout=15)
        
        # Анализируем HTML
        html = response.text
        
        # 1. Ищем все классы
        classes = re.findall(r'class="([^"]+)"', html[:8000])
        unique_classes = list(set(classes))[:30]
        
        # 2. Ищем элементы с ценами
        price_patterns = [
            r'>(\d{3,})\s*руб<',
            r'>(\d{3,})\s*₽<',
            r'(\d{3,})\s*руб',
            r'(\d{3,})\s*₽'
        ]
        
        prices = []
        for pattern in price_patterns:
            prices.extend(re.findall(pattern, html[:10000], re.IGNORECASE))
        
        # 3. Ищем элементы с black russia
        black_russia_matches = re.findall(r'black.*?russia|black russia|br', html[:10000], re.IGNORECASE)
        
        # 4. Ищем структуру товаров
        items_html = []
        item_pattern = r'<div[^>]*class="[^"]*item[^"]*"[^>]*>.*?руб.*?</div>'
        items_html = re.findall(item_pattern, html[:15000], re.DOTALL | re.IGNORECASE)
        
        # Формируем отчет
        report = f"""
📊 <b>АНАЛИЗ FUNPAY BLACK RUSSIA</b>

✅ Статус: {response.status_code}
📏 HTML размер: {len(html)} символов

🎯 <b>Найдено:</b>
• Классов: {len(classes)} (уникальных: {len(unique_classes)})
• Цен: {len(prices)} раз
• Упоминаний Black Russia: {len(black_russia_matches)}
• Потенциальных товаров: {len(items_html)}

🔍 <b>Примеры классов:</b>
{chr(10).join(unique_classes[:15])}

💰 <b>Примеры цен:</b>
{chr(10).join(list(set(prices))[:10])}

🛒 <b>Пример товара (если найден):</b>
"""
        
        if items_html:
            # Берем первый товар и очищаем
            sample_item = items_html[0]
            sample_item = re.sub(r'\s+', ' ', sample_item)
            sample_item = sample_item[:500] + "..." if len(sample_item) > 500 else sample_item
            report += f"\n<pre>{sample_item}</pre>"
        else:
            report += "\n❌ Товары не найдены по шаблону"
        
        report += "\n\n<b>Пришлите этот отчет разработчику!</b>"
        
        # Отправляем в Telegram
        send_telegram(report)
        
        return f"""
        <h1>✅ Отчет отправлен в Telegram!</h1>
        <p>Проверьте Telegram-бота</p>
        <p>Найдено: {len(items_html)} потенциальных товаров</p>
        <p>Пришлите отчет разработчику для настройки парсинга</p>
        """
        
    except Exception as e:
        error_msg = f"❌ Ошибка: {str(e)}"
        send_telegram(error_msg)
        return error_msg

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
