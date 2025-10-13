# ai_sudoku_game.py
import streamlit as st
import numpy as np
import random
import time

st.set_page_config(page_title="🎮 AI Sudoku Game", page_icon="🎯", layout="centered")

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        color: white;
        text-align: center;
        font-size: 3em;
        margin-bottom: 20px;
        text-shadow: 2px 2px 4px #000000;
    }
    .stButton>button {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 10px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background: linear-gradient(45deg, #FF8E8E, #6EDBD6);
        color: white;
    }
    .congratulations {
        background: linear-gradient(45deg, #FFD700, #FFA500);
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        color: white;
        font-size: 2em;
        font-weight: bold;
        margin: 20px 0;
        animation: pulse 2s infinite;
        border: 5px solid #FF8C00;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    .cell-correct {
        background-color: #90EE90 !important;
    }
    .cell-wrong {
        background-color: #FFB6C1 !important;
    }
</style>
""", unsafe_allow_html=True)

class SudokuGenerator:
    def __init__(self):
        self.board = np.zeros((9, 9), dtype=int)

    def is_valid(self, board, row, col, num):
        # Check row
        if num in board[row]:
            return False
        
        # Check column
        if num in board[:, col]:
            return False
        
        # Check 3x3 box
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
        board = np.zeros((9, 9), dtype=int)
        
        # Fill diagonal boxes
        for box in range(3):
            numbers = list(range(1, 10))
            random.shuffle(numbers)
            for i in range(3):
                for j in range(3):
                    board[box * 3 + i][box * 3 + j] = numbers.pop()
        
        # Solve the board
        self.solve(board)
        solved_board = board.copy()
        
        # Remove numbers based on difficulty
        cells_to_remove = int(81 * difficulty)
        positions = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(positions)
        
        for i, (row, col) in enumerate(positions):
            if i >= cells_to_remove:
                break
            board[row][col] = 0
            
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
    if 'board' not in st.session_state or 'solved_board' not in st.session_state:
        return False
    return np.array_equal(st.session_state.board, st.session_state.solved_board)

def get_hint():
    if st.session_state.selected_cell:
        row, col = st.session_state.selected_cell
        if st.session_state.board[row][col] == 0:
            correct_num = st.session_state.solved_board[row][col]
            st.session_state.board[row][col] = correct_num
            st.session_state.hints_used += 1
            return f"💡 Hint: Number {correct_num} placed at ({row + 1}, {col + 1})"
        else:
            return "⚠️ Selected cell is not empty!"
    else:
        return "⚠️ Please select an empty cell first!"

def display_sudoku_board():
    st.markdown("### 🎯 Sudoku Board")
    
    # Create the Sudoku grid
    for i in range(9):
        cols = st.columns(9)
        for j in range(9):
            with cols[j]:
                cell_value = st.session_state.board[i][j]
                display_value = cell_value if cell_value != 0 else ""
                
                # Button styling
                button_style = ""
                if st.session_state.selected_cell == (i, j):
                    button_style = "background: #FFEB3B !important; color: black !important;"
                
                if st.button(
                    str(display_value) if display_value else "⋅",
                    key=f"cell_{i}_{j}",
                    use_container_width=True,
                    help=f"Row {i+1}, Column {j+1}"
                ):
                    st.session_state.selected_cell = (i, j)
                    st.rerun()

def display_number_pad():
    if st.session_state.selected_cell:
        row, col = st.session_state.selected_cell
        if st.session_state.board[row][col] == 0:
            st.markdown("### 🔢 Enter Number:")
            cols = st.columns(9)
            for i, num in enumerate(range(1, 10)):
                with cols[i]:
                    if st.button(str(num), key=f"num_{num}", use_container_width=True):
                        # Check if the move is correct
                        if num == st.session_state.solved_board[row][col]:
                            st.session_state.board[row][col] = num
                            st.success(f"✅ Correct! Number {num} placed.")
                            if check_win():
                                st.session_state.game_won = True
                        else:
                            st.session_state.mistakes += 1
                            st.error(f"❌ Incorrect! Try again.")
                        st.rerun()

def main():
    st.markdown('<div class="main-header">🎮 AI Sudoku Game</div>', unsafe_allow_html=True)
    
    initialize_game()

    # Game controls
    st.markdown("### 🎮 Game Controls")
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
        if st.button("✅ Check Solution", use_container_width=True):
            if check_win():
                st.session_state.game_won = True
                st.success("🎉 Congratulations! You solved the Sudoku!")
            else:
                st.error("❌ Not quite right! Keep trying!")
            st.rerun()

    # Celebration
    if st.session_state.game_won:
        st.balloons()
        st.markdown('<div class="congratulations">🎉 CONGRATULATIONS! 🎉<br>You solved the Sudoku!</div>', unsafe_allow_html=True)

    # Game stats
    st.markdown("### 📊 Game Statistics")
    elapsed_time = int(time.time() - st.session_state.start_time)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("⏰ Time", f"{elapsed_time}s")
    with col2:
        st.metric("💡 Hints Used", st.session_state.hints_used)
    with col3:
        st.metric("❌ Mistakes", st.session_state.mistakes)

    st.markdown("---")

    # Selected cell info
    if st.session_state.selected_cell:
        row, col = st.session_state.selected_cell
        st.info(f"📍 Selected Cell: Row {row + 1}, Column {col + 1}")

    # Display components
    display_sudoku_board()
    display_number_pad()

    # Instructions
    with st.expander("📖 How to Play"):
        st.markdown("""
        ## 🎯 How to Play Sudoku
        
        1. **Click on any empty cell** to select it
        2. **Use the number pad** that appears to enter your guess (1-9)
        3. **Rules:**
           - Each row must contain all numbers 1-9 exactly once
           - Each column must contain all numbers 1-9 exactly once  
           - Each 3x3 box must contain all numbers 1-9 exactly once
        
        4. **Features:**
           - 🔄 **New Game**: Start a fresh puzzle
           - 💡 **Get Hint**: Reveal one correct number (affects your score)
           - 🤖 **AI Solve**: See the complete solution
           - ✅ **Check**: Verify your current progress
        
        **Tip:** Fewer hints and mistakes = better score!
        """)

if __name__ == "__main__":
    main()
