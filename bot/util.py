from collections import defaultdict

from prettytable import ALL, PrettyTable

CURRENCY_RATES = {
    'RUB': 1,
    'USD': 96,
    'EUR': 102,
    'RSD': 0.85
}


def convert_record_currency(amount: float, given_currency: str, expected_currency: str) -> float:
    amount_in_rub = amount * CURRENCY_RATES[given_currency]
    expected_amount = amount_in_rub / CURRENCY_RATES[expected_currency]
    return round(expected_amount, 2)


def create_table(
        rows: list[tuple],
        title: str | None = None,
        align: str = 'c',
        field_names: tuple[str, str] | None = None,
        **kwargs: object
) -> PrettyTable:
    table = PrettyTable(
        title=title,
        hrules=ALL,
        vrules=ALL,
        align=align,
        valign='m',
        max_width=21,
        max_table_width=31,
        field_names=field_names,
        **kwargs
    )
    table.add_rows(rows)
    return table


def is_number(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


def create_report_table(records: list, main_currency: str, **kwargs) -> PrettyTable:
    total_sum = 0
    amount_per_category = defaultdict(float)

    for r in records:
        category_name, amount, currency = r['category']['name'], r['amount'], r['currency']

        if currency != main_currency:
            amount = convert_record_currency(amount, currency, main_currency)

        amount_per_category[category_name] += amount
        total_sum += amount

    sorted_results = sorted(
        amount_per_category.items(),
        key=lambda x: x[1],
        reverse=True
    )

    table = PrettyTable(
        hrules=ALL,
        vrules=ALL,
        align='l',
        valign='m',
        max_width=21,
        max_table_width=33,
        field_names=('CATEGORY', main_currency, '%'),
        **kwargs
    )

    for category, amount in sorted_results:
        percentage = (amount / total_sum) * 100 if total_sum else 0
        table.add_row([category, f'{amount:.1f}', f'{percentage:.0f}'])

    table.add_row(['TOTAL', f'{total_sum:.1f}', '100'])

    return table
