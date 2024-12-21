# -*- coding: utf-8 -*-
# pip install pymongo
from pymongo import MongoClient
from yandex_cloud_ml_sdk import YCloudML
import json

# Подключение к MongoDB
def get_reviews_from_mongo():
    client = MongoClient("mongodb://localhost:27017")  # Локальный MongoDB
    db = client["config"]  # название датабазы
    collection = db["comments_database"]
    print(collection.find_one())

    # Извлечь отзывы
    # Извлечь только записи, где категория, важность или ответ еще не заполнены
    reviews = collection.find(
        {"date": {"$regex": "^(2024-11|2024-12)"}},
        {"_id": 1, "text_comment": 1}

    )
    return reviews, collection

'''

    reviews = collection.find(
        {
            "$and": [
                {"date": {"$regex": "^(2024-11|2024-12)"}},
                {
                    "$or": [
                        {"category": {"$exists": False}},
                        {"importance": {"$exists": False}},
                        {"answer": {"$exists": False}},
                        {"kratko": {"$exists": False}},
                        {"alarm": {"$exists": False}},
                        {"subcategory": {"$exists": False}}
                    ]
                }
            ]
        },
        {"_id": 1, "text_comment": 1}
    )
    return reviews, collection
'''


def classify_review(review_text):
    sdk = YCloudML(folder_id="b1g18jldnbpmeu58poqd", auth="AQVN3P6XL4XNCS5OBXz7ytktocp5A3LJ0fxt_OPF")
    model = sdk.models.completions('yandexgpt')
    model = model.configure(temperature=0.5)
    messages = [
        {
            "role": "system",
            "text": "У нас есть отзыв, его нужно определить на одну из трех категорий (благодарность, жалоба, и предложения), \
            также выявить, насколько важен этот отзыв. Если он важен (если важен, то будет отправляться пуш директору, его стоит беспокоить только по важным отзывам),\
            то дай ответ: да или нет. Важно, когда происходят аварии и какие-то необратимые мероприятия, также важно, когда консультанты очень хорошо работают.\
            Также если ты можешь дать ответ на данное обращение, то тогда распиши его (например, что ты можешь сам подготовить ответ клиенту на данное обращение)\
            Также дай мне ответ в виде была авария или нет, \
            Также напиши подкатегорию для этого: (качество обслуживания, продукты и услуги, работа мобильного приложения и сайта, прочее (если к остальному не относится)) \
            Дай мне ответ в виде JSON, чтобы можно было вставить в MongoDB:\
            '{\"category\": (твой ответ в формате json), \"importance\": (да или нет в формате json), \"answer\": (твой ответ (например, спасибо большое за ваше обращение, ваше мнение очень ценно для нас \
            или если его нет, то пиши, что нужна помощь оператора в формате json), \"kratko\": (напиши в 3-5 словах краткое описание отзыва), \"alarm\": (да или нет), \"subcategory\": (подкатегория из списка)"
        },
        {
            "role": "user",
            "text": review_text,
        },
    ]
    result = model.run(messages)

    # Если результат есть, извлекаем данные из ответа
    if result and len(result.alternatives) > 0:
        gpt_text = result.alternatives[0].text.strip()
        try:
            # Пытаемся преобразовать текст в JSON
            # print(f"Ответ модели 1: {gpt_text}")

            # Убираем лишние обратные кавычки, если они присутствуют
            if gpt_text.startswith("```") and gpt_text.endswith("```"):
                gpt_text = gpt_text[3:-3].strip()
            gpt_response = json.loads(gpt_text)  # Преобразуем строку в формат JSON (это нужно делать с осторожностью)
            return gpt_response
        except Exception as e:
            print(f"Ошибка при парсинге ответа: {e}")
            print(f"Ответ модели: {gpt_text}")

            return None
    else:
        print("Ошибка в запросе или пустой ответ.")
        return None

# Основная логика
if __name__ == "__main__":

    # Извлекаем отзывы из MongoDB
    reviews, collection = get_reviews_from_mongo()

    for record in reviews:
        review_id = record["_id"]
        review_text = record["text_comment"]
        # review_date = record["date"]

        # print(f"Обрабатываю отзыв с ID: {review_id}, дата: {review_date}")
        print(f"Обрабатываю отзыв с ID: {review_id}")


        # Обрабатываем текст через GPT
        gpt_response = classify_review(review_text)
        # print(f"Ответ GPT: {gpt_response}")

        if gpt_response:

            print(f"Ответ модели: {gpt_response}")

            collection.update_one(
                {"_id": review_id},
                {
                    "$set": gpt_response
                }, True
            )
            print(f"Отзыв с ID {review_id} успешно обновлен")
        else:
            print(f"Не удалось обработать отзыв с ID {review_id}")

    print("Все новые записи обработаны.")


