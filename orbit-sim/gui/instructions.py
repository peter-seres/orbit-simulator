import arcade

from settings import AppSettings


def generate_instructions(x=0, y=0, y_sep: int = 20, inst_font: int = 11, title_font: int = 14, color=arcade.color.WHITE):

    yield arcade.create_text_sprite(
        text="Instructions",
        start_x=x,
        start_y=y,
        font_size=title_font,
        bold=True,
        color=color
    )

    for inst in AppSettings.INSTRUCTIONS:
        y -= y_sep
        yield arcade.create_text_sprite(
            text=inst,
            start_x=x,
            start_y=y,
            font_size=inst_font,
            color=color
        )
