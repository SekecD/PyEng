import random
import time
from typing import Callable, Tuple

import core
from data import AnyWordList

def run_round(mode_logic_func: Callable, word_list: AnyWordList, list_name: str, list_type: str, mode_name: str):
    if not word_list:
        print(f"Словарь '{list_name}' пуст.")
        return

    print(f"\n--- Режим: {mode_name} | Словарь: {list_name} ---")
    start_ts = time.time()
    total_processed, correct, incorrect = mode_logic_func(word_list, list_type)
    end_ts = time.time()

    results = core.calculate_results(start_ts, total_processed, correct, incorrect)
    results['Mode'] = mode_name
    results['Dictionary'] = list_name
    core.save_result(results)

    print(f"\nИтог [{mode_name} | {list_name}]:")
    print(f"  Проверено: {total_processed}/{len(word_list)}")
    print(f"  Верно: {correct}, Неверно: {incorrect}")
    print(f"  Время: {results['TimeSec']} сек.")
    print(f"  Точность: {results['Accuracy']}")


def _mode_sequential(word_list: AnyWordList, list_type: str) -> Tuple[int, int, int]:
    total = len(word_list)
    correct = 0
    processed = 0

    check_func = core.check_verb_forms_eng_prompt if list_type == "verb" else core.check_word_rus_eng_prompt

    for i, item in enumerate(word_list, 1):
        print(f"\n{i}/{total}: ", end="")
        if check_func(item):
            correct += 1
        processed += 1

    incorrect = processed - correct
    return processed, correct, incorrect

def _mode_random(word_list: AnyWordList, list_type: str) -> Tuple[int, int, int]:
    active_list = word_list.copy()
    random.shuffle(active_list)
    total = len(active_list)
    correct = 0
    processed = 0

    check_func = core.check_verb_3_forms_rus_prompt if list_type == "verb" else core.check_word_eng_rus_prompt

    for i, item in enumerate(active_list, 1):
        print(f"\n{i}/{total}: ", end="")
        if check_func(item):
            correct += 1
        processed += 1

    incorrect = processed - correct
    return processed, correct, incorrect

def _mode_spaced_repetition(word_list: AnyWordList, list_type: str) -> Tuple[int, int, int]:
    total = len(word_list)
    correct = 0
    processed = 0
    tracker = core.SpacedRepetitionTracker(word_list)

    check_func = core.check_verb_3_forms_rus_prompt if list_type == "verb" else core.check_word_eng_rus_prompt

    for i in range(total):
        item = tracker.get_next_item()
        if item is None:
            print("Не удалось получить следующее слово от трекера.")
            break

        print(f"\n{i+1}/{total}: ", end="")
        is_correct = check_func(item)
        tracker.update_score(item, is_correct)

        if is_correct:
            correct += 1
        processed += 1

    incorrect = processed - correct
    return processed, correct, incorrect

def run_mode_1_sequential(word_list: AnyWordList, list_name: str, list_type: str):
    run_round(_mode_sequential, word_list, list_name, list_type, "Подряд")

def run_mode_2_spaced_repetition(word_list: AnyWordList, list_name: str, list_type: str):
    run_round(_mode_spaced_repetition, word_list, list_name, list_type, "Умное повторение")

def run_mode_3_random(word_list: AnyWordList, list_name: str, list_type: str):
    run_round(_mode_random, word_list, list_name, list_type, "Случайно")