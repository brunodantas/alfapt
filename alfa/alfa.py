from datetime import datetime

import reflex as rx
from unidecode import unidecode

from .words import word_list


def get_today():
    return datetime.today().date().isoformat()


def get_todays_word(today):
    h = hash(today)
    return word_list[int(h) % len(word_list)].split()[0]


class State(rx.State):
    """The app state."""

    word = ""
    words = [w.split()[0] for w in word_list]
    guessed = False
    today = ""
    tries = 0
    start = datetime.now()
    duration = ""
    words_before = []
    words_after = []
    valid_guess = True

    @rx.event
    def init(self):
        today = get_today()
        if self.today != today:
            self.today = today
            self.word = get_todays_word(today)
            self.guessed = False
            self.start = datetime.now()
        print(self.word)

    @rx.event
    def guess_word(self, form_data):
        guess = form_data["guess"].lower().strip()
        self.guessed = unidecode(self.word) == unidecode(guess)
        self.valid_guess = unidecode(guess).isalpha() and len(guess) > 1
        if not self.valid_guess:
            return
        self.tries += 1
        if not self.guessed:
            if unidecode(guess) < unidecode(self.word):
                self.words_before.append(guess)
                self.words_before.sort()
            else:
                self.words_after.append(guess)
                self.words_after.sort()
        else:
            end = (datetime.now() - self.start).seconds
            self.duration = f"{end//60} minutos e {end%60} segundos"


def show_form():
    return rx.form(
        rx.vstack(
            rx.input(
                name="guess",
                placeholder="Digite uma palavra da língua portuguesa",
                size="3",
                type="text",
                required=True,
                autofocus=True,
                auto_complete=False,
                width="50%",
            ),
            rx.button(
                "Adivinhar", type="submit", align="center", width="50%", size="3"
            ),
            rx.cond(
                State.valid_guess,
                rx.text(),
                rx.text("Palavra inválida", color_scheme="red"),
            ),
            align="center",
        ),
        on_submit=State.guess_word,
        reset_on_submit=True,
    )


def show_word(word):
    return rx.text(word)


def show_words_before():
    return rx.vstack(
        rx.text("A palavra vem depois de:"),
        rx.foreach(State.words_before, show_word),
        align="center",
    )


def show_words_after():
    return rx.vstack(
        rx.text("A palavra vem antes de:"),
        rx.foreach(State.words_after, show_word),
        align="center",
    )


def show_win_state():
    return rx.card(
        rx.vstack(
            rx.text("🎉 Você adivinhou a palavra! 🎉", size="5"),
            rx.text.strong(State.word, size=5),
            rx.text(f"Tentativas: {State.tries}"),
            rx.text(f"Tempo: {State.duration}"),
            rx.button(
                "Copiar",
                on_click=rx.set_clipboard(
                    "🎉 Eu adivinhei a palavra de hoje no AlfaPT! 🎉\n"
                    f"Tentativas: {State.tries}\n"
                    f"Tempo: {State.duration}\n"
                    "https://alfa-navy-panda.reflex.run"
                ),
            ),
            align="center",
        )
    )


@rx.page(title="AlfaPT", description="Jogo de adivinhar palavras", on_load=State.init)
def index() -> rx.Component:
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.heading("AlfaPT"),
        rx.vstack(
            rx.section(
                rx.text(
                    "Tente adivinhar a palavra do dia. "
                    "Cada tentativa revela a posição alfabética da palavra.",
                    align="center",
                    size="5",
                ),
                rx.text("Obs: acentos são desconsiderados.", align="center"),
                width="100%",
            ),
            rx.cond(State.words_before, show_words_before()),
            rx.cond(State.guessed, show_win_state(), show_form()),
            rx.cond(State.words_after, show_words_after()),
            align="center",
        ),
    )


app = rx.App()
app.add_page(index)
