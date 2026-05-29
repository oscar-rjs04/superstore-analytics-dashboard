def kpi_card(col, label: str, value: str, delta: str = None, help: str = None, delta_color: str = "normal"):
    delta_html = ""
    if delta is not None:
        is_positive = not str(delta).startswith("-")
        if delta_color == "inverse":
            color = "#DC2626" if is_positive else "#16A34A"
        elif delta_color == "off":
            color = "#6B7280"
        else:
            color = "#16A34A" if is_positive else "#DC2626"
        delta_html = f'<div style="font-size:0.85rem;color:{color};margin-top:4px;">{delta}</div>'

    tooltip = f' title="{help}"' if help else ""

    col.markdown(f"""
        <div style="
            background:#ffffff;
            border:1px solid #E5E7EB;
            border-radius:10px;
            padding:16px 20px;
            box-shadow:0 1px 3px rgba(0,0,0,0.05);
        "{tooltip}>
            <div style="font-size:0.8rem;color:#6B7280;font-weight:500;text-transform:uppercase;letter-spacing:0.05em;">{label}</div>
            <div style="font-size:1.6rem;font-weight:700;color:#111827;margin-top:4px;">{value}</div>
            {delta_html}
        </div>
        """, unsafe_allow_html=True)
