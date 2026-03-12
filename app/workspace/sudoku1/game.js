class SudokuGame {
    constructor() {
        this.grid = Array(9).fill(null).map(() => Array(9).fill(0));
        this.originalGrid = Array(9).fill(null).map(() => Array(9).fill(0));
        this.solution = Array(9).fill(null).map(() => Array(9).fill(0));
        this.selectedCell = null;
        this.difficulty = 'easy';
        this.startTime = null;
        this.timerInterval = null;
        this.hints = 3;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.newGame();
        this.startTimer();
    }

    setupEventListeners() {
        document.getElementById('newGameBtn').addEventListener('click', () => this.newGame());
        document.getElementById('solveBtn').addEventListener('click', () => this.solve());
        document.getElementById('clearBtn').addEventListener('click', () => this.clearBoard());
        document.getElementById('hintBtn').addEventListener('click', () => this.getHint());
        document.getElementById('difficultySelect').addEventListener('change', (e) => {
            this.difficulty = e.target.value;
            this.newGame();
        });

        document.addEventListener('keydown', (e) => this.handleKeyPress(e));
    }

    generatePuzzle() {
        // Generate a valid Sudoku solution
        this.grid = Array(9).fill(null).map(() => Array(9).fill(0));
        this.fillGrid();
        
        // Copy the solution
        this.solution = this.grid.map(row => [...row]);
        
        // Remove numbers based on difficulty
        const cellsToRemove = {
            easy: 30,
            medium: 40,
            hard: 50
        }[this.difficulty];

        let removed = 0;
        while (removed < cellsToRemove) {
            const row = Math.floor(Math.random() * 9);
            const col = Math.floor(Math.random() * 9);
            
            if (this.grid[row][col] !== 0) {
                this.grid[row][col] = 0;
                removed++;
            }
        }

        // Store the original puzzle
        this.originalGrid = this.grid.map(row => [...row]);
    }

    fillGrid() {
        for (let row = 0; row < 9; row++) {
            for (let col = 0; col < 9; col++) {
                if (this.grid[row][col] === 0) {
                    const numbers = this.getRandomNumbers();
                    
                    for (let num of numbers) {
                        if (this.isValid(row, col, num)) {
                            this.grid[row][col] = num;
                            
                            if (this.fillGrid()) {
                                return true;
                            }
                            
                            this.grid[row][col] = 0;
                        }
                    }
                    return false;
                }
            }
        }
        return true;
    }

    getRandomNumbers() {
        const numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9];
        for (let i = numbers.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [numbers[i], numbers[j]] = [numbers[j], numbers[i]];
        }
        return numbers;
    }

    isValid(row, col, num) {
        // Check row
        for (let i = 0; i < 9; i++) {
            if (this.grid[row][i] === num) return false;
        }

        // Check column
        for (let i = 0; i < 9; i++) {
            if (this.grid[i][col] === num) return false;
        }

        // Check 3x3 box
        const boxRow = Math.floor(row / 3) * 3;
        const boxCol = Math.floor(col / 3) * 3;
        for (let i = boxRow; i < boxRow + 3; i++) {
            for (let j = boxCol; j < boxCol + 3; j++) {
                if (this.grid[i][j] === num) return false;
            }
        }

        return true;
    }

    renderGrid() {
        const gridElement = document.getElementById('sudokuGrid');
        gridElement.innerHTML = '';

        for (let row = 0; row < 9; row++) {
            for (let col = 0; col < 9; col++) {
                const cell = document.createElement('div');
                cell.className = 'sudoku-cell';
                cell.dataset.row = row;
                cell.dataset.col = col;

                if (this.originalGrid[row][col] !== 0) {
                    cell.textContent = this.grid[row][col];
                    cell.classList.add('given');
                } else if (this.grid[row][col] !== 0) {
                    cell.textContent = this.grid[row][col];
                }

                cell.addEventListener('click', () => this.selectCell(row, col, cell));
                gridElement.appendChild(cell);
            }
        }

        this.updateRelatedCells();
    }

    selectCell(row, col, cellElement) {
        if (this.originalGrid[row][col] !== 0) return;

        // Remove previous selection
        document.querySelectorAll('.sudoku-cell.selected').forEach(cell => {
            cell.classList.remove('selected');
        });

        this.selectedCell = { row, col, element: cellElement };
        cellElement.classList.add('selected');
        this.updateRelatedCells();
    }

    updateRelatedCells() {
        document.querySelectorAll('.sudoku-cell.related').forEach(cell => {
            cell.classList.remove('related');
        });

        if (!this.selectedCell) return;

        const { row, col } = this.selectedCell;

        // Highlight related cells
        for (let i = 0; i < 9; i++) {
            // Same row
            if (i !== col) {
                const cell = document.querySelector(`[data-row="${row}"][data-col="${i}"]`);
                if (cell && !cell.classList.contains('selected')) {
                    cell.classList.add('related');
                }
            }
            // Same column
            if (i !== row) {
                const cell = document.querySelector(`[data-row="${i}"][data-col="${col}"]`);
                if (cell && !cell.classList.contains('selected')) {
                    cell.classList.add('related');
                }
            }
        }

        // Same 3x3 box
        const boxRow = Math.floor(row / 3) * 3;
        const boxCol = Math.floor(col / 3) * 3;
        for (let i = boxRow; i < boxRow + 3; i++) {
            for (let j = boxCol; j < boxCol + 3; j++) {
                if (i !== row || j !== col) {
                    const cell = document.querySelector(`[data-row="${i}"][data-col="${j}"]`);
                    if (cell && !cell.classList.contains('selected')) {
                        cell.classList.add('related');
                    }
                }
            }
        }
    }

    handleKeyPress(e) {
        if (!this.selectedCell) return;

        const { row, col } = this.selectedCell;

        if (e.key >= '1' && e.key <= '9') {
            const num = parseInt(e.key);
            this.setCell(row, col, num);
        } else if (e.key === 'Backspace' || e.key === 'Delete' || e.key === '0') {
            this.setCell(row, col, 0);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            if (row > 0) {
                const cell = document.querySelector(`[data-row="${row - 1}"][data-col="${col}"]`);
                if (cell) cell.click();
            }
        } else if (e.key === 'ArrowDown') {
            e.preventDefault();
            if (row < 8) {
                const cell = document.querySelector(`[data-row="${row + 1}"][data-col="${col}"]`);
                if (cell) cell.click();
            }
        } else if (e.key === 'ArrowLeft') {
            e.preventDefault();
            if (col > 0) {
                const cell = document.querySelector(`[data-row="${row}"][data-col="${col - 1}"]`);
                if (cell) cell.click();
            }
        } else if (e.key === 'ArrowRight') {
            e.preventDefault();
            if (col < 8) {
                const cell = document.querySelector(`[data-row="${row}"][data-col="${col + 1}"]`);
                if (cell) cell.click();
            }
        }
    }

    setCell(row, col, value) {
        if (this.originalGrid[row][col] !== 0) return;

        this.grid[row][col] = value;
        const cell = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
        
        if (value === 0) {
            cell.textContent = '';
            cell.classList.remove('error', 'hint');
        } else {
            cell.textContent = value;
            
            // Check if value is correct
            if (value !== this.solution[row][col]) {
                cell.classList.add('error');
            } else {
                cell.classList.remove('error');
            }
        }

        this.checkWin();
    }

    checkWin() {
        let complete = true;
        for (let row = 0; row < 9; row++) {
            for (let col = 0; col < 9; col++) {
                if (this.grid[row][col] === 0 || this.grid[row][col] !== this.solution[row][col]) {
                    complete = false;
                    break;
                }
            }
            if (!complete) break;
        }

        if (complete) {
            this.showMessage('🎉 Congratulations! You solved the Sudoku!', 'success');
            clearInterval(this.timerInterval);
        }
    }

    solve() {
        this.grid = this.solution.map(row => [...row]);
        this.renderGrid();
        this.showMessage('Puzzle solved!', 'success');
        clearInterval(this.timerInterval);
    }

    clearBoard() {
        this.grid = this.originalGrid.map(row => [...row]);
        this.renderGrid();
        this.showMessage('Board cleared!', '');
    }

    getHint() {
        if (this.hints <= 0) {
            this.showMessage('No more hints available!', 'error');
            return;
        }

        let found = false;
        for (let row = 0; row < 9 && !found; row++) {
            for (let col = 0; col < 9 && !found; col++) {
                if (this.grid[row][col] === 0) {
                    const cell = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
                    this.grid[row][col] = this.solution[row][col];
                    cell.textContent = this.solution[row][col];
                    cell.classList.add('hint');
                    found = true;
                    this.hints--;
                    this.showMessage(`Hint used! (${this.hints} remaining)`, '');
                }
            }
        }

        if (!found) {
            this.showMessage('No empty cells to hint!', 'error');
        }
    }

    newGame() {
        clearInterval(this.timerInterval);
        this.generatePuzzle();
        this.renderGrid();
        this.selectedCell = null;
        this.startTime = null;
        this.hints = 3;
        this.startTimer();
        this.showMessage('New game started!', '');
        document.getElementById('difficultySelect').value = this.difficulty;
        document.getElementById('difficulty').textContent = this.difficulty.charAt(0).toUpperCase() + this.difficulty.slice(1);
    }

    startTimer() {
        this.startTime = Date.now();
        this.timerInterval = setInterval(() => {
            const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
            const minutes = Math.floor(elapsed / 60);
            const seconds = elapsed % 60;
            document.getElementById('timer').textContent = 
                `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        }, 1000);
    }

    showMessage(message, className = '') {
        const messageElement = document.getElementById('message');
        messageElement.textContent = message;
        messageElement.className = className;
    }
}

// Initialize game when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new SudokuGame();
});
