from math import ceil

from telegram import MAX_MESSAGE_LENGTH, InlineKeyboardButton, Bot, ParseMode
from telegram.error import TelegramError


def split_message(msg):
    if len(msg) < MAX_MESSAGE_LENGTH:
        return [msg]

    else:
        lines = msg.splitlines(True)
        small_msg = ""
        result = []
        for line in lines:
            if len(small_msg) + len(line) < MAX_MESSAGE_LENGTH:
                small_msg += line
            else:
                result.append(small_msg)
                small_msg = line
        else:
            # Else statement at the end of the for loop, so append the leftover string.
            result.append(small_msg)

        return result


def paginate_modules(page_n, module_dict):
    modules = sorted(
        [EqInlineKeyboardButton(x.__name__, callback_data="help_module({})".format(x.__name__.lower())) for x in
         module_dict.values()])

    pairs = list(zip(modules[::2], modules[1::2]))

    if len(modules) % 2 == 1:
        pairs.append((modules[-1],))

    max_num_pages = ceil(len(pairs) / 7)
    modulo_page = page_n % max_num_pages

    # can only have a certain amount of buttons side by side
    if len(pairs) > 7:
        pairs = pairs[modulo_page * 7:7 * (modulo_page + 1)] + [
            (EqInlineKeyboardButton("<", callback_data="help_prev({})".format(modulo_page)),
             EqInlineKeyboardButton(">", callback_data="help_next({})".format(modulo_page)))]

    return pairs


def send_to_list(bot: Bot, send_to: list, message: str, markdown=False):
    for user_id in set(send_to):
        try:
            bot.send_message(user_id, message, parse_mode=ParseMode.MARKDOWN if markdown else None)
        except TelegramError:
            pass  # ignore users who fail


class EqInlineKeyboardButton(InlineKeyboardButton):
    def __eq__(self, other):
        return self.text == other.text

    def __lt__(self, other):
        return self.text < other.text

    def __gt__(self, other):
        return self.text > other.text
