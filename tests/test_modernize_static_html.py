from scripts.modernize_static_html import modernize_html


def test_converts_font_tag_to_css_classes():
    html = '<strong><font color="#248d6c" size="6" class="iw-215">Titel</font></strong>'

    result = modernize_html(html)

    assert "<font" not in result
    assert "</font>" not in result
    assert (
        '<strong><span class="legacy-font legacy-font-size-6 '
        'legacy-font-color-248d6c iw-215">Titel</span></strong>'
    ) == result


def test_converts_weebly_layout_table_to_divs():
    html = (
        '<table class="ew-multicol-table"><tbody class="ew-multicol-tbody">'
        '<tr class="ew-multicol-tr"><td class="ew-multicol-col iw-015">A</td>'
        '<td class="ew-multicol-col iw-016">B</td></tr></tbody></table>'
    )

    result = modernize_html(html)

    assert "<table" not in result
    assert "<tbody" not in result
    assert "<tr" not in result
    assert "<td" not in result
    assert result == (
        '<div class="ew-multicol-table"><div class="ew-multicol-tbody">'
        '<div class="ew-multicol-tr"><div class="ew-multicol-col iw-015">A</div>'
        '<div class="ew-multicol-col iw-016">B</div></div></div></div>'
    )
