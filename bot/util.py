from prettytable import ALL, PrettyTable


def create_table(
        rows: list[tuple],
        title: str | None = None,
        align: str = 'c',
        **kwargs
) -> PrettyTable:
    table = PrettyTable(
        title=title,
        hrules=ALL,
        vrules=ALL,
        align=align,
        valign='m',
        max_width=21,
        max_table_width=31,
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
