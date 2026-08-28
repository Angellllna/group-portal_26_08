"""Тематичні приклади опитувань.

Вимога таску POL-2: опитування живуть у базі, а не в HTML-шаблонах.
Міграція ідемпотентна — повторний запуск нічого не дублює.
"""

from django.db import migrations
from django.utils.text import slugify

# (питання, тип, обов'язкове, [(варіант, правильний), ...])
EXAMPLE_POLLS = [
    {
        "title": "Чи розпізнаєш ти маніпуляцію казино?",
        "description": "Коротка перевірка: чи бачиш ти прийоми, якими гру роблять затягуючою.",
        "pages": [
            {
                "title": "Що ти бачиш на екрані",
                "questions": [
                    (
                        "Автомат зупинився за один символ до джекпоту. Що це?",
                        "single_choice",
                        True,
                        [
                            ("Ефект «майже виграшу» — спеціально спроєктований", True),
                            ("Просто невдача, випадковість", False),
                            ("Знак, що виграш скоро буде", False),
                        ],
                    ),
                    (
                        "Гроші в грі показані фішками, а не гривнями. Навіщо?",
                        "single_choice",
                        True,
                        [
                            ("Щоб втрата відчувалась не як втрата справжніх грошей", True),
                            ("Щоб було зручніше рахувати", False),
                            ("Такі вимоги закону", False),
                        ],
                    ),
                ],
            },
            {
                "title": "Що ти робиш далі",
                "questions": [
                    (
                        "Які прийоми утримання ти помічав в іграх? (кілька варіантів)",
                        "multiple_choice",
                        True,
                        [
                            ("Щоденні нагороди за вхід", True),
                            ("Таймер «пропозиція згорить»", True),
                            ("Безкоштовні спроби на початку", True),
                            ("Кнопка «вийти з гри»", False),
                        ],
                    ),
                    (
                        "Що б ти порадив другу, який програв і хоче відігратися?",
                        "text",
                        False,
                        [],
                    ),
                ],
            },
        ],
    },
    {
        "title": "Що ти знаєш про азартні механіки?",
        "description": "Базові поняття: ставка, шанс, перевага закладу.",
        "pages": [
            {
                "title": "Основи",
                "questions": [
                    (
                        "Хто в довгій грі залишається у плюсі?",
                        "single_choice",
                        True,
                        [
                            ("Заклад — за рахунок математичної переваги", True),
                            ("Найдосвідченіший гравець", False),
                            ("Той, хто ставить найбільше", False),
                        ],
                    ),
                    (
                        "Попередні програші впливають на шанс наступного спіну?",
                        "single_choice",
                        True,
                        [
                            ("Ні, кожен спін незалежний", True),
                            ("Так, шанс зростає", False),
                        ],
                    ),
                ],
            },
        ],
    },
    {
        "title": "Як реклама впливає на рішення користувача?",
        "description": "Про те, що реклама показує — і що вона старанно ховає.",
        "pages": [
            {
                "title": "Що показують",
                "questions": [
                    (
                        "Чому в рекламі завжди виграють?",
                        "single_choice",
                        True,
                        [
                            ("Показують винятки й мовчать про статистику програшів", True),
                            ("Бо виграти справді легко", False),
                        ],
                    ),
                    (
                        "Які сигнали в рекламі мають насторожити? (кілька варіантів)",
                        "multiple_choice",
                        True,
                        [
                            ("«Легкі гроші без зусиль»", True),
                            ("Зворотний відлік до кінця акції", True),
                            ("Попередження про ризик", False),
                        ],
                    ),
                ],
            },
        ],
    },
    {
        "title": "Лутбокси: гра чи азартна механіка?",
        "description": "Де закінчується ігровий контент і починається ставка.",
        "pages": [
            {
                "title": "Ознаки",
                "questions": [
                    (
                        "Що робить лутбокс схожим на азартну гру?",
                        "single_choice",
                        True,
                        [
                            ("Плата за випадковий результат невідомої цінності", True),
                            ("Яскрава анімація відкриття", False),
                        ],
                    ),
                    (
                        "Чи вважаєш ти, що лутбокси треба обмежувати для дітей? Поясни.",
                        "text",
                        False,
                        [],
                    ),
                ],
            },
        ],
    },
    {
        "title": "Чому виникає бажання відігратися?",
        "description": "Психологія втрати і хибне відчуття контролю.",
        "pages": [
            {
                "title": "Реакція на втрату",
                "questions": [
                    (
                        "Як називається спроба повернути втрачене новими ставками?",
                        "single_choice",
                        True,
                        [
                            ("Погоня за втратами", True),
                            ("Стратегія подвоєння", False),
                            ("Розумний ризик", False),
                        ],
                    ),
                    (
                        "Чим це небезпечно?",
                        "single_choice",
                        True,
                        [
                            ("Втрата зростає разом зі ставками", True),
                            ("Нічим, це нормальна тактика", False),
                        ],
                    ),
                ],
            },
        ],
    },
]


def create_example_polls(apps, schema_editor):
    Poll = apps.get_model("polls", "Poll")
    PollPage = apps.get_model("polls", "PollPage")
    Question = apps.get_model("polls", "Question")
    AnswerOption = apps.get_model("polls", "AnswerOption")

    for poll_data in EXAMPLE_POLLS:
        # у міграції працює historical model, тому slug рахуємо вручну:
        # Poll.save() з моделі застосунку тут недоступний
        slug = slugify(poll_data["title"], allow_unicode=True)

        if Poll.objects.filter(slug=slug).exists():
            continue

        poll = Poll.objects.create(
            title=poll_data["title"],
            slug=slug,
            description=poll_data["description"],
            is_active=True,
            allow_retake=True,
            show_result=True,
        )

        for page_position, page_data in enumerate(poll_data["pages"], start=1):
            page = PollPage.objects.create(
                poll=poll,
                title=page_data["title"],
                position=page_position,
            )

            for q_position, (text, q_type, required, options) in enumerate(
                page_data["questions"], start=1
            ):
                question = Question.objects.create(
                    page=page,
                    text=text,
                    question_type=q_type,
                    is_required=required,
                    position=q_position,
                )

                for o_position, (option_text, is_correct) in enumerate(options, start=1):
                    AnswerOption.objects.create(
                        question=question,
                        text=option_text,
                        is_correct=is_correct,
                        position=o_position,
                    )


def delete_example_polls(apps, schema_editor):
    Poll = apps.get_model("polls", "Poll")

    slugs = [
        slugify(poll_data["title"], allow_unicode=True)
        for poll_data in EXAMPLE_POLLS
    ]
    Poll.objects.filter(slug__in=slugs).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("polls", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_example_polls, delete_example_polls),
    ]
