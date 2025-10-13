import streamlit as st
import numpy as np
import random
import time

st.set_page_config(page_title="AI Sudoku Game", page_icon="🎯", layout="centered")


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
        # Fill diagonal boxes first
        for box in range(3):
            numbers = list(range(1, 10))
            random.shuffle(numbers)
            for i in range(3):
                for j in range(3):
                    self.board[box * 3 + i][box * 3 + j] = numbers.pop()

        self.solve(self.board)

        cells_to_remove = int(81 * difficulty)
        removed = 0

        while removed < cells_to_remove:
            row = random.randint(0, 8)
            col = random.randint(0, 8)
            if self.board[row][col] != 0:
                self.board[row][col] = 0
                removed += 1

        return self.board


def initialize_session_state():
    if 'board' not in st.session_state:
        generator = SudokuGenerator()
        st.session_state.board = generator.generate(0.5)
        st.session_state.original_board = st.session_state.board.copy()
        st.session_state.start_time = time.time()
        st.session_state.mistakes = 0
        st.session_state.hints_used = 0
        st.session_state.game_over = False


def display_board():
    st.markdown("""
    <style>
    .sudoku-board {
        display: grid;
        grid-template-columns: repeat(9, 1fr);
        gap: 2px;
        max-width: 450px;
        margin: 0 auto;
    }
    .sudoku-cell {
        width: 45px;
        height: 45px;
        text-align: center;
        font-size: 20px;
        font-weight: bold;
        border: 1px solid #ccc;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .thick-right {
        border-right: 3px solid #000;
    }
    .thick-bottom {
        border-bottom: 3px solid #000;
    }
    .original {
        background-color: #e6f3ff;
        color: #0066cc;
    }
    .user-input {
        background-color: white;
        color: black;
    }
    </style>
    """, unsafe_allow_html=True)

    # Create the board HTML
    board_html = '<div class="sudoku-board">'
    for i in range(9):
        for j in range(9):
            value = st.session_state.board[i][j]
            cell_class = "sudoku-cell "

            # Add thick borders for 3x3 boxes
            if j in [2, 5]:
                cell_class += "thick-right "
            if i in [2, 5]:
                cell_class += "thick-bottom "

            # Different styles for original vs user input
            if st.session_state.original_board[i][j] != 0:
                cell_class += "original"
                cell_content = f'<div class="{cell_class}">{value}</div>'
            else:
                cell_class += "user-input"
                if value == 0:
                    cell_content = f'<div class="{cell_class}"></div>'
                else:
                    cell_content = f'<div class="{cell_class}">{value}</div>'

            board_html += cell_content
    board_html += '</div>'

    st.markdown(board_html, unsafe_allow_html=True)


def main():
    st.title("🎯 AI Sudoku Game")
    st.markdown("---")

    initialize_session_state()

    # Sidebar for controls
    with st.sidebar:
        st.header("Game Controls")

        if st.button("🔄 New Game", use_container_width=True):
            generator = SudokuGenerator()
            st.session_state.board = generator.generate(0.5)
            st.session_state.original_board = st.session_state.board.copy()
            st.session_state.start_time = time.time()
            st.session_state.mistakes = 0
            st.session_state.hints_used = 0
            st.session_state.game_over = False
            st.rerun()

        if st.button("🤖 AI Solve", use_container_width=True):
            temp_board = st.session_state.board.copy()
            generator = SudokuGenerator()
            if generator.solve(temp_board):
                st.session_state.board = temp_board
                st.success("Puzzle solved with AI!")
            else:
                st.error("No solution found!")
            st.rerun()

        if st.button("💡 Get Hint", use_container_width=True):
            # Find first empty cell and fill it
            generator = SudokuGenerator()
            temp_board = st.session_state.board.copy()
            if generator.solve(temp_board):
                for i in range(9):
                    for j in range(9):
                        if st.session_state.board[i][j] == 0:
                            st.session_state.board[i][j] = temp_board[i][j]
                            st.session_state.hints_used += 1
                            st.success(f"Hint: {temp_board[i][j]} at position ({i + 1}, {j + 1})")
                            st.rerun()
                            return
            st.warning("No empty cells found!")

        st.markdown("---")
        st.header("Game Info")

        elapsed_time = int(time.time() - st.session_state.start_time)
        st.metric("⏰ Time", f"{elapsed_time}s")
        st.metric("❌ Mistakes", st.session_state.mistakes)
        st.metric("💡 Hints Used", st.session_state.hints_used)

    # Main game area
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        display_board()

        st.markdown("---")
        st.subheader("Number Input")

        # Number pad
        cols = st.columns(5)
        with cols[1]:
            if st.button("1", use_container_width=True):
                # Simple implementation - you can enhance this
                st.info("Click on the board and use keyboard numbers 1-9")
        with cols[2]:
            if st.button("2", use_container_width=True):
                st.info("Click on the board and use keyboard numbers 1-9")
        with cols[3]:
            if st.button("3", use_container_width=True):
                st.info("Click on the board and use keyboard numbers 1-9")

        st.markdown("### How to Play")
        st.write("""
        1. The AI-generated puzzle is shown above
        2. Use **New Game** for a fresh puzzle
        3. Use **AI Solve** to see the solution
        4. Use **Get Hint** for help when stuck
        5. Numbers in blue are original clues
        """)


if __name__ == "__main__":
    main()