# ============================================================
# ไฟล์      : english_app.py  (XP Edition)
# โปรเจกต์  : 1 Year to Fluent — Gamification Update
# วิธีรัน   : streamlit run english_app.py
# ต้องมี    : data.py อยู่ในโฟลเดอร์เดียวกัน
# ============================================================

import streamlit as st
from gtts import gTTS
import io
from data import lessons_data   # ดึงข้อมูลบทเรียนทั้งหมดจากไฟล์ data.py


# ============================================================
# 1. ตั้งค่าหน้าเว็บ
# ============================================================

st.set_page_config(
    page_title="1 Year to Fluent",
    page_icon="🏆",
    layout="wide"
)

# CSS ตกแต่งหน้าตาแอปให้สวยงามและโค้งมน
st.markdown("""
<style>
    /* Sidebar พื้นหลังสีกรมท่าเข้ม */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    [data-testid="stSidebar"] * { color: white !important; }

    /* กล่อง XP สีทอง */
    .xp-box {
        background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
        border-radius: 16px;
        padding: 16px 20px;
        text-align: center;
        margin-bottom: 12px;
        box-shadow: 0 4px 15px rgba(253,160,133,0.4);
    }
    .xp-box h2 { color: #1a1a2e !important; margin: 0; font-size: 2rem; }
    .xp-box p  { color: #1a1a2e !important; margin: 0; font-size: 0.85rem; opacity: 0.8; }

    /* การ์ดประโยคมีเส้นซ้ายสีฟ้า */
    .phrase-card {
        background: #f8faff;
        border-left: 5px solid #4a90e2;
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 10px;
    }
    /* กล่องคำถาม Quiz สีม่วงอ่อน */
    .quiz-card {
        background: #f0f0ff;
        border-left: 5px solid #7c5cbf;
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 6px;
    }
    /* ปุ่ม primary สีเขียวสดใส */
    div[data-testid="stButton"] button[kind="primary"] {
        border-radius: 14px !important;
        font-size: 1.1rem !important;
        padding: 14px !important;
        background: linear-gradient(135deg, #43e97b, #38f9d7) !important;
        border: none !important;
        color: #1a1a2e !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# 2. ระบบ Session State — หน่วยความจำของแอปตลอด Session
# ============================================================

# completed_days: list เก็บชื่อ Day ที่เรียนจบแล้ว
if "completed_days" not in st.session_state:
    st.session_state.completed_days = []

# total_xp: คะแนนประสบการณ์รวมทั้งหมด เริ่มต้นที่ 0
if "total_xp" not in st.session_state:
    st.session_state.total_xp = 0

# quiz_answers: เก็บคำตอบของผู้ใช้ {index: "คำตอบ"}
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}

# quiz_checked: True = กดตรวจแล้ว / False = ยังไม่ได้กด
if "quiz_checked" not in st.session_state:
    st.session_state.quiz_checked = False

# current_day: ใช้ตรวจจับการเปลี่ยน Day เพื่อรีเซ็ต quiz
if "current_day" not in st.session_state:
    st.session_state.current_day = None


# ============================================================
# 3. ฟังก์ชันช่วย
# ============================================================

def get_audio_bytes(text: str) -> bytes:
    """แปลงประโยคภาษาอังกฤษเป็นไฟล์เสียง MP3 ใน Memory"""
    tts = gTTS(text=text, lang="en", slow=False)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf.read()


def xp_to_level(xp: int) -> tuple:
    """
    แปลง XP → Level
    สูตร: ทุก 100 XP = 1 Level (เริ่มที่ Level 1)
    คืนค่า: (level, xp_in_level, xp_per_level)
    """
    xp_per_level = 100
    level        = (xp // xp_per_level) + 1
    xp_in_level  = xp % xp_per_level
    return level, xp_in_level, xp_per_level


# ============================================================
# 4. Sidebar — XP Dashboard + เมนูบทเรียน
# ============================================================

with st.sidebar:

    # --- กล่อง XP สีทองสไตล์ Duolingo ---
    level, xp_in_level, xp_per_level = xp_to_level(st.session_state.total_xp)

    st.markdown(f"""
    <div class="xp-box">
        <p>🏆 ค่าประสบการณ์ของคุณ</p>
        <h2>{st.session_state.total_xp} XP</h2>
        <p>Level {level} &nbsp;|&nbsp; อีก {xp_per_level - xp_in_level} XP ขึ้นเลเวล</p>
    </div>
    """, unsafe_allow_html=True)

    # Progress Bar XP ภายใน Level ปัจจุบัน
    st.progress(
        xp_in_level / xp_per_level,
        text=f"Level {level}  →  Level {level + 1}"
    )
    st.divider()

    # --- สถิติรวม ---
    total_days    = len(lessons_data)
    completed_num = len(st.session_state.completed_days)
    overall_pct   = completed_num / total_days if total_days > 0 else 0

    # st.metric แสดงตัวเลขใหญ่พร้อม delta
    st.metric(
        label="📚 ความก้าวหน้ารวม",
        value=f"{completed_num} / {total_days} วัน",
        delta=f"+{completed_num * 50} XP" if completed_num > 0 else "เริ่มเรียนได้เลย!"
    )
    st.progress(overall_pct, text=f"{int(overall_pct * 100)}% สำเร็จแล้ว")
    st.divider()

    st.markdown("### 📖 สารบัญบทเรียน")

    # สร้างป้ายชื่อพร้อมไอคอนสถานะ
    all_days   = list(lessons_data.keys())
    day_labels = []

    for day_name in all_days:
        if day_name in st.session_state.completed_days:
            day_labels.append(f"✅  {day_name}")   # เรียนจบแล้ว
        else:
            day_labels.append(f"📖  {day_name}")   # ยังไม่จบ

    selected_label = st.radio(
        label="",
        options=day_labels,
        label_visibility="collapsed"
    )

    # ตัด prefix ไอคอน 4 ตัวอักษรออก ("✅  " หรือ "📖  ") เพื่อได้ชื่อ Day จริง
    selected_day = selected_label[3:]


# ============================================================
# 5. รีเซ็ต Quiz เมื่อเปลี่ยน Day
# ============================================================

if st.session_state.current_day != selected_day:
    st.session_state.current_day  = selected_day
    st.session_state.quiz_answers = {}
    st.session_state.quiz_checked = False


# ============================================================
# 6. ดึงข้อมูลบทเรียนที่เลือก
# ============================================================

lesson       = lessons_data[selected_day]
lesson_title = lesson["title"]
phrases      = lesson["phrases"]   # list 10 ประโยค
quiz_list    = lesson["quizzes"]   # list 3 ควิซ
is_completed = selected_day in st.session_state.completed_days


# ============================================================
# 7. Header หน้าเนื้อหา
# ============================================================

col_title, col_badge = st.columns([8, 2])

with col_title:
    st.title(lesson_title)

with col_badge:
    if is_completed:
        st.success("✅ เรียนจบแล้ว!\n\n+50 XP รับไปแล้ว 🎉")
    else:
        st.info("🏆 ทำควิซให้ผ่าน\n\nรับ **+50 XP!**")

st.write("กดลูกศร ▶ เพื่อดูคำแปล — ลองเดาความหมายก่อนนะ! 😊")
st.divider()


# ============================================================
# 8. แสดงประโยคบทเรียน (10 ประโยค)
# ============================================================

for i, phrase in enumerate(phrases):

    col_text, col_audio = st.columns([10, 1])

    with col_text:
        st.markdown(f"""
        <div class="phrase-card">
            <strong>{i + 1}. {phrase['english']}</strong>
        </div>
        """, unsafe_allow_html=True)

    with col_audio:
        # ปุ่ม 🔊 — key ไม่ซ้ำกันทุกปุ่ม
        if st.button("🔊", key=f"audio_{selected_day}_{i}", help="ฟังการออกเสียง"):
            audio_bytes = get_audio_bytes(phrase["english"])
            st.audio(audio_bytes, format="audio/mp3")

    with st.expander("👁️ ดูคำอ่านและคำแปล"):
        col_l, col_r = st.columns(2)
        with col_l:
            st.info(f"🔤 **คำอ่าน**\n\n{phrase['pronunciation']}")
        with col_r:
            st.success(f"✅ **คำแปล**\n\n{phrase['meaning']}")

    st.write("")


# ============================================================
# 9. Quiz Section (3 ข้อ)
# ============================================================

st.divider()

col_quiz_h, col_xp_h = st.columns([7, 3])
with col_quiz_h:
    st.subheader("🧠 แบบทดสอบประจำบท")
with col_xp_h:
    st.markdown("""
    <div style='background:linear-gradient(135deg,#f6d365,#fda085);
                border-radius:10px; padding:10px 14px; text-align:center; margin-top:8px;'>
        <strong style='color:#1a1a2e; font-size:1rem;'>🏆 ผ่านทุกข้อ = +50 XP</strong>
    </div>
    """, unsafe_allow_html=True)

st.write("เลือกคำตอบให้ครบทั้ง 3 ข้อ แล้วกด **'ตรวจคำตอบ'**")
st.write("")

for q_idx, quiz in enumerate(quiz_list):

    # กล่องคำถามสีม่วงอ่อน
    st.markdown(f"""
    <div class="quiz-card">
        <strong>ข้อ {q_idx + 1}: {quiz['question']}</strong>
    </div>
    """, unsafe_allow_html=True)

    selected_option = st.radio(
        label=f"q{q_idx}",
        options=quiz["options"],
        key=f"quiz_{selected_day}_{q_idx}",
        index=None,
        label_visibility="collapsed"
    )

    # บันทึกคำตอบทันทีที่เลือก
    if selected_option is not None:
        st.session_state.quiz_answers[q_idx] = selected_option

    # แสดงผลหลังกดตรวจแล้ว
    if st.session_state.quiz_checked:
        user_ans    = st.session_state.quiz_answers.get(q_idx)
        correct_ans = quiz["answer"]
        if user_ans == correct_ans:
            st.success("✅ ถูกต้อง!")
        else:
            st.error(f"❌ ยังไม่ถูก — เฉลยคือ: **{correct_ans}**")

    st.write("")


# ============================================================
# 10. ปุ่ม "ตรวจคำตอบ"
# ============================================================

all_answered = len(st.session_state.quiz_answers) == len(quiz_list)

if st.button(
    "📝 ตรวจคำตอบ",
    disabled=not all_answered,   # disable ถ้าตอบไม่ครบ
    use_container_width=True
):
    st.session_state.quiz_checked = True
    st.rerun()

if not all_answered and not st.session_state.quiz_checked:
    remaining = len(quiz_list) - len(st.session_state.quiz_answers)
    st.caption(f"⚠️ กรุณาตอบอีก {remaining} ข้อ ก่อนกดตรวจ")


# ============================================================
# 11. ปุ่มจบบทเรียน + ระบบ XP (หัวใจของ Gamification)
# ============================================================

if st.session_state.quiz_checked:

    # ตรวจว่าถูกทุกข้อไหม
    all_correct = all(
        st.session_state.quiz_answers.get(i) == quiz_list[i]["answer"]
        for i in range(len(quiz_list))
    )

    if all_correct:
        st.divider()

        if is_completed:
            # ===== เคยจบแล้ว: ห้ามให้ XP ซ้ำ (กันปั๊มคะแนน) =====
            st.success(
                f"🏆 คุณเรียนจบ **{selected_day}** ไปแล้ว!\n\n"
                "XP ถูกรับไปแล้วในครั้งก่อนหน้า — ไม่สามารถรับซ้ำได้"
            )

        else:
            # ===== ยังไม่เคยจบ: แสดงปุ่มรับ XP =====
            st.info("🎯 ยอดเยี่ยมมาก! คุณตอบถูกทุกข้อแล้ว\n\nกดปุ่มด้านล่างเพื่อรับ XP!")

            if st.button(
                f"🎉 บันทึกว่าเรียนจบ {selected_day} และรับ +50 XP!",
                type="primary",
                use_container_width=True
            ):
                # Step 1: เพิ่ม Day เข้า completed_days
                st.session_state.completed_days.append(selected_day)

                # Step 2: บวก XP +50
                st.session_state.total_xp += 50

                # Step 3: รีเซ็ต Quiz สำหรับรอบถัดไป
                st.session_state.quiz_answers = {}
                st.session_state.quiz_checked = False

                # Step 4: ลูกโป่งฉลอง
                st.balloons()

                # Step 5: รีเฟรชหน้า อัปเดต XP + ✅ ใน Sidebar
                st.rerun()

    else:
        # ===== ตอบผิดบางข้อ: ให้กำลังใจ =====
        st.warning("💪 ยังมีบางข้อที่ตอบผิด กลับไปทบทวนด้านบนแล้วลองใหม่นะ!")

        if st.button("🔄 ลองทำควิซใหม่", use_container_width=True):
            st.session_state.quiz_answers = {}
            st.session_state.quiz_checked = False
            st.rerun()


# ============================================================
# 12. Footer
# ============================================================

st.divider()
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    st.caption(f"🏆 XP รวม: **{st.session_state.total_xp}** คะแนน")
with col_f2:
    st.caption("🌟 1 Year to Fluent — สร้างด้วย Python & Streamlit")
with col_f3:
    st.caption(f"📚 เรียนจบแล้ว: **{len(st.session_state.completed_days)}** / {len(lessons_data)} วัน")
