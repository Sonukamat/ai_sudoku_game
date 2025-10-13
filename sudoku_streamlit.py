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
                    board[box * 3 + i][box * 3 + j] = numbers.pop()

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
            return f"💡 Hint: Number {correct_num} placed at ({row + 1}, {col + 1})"
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
        st.markdown('<div class="congratulations">🎉 CONGRATULATIONS! 🎉<br>You solved the Sudoku!</div>',
                    unsafe_allow_html=True)

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
        st.info(f"📍 Selected: Row {row + 1}, Column {col + 1}")

        if st.session_state.board[row][col] == 0:
            # Add number input for empty cells
            st.subheader("Enter a number:")
            col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns(9)
            
            for i, btn_col in enumerate([col1, col2, col3, col4, col5, col6, col7, col8, col9], 1):
                with btn_col:
                    if st.button(str(i), key=f"num_{i}", use_container_width=True):
                        # Check if the move is valid
                        if i == st.session_state.solved_board[row][col]:
                            st.session_state.board[row][col] = i
                            st.success(f"✅ Correct! Number {i} placed.")
                            if check_win():
                                st.session_state.game_won = True
                        else:
                            st.session_state.mistakes += 1
                            st.error(f"❌ Incorrect! Try again.")
                        st.rerun()

    # Sudoku board display
    st.subheader("🎯 Sudoku Board")
    
    # Create the Sudoku grid
    for i in range(9):
        cols = st.columns(9)
        for j in range(9):
            with cols[j]:
                cell_value = st.session_state.board[i][j]
                display_value = cell_value if cell_value != 0 else ""
                
                # Determine cell styling
                cell_class = "sudoku-cell"
                if st.session_state.selected_cell == (i, j):
                    cell_class += " selected-cell"
                
                # Add thicker borders for 3x3 boxes
                border_style = ""
                if i % 3 == 0 and i != 0:
                    border_style += "border-top: 3px solid #333; "
                if j % 3 == 0 and j != 0:
                    border_style += "border-left: 3px solid #333; "
                if i == 8:
                    border_style += "border-bottom: 3px solid #333; "
                if j == 8:
                    border_style += "border-right: 3px solid #333; "
                
                if st.button(
                    str(display_value) if display_value else "⋅",
                    key=f"cell_{i}_{j}",
                    use_container_width=True,
                    help=f"Row {i+1}, Column {j+1}"
                ):
                    st.session_state.selected_cell = (i, j)
                    st.rerun()
                
                # Apply CSS styling
                st.markdown(f"""
                <style>
                    [data-testid="column"] [data-testid="stButton"]:nth-child({j + 1}) button {{
                        {border_style}
                        background: {'#e8f5e8' if cell_value != 0 else 'white'} !important;
                        font-weight: bold;
                        font-size: 18px;
                        height: 50px;
                    }}
                    [data-testid="column"] [data-testid="stButton"]:nth-child({j + 1}) button:hover {{
                        background: #f0f0f0 !important;
                    }}
                </style>
                """, unsafe_allow_html=True)

    # Instructions
    with st.expander("📖 How to Play"):
        st.markdown("""
        1. **Click on any empty cell** to select it
        2. **Use the number buttons** that appear below to enter your guess
        3. **Get hints** if you're stuck (but it counts against your score!)
        4. **Check your progress** with the Check button
        5. **Complete the puzzle** with all correct numbers to win!
        
        **Tips:**
        - Each row, column, and 3x3 box must contain numbers 1-9 exactly once
        - Use logic and elimination to solve the puzzle
        - Fewer hints and mistakes = better score!
        """)

if __name__ == "__main__":
    main()
