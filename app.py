import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
import pandas as pd
from fpdf import FPDF

st.set_page_config(page_title="מחולל סילבוסים", layout="centered")

# עיצוב RTL בהתאמה לעברית
st.markdown(
    """
    <style>
    body, .css-1cpxqw2, .stTextInput, .stTextArea, .stButton, textarea, input {
        direction: RTL;
        text-align: right;
        font-family: Arial;
    }
    .block-container {
        background-color: #f4f4f9;
        border: 2px solid #e0e0e0;
        padding: 2em;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📓 מחולל סילבוסים לבית הספר הדמוקרטי")

# טופס קלט מהמשתמש
with st.form("syllabus_form"):
    st.subheader("🧾 פרטי הקורס")
    col1, col2 = st.columns(2)
    with col1:
        course_name = st.text_input("שם השיעור")
        teacher = st.text_input("שם המורה")
        hours_per_week = st.text_input("שעות שבועיות")
        divisions = st.multiselect("חטיבה", ["חטיבה צעירה", "חטיבת ג-ד", "חטיבת ה-ו", "חטיבה בוגרת", "תיכון"])
        domain = st.selectbox("תחום דעת", ["מקצועות הליבה", "מדעים", "העשרה", "אומנויות", "חינוך גופני ותנועה", "מדעי הרוח והחברה", "יזמות", "מלאכת כפיים"])
    with col2:
        requirements = st.text_area("📋 דרישות הקורס (שורה לכל דרישה)")
        equipment = st.text_area("🛠️ ציוד נדרש (שורה לכל פריט)")

    summary = st.text_area("📚 תקציר הקורס")
    submitted = st.form_submit_button("✏️ צור סילבוס")

# פונקציה לציור טקסטים על גבי תבנית המקורית

def generate_syllabus_image(course_name, teacher, hours_per_week, division, domain, requirements_list, summary, equipment_list):
    template_path = "syllabus_template_clean.png"
    image = Image.open(template_path).convert("RGBA")
    draw = ImageDraw.Draw(image)

    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font_medium = ImageFont.truetype(font_path, 30)
    font_small = ImageFont.truetype(font_path, 26)

    # כותרת ראשית
    draw.text((640, 145), course_name, font=font_medium, fill="black", anchor="mm")
    # פרטים טכניים בצד ימין
    draw.text((1050, 280), teacher, font=font_small, fill="black", anchor="ra")
    draw.text((1050, 330), hours_per_week, font=font_small, fill="black", anchor="ra")
    draw.text((1050, 380), division, font=font_small, fill="black", anchor="ra")
    draw.text((1050, 430), domain, font=font_small, fill="black", anchor="ra")

    # דרישות הקורס - מיושרות שמאלה ברשימה ממוספרת
    req_start_y = 540
    for i, line in enumerate(requirements_list):
        draw.text((410, req_start_y + i * 35), f"{i+1}. {line}", font=font_small, fill="black", anchor="la")

    # תקציר הקורס
    draw.multiline_text((100, 690), summary, font=font_small, fill="black", spacing=5, align="right")

    # ציוד נדרש - רשימת תבליטים
    equip_start_y = 900
    for i, line in enumerate(equipment_list):
        draw.text((100, equip_start_y + i * 30), f"- {line}", font=font_small, fill="black", anchor="la")

    output_path = "סילבוס_ממולא.png"
    image.save(output_path)
    return output_path

# תצוגה מקדימה ושמירה
if submitted:
    if course_name and teacher and divisions:
        for division in divisions:
            img_path = generate_syllabus_image(
                course_name,
                teacher,
                hours_per_week,
                division,
                domain,
                requirements.splitlines(),
                summary,
                equipment.splitlines()
            )

            st.success(f"✅ סילבוס נוצר עבור {division}")
            st.image(img_path, caption="תצוגה מקדימה של הסילבוס", use_container_width=True)

            with open("סילבוס_ממולא.png", "rb") as file:
                st.download_button("📥 הורד סילבוס", file, file_name=f"סילבוס_{division}.png")

            row = pd.DataFrame.from_dict({
                "שם שיעור": [course_name],
                "מורה": [teacher],
                "חטיבה": [division],
                "ש""ש": [hours_per_week],
                "תחום דעת": [domain],
                "דרישות": [requirements],
                "ציוד": [equipment],
                "תקציר": [summary]
            })

            if os.path.exists("syllabus_data.csv"):
                existing = pd.read_csv("syllabus_data.csv")
                updated = pd.concat([existing, row], ignore_index=True)
            else:
                updated = row

            updated.to_csv("syllabus_data.csv", index=False)

    else:
        st.error("אנא מלא את כל שדות החובה: שם שיעור, מורה, חטיבה")

# הצגת סילבוסים שהוזנו
st.markdown("---")
st.subheader("📚 סילבוסים שהוזנו")
if os.path.exists("syllabus_data.csv"):
    df = pd.read_csv("syllabus_data.csv")

    divisions_filter = st.multiselect("סנן לפי חטיבה", df["חטיבה"].dropna().unique().tolist(), default=df["חטיבה"].dropna().unique().tolist())
    if divisions_filter:
        df = df[df["חטיבה"].isin(divisions_filter)]

    st.dataframe(df)

    if st.button("📄 הורד ידיעון PDF מרוכז"):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_font('DejaVu', '', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', uni=True)

        for _, row in df.iterrows():
            pdf.add_page()
            pdf.set_font("DejaVu", size=14)
            pdf.cell(0, 10, f"שם שיעור: {row['שם שיעור']}", ln=True, align="R")
            pdf.cell(0, 10, f"מורה: {row['מורה']}", ln=True, align="R")
            pdf.cell(0, 10, f"ש""ש: {row['ש""ש']} | חטיבה: {row['חטיבה']}", ln=True, align="R")
            pdf.cell(0, 10, f"תחום דעת: {row['תחום דעת']}", ln=True, align="R")
            pdf.ln(5)
            pdf.set_font("DejaVu", size=12)
            pdf.multi_cell(0, 8, f"דרישות הקורס:\n{row['דרישות']}", align="R")
            pdf.multi_cell(0, 8, f"\nציוד נדרש:\n{row['ציוד']}", align="R")
            pdf.multi_cell(0, 8, f"\nתקציר הקורס:\n{row['תקציר']}", align="R")

        pdf_output = "ידיעון_סילבוסים.pdf"
        pdf.output(pdf_output)
        with open(pdf_output, "rb") as f:
            st.download_button("📘 הורד קובץ PDF מרוכז", f, file_name=pdf_output)
else:
    st.info("טרם הוזנו סילבוסים לאפליקציה.")
