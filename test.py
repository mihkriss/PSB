# -*- coding: utf-8 -*-
from pymongo import MongoClient
from yandex_cloud_ml_sdk import YCloudML
import json
from datetime import datetime

# Подключение к MongoDB
def get_reviews_from_mongo():
    client = MongoClient("mongodb://localhost:27017")  # Локальный MongoDB
    db = client["config"]  # Название базы данных
    collection = db["comments_database"]

    today = datetime.now().strftime("%Y-%m-%d")  # Текущая дата в формате 'YYYY-MM-DD'

    # Извлечь отзывы с текущей датой
    reviews = collection.find(
        {"date": {"$regex": f"^{today}"}},  # Фильтр по текущей дате
        sort=[("date", -1)]  # Сортировка по дате
    )
    return reviews, collection

def classify_review(review_text):
    sdk = YCloudML(folder_id="b1g18jldnbpmeu58poqd", auth="AQVN3P6XL4XNCS5OBXz7ytktocp5A3LJ0fxt_OPF")
    model = sdk.models.completions('yandexgpt')
    model = model.configure(temperature=0.5)

    messages = [
        {
            "role": "system",
            "text": "У нас есть отзыв, его нужно определить на одну из трех категорий (благодарность, жалоба, предложения), \
            также выявить, насколько важен этот отзыв. Если он важен (если важен, то будет отправляться пуш директору, его стоит беспокоить только по важным отзывам),\
            то дай ответ: да или нет. Важно, когда происходят аварии и какие-то необратимые мероприятия, также важно, когда консультанты очень хорошо работают.\
            Также если ты можешь дать ответ на данное обращение, то тогда распиши его (например, что ты можешь сам подготовить ответ клиенту на данное обращение)\
            Также дай мне ответ в виде была авария или нет, \
            Также напиши подкатегорию для этого: (качество обслуживания, продукты и услуги, работа мобильного приложения и сайта, прочее (если к остальному не относится)) \
            Дай мне ответ в формате JSON, чтобы можно было вставить в MongoDB."
        },
        {
            "role": "user",
            "text": review_text,
        },
    ]

    result = model.run(messages)

    if result and len(result.alternatives) > 0:
        gpt_text = result.alternatives[0].text.strip()
        try:
            if gpt_text.startswith("```") and gpt_text.endswith("```"):
                gpt_text = gpt_text[3:-3].strip()
            gpt_response = json.loads(gpt_text)  # Преобразуем строку в JSON
            return gpt_response
        except Exception as e:
            print(f"Ошибка при парсинге ответа: {e}")
            print(f"Ответ модели: {gpt_text}")
            return None
    else:
        print("Ошибка в запросе или пустой ответ.")
        return None

def save_comments_to_db(collection, comments):
    if comments:
        for comment in comments:
            # Преобразуем _id.$oid в строку, если существует
            if "_id" in comment and "$oid" in comment["_id"]:
                comment["_id"] = comment["_id"]["$oid"]

            '''# Проверяем, существует ли запись в базе
            if not collection.find_one({
                "text_comment": comment["text_comment"],
                "date": comment["date"],
                "name": comment["name"]
            }):'''
            collection.insert_one(comment)
        print(f"Комментарии успешно добавлены в базу данных.")

if __name__ == "__main__":
    reviews, collection = get_reviews_from_mongo()

    with open('example.txt', 'r', encoding='utf-8') as file:
        input_json = json.loads(file.read())  # Преобразуем текст в JSON

    save_comments_to_db(collection, [input_json])

    for record in reviews:
        review_id = record["_id"]
        review_text = record["text_comment"]

        print(f"Обрабатываю отзыв с ID: {review_id}")

        gpt_response = classify_review(review_text)

        if gpt_response:
            collection.update_one(
                {"_id": review_id},
                {"$set": gpt_response}
            )
            print(f"Отзыв с ID {review_id} успешно обновлен.")
        else:
            print(f"Не удалось обработать отзыв с ID {review_id}.")

    print("Все новые записи обработаны.")
