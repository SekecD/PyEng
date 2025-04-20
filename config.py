MAX_ATTEMPTS: int = 3

RESULTS_FILENAME: str = "game_results.csv"
RESULTS_ENCODING: str = "utf-8"

TIMESTAMP_FORMAT: str = "%Y-%m-%d %H:%M:%S"

CSV_HEADERS: list[str] = [
    'Timestamp', 'Mode', 'Dictionary', 'TimeSec', 'Total', 'Correct', 'Incorrect', 'Accuracy'
]

INITIAL_SCORE: int = 0
SCORE_INCREMENT_CORRECT: int = 2
SCORE_DECREMENT_INCORRECT: int = -3