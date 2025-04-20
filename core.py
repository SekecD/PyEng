import time
import csv
import os
import random
from typing import Dict, Any, Union, List

import config as cfg
from data import VerbItem, WordPairItem, AnyWordList


def ask_user(prompt: str) -> str:
    return input(f"{prompt}: ").strip()

def is_correct(user_input: str, correct_answer: str) -> bool:
    return user_input.strip().lower() == correct_answer.strip().lower()


def _check_single_verb_form(prompt: str, correct_form: str, attempts_left: int) -> tuple[bool, int]:
    user_input = ask_user(prompt)
    if is_correct(user_input, correct_form):
        print("  + Верно")
        return True, attempts_left
    else:
        attempts_left -= 1
        if attempts_left > 0:
            print(f"  - Неверно. Осталось попыток: {attempts_left}")
        else:
            print(f"  - Неверно.")
        return False, attempts_left

def check_verb_forms_eng_prompt(item: VerbItem) -> bool:
    attempts = cfg.MAX_ATTEMPTS
    form2_ok = False
    form3_ok = False

    print(f"Глагол: {item.base} ({item.translation})")

    form2_ok, attempts = _check_single_verb_form(f"  2-я форма", item.f2, attempts)
    if attempts == 0 and not form2_ok:
        print(f"  ! Правильно: {item.base}, {item.f2}, {item.f3}")
        return False

    if attempts > 0:
        form3_ok, attempts = _check_single_verb_form(f"  3-я форма", item.f3, attempts)
        if attempts == 0 and not form3_ok:
            print(f"  ! Правильно: {item.base}, {item.f2}, {item.f3}")
            return False

    if form2_ok and form3_ok:
         print("  ++ Все формы верны!")
         return True
    else:
         return False

def check_word_rus_eng_prompt(item: WordPairItem) -> bool:
    user_input = ask_user(f"Перевод '{item.eng}'")
    if is_correct(user_input, item.rus):
        print("  + Верно")
        return True
    else:
        print(f"  - Неверно. Правильно: '{item.rus}'")
        return False

def check_verb_3_forms_rus_prompt(item: VerbItem) -> bool:
    print(f"Переведите и назовите 3 формы: '{item.translation}'")
    user_input_str = ask_user("  Введите 3 формы через пробел")
    user_forms = user_input_str.split()

    is_forms_correct = (
        len(user_forms) == 3 and
        is_correct(user_forms[0], item.base) and
        is_correct(user_forms[1], item.f2) and
        is_correct(user_forms[2], item.f3)
    )

    if is_forms_correct:
        print("  + Верно")
        return True
    else:
        print(f"  - Неверно. Правильно: {item.base}, {item.f2}, {item.f3}")
        return False

def check_word_eng_rus_prompt(item: WordPairItem) -> bool:
    user_input = ask_user(f"Перевод '{item.rus}'")
    if is_correct(user_input, item.eng):
        print("  + Верно")
        return True
    else:
        print(f"  - Неверно. Правильно: '{item.eng}'")
        return False

def save_result(result_data: Dict[str, Any]):
    file_exists = os.path.isfile(cfg.RESULTS_FILENAME)
    try:
        with open(cfg.RESULTS_FILENAME, 'a', newline='', encoding=cfg.RESULTS_ENCODING) as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=cfg.CSV_HEADERS, extrasaction='ignore')
            if not file_exists or os.path.getsize(cfg.RESULTS_FILENAME) == 0:
                writer.writeheader()
            writer.writerow(result_data)
    except IOError as e:
        print(f"{e}")
    except Exception as e:
        print(f"{e}")

def calculate_results(start_ts: float, total: int, correct: int, incorrect: int) -> Dict[str, Any]:
    end_ts = time.time()
    time_sec = end_ts - start_ts
    accuracy = (correct / total * 100) if total > 0 else 0
    return {
        'Timestamp': time.strftime(cfg.TIMESTAMP_FORMAT),
        'TimeSec': f"{time_sec:.2f}",
        'Total': total,
        'Correct': correct,
        'Incorrect': incorrect,
        'Accuracy': f"{accuracy:.1f}%"
    }

class SpacedRepetitionTracker:
    def __init__(self, items: AnyWordList):
        self.items = items
        self.word_states: Dict[str, Dict[str, int]] = {
            self._get_item_key(item): {"score": cfg.INITIAL_SCORE}
            for item in items
        }
        self.history: List[str] = []

    def _get_item_key(self, item: Union[VerbItem, WordPairItem]) -> str:
        if isinstance(item, VerbItem):
            return item.base.lower()
        elif isinstance(item, WordPairItem):
            return item.eng.lower()
        else:
            raise TypeError(f"{type(item)}")

    def _get_item_by_key(self, key: str) -> Union[VerbItem, WordPairItem, None]:
        search_key = key.lower()
        for item in self.items:
            item_key = self._get_item_key(item)
            if item_key == search_key:
                return item
        return None

    def get_next_item(self) -> Union[VerbItem, WordPairItem, None]:
        if not self.word_states: return None
        if not self.word_states.values(): return None
        min_score = min(state["score"] for state in self.word_states.values())

        candidates = [k for k, state in self.word_states.items() if state["score"] == min_score]

        eligible_candidates = [c for c in candidates if c not in self.history[-(len(candidates)//2 + 1):]]
        if not eligible_candidates: eligible_candidates = candidates

        chosen_key = random.choice(eligible_candidates)
        self.history.append(chosen_key)
        if len(self.history) > len(self.items) * 2: self.history = self.history[-len(self.items):]

        return self._get_item_by_key(chosen_key)

    def update_score(self, item: Union[VerbItem, WordPairItem], correct: bool):
        key = self._get_item_key(item)
        if key in self.word_states:
            score = self.word_states[key]["score"]
            increment = cfg.SCORE_INCREMENT_CORRECT if correct else cfg.SCORE_DECREMENT_INCORRECT
            self.word_states[key]["score"] = score + increment
        else:
            print(f"[Предупреждение] Попытка обновить score для неизвестного ключа: {key}")