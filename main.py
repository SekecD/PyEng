import sys
from typing import NamedTuple, Optional
import game_modes
import core
import data
from data import AnyWordList
from core import DailyStats

class DictionarySelection(NamedTuple):
    word_list: Optional[AnyWordList]
    list_name: str
    list_type: str

def display_mode_menu():
    print("\nРежимы:")
    print("  1. Подряд (Англ -> формы/перевод)")
    print("  2. Умное повторение (Рус -> формы/слово)")
    print("  3. Случайно (Рус -> формы/слово)")
    print("  4. Статистика за сегодня")
    print("  0. Выход")


def display_stats(stats: DailyStats):
    print("\n--- Статистика за сегодня ---")
    if stats.sessions == 0:
        print("  Сегодня еще не было тренировок.")
    else:
        print(f"  Тренировок запущено: {stats.sessions}")
        print(f"  Всего слов проверено: {stats.total_words}")
        print(f"  Правильных ответов: {stats.correct}")
        print(f"  Ошибок: {stats.incorrect}")
        minutes, seconds = divmod(int(stats.total_time_sec), 60)
        time_str = f"{minutes} мин {seconds} сек" if minutes > 0 else f"{seconds} сек"
        print(f"  Затрачено времени: {time_str} ({stats.total_time_sec:.2f} сек)")
    print("---------------------------")

def select_mode() -> int:
    while True:
        display_mode_menu()
        choice_str = core.ask_user("Выберите номер режима")
        try:
            choice = int(choice_str)
            if 0 <= choice <= 4:
                return choice
            else:
                print("! Неверный номер режима.")
        except ValueError:
            print("! Введите число.")

def display_dictionary_menu():
    print("\nСловари:")
    for i, name in enumerate(data.DICTIONARIES.keys(), 1):
         print(f"  {i}. {name}")
    print("  0. Назад (к выбору режима)")

def select_dictionary() -> DictionarySelection:
    dict_keys = list(data.DICTIONARIES.keys())
    while True:
        display_dictionary_menu()
        choice_str = core.ask_user("Выберите номер словаря")
        try:
            choice = int(choice_str)
            if choice == 0:
                return DictionarySelection(None, "", "")
            elif 1 <= choice <= len(dict_keys):
                dict_name = dict_keys[choice - 1]
                word_list = data.DICTIONARIES[dict_name]
                list_type = data.get_list_type(word_list)
                if list_type == "unknown":
                     continue
                return DictionarySelection(word_list, dict_name, list_type)
            else:
                print("! Неверный номер словаря.")
        except ValueError:
            print("! Введите число.")

def main():
    mode_runners = {
        1: game_modes.run_mode_1_sequential,
        2: game_modes.run_mode_2_spaced_repetition,
        3: game_modes.run_mode_3_random,
    }

    while True:

        selected_mode = select_mode()
        if selected_mode == 0:
            print("Завершение работы.")
            sys.exit(0)

        elif selected_mode == 4:
            today_stats = core.get_daily_stats()
            display_stats(today_stats)
            core.ask_user("\nНажмите Enter для возврата в меню...")
            continue
        else:
            selection = select_dictionary()
            if selection.word_list is None:
                continue

            runner_func = mode_runners.get(selected_mode)
            if runner_func:
                try:
                    runner_func(selection.word_list, selection.list_name, selection.list_type)
                except Exception as e:
                    print(f"\n[Критическая ошибка] Во время выполнения режима: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"! Ошибка: не найдена функция для режима {selected_mode}.")

        selection = select_dictionary()

        if selection.word_list is None:
            continue

        runner_func = mode_runners.get(selected_mode)
        if runner_func:
            try:
                runner_func(selection.word_list, selection.list_name, selection.list_type)
            except Exception as e:
                print(f"{e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"! н найдена функция для режима {selected_mode}.")

        play_again = core.ask_user("\nЕще раунд? (y/n)").lower()
        if play_again != 'y':
            print("До встречи!")
            break

if __name__ == "__main__":
    main()