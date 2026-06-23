import streamlit as st
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

# ── 페이지 설정 ──────────────────────────────────────────────────
st.set_page_config(
    page_title="🐙 쭈꾸미 할일",
    page_icon="🐙",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── 상수 ─────────────────────────────────────────────────────────
STORAGE_FILE = Path("todos.json")
CATEGORIES   = ["업무", "개인", "공부"]
CAT_ICONS    = {"전체": "🐙", "업무": "🔥", "개인": "🍺", "공부": "📚"}
CAT_COLORS   = {"업무": "#FF3300", "개인": "#FF8C00", "공부": "#CC00AA"}

# ── 쭈꾸미 CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
/* 배경 */
.stApp {
    background-color: #1A0505;
    background-image:
        radial-gradient(ellipse 60% 40% at 20% 30%, #3D0A0A 0%, transparent 60%),
        radial-gradient(ellipse 50% 60% at 80% 70%, #2A0808 0%, transparent 60%);
}

/* 사이드바 숨김 */
[data-testid="stSidebar"],
[data-testid="collapsedControl"] { display: none; }

/* 메인 카드 */
.main .block-container {
    background: #2A0808;
    border: 1.5px solid #5A1515;
    border-radius: 20px;
    padding: 2.5rem 2.5rem !important;
    max-width: 700px !important;
    box-shadow: 0 8px 40px rgba(180, 20, 20, .25),
                inset 0 1px 0 rgba(255, 100, 100, .06);
}

/* 제목 */
h1 { color: #FF4444 !important; text-shadow: 0 0 20px rgba(255,68,68,.35) !important; }
h2, h3 { color: #CC4444 !important; }

/* 일반 텍스트 */
.stMarkdown p, .stMarkdown span, p { color: #FFD0D0; }

/* 텍스트 입력 */
input[type="text"] {
    background: #1A0404 !important;
    border: 1.5px solid #5A1515 !important;
    border-radius: 10px !important;
    color: #FFD0D0 !important;
}
input[type="text"]:focus {
    border-color: #FF3300 !important;
    box-shadow: 0 0 0 3px rgba(255, 51, 0, .2) !important;
}

/* 셀렉트 */
[data-baseweb="select"] > div {
    background: #1A0404 !important;
    border: 1.5px solid #5A1515 !important;
    border-radius: 10px !important;
    color: #FFD0D0 !important;
}
[data-baseweb="popover"] { background: #1A0404 !important; }
[data-baseweb="menu"]    { background: #1A0404 !important; }
[role="option"]          { background: #1A0404 !important; color: #FFD0D0 !important; }
[role="option"]:hover    { background: #3D0A0A !important; }

/* 기본 버튼 (필터 탭용) */
.stButton > button {
    background: transparent !important;
    border: 1.5px solid #5A1515 !important;
    border-radius: 99px !important;
    color: #CC6666 !important;
    font-weight: 600 !important;
    transition: all .15s !important;
    width: 100%;
}
.stButton > button:hover {
    border-color: #FF4444 !important;
    color: #FF9999 !important;
    background: rgba(139, 0, 0, .2) !important;
}

/* 폼 제출 버튼 (primary) */
[data-testid="baseButton-primary"],
button[kind="primaryFormSubmit"] {
    background: linear-gradient(135deg, #8B0000, #CC2200, #FF3300) !important;
    color: #FFE0DC !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    box-shadow: 0 0 16px rgba(255, 51, 0, .35) !important;
    transition: opacity .15s !important;
}
[data-testid="baseButton-primary"]:hover { opacity: .85 !important; }

/* 폼 제출 버튼 (secondary — 취소) */
[data-testid="baseButton-secondary"],
button[kind="secondaryFormSubmit"] {
    background: transparent !important;
    border: 1.5px solid #5A1515 !important;
    border-radius: 10px !important;
    color: #8B4040 !important;
    font-weight: 600 !important;
    transition: all .15s !important;
}

/* 진행률 바 */
[data-testid="stProgressBar"] {
    background: #3D0A0A !important;
    border-radius: 99px !important;
    height: 10px !important;
}
[data-testid="stProgressBar"] > div {
    background: linear-gradient(90deg, #8B0000, #CC2200, #FF4400, #FF6644) !important;
    box-shadow: 0 0 10px rgba(255, 68, 0, .5);
    border-radius: 99px !important;
}

/* 폼 컨테이너 */
[data-testid="stForm"] {
    background: #1A0404 !important;
    border: 1px solid #5A1515 !important;
    border-radius: 14px !important;
    padding: 1rem !important;
}

/* 체크박스 */
[data-testid="stCheckbox"] p,
[data-testid="stCheckbox"] span { color: #FFD0D0 !important; }

/* 구분선 */
hr { border-color: #3D0A0A !important; }

/* 알림 */
[data-testid="stAlert"] { border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)


# ── 데이터 로드 / 저장 ────────────────────────────────────────────
def load_todos() -> list:
    """todos.json 파일에서 데이터 로드. 오류 시 빈 리스트 반환."""
    if STORAGE_FILE.exists():
        try:
            data = json.loads(STORAGE_FILE.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception:
            return []
    return []


def save_todos(todos: list) -> None:
    """todos.json 파일에 데이터 저장."""
    STORAGE_FILE.write_text(
        json.dumps(todos, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# ── 세션 상태 초기화 ─────────────────────────────────────────────
if "todos"           not in st.session_state:
    st.session_state.todos           = load_todos()
if "active_category" not in st.session_state:
    st.session_state.active_category = "전체"
if "editing_id"      not in st.session_state:
    st.session_state.editing_id      = None


# ── 핵심 함수 ────────────────────────────────────────────────────
def add_todo(title: str, category: str) -> bool:
    if not title.strip():
        return False
    st.session_state.todos.append({
        "id":        str(uuid.uuid4()),
        "title":     title.strip(),
        "category":  category,
        "completed": False,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    })
    save_todos(st.session_state.todos)
    return True


def delete_todo(todo_id: str) -> None:
    st.session_state.todos = [t for t in st.session_state.todos if t["id"] != todo_id]
    if st.session_state.editing_id == todo_id:
        st.session_state.editing_id = None
    save_todos(st.session_state.todos)


def toggle_todo(todo_id: str) -> None:
    for t in st.session_state.todos:
        if t["id"] == todo_id:
            t["completed"] = not t["completed"]
            break
    save_todos(st.session_state.todos)


def update_todo(todo_id: str, title: str, category: str) -> bool:
    if not title.strip():
        return False
    for t in st.session_state.todos:
        if t["id"] == todo_id:
            t["title"]    = title.strip()
            t["category"] = category
            break
    st.session_state.editing_id = None
    save_todos(st.session_state.todos)
    return True


def calc_progress(lst: list) -> tuple[int, int, int]:
    """(pct, done, total) 반환. 항목 0개이면 (0, 0, 0)."""
    if not lst:
        return 0, 0, 0
    done = sum(1 for t in lst if t["completed"])
    return round(done / len(lst) * 100), done, len(lst)


# ════════════════════════════════════════════════════════════════
# UI
# ════════════════════════════════════════════════════════════════

# ── 제목 ─────────────────────────────────────────────────────────
st.markdown("# 🐙 쭈꾸미 할일")
st.markdown(
    '<p style="color:#8B4040; font-size:13px; margin-top:-12px;">'
    "오늘 할일, 매콤하게 해치워버리자! 🌶️</p>",
    unsafe_allow_html=True,
)
st.divider()

# ── 진행률 섹션 ──────────────────────────────────────────────────
st.markdown(
    '<p style="color:#FF6666; font-weight:700; font-size:13px; letter-spacing:.5px;">'
    "🌶️ 오늘의 매운맛 진행률</p>",
    unsafe_allow_html=True,
)

overall_pct, done, total = calc_progress(st.session_state.todos)
st.progress(overall_pct / 100)
st.markdown(
    f'<p style="color:#7A3030; font-size:11px; margin-top:4px;">'
    f"전체 {overall_pct}% (완료 {done} / 전체 {total})</p>",
    unsafe_allow_html=True,
)

# 카테고리별 진행률 카드
c1, c2, c3 = st.columns(3)
for col, cat in zip([c1, c2, c3], CATEGORIES):
    cat_list = [t for t in st.session_state.todos if t["category"] == cat]
    pct, d, tot = calc_progress(cat_list)
    color = CAT_COLORS[cat]
    with col:
        st.markdown(
            f'<div style="background:#200606; border:1px solid #4A1010; border-radius:10px; padding:10px 12px;">'
            f'  <div style="display:flex; justify-content:space-between; font-size:11px; font-weight:700; color:#CC6666; margin-bottom:6px;">'
            f'    <span>{CAT_ICONS[cat]} {cat}</span><span>{pct}%</span>'
            f'  </div>'
            f'  <div style="background:#3D0A0A; border-radius:99px; height:5px; overflow:hidden;">'
            f'    <div style="background:{color}; height:100%; width:{pct}%; border-radius:99px; box-shadow:0 0 6px {color}80;"></div>'
            f'  </div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# ── 카테고리 필터 탭 ─────────────────────────────────────────────
filter_cats = ["전체"] + CATEGORIES
f_cols = st.columns(len(filter_cats))

for i, cat in enumerate(filter_cats):
    label = f"{CAT_ICONS[cat]} {cat}"
    is_active = st.session_state.active_category == cat
    with f_cols[i]:
        if is_active:
            # 활성 탭: HTML로 강조 표시
            st.markdown(
                f'<div style="background:#8B0000; border:1.5px solid #FF3300; border-radius:99px;'
                f' text-align:center; padding:7px 4px; font-size:13px; font-weight:700;'
                f' color:#FFD0D0; box-shadow:0 0 10px rgba(255,51,0,.3);">{label}</div>',
                unsafe_allow_html=True,
            )
        else:
            if st.button(label, key=f"filter_{cat}", use_container_width=True):
                st.session_state.active_category = cat
                st.session_state.editing_id      = None
                st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ── 할일 추가 폼 ─────────────────────────────────────────────────
with st.form("add_form", clear_on_submit=True):
    a1, a2, a3 = st.columns([5, 2, 1.8])
    with a1:
        new_title = st.text_input(
            "제목",
            placeholder="오늘 해치울 일은? 🐙",
            label_visibility="collapsed",
        )
    with a2:
        new_cat = st.selectbox("카테고리", CATEGORIES, label_visibility="collapsed")
    with a3:
        submitted = st.form_submit_button(
            "+ 추가 🌶️",
            use_container_width=True,
            type="primary",
        )

if submitted:
    if add_todo(new_title, new_cat):
        # 현재 필터와 다른 카테고리 추가 시 전체 탭으로 리셋
        if st.session_state.active_category not in ("전체", new_cat):
            st.session_state.active_category = "전체"
        st.rerun()
    else:
        st.error("할일을 입력해주세요! 🐙")

st.divider()

# ── 할일 목록 ────────────────────────────────────────────────────
filtered = [
    t for t in st.session_state.todos
    if st.session_state.active_category in ("전체", t["category"])
]

if not filtered:
    st.markdown(
        '<div style="text-align:center; color:#6B2020; padding:40px 0 32px;">'
        '<div style="font-size:48px; margin-bottom:12px; filter:drop-shadow(0 0 12px rgba(255,51,0,.3));">🐙</div>'
        '<p style="color:#6B2020;">할일이 없어요~ 쭈꾸미처럼 유유자적하자!</p>'
        "</div>",
        unsafe_allow_html=True,
    )
else:
    for todo in filtered:

        if st.session_state.editing_id == todo["id"]:
            # ── 편집 모드 ────────────────────────────────────────
            with st.form(f"edit_form_{todo['id']}"):
                e1, e2, e3, e4 = st.columns([4, 2, 1.4, 1.2])
                with e1:
                    edit_title = st.text_input(
                        "제목 수정",
                        value=todo["title"],
                        label_visibility="collapsed",
                    )
                with e2:
                    edit_cat = st.selectbox(
                        "카테고리",
                        CATEGORIES,
                        index=CATEGORIES.index(todo["category"]),
                        label_visibility="collapsed",
                    )
                with e3:
                    do_save = st.form_submit_button(
                        "저장 🌶️",
                        use_container_width=True,
                        type="primary",
                    )
                with e4:
                    do_cancel = st.form_submit_button(
                        "취소",
                        use_container_width=True,
                        type="secondary",
                    )

            if do_save:
                if not update_todo(todo["id"], edit_title, edit_cat):
                    st.error("제목을 입력해주세요! 🐙")
                else:
                    st.rerun()
            if do_cancel:
                st.session_state.editing_id = None
                st.rerun()

        else:
            # ── 보기 모드 ────────────────────────────────────────
            col_chk, col_title, col_badge, col_edit, col_del = st.columns(
                [0.5, 5, 1.6, 0.65, 0.65]
            )

            # 완료 체크박스
            with col_chk:
                checked = st.checkbox(
                    "",
                    value=todo["completed"],
                    key=f"chk_{todo['id']}",
                    label_visibility="collapsed",
                )
                if checked != todo["completed"]:
                    toggle_todo(todo["id"])
                    st.rerun()

            # 제목 (완료 시 취소선 + 연한 색)
            with col_title:
                color = "#5A2020" if todo["completed"] else "#FFD0D0"
                deco  = "line-through" if todo["completed"] else "none"
                st.markdown(
                    f'<p style="color:{color}; text-decoration:{deco}; font-size:14px; margin:6px 0;">'
                    f"{todo['title']}</p>",
                    unsafe_allow_html=True,
                )

            # 카테고리 뱃지
            with col_badge:
                bc = CAT_COLORS[todo["category"]]
                st.markdown(
                    f'<div style="margin-top:4px;">'
                    f'<span style="background:{bc}30; color:{bc}; border:1px solid {bc}60;'
                    f' border-radius:6px; font-size:11px; font-weight:700; padding:3px 8px;">'
                    f"{todo['category']}</span></div>",
                    unsafe_allow_html=True,
                )

            # 수정 버튼
            with col_edit:
                if st.button("✏️", key=f"edit_{todo['id']}", help="수정", use_container_width=True):
                    st.session_state.editing_id = todo["id"]
                    st.rerun()

            # 삭제 버튼
            with col_del:
                if st.button("🗑️", key=f"del_{todo['id']}", help="삭제", use_container_width=True):
                    delete_todo(todo["id"])
                    st.rerun()

            st.markdown(
                '<hr style="margin:2px 0; border-color:#3D0A0A;">',
                unsafe_allow_html=True,
            )
