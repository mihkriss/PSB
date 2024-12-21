#6765a101fe7138f5de950712

from pymongo import MongoClient

def get_reviews_from_mongo():
    client = MongoClient("mongodb://localhost:27017")  # Локальный MongoDB
    db = client["comments_database"]  # название датабазы
    collection = db["comments_1"]
    # Извлечь отзывы
    # Извлечь только записи, где категория, важность или ответ еще не заполнены
    reviews = collection.find(
        {
            "$or": [
                {"category": {"$exists": False}},
                {"alarm": {"$exists": False}},
                {"answer": {"$exists": False}}
           #     {"kratko": {"$kratko": False}}
            ]
        },
        {"_id": 1, "text_comment": 1}
    )
    return reviews, collection

# Основная логика
if __name__ == "__main__":
    # Извлекаем отзывы из MongoDB
    reviews, collection = get_reviews_from_mongo()


    for record in reviews:
        review_id = record["_id"]
        review_text = record["text_comment"]

        print(f"Обрабатываю отзыв с ID: {review_id}, текст: {review_text}")


        collection.replace_one(
            {"_id": review_id},
            {"text_comment": "aaaaaaaaaaaaaaaaaaaaaaaaaaa"}, True
        )
        print(f"Отзыв с ID {review_id} успешно обновлен")

    print("Все новые записи обработаны.")


