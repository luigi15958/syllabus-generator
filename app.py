import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os

st.set_page_config(page_title="מחולל סילבוסים", layout="centered")
st.title("📓 מחולל סילבוסים לבית הספר הדמוקרטי")

# טופס קלט מהמשתמש
with st.form("syllabus_form"):
    col1, col2 = st.columns(2)
    with col1:
        course_name = st.text_input("שם השיעור")
        teacher = st.text_input("שם המורה")
        hours_per_week = st.text_input("שעות שבועיות")
        grade = st.text_input("כיתה")
    with col2:
        requirements = st.text_area("דרישות הקורס (שורה לכל דרישה)")
        equipment = st.text_area("ציוד נדרש (שורה לכל פריט)")

    summary = st.text_area("תקציר הקורס")
    submitted = st.form_submit_button("צור סילבוס")

if submitted:
    template_path = "syllabus_template.png"
    if not os.path.exists(template_path):
        st.error("יש להעלות את קובץ התבנית 'syllabus_template.png' לתיקייה הראשית של האפליקציה.")
    else:
        image = Image.open(template_path).convert("RGBA")
        draw = ImageDraw.Draw(image)

        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        font_small = ImageFont.truetype(font_path, 26)
        font_medium = ImageFont.truetype(font_path, 32)

        draw.text((540, 240), course_name, font=font_medium, fill="black", anchor="ra")
        draw.text((540, 285), teacher, font=font_medium, fill="black", anchor="ra")
        draw.text((540, 330), hours_per_week, font=font_medium, fill="black", anchor="ra")
        draw.text((540, 375), grade, font=font_medium, fill="black", anchor="ra")

        y = 440
        for i, req in enumerate(requirements.splitlines()):
            draw.text((535, y + i * 50), req.strip(), font=font_small, fill="black", anchor="ra")

        draw.multiline_text((245, 590), summary, font=font_small, fill="black", anchor="la", spacing=6)

        y = 885
        for i, item in enumerate(equipment.splitlines()):
            draw.text((260, y + i * 45), item.strip(), font=font_small, fill="black", anchor="la")

        output_path = "סילבוס_ממולא.png"
        image.save(output_path)

        st.success("הסילבוס נוצר בהצלחה!")
        st.image(output_path, caption="סילבוס ממולא")
        with open(output_path, "rb") as file:
            st.download_button("הורד סילבוס", file, file_name="סילבוס_ממולא.png")
