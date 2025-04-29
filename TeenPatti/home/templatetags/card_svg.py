# -*- coding: utf-8 -*-
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def card_svg(code, width=48, height=72):
    s = str(code)
    rank = s[:-1] or s
    suit = s[-1]

    mapping = {
      "H": {"symbol": "♥", "color": "red"},
      "♥": {"symbol": "♥", "color": "red"},
      "D": {"symbol": "♦", "color": "red"},
      "♦": {"symbol": "♦", "color": "red"},
      "C": {"symbol": "♣", "color": "black"},
      "♣": {"symbol": "♣", "color": "black"},
      "S": {"symbol": "♠", "color": "black"},
      "♠": {"symbol": "♠", "color": "black"},
    }
    info = mapping.get(suit, {"symbol": "?", "color": "black"})
    symbol, color = info["symbol"], info["color"]

    svg = f'''
    <svg width="{width}" height="{height}" viewBox="0 0 48 72"
         xmlns="http://www.w3.org/2000/svg"
         class="inline-block align-middle">
      <rect width="48" height="72"
            rx="4" ry="4" fill="white" stroke="black"/>
      <text x="4" y="12" font-size="10" fill="{color}"
            font-family="Times New Roman, serif">{rank}</text>
      <text x="44" y="60" font-size="10" fill="{color}"
            font-family="Times New Roman, serif"
            text-anchor="end">{rank}</text>
      <text x="24" y="36" font-size="16" fill="{color}"
            font-family="Times New Roman, serif"
            text-anchor="middle" dominant-baseline="central">
        {symbol}
      </text>
    </svg>'''
    return mark_safe(svg)