# sudoku_streamlit.py
import streamlit as st
import numpy as np
import random
import time

st.set_page_config(page_title="🎮 AI Sudoku Game", page_icon="🎯", layout="centered")

# Custom CSS for better styling
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #1e3c72, #2a5298);
    }
    .sudoku-cell {
        background: white;
        border: 1px solid #ccc;
        border-radius: 5px;
        padding: 10px;
        text-align: center;
        font-weight: bold;
        font-size: 18px;
    }
    .selected-cell {
        background: #ffeb3b !important;
        border: 2px solid #ff9800 !important;
    }
    .congratulations {
        background: linear-gradient(45deg, #FFD700, #FFA500);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        color: white;
        font-size: 1.5em;
        font-weight: bold;
        margin: 20px 0;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
</style>
""", unsafe_allow_html=True)

class SudokuGenerator:
    def __init__(self):
        self.board = np.zeros((9, 9), dtype=int)
    
    def is_valid(self, board, row, col, num):
        if num in board[row]:
            return False
        if num in board[:, col]:
            return False
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if board[start_row + i][start_col + j] == num:
                    return False
        return True
    
    def solve(self, board):
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    for num in range(1, 10):
                        if self.is_valid(board, i, j, num):
                            board[i][j] = num
                            if self.solve(board):
                                return True
                            board[i][j] = 0
                    return False
        return True
    
    def generate(self, difficulty=0.5):
        # Create empty board
        board = np.zeros((9, 9), dtype=int)
        
        # Fill diagonal boxes
        for box in range(3):
            numbers = list(range(1, 10))
            random.shuffle(numbers)
            for i in range(3):
                for j in range(3):
                    board[box*3 + i][box*3 + j] = numbers.pop()
        
        # Solve the board
        self.solve(board)
        solved_board = board.copy()

        # Remove numbers based on difficulty
        cells_to_remove = int(81 * difficulty)
        removed = 0
        
        positions = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(positions)
        
        for row, col in positions:
            if removed >= cells_to_remove:
                break
            if board[row][col] != 0:
                board[row][col] = 0
                removed += 1
        
        return board, solved_board

def initialize_game():
    if 'board' not in st.session_state:
        generator = SudokuGenerator()
        st.session_state.board, st.session_state.solved_board = generator.generate(0.5)
        st.session_state.start_time = time.time()
        st.session_state.mistakes = 0
        st.session_state.hints_used = 0
        st.session_state.selected_cell = None
        st.session_state.game_won = False

def check_win():
    for i in range(9):
        for j in range(9):
            if st.session_state.board[i][j] != st.session_state.solved_board[i][j]:
                return False
    return True

def get_hint():
    if st.session_state.selected_cell:
        row, col = st.session_state.selected_cell
        if st.session_state.board[row][col] == 0:
            correct_num = st.session_state.solved_board[row][col]
            st.session_state.board[row][col] = correct_num
            st.session_state.hints_used += 1
            return f"💡 Hint: Number {correct_num} placed at ({row+1}, {col+1})"
        else:
            return "⚠️ Selected cell is not empty!"
    else:
        return "⚠️ Please select an empty cell first!"

def main():
    st.title("🎮 AI Sudoku Game")
    
    initialize_game()
    
    # Game controls
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔄 New Game", use_container_width=True):
            generator = SudokuGenerator()
            st.session_state.board, st.session_state.solved_board = generator.generate(0.5)
            st.session_state.start_time = time.time()
            st.session_state.mistakes = 0
            st.session_state.hints_used = 0
            st.session_state.selected_cell = None
            st.session_state.game_won = False
            st.rerun()
    
    with col2:
        if st.button("🤖 AI Solve", use_container_width=True):
            st.session_state.board = st.session_state.solved_board.copy()
            st.session_state.game_won = True
            st.rerun()
    
    with col3:
        if st.button("💡 Get Hint", use_container_width=True):
            hint_msg = get_hint()
            st.success(hint_msg)
            if check_win():
                st.session_state.game_won = True
            st.rerun()
    
    with col4:
        if st.button("✅ Check", use_container_width=True):
            if check_win():
                st.session_state.game_won = True
            st.rerun()
    
    # Celebration
    if st.session_state.game_won:
        st.balloons()
        st.markdown('<div class="congratulations">🎉 CONGRATULATIONS! 🎉<br>You solved the Sudoku!</div>', unsafe_allow_html=True)
    
    # Game stats
    elapsed_time = int(time.time() - st.session_state.start_time)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("⏰ Time", f"{elapsed_time}s")
    with col2:
        st.metric("💡 Hints", st.session_state.hints_used)
    with col3:
        st.metric("❌ Mistakes", st.session_state.mistakes)
    
    st.markdown("---")
    
    # Selected cell info
    if st.session_state.selected_cell:
        row, col = st.session_state.selected_cell
        st.info(f"📍 Selected: Row {row+1}, Column {col+1}")
        
        if st.session_state.board[row][col] == 0:
