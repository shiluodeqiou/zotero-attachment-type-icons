#!/usr/bin/env python3
"""
Generate the icon set and style.css for Attachment Type Icons.

The artwork is Zotero's own attachment icon geometry (item-type/16/{light,dark,white}/
attachment-pdf{,-link}.svg), with the badge recoloured per file family. Keeping the
geometry byte-identical is what makes the icons sit flush with the native PDF/EPUB ones.

Edit FAMILIES below and re-run to change colours or add a format family.
"""

import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ICONS = os.path.join(ROOT, "icons")

# itemTypeSuffix -> badge base colour. The lighter inner tint is derived (60% toward
# white), which is the ratio Zotero uses for PDF (#DB2C3A -> #F1ABB0) and EPUB
# (#39BF68 -> #B0E5C3).
#
# NOTE on PowerPoint: its brand colour (#C43E1C) shares the page geometry with PDF and
# reads as the same red at 16px, so the two are genuinely hard to tell apart in a list.
# A saturated orange separates cleanly in both themes, at some cost to brand fidelity.
# Excel needs no such nudge -- EPUB is also green, but its glyph is a book, not a page.
FAMILIES = {
    "Word":       "#2B579A",  # Word blue
    "Excel":      "#217346",  # Excel green
    "PowerPoint": "#E8730C",  # orange, deliberately not the brand's #C43E1C (see above)
    "Markdown":   "#8250DF",  # purple: Markdown has no brand colour, and this one clashes
                              # with none of the above nor with PDF red / EPUB green
}

# Filename stem per family (lowercased suffix works, but be explicit).
STEMS = {"Word": "word", "Excel": "excel", "PowerPoint": "powerpoint", "Markdown": "markdown"}


def tint(hex_colour, ratio=0.6):
    """Mix `hex_colour` toward white by `ratio`."""
    r, g, b = (int(hex_colour[i:i + 2], 16) for i in (1, 3, 5))
    mix = lambda c: round(c + ratio * (255 - c))
    return "#{:02X}{:02X}{:02X}".format(mix(r), mix(g), mix(b))


# --- Zotero's geometry, with the badge colours parameterised -------------------------

LIGHT = '''<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
<path opacity="0.5" d="M11.707 0H3V16H16V4.293L11.707 0Z" fill="white"/>
<path d="M11.293 1L15 4.707V15H4V1H11.293Z" fill="white"/>
<path opacity="0.2" d="M11.707 0H3V16H16V4.293L11.707 0ZM12 1.707L14.293 4H12V1.707ZM4 15V1H11V5H15V15H4Z" fill="black"/>
<path opacity="0.08" d="M12 1.70703V4H14.293L12 1.70703Z" fill="black"/>
<path d="M8 4H1V6H8V4Z" fill="__TINT__"/>
<path d="M8 4V6H1V4H8ZM9 3H0V7H9V3Z" fill="__BASE__"/>
</svg>
'''

DARK = '''<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
<path opacity="0.24" d="M12 1.70703V4H14.293L12 1.70703Z" fill="white"/>
<path opacity="0.36" d="M8 4H1V6H8V4Z" fill="__BASE__"/>
<path opacity="0.9" d="M8 4V6H1V4H8ZM9 3H0V7H9V3Z" fill="__BASE__"/>
<path opacity="0.6" fill-rule="evenodd" clip-rule="evenodd" d="M3 0H11.707L16 4.293V16H3V7H4V15H15V5H11V1H4V3H3V0ZM14.293 4L12 1.707V4H14.293Z" fill="white"/>
</svg>
'''

LIGHT_LINK = '''<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
<path opacity="0.5" d="M7.5 13.5C7.5 12.9696 7.71071 12.4609 8.08579 12.0858C8.46086 11.7107 8.96957 11.5 9.5 11.5C10.0304 11.5 10.5391 11.7107 10.9142 12.0858C11.2893 12.4609 11.5 12.9696 11.5 13.5C11.5 12.9696 11.7107 12.4609 12.0858 12.0858C12.4609 11.7107 12.9696 11.5 13.5 11.5C13.669 11.5021 13.8371 11.5259 14 11.571V10H15V4.293L10.707 0H3V15H6V14H7.571C7.52594 13.8371 7.50207 13.669 7.5 13.5Z" fill="white"/>
<path d="M7.5 13.5C7.5 12.9696 7.71071 12.4609 8.08579 12.0858C8.46086 11.7107 8.96957 11.5 9.5 11.5C10.0304 11.5 10.5391 11.7107 10.9142 12.0858C11.2893 12.4609 11.5 12.9696 11.5 13.5C11.5 12.9696 11.7107 12.4609 12.0858 12.0858C12.4609 11.7107 12.9696 11.5 13.5 11.5C13.669 11.5021 13.8371 11.5259 14 11.571V4.707L10.293 1H4V14H7.571C7.52594 13.8371 7.50207 13.669 7.5 13.5Z" fill="white"/>
<path opacity="0.08" d="M11 1.70703V4H13.293L11 1.70703Z" fill="black"/>
<path opacity="0.2" d="M6 14H4V1H10V5H14V10H15V4.293L10.707 0H3V15H6V14ZM11 1.707L13.293 4H11V1.707Z" fill="black"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M9.5 11C10.3178 11 11.0439 11.3927 11.5 11.9998C11.9561 11.3927 12.6822 11 13.5 11C14.8807 11 16 12.1193 16 13.5C16 14.8807 14.8807 16 13.5 16C12.6822 16 11.9561 15.6073 11.5 15.0002C11.0439 15.6073 10.3178 16 9.5 16C8.11929 16 7 14.8807 7 13.5C7 12.1193 8.11929 11 9.5 11ZM10.9146 13H9.5C9.22386 13 9 13.2239 9 13.5C9 13.7761 9.22386 14 9.5 14H10.9146C10.7087 14.5826 10.1531 15 9.5 15C8.67157 15 8 14.3284 8 13.5C8 12.6716 8.67157 12 9.5 12C10.1531 12 10.7087 12.4174 10.9146 13ZM12.0854 14H13.5C13.7761 14 14 13.7761 14 13.5C14 13.2239 13.7761 13 13.5 13H12.0854C12.2913 12.4174 12.8469 12 13.5 12C14.3284 12 15 12.6716 15 13.5C15 14.3284 14.3284 15 13.5 15C12.8469 15 12.2913 14.5826 12.0854 14Z" fill="#888888"/>
<path d="M7 4H1V6H7V4Z" fill="__TINT__"/>
<path d="M7 4V6H1V4H7ZM8 3H0V7H8V3Z" fill="__BASE__"/>
</svg>
'''

DARK_LINK = '''<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
<path opacity="0.24" d="M11 1.70703V4H13.293L11 1.70703Z" fill="white"/>
<path opacity="0.6" fill-rule="evenodd" clip-rule="evenodd" d="M9.5 11C10.3178 11 11.0439 11.3927 11.5 11.9998C11.9561 11.3927 12.6822 11 13.5 11C14.8807 11 16 12.1193 16 13.5C16 14.8807 14.8807 16 13.5 16C12.6822 16 11.9561 15.6073 11.5 15.0002C11.0439 15.6073 10.3178 16 9.5 16C8.11929 16 7 14.8807 7 13.5C7 12.1193 8.11929 11 9.5 11ZM10.9146 13H9.5C9.22386 13 9 13.2239 9 13.5C9 13.7761 9.22386 14 9.5 14H10.9146C10.7087 14.5826 10.1531 15 9.5 15C8.67157 15 8 14.3284 8 13.5C8 12.6716 8.67157 12 9.5 12C10.1531 12 10.7087 12.4174 10.9146 13ZM12.0854 14H13.5C13.7761 14 14 13.7761 14 13.5C14 13.2239 13.7761 13 13.5 13H12.0854C12.2913 12.4174 12.8469 12 13.5 12C14.3284 12 15 12.6716 15 13.5C15 14.3284 14.3284 15 13.5 15C12.8469 15 12.2913 14.5826 12.0854 14Z" fill="white"/>
<path opacity="0.36" d="M7 4H1V6H7V4Z" fill="__BASE__"/>
<path opacity="0.9" d="M7 4V6H1V4H7ZM8 3H0V7H8V3Z" fill="__BASE__"/>
<g opacity="0.6">
<path d="M4 14H6V15H3V7H4V14Z" fill="white"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M4 3V1H10V5H14V10H15V4.293L10.707 0H3V3H4ZM13.293 4L11 1.707V4H13.293Z" fill="white"/>
</g>
</svg>
'''

# The selected-and-focused ("white") variant carries no colour at all, so a single
# shared file serves every family -- exactly as Zotero's own PDF and EPUB icons are
# indistinguishable once a row is selected.
WHITE = '''<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
<path opacity="0.4" d="M11.5 0.5V4.5H15.5L11.5 0.5Z" fill="white"/>
<path opacity="0.4" d="M8 4H1V6H8V4Z" fill="white"/>
<path d="M11.707 0H3V3H0V7H3V16H16V4.293L11.707 0ZM12 1.707L14.293 4H12V1.707ZM1 6V4H8V6H1ZM15 15H4V7H9V3H4V1H11V5H15V15Z" fill="white"/>
</svg>
'''

WHITE_LINK = '''<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
<path opacity="0.4" d="M13.293 4.00003H11V1.70703L13.293 4.00003ZM7 6.00003V4.00003H1V6.00003H7Z" fill="white"/>
<path d="M13.5 11C12.678 11 11.956 11.402 11.5 12.014C11.044 11.402 10.321 11 9.5 11C8.119 11 7 12.119 7 13.5C7 14.881 8.119 16 9.5 16C10.322 16 11.045 15.598 11.5 14.986C11.956 15.598 12.678 16 13.5 16C14.881 16 16 14.881 16 13.5C16 12.119 14.881 11 13.5 11ZM9.5 15C8.673 15 8 14.327 8 13.5C8 12.673 8.673 12 9.5 12C10.151 12 10.701 12.419 10.908 13H9.5C9.224 13 9 13.224 9 13.5C9 13.776 9.224 14 9.5 14H10.908C10.701 14.581 10.151 15 9.5 15ZM13.5 15C12.849 15 12.299 14.581 12.092 14H13.5C13.776 14 14 13.776 14 13.5C14 13.224 13.776 13 13.5 13H12.092C12.299 12.419 12.849 12 13.5 12C14.327 12 15 12.673 15 13.5C15 14.327 14.327 15 13.5 15ZM10.707 0H3V3H0V7H3V15H6V14H4V7H8V3H4V1H10V5H14V10H15V4.293L10.707 0ZM7 4V6H1V4H7ZM11 4V1.707L13.293 4H11Z" fill="white"/>
</svg>
'''


def write(name, content):
    path = os.path.join(ICONS, name)
    with open(path, "w") as f:
        f.write(content)
    return name


def main():
    os.makedirs(ICONS, exist_ok=True)
    written = [write("page-white.svg", WHITE), write("page-link-white.svg", WHITE_LINK)]

    for family, base in FAMILIES.items():
        stem = STEMS[family]
        subs = {"__BASE__": base, "__TINT__": tint(base)}
        for suffix, template in (
            ("light", LIGHT), ("dark", DARK),
            ("link-light", LIGHT_LINK), ("link-dark", DARK_LINK),
        ):
            svg = template
            for k, v in subs.items():
                svg = svg.replace(k, v)
            written.append(write("{}-{}.svg".format(stem, suffix), svg))

    # --- style.css ---------------------------------------------------------------
    #
    # Specificity has to be matched against Zotero's own generated rules in
    # scss/components/_item-tree.scss, which emit three tiers for the *default*
    # (unrecognised) item type:
    #
    #   .icon-item-type                                                       (0,1,0)
    #   .focus-states-target .row .icon-item-type                             (0,3,0)
    #   .focus-states-target:focus-within .row.selected .icon-item-type       (0,5,0)
    #
    # Our item types are unrecognised by Zotero, so those defaults (document.svg --
    # the blank page) are what we are overriding. Mirroring each tier with the
    # [data-item-type] attribute added puts us one point ahead at every tier, so the
    # cascade resolves correctly without !important.
    lines = [
        "/* Attachment Type Icons -- GENERATED by tools/gen-icons.py, do not edit by hand. */",
        "",
    ]

    def rules(scheme, variant):
        out = []
        for family in FAMILIES:
            stem = STEMS[family]
            for kind, itype in (("", family), ("link-", family + "Link")):
                sel = '[data-item-type="attachment{}"]'.format(itype)
                out.append(
                    "\t.icon-item-type{s},\n"
                    "\t.focus-states-target .row .icon-item-type{s} {{\n"
                    "\t\tbackground: url(\"icons/{stem}-{kind}{v}.svg\") no-repeat center/contain;\n"
                    "\t}}".format(s=sel, stem=stem, kind=kind, v=variant)
                )
        return out

    for scheme in ("light", "dark"):
        lines.append("@media (prefers-color-scheme: {}) {{".format(scheme))
        lines.extend(rules(scheme, scheme))
        lines.append("}")
        lines.append("")

    lines.append("/* Selected in a focused tree: Zotero switches to an all-white glyph, which")
    lines.append("   carries no badge colour, so one shared file covers every family and both")
    lines.append("   colour schemes. At (0,6,0) these outrank the per-scheme rules above. */")
    for family in FAMILIES:
        for kind, itype in (("page-white", family), ("page-link-white", family + "Link")):
            lines.append(
                '.focus-states-target:focus-within .row.selected '
                '.icon-item-type[data-item-type="attachment{}"] {{'.format(itype)
            )
            lines.append('\tbackground: url("icons/{}.svg") no-repeat center/contain;'.format(kind))
            lines.append("}")
    lines.append("")

    css = "\n".join(lines)
    with open(os.path.join(ROOT, "style.css"), "w") as f:
        f.write(css)

    print("wrote {} icons + style.css".format(len(written)))
    for n in sorted(written):
        print("  icons/" + n)


if __name__ == "__main__":
    main()
