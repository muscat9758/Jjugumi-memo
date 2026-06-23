import streamlit as st
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

# ── 페이지 설정 ──────────────────────────────────────────────────
st.set_page_config(
    page_title="🐹 꾸잉이 할일",
    page_icon="🐹",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── 상수 ─────────────────────────────────────────────────────────
STORAGE_FILE = Path("todos.json")
CATEGORIES   = ["업무", "개인", "공부"]
CAT_ICONS    = {"전체": "🐹", "업무": "💼", "개인": "🏡", "공부": "📗"}
CAT_COLORS   = {"업무": "#C47B40", "개인": "#E07B4A", "공부": "#7AAD5E"}
CAT_BG       = {"업무": "#F5E8D8", "개인": "#FAE8DC", "공부": "#E8F0E0"}

# ── 꾸잉이 CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
/* 배경 — 건초 도트 패턴 */
.stApp {
    background-color: #FAF0E4;
    background-image:
        radial-gradient(circle, #E8D5BC 1.5px, transparent 1.5px),
        radial-gradient(circle, #EDD9BF 1px, transparent 1px);
    background-size: 32px 32px, 16px 16px;
    background-position: 0 0, 8px 8px;
}

/* 사이드바 숨김 */
[data-testid="stSidebar"],
[data-testid="collapsedControl"] { display: none; }

/* 메인 카드 */
.main .block-container {
    background: #FFFAF4;
    border: 2px solid #E8CBA8;
    border-radius: 24px;
    padding: 2.5rem 2.5rem 3rem !important;
    max-width: 700px !important;
    box-shadow: 0 6px 32px rgba(160, 90, 40, .12), 0 2px 8px rgba(160, 90, 40, .08);
}

/* 제목 */
h1 { color: #7A3E18 !important; letter-spacing: -.3px !important; }
h2, h3 { color: #A05A28 !important; }

/* 일반 텍스트 */
.stMarkdown p, p, label { color: #4A2E1A; }

/* 텍스트 입력 */
input[type="text"] {
    background: #fff !important;
    border: 1.5px solid #E0C4A0 !important;
    border-radius: 12px !important;
    color: #4A2E1A !important;
}
input[type="text"]:focus {
    border-color: #C47B40 !important;
    box-shadow: 0 0 0 3px rgba(196, 123, 64, .15) !important;
}

/* 셀렉트 */
[data-baseweb="select"] > div {
    background: #fff !important;
    border: 1.5px solid #E0C4A0 !important;
    border-radius: 12px !important;
    color: #4A2E1A !important;
}
[data-baseweb="popover"],
[data-baseweb="menu"]   { background: #FFFAF4 !important; }
[role="option"]          { background: #FFFAF4 !important; color: #4A2E1A !important; }
[role="option"]:hover    { background: #FFF3E8 !important; }

/* 기본 버튼 (필터 탭) */
.stButton > button {
    background: #fff !important;
    border: 1.5px solid #E0C4A0 !important;
    border-radius: 99px !important;
    color: #B8845A !important;
    font-weight: 600 !important;
    transition: all .15s !important;
    width: 100%;
}
.stButton > button:hover {
    border-color: #C47B40 !important;
    color: #7A3E18 !important;
    background: #FFF8F0 !important;
}

/* primary 버튼 (추가, 저장) */
[data-testid="baseButton-primary"],
button[kind="primaryFormSubmit"] {
    background: linear-gradient(135deg, #A85E30, #C47B40, #E09050) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    box-shadow: 0 3px 12px rgba(196, 123, 64, .35) !important;
    transition: opacity .15s !important;
}
[data-testid="baseButton-primary"]:hover { opacity: .88 !important; }

/* secondary 버튼 (취소) */
[data-testid="baseButton-secondary"],
button[kind="secondaryFormSubmit"] {
    background: #fff !important;
    border: 1.5px solid #E0C4A0 !important;
    border-radius: 10px !important;
    color: #B8845A !important;
    font-weight: 600 !important;
}
[data-testid="baseButton-secondary"]:hover {
    border-color: #B8845A !important;
    color: #7A4E28 !important;
}

/* 진행률 바 */
[data-testid="stProgressBar"] {
    background: #EDD5B8 !important;
    border-radius: 99px !important;
    height: 12px !important;
}
[data-testid="stProgressBar"] > div {
    background: linear-gradient(90deg, #A85E30, #C47B40, #E09050, #F4B860) !important;
    box-shadow: 0 2px 8px rgba(196, 123, 64, .4) !important;
    border-radius: 99px !important;
}

/* 폼 컨테이너 */
[data-testid="stForm"] {
    background: #FFF8F0 !important;
    border: 1.5px solid #E0C4A0 !important;
    border-radius: 16px !important;
    padding: 1rem !important;
}

/* 체크박스 */
[data-testid="stCheckbox"] p,
[data-testid="stCheckbox"] span { color: #4A2E1A !important; }

/* 구분선 */
hr { border-color: #EDD5B8 !important; border-style: dashed !important; }

/* 알림 */
[data-testid="stAlert"] { border-radius: 12px !important; }
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
st.markdown("# 🐹 꾸잉이 할일")
st.markdown(
    '<p style="color:#B8845A; font-size:13px; margin-top:-12px;">'
    "꾸잉꾸잉~ 오늘도 열심히 해봐요! 🥕</p>",
    unsafe_allow_html=True,
)
st.divider()

# ── 진행률 섹션 ──────────────────────────────────────────────────
st.markdown(
    '<div style="background:#FFF3E8; border:1.5px solid #E8C89A; border-radius:16px; padding:18px 20px; margin-bottom:8px;">',
    unsafe_allow_html=True,
)
st.markdown(
    '<p style="color:#A05A28; font-weight:800; font-size:12px; letter-spacing:.3px; margin-bottom:8px;">🥕 오늘의 당근 수확 진행률</p>',
    unsafe_allow_html=True,
)

overall_pct, done, total = calc_progress(st.session_state.todos)
st.progress(overall_pct / 100)
st.markdown(
    f'<p style="color:#B8845A; font-size:11px; margin-top:4px;">'
    f"전체 {overall_pct}% (완료 {done} / 전체 {total})</p>",
    unsafe_allow_html=True,
)

# 카테고리별 진행률 카드
c1, c2, c3 = st.columns(3)
for col, cat in zip([c1, c2, c3], CATEGORIES):
    cat_list = [t for t in st.session_state.todos if t["category"] == cat]
    pct, d, tot = calc_progress(cat_list)
    color = CAT_COLORS[cat]
    bg    = CAT_BG[cat]
    with col:
        st.markdown(
            f'<div style="background:{bg}; border:1.5px solid #E8CBA8; border-radius:12px; padding:10px 12px;">'
            f'  <div style="display:flex; justify-content:space-between; font-size:11px; font-weight:700;'
            f'  color:#8B5E38; margin-bottom:6px;">'
            f'    <span>{CAT_ICONS[cat]} {cat}</span><span>{pct}%</span>'
            f'  </div>'
            f'  <div style="background:#EDD5B8; border-radius:99px; height:5px; overflow:hidden;">'
            f'    <div style="background:{color}; height:100%; width:{pct}%; border-radius:99px;"></div>'
            f'  </div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ── 카테고리 필터 탭 ─────────────────────────────────────────────
filter_cats = ["전체"] + CATEGORIES
f_cols = st.columns(len(filter_cats))

for i, cat in enumerate(filter_cats):
    label     = f"{CAT_ICONS[cat]} {cat}"
    is_active = st.session_state.active_category == cat
    with f_cols[i]:
        if is_active:
            st.markdown(
                f'<div style="background:#C47B40; border:1.5px solid #C47B40; border-radius:99px;'
                f' text-align:center; padding:7px 4px; font-size:13px; font-weight:700;'
                f' color:#fff; box-shadow:0 2px 10px rgba(196,123,64,.35);">{label}</div>',
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
            placeholder="꾸잉이에게 할일 알려주기 🥕",
            label_visibility="collapsed",
        )
    with a2:
        new_cat = st.selectbox("카테고리", CATEGORIES, label_visibility="collapsed")
    with a3:
        submitted = st.form_submit_button(
            "+ 추가 🐹",
            use_container_width=True,
            type="primary",
        )

if submitted:
    if add_todo(new_title, new_cat):
        if st.session_state.active_category not in ("전체", new_cat):
            st.session_state.active_category = "전체"
        st.rerun()
    else:
        st.error("할일을 입력해주세요! 꾸잉~ 🐹")

st.divider()

# ── 할일 목록 ────────────────────────────────────────────────────
filtered = [
    t for t in st.session_state.todos
    if st.session_state.active_category in ("전체", t["category"])
]

if not filtered:
    st.markdown(
        '<div style="text-align:center; color:#C8A880; padding:40px 0 32px;">'
        '<div style="font-size:52px; margin-bottom:12px;">🐹</div>'
        '<p style="color:#C8A880; font-size:14px; line-height:2;">할일이 없어요~<br>꾸잉꾸잉, 당근이나 먹어요!</p>'
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
                        "저장 🥕",
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
                    st.error("제목을 입력해주세요! 꾸잉~ 🐹")
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

            with col_title:
                color = "#C8A880" if todo["completed"] else "#4A2E1A"
                deco  = "line-through" if todo["completed"] else "none"
                st.markdown(
                    f'<p style="color:{color}; text-decoration:{deco}; font-size:14px; margin:6px 0;">'
                    f"{todo['title']}</p>",
                    unsafe_allow_html=True,
                )

            with col_badge:
                bc  = CAT_COLORS[todo["category"]]
                bgc = CAT_BG[todo["category"]]
                st.markdown(
                    f'<div style="margin-top:4px;">'
                    f'<span style="background:{bgc}; color:{bc}; border:1.5px solid {bc}50;'
                    f' border-radius:99px; font-size:11px; font-weight:700; padding:3px 10px;">'
                    f"{todo['category']}</span></div>",
                    unsafe_allow_html=True,
                )

            with col_edit:
                if st.button("✏️", key=f"edit_{todo['id']}", help="수정", use_container_width=True):
                    st.session_state.editing_id = todo["id"]
                    st.rerun()

            with col_del:
                if st.button("🗑️", key=f"del_{todo['id']}", help="삭제", use_container_width=True):
                    delete_todo(todo["id"])
                    st.rerun()

            st.markdown(
                '<hr style="margin:2px 0; border-color:#F0E0CC; border-style:solid;">',
                unsafe_allow_html=True,
            )
