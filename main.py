from ctypes import c_bool

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Установить широкую страницу
st.set_page_config(page_title="Дашборд", layout="wide")

# Заголовок
st.title("Дашборд удовлетворенности клиентов")

# Разделение области на две части: индекс удовлетворенности и график категорий
col1, col2, col3 = st.columns([2, 4, 3])

c_j = 123
c_b = 112
c_p = 4
counts = [c_j, c_b, c_p]
percentages = [round(c_j * 100 / (sum(counts))), round(c_b * 100 / sum(counts)), round(c_p * 100/ sum(counts))]


# Индекс удовлетворенности клиентов
with col1:
    st.subheader("ИКС")
    # Полукруговая диаграмма
    fig, ax = plt.subplots(figsize=(4, 2))
    mean_rating = 10 - (9 * percentages[0] / 100) + 5 * (percentages[1] / 100) + 4 * (percentages[2] / 100)
    values = [10 - mean_rating, mean_rating]
    colors = ['#d9d9d9', '#76c893']
    wedges, texts = ax.pie(
        values,
        colors=colors,
        startangle=270,
        radius=1.0,
        wedgeprops={"width": 0.3}
    )
    plt.text(0, 0, str(mean_rating), ha='center', va='center', fontsize=20, fontweight='bold')
    ax.set(aspect="equal")
    st.pyplot(fig)

    st.subheader("Доля автоответов")
    # Полукруговая диаграмма
    fig, ax = plt.subplots(figsize=(4, 2))
    part_auto = 0.6
    values = [1 - part_auto, part_auto]
    colors = ['#d9d9d9', '#76c893']
    wedges, texts = ax.pie(
        values,
        colors=colors,
        startangle=270,
        radius=1.0,
        wedgeprops={"width": 0.3}
    )
    plt.text(0, 0, str(part_auto), ha='center', va='center', fontsize=20, fontweight='bold')
    ax.set(aspect="equal")
    st.pyplot(fig)

# График категорий
with col2:
    st.subheader("Категории")
    # Данные для графика
    categories = ["Жалобы", "Благодарности", "Предложения"]
    counts = [c_j, c_b, c_p]
    percentages = [round(c_j * 100 / (sum(counts))), round(c_b * 100 / sum(counts)), round(c_p * 100/ sum(counts))]

    # Построение столбчатой диаграммы
    fig, ax = plt.subplots(figsize=(3, 1.5))
    bars = ax.bar(categories, percentages, color=['#d9534f', '#5bc0de', '#5cb85c'])
    ax.set_ylabel("Процент от общего количества")
    ax.set_ylim(0, 60)
    ax.bar_label(bars, labels=[f"{count} ({percent}%)" for count, percent in zip(counts, percentages)])
    st.pyplot(fig)

    kategories = ["Приложение", "Обслуживание", "Продукты"]
    k_j = 10
    k_b = 141
    k_p = 54
    counts = [k_j, k_b, k_p]
    percentages = [round(k_j * 100 / (sum(counts))), round(k_b * 100 / sum(counts)), round(k_p * 100/ sum(counts))]

    # Построение столбчатой диаграммы
    fig, ax = plt.subplots(figsize=(3, 1.5))
    bars = ax.bar(kategories, percentages, color=['#d9534f', '#5bc0de', '#5cb85c'])
    ax.set_ylabel("Процент от общего количества")
    ax.set_ylim(0, 60)
    ax.bar_label(bars, labels=[f"{count} ({percent}%)" for count, percent in zip(counts, percentages)])
    st.pyplot(fig)

with col3:
    # Средняя оценка и количество отзывов
    st.subheader("Средняя оценка и количество отзывов")
    col1, col2 = st.columns(2)
    col1.metric("Средняя оценка", "4.3")
    col2.metric("Количество отзывов", "174")

    # Динамика
    st.subheader("Динамика")
    col1, col2, col3 = st.columns(3)
    col1.metric("Текущий месяц", "4.3")
    col2.metric("Прошлый месяц", "4.26")
    col3.metric("Изменение", "+0.037")

    # Доля отрицательных отзывов
    st.subheader("Доля отрицательных отзывов")
    col1, col2 = st.columns(2)
    col1.metric("Текущий месяц", "8%")
    col2.metric("Изменение с прошлым месяцем", "-1,5%")

