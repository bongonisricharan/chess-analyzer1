import streamlit as st

from engine import (INITIAL_BOARD,evaluate,get_best_move,get_moves,
                    make_move,square_name)

st.set_page_config(page_title="Chess Position Analyzer",page_icon="♟️")

PIECES={
    "k":"\u265A\uFE0E","q":"\u265B\uFE0E","r":"\u265C\uFE0E",
    "b":"\u265D\uFE0E","n":"\u265E\uFE0E","p":"\u265F\uFE0E",
}

def reset_state():
    s=st.session_state
    s.board=[row[:] for row in INITIAL_BOARD]
    s.selected=None
    s.possible=[]
    s.ai_move=None
    s.evaluation=0.0
    s.side="White"
    s.message="Click a piece, then click a highlighted square to move it."

if "board" not in st.session_state:
    reset_state()

def on_square_click(r,c):
    s=st.session_state
    s.ai_move=None

    if s.selected is not None and (r,c) in s.possible:
        mover=s.board[s.selected[0]][s.selected[1]]
        s.board=make_move(s.board,s.selected,(r,c))
        s.selected=None
        s.possible=[]
        s.side="Black" if mover.isupper() else "White"
        s.message="Position changed. Click Analyze Position when ready."
        return

    if s.board[r][c] is not None:
        s.selected=(r,c)
        s.possible=get_moves(s.board,r,c)
        s.message="Highlighted squares show where the selected piece can move."
    else:
        s.selected=None
        s.possible=[]

def on_analyze():
    s=st.session_state
    s.selected=None
    s.possible=[]

    result=get_best_move(s.board,s.side=="White")
    if result is None:
        s.ai_move=None
        s.evaluation=evaluate(s.board)
        s.message=f"No {s.side} move is available."
        return

    (frm,to),score=result
    s.ai_move=(frm,to)
    s.evaluation=score
    s.message="Blue = move from, orange = move to."

def square_style(r,c):
    s=st.session_state
    board=s.board
    piece=board[r][c]

    background="#f0d9b5" if (r+c)%2==0 else "#b58863"
    if s.selected==(r,c):
        background="#64b5f6"
    elif s.ai_move and s.ai_move[1]==(r,c):
        background="#ffb74d"
    elif s.ai_move and s.ai_move[0]==(r,c):
        background="#4dd0e1"
    elif (r,c) in s.possible:
        background="#ef9a9a" if piece else "#a5d6a7"

    if piece and piece.isupper():
        text="color:#fff !important; text-shadow:0 0 3px #000,0 0 3px #000,0 1px 2px #000;"
    elif piece:
        text="color:#1a1a1a !important;"
    else:
        text="color:#2e7d32 !important;"

    return (f".st-key-sq_{r}_{c} button {{ background:{background} !important; }}"
            f".st-key-sq_{r}_{c} button p {{ {text} }}")

STATIC_CSS="""
.st-key-board { max-width:560px; margin:0 auto; gap:0 !important; }
.st-key-board [data-testid="stHorizontalBlock"] { flex-wrap:nowrap !important; gap:0 !important; }
.st-key-board [data-testid="stColumn"] { min-width:0 !important; flex:1 1 0 !important; width:auto !important; }
.st-key-board [data-testid="stElementContainer"] { width:100% !important; }
.st-key-board button {
    width:100%; aspect-ratio:1; min-height:0; padding:0;
    border:0 !important; border-radius:0 !important;
}
.st-key-board button p { font-size:clamp(20px,6.5vw,40px); line-height:1; }
.rank-label,.file-label {
    display:flex; align-items:center; justify-content:center;
    color:#999; font-weight:bold; font-size:14px;
}
.rank-label { aspect-ratio:1; width:100%; }
.st-key-analyze button,.st-key-reset button { width:100%; }
"""

def format_eval(value):
    value=round(value,2)
    if value==0:
        return "0.00"
    return f"{value:+.2f}"

st.title("Chess Position Analyzer")

css=STATIC_CSS+"".join(square_style(r,c) for r in range(8) for c in range(8))
st.markdown(f"<style>{css}</style>",unsafe_allow_html=True)

with st.container(key="board"):
    for r in range(8):
        cols=st.columns(9)
        cols[0].markdown(f'<div class="rank-label">{8-r}</div>',unsafe_allow_html=True)
        for c in range(8):
            piece=st.session_state.board[r][c]
            if piece:
                label=PIECES[piece.lower()]
            elif (r,c) in st.session_state.possible:
                label="●"
            else:
                label="\u00a0"
            cols[c+1].button(label,key=f"sq_{r}_{c}",
                             on_click=on_square_click,args=(r,c))

    letters=st.columns(9)
    for c in range(8):
        letters[c+1].markdown(f'<div class="file-label">{"abcdefgh"[c]}</div>',
                              unsafe_allow_html=True)

st.radio("Side to move",["White","Black"],horizontal=True,key="side")

left,right=st.columns(2)
left.button("Analyze Position",type="primary",key="analyze",on_click=on_analyze)
right.button("Reset Position",key="reset",on_click=reset_state)

m1,m2=st.columns(2)
m1.metric("Evaluation (White - Black)",format_eval(st.session_state.evaluation))
if st.session_state.ai_move:
    frm,to=st.session_state.ai_move
    m2.metric("Best move",f"{square_name(*frm)} → {square_name(*to)}")
else:
    m2.metric("Best move","-")

st.caption(st.session_state.message)