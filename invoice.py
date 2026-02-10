"""
Better Invoice Generator (PDF) - ReportLab Platypus

Install:
  python3 -m pip install reportlab

Optional (for ₹ and Unicode):
  Place DejaVuSans.ttf and DejaVuSans-Bold.ttf in the same folder as this script.

Run:
  python invoice_generator_better.py

Output:
  invoice_<invoice_number>.pdf
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Dict, List, Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    HRFlowable,
    KeepTogether,
)

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# -----------------------------
# Helpers
# -----------------------------

TWOPLACES = Decimal("0.01")


def D(x: Any) -> Decimal:
    if isinstance(x, Decimal):
        return x
    if x is None:
        return Decimal("0")
    return Decimal(str(x))


def money(x: Decimal, currency_symbol: str = "₹") -> str:
    x = D(x).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
    return f"{currency_symbol}{x:,.2f}"


def safe_br(text: str) -> str:
    """Convert newlines to <br/> for Paragraph."""
    return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>")


def try_register_unicode_fonts(font_dir: Path) -> Dict[str, Any]:
    """
    If DejaVu fonts exist in folder, register them for Unicode (₹ etc.).
    Returns chosen font names for regular/bold and a unicode support flag.
    """
    regular = font_dir / "DejaVuSans.ttf"
    bold = font_dir / "DejaVuSans-Bold.ttf"

    base = "Helvetica"
    base_bold = "Helvetica-Bold"

    if regular.exists():
        pdfmetrics.registerFont(TTFont("DejaVu", str(regular)))
        base = "DejaVu"
    if bold.exists():
        pdfmetrics.registerFont(TTFont("DejaVu-Bold", str(bold)))
        base_bold = "DejaVu-Bold"

    supports_unicode = base.startswith("DejaVu") or base_bold.startswith("DejaVu")
    return {"regular": base, "bold": base_bold, "supports_unicode": supports_unicode}


# -----------------------------
# Data Models
# -----------------------------

@dataclass
class Party:
    name: str
    address_lines: List[str] = field(default_factory=list)
    phone: str = ""
    email: str = ""
    tax_id_label: str = "GSTIN"
    tax_id_value: str = ""
    extra: List[str] = field(default_factory=list)


@dataclass
class LineItem:
    description: str
    quantity: Decimal
    unit_price: Decimal
    unit: str = "pcs"
    sku: str = ""
    tax_rate: Decimal = Decimal("0.00")  # e.g. 0.18

    @property
    def amount(self) -> Decimal:
        return (D(self.quantity) * D(self.unit_price)).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

    @property
    def tax_amount(self) -> Decimal:
        return (self.amount * D(self.tax_rate)).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

    @property
    def total(self) -> Decimal:
        return (self.amount + self.tax_amount).quantize(TWOPLACES, rounding=ROUND_HALF_UP)


@dataclass
class Invoice:
    invoice_number: str
    invoice_date: date
    due_date: date
    currency_symbol: str = "₹"

    seller: Party = field(default_factory=Party)
    buyer: Party = field(default_factory=Party)

    # Invoice-level adjustments
    shipping: Decimal = Decimal("0.00")
    discount_rate: Decimal = Decimal("0.00")     # 0.05 = 5%
    discount_amount: Decimal = Decimal("0.00")   # overrides discount_rate if > 0
    global_tax_rate: Decimal = Decimal("0.00")   # applied to items where item.tax_rate == 0

    # Meta
    payment_terms: str = "Due on receipt"
    purchase_order: str = ""
    place_of_supply: str = ""
    notes: str = ""
    terms_and_conditions: str = ""
    bank_details: Dict[str, str] = field(default_factory=dict)

    logo_path: Optional[str] = None
    items: List[LineItem] = field(default_factory=list)

    def subtotal(self) -> Decimal:
        return sum((i.amount for i in self.items), Decimal("0.00")).quantize(TWOPLACES)

    def discount_value(self) -> Decimal:
        if D(self.discount_amount) > 0:
            return D(self.discount_amount).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
        return (self.subtotal() * D(self.discount_rate)).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

    def item_tax_total(self) -> Decimal:
        return sum((i.tax_amount for i in self.items), Decimal("0.00")).quantize(TWOPLACES)

    def global_tax_value(self) -> Decimal:
        base = sum((i.amount for i in self.items if D(i.tax_rate) == 0), Decimal("0.00"))
        return (base * D(self.global_tax_rate)).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

    def total_tax(self) -> Decimal:
        return (self.item_tax_total() + self.global_tax_value()).quantize(TWOPLACES)

    def total(self) -> Decimal:
        total = self.subtotal() - self.discount_value() + D(self.shipping) + self.total_tax()
        return total.quantize(TWOPLACES, rounding=ROUND_HALF_UP)


# -----------------------------
# Rendering
# -----------------------------

class InvoiceRenderer:
    def __init__(self, inv: Invoice):
        self.inv = inv
        fonts = try_register_unicode_fonts(Path.cwd())
        self.font = fonts["regular"]
        self.font_bold = fonts["bold"]
        if not fonts.get("supports_unicode", False) and "₹" in self.inv.currency_symbol:
            self.inv.currency_symbol = "Rs."

        self.styles = getSampleStyleSheet()
        self._build_styles()

    def _build_styles(self):
        # Base styles
        self.styles.add(ParagraphStyle(
            name="TitleX",
            fontName=self.font_bold,
            fontSize=20,
            leading=24,
        ))
        self.styles.add(ParagraphStyle(
            name="H2",
            fontName=self.font_bold,
            fontSize=10.5,
            leading=13,
        ))
        self.styles.add(ParagraphStyle(
            name="BodyX",
            fontName=self.font,
            fontSize=9,
            leading=12,
        ))
        self.styles.add(ParagraphStyle(
            name="SmallX",
            fontName=self.font,
            fontSize=8.5,
            leading=11,
        ))
        self.styles.add(ParagraphStyle(
            name="RightX",
            fontName=self.font,
            fontSize=9,
            leading=12,
            alignment=TA_RIGHT,
        ))
        self.styles.add(ParagraphStyle(
            name="RightBoldX",
            fontName=self.font_bold,
            fontSize=9,
            leading=12,
            alignment=TA_RIGHT,
        ))
        self.styles.add(ParagraphStyle(
            name="CenterX",
            fontName=self.font,
            fontSize=9,
            leading=12,
            alignment=TA_CENTER,
        ))

    def _party_html(self, p: Party) -> str:
        lines = [f"<b>{safe_br(p.name)}</b>"]
        for a in p.address_lines:
            lines.append(safe_br(a))
        for e in p.extra:
            lines.append(safe_br(e))
        if p.phone:
            lines.append(f"Phone: {safe_br(p.phone)}")
        if p.email:
            lines.append(f"Email: {safe_br(p.email)}")
        if p.tax_id_value:
            lines.append(f"{safe_br(p.tax_id_label)}: {safe_br(p.tax_id_value)}")
        return "<br/>".join(lines)

    def build_pdf(self, out_path: Path):
        doc = SimpleDocTemplate(
            str(out_path),
            pagesize=A4,
            leftMargin=18 * mm,
            rightMargin=18 * mm,
            topMargin=16 * mm,
            bottomMargin=16 * mm,
            title=f"Invoice {self.inv.invoice_number}",
        )

        story: List[Any] = []

        story.extend(self._header_block())
        story.append(Spacer(1, 6 * mm))
        story.extend(self._billto_and_meta_block())
        story.append(Spacer(1, 7 * mm))
        story.append(self._items_table())
        story.append(Spacer(1, 6 * mm))
        story.append(self._totals_block())
        story.append(Spacer(1, 6 * mm))
        story.extend(self._notes_terms_bank_block())
        story.append(Spacer(1, 6 * mm))
        story.append(Paragraph("Thank you for your business.", self.styles["CenterX"]))

        doc.build(story)

    def _header_block(self) -> List[Any]:
        parts: List[Any] = []

        # 1) Top header row: INVOICE title on left, logo on right
        title = Paragraph("INVOICE", self.styles["TitleX"])
        
        logo_flowable = ""
        if self.inv.logo_path and Path(self.inv.logo_path).exists():
            # Set width with preserveAspectRatio to avoid distortion
            logo_flowable = Image(self.inv.logo_path, width=70 * mm, height=28 * mm, kind='proportional')

        header_tbl = Table([[title, logo_flowable]], colWidths=[110 * mm, 75 * mm])
        header_tbl.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (0, 0), "LEFT"),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))

        parts.append(header_tbl)
        parts.append(Spacer(1, 3 * mm))

        # 2) Seller details BELOW the header row (can wrap safely, no KeepTogether)
        parts.append(Paragraph(self._party_html(self.inv.seller), self.styles["BodyX"]))
        parts.append(Spacer(1, 4 * mm))

        # Divider line
        parts.append(HRFlowable(width="100%", thickness=1, color=colors.black))

        return parts


    def _billto_and_meta_block(self) -> List[Any]:
        bill_to = Paragraph("<b>BILL TO</b><br/>" + self._party_html(self.inv.buyer), self.styles["BodyX"])

        meta_rows = [
            ["Invoice #", safe_br(self.inv.invoice_number)],
            ["Invoice date", self.inv.invoice_date.isoformat()],
            ["Due date", self.inv.due_date.isoformat()],
            ["Payment terms", safe_br(self.inv.payment_terms)],
        ]
        if self.inv.purchase_order:
            meta_rows.append(["PO #", safe_br(self.inv.purchase_order)])
        if self.inv.place_of_supply:
            meta_rows.append(["Place of supply", safe_br(self.inv.place_of_supply)])

        meta_tbl = Table(meta_rows, colWidths=[32 * mm, 53 * mm])
        meta_tbl.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), self.font_bold),
            ("FONTNAME", (1, 0), (1, -1), self.font),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
        ]))

        outer = Table([[bill_to, meta_tbl]], colWidths=[105 * mm, 80 * mm])
        outer.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOX", (0, 0), (0, 0), 0.5, colors.lightgrey),
            ("BOX", (1, 0), (1, 0), 0.5, colors.lightgrey),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))

        return [outer]

    def _items_table(self) -> Table:
        headers = ["Description", "Qty", "Unit", "Unit Price", "Amount", "Tax"]

        data: List[List[Any]] = [headers]
        for it in self.inv.items:
            desc = it.description
            if it.sku:
                desc = f"{desc}<br/><font size=8 color='#555555'>SKU: {safe_br(it.sku)}</font>"

            data.append([
                Paragraph(desc, self.styles["BodyX"]),
                Paragraph(str(it.quantity), self.styles["RightX"]),
                Paragraph(safe_br(it.unit), self.styles["BodyX"]),
                Paragraph(money(it.unit_price, self.inv.currency_symbol), self.styles["RightX"]),
                Paragraph(money(it.amount, self.inv.currency_symbol), self.styles["RightX"]),
                Paragraph(money(it.tax_amount, self.inv.currency_symbol), self.styles["RightX"]),
            ])

        tbl = Table(
            data,
            colWidths=[78 * mm, 12 * mm, 14 * mm, 28 * mm, 28 * mm, 22 * mm],
            repeatRows=1
        )
        tbl.setStyle(TableStyle([
            # Header
            ("FONTNAME", (0, 0), (-1, 0), self.font_bold),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("ALIGN", (1, 0), (-1, 0), "RIGHT"),
            ("ALIGN", (0, 0), (0, 0), "LEFT"),
            # Body
            ("FONTNAME", (0, 1), (-1, -1), self.font),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ("ALIGN", (0, 1), (0, -1), "LEFT"),
            # Grid + padding
            ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        return tbl

    def _totals_block(self) -> Table:
        rows: List[List[Any]] = []

        rows.append(["Subtotal", money(self.inv.subtotal(), self.inv.currency_symbol)])

        disc = self.inv.discount_value()
        if disc > 0:
            rows.append(["Discount", money(-disc, self.inv.currency_symbol)])

        if D(self.inv.shipping) != 0:
            rows.append(["Shipping", money(D(self.inv.shipping), self.inv.currency_symbol)])

        item_tax = self.inv.item_tax_total()
        global_tax = self.inv.global_tax_value()

        if item_tax > 0:
            rows.append(["Item taxes", money(item_tax, self.inv.currency_symbol)])
        if global_tax > 0:
            rows.append(["Tax", money(global_tax, self.inv.currency_symbol)])

        rows.append(["Total", money(self.inv.total(), self.inv.currency_symbol)])

        tbl = Table(rows, colWidths=[40 * mm, 40 * mm])
        tbl.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),

            ("FONTNAME", (0, 0), (-1, -2), self.font),
            ("FONTNAME", (0, -1), (-1, -1), self.font_bold),
            ("BACKGROUND", (0, -1), (-1, -1), colors.whitesmoke),

            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ]))

        # Right-align totals by wrapping in a 2-col layout
        wrapper = Table([[ "", tbl ]], colWidths=[105 * mm, 80 * mm])
        wrapper.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
        return wrapper

    def _notes_terms_bank_block(self) -> List[Any]:
        blocks: List[Any] = []

        if self.inv.notes:
            blocks.append(Paragraph("<b>Notes</b>", self.styles["H2"]))
            blocks.append(Spacer(1, 2 * mm))
            blocks.append(Paragraph(safe_br(self.inv.notes), self.styles["BodyX"]))
            blocks.append(Spacer(1, 4 * mm))

        if self.inv.terms_and_conditions:
            blocks.append(Paragraph("<b>Terms & Conditions</b>", self.styles["H2"]))
            blocks.append(Spacer(1, 2 * mm))
            blocks.append(Paragraph(safe_br(self.inv.terms_and_conditions), self.styles["BodyX"]))
            blocks.append(Spacer(1, 4 * mm))

        if self.inv.bank_details:
            blocks.append(Paragraph("<b>Bank / Payment Details</b>", self.styles["H2"]))
            blocks.append(Spacer(1, 2 * mm))
            lines = "<br/>".join([f"{safe_br(k)}: {safe_br(v)}" for k, v in self.inv.bank_details.items()])
            blocks.append(Paragraph(lines, self.styles["BodyX"]))

        return blocks


# -----------------------------
# Example Usage
# -----------------------------

def build_sample_invoice() -> Invoice:
    inv = Invoice(
        invoice_number="INV-2026-0001",
        invoice_date=date.today(),
        due_date=date.today(),
        currency_symbol="₹",
        seller=Party(
            name="ACME Solutions Pvt. Ltd.",
            address_lines=["123 Business Park, Phase 2", "Chandigarh, India 160017"],
            phone="+91-98765-43210",
            email="billing@acme.example",
            tax_id_label="GSTIN",
            tax_id_value="06ABCDE1234F1Z5",
            extra=["acme.example"],
        ),
        buyer=Party(
            name="Client Company Ltd.",
            address_lines=["45 Client Street", "Gurugram, India 122001"],
            phone="+91-99999-11111",
            email="ap@client.example",
            tax_id_label="GSTIN",
            tax_id_value="07PQRSX5678L1Z2",
        ),
        purchase_order="PO-88421",
        place_of_supply="Haryana",
        payment_terms="Net 15",
        notes="Please review the invoice and pay by the due date.\nFor questions, email billing@acme.example.",
        terms_and_conditions="1) Late payments may incur a fee.\n2) Goods once sold are not returnable.",
        bank_details={
            "Account Name": "ACME Solutions Pvt. Ltd.",
            "Account Number": "1234567890",
            "IFSC": "HDFC0001234",
            "Bank": "HDFC Bank",
            "UPI": "acme@upi",
        },
        shipping=Decimal("250.00"),
        discount_rate=Decimal("0.05"),
        global_tax_rate=Decimal("0.18"),
        items=[
            LineItem("Monthly subscription - Workforce Analytics (Feb 2026)", D("1"), D("25000.00"), unit="service"),
            LineItem("Implementation support - 10 hours", D("10"), D("1500.00"), unit="hrs"),
            LineItem("On-site training (2 sessions) - includes materials", D("2"), D("8000.00"), unit="session"),
            LineItem("Hardware accessory pack", D("3"), D("1200.00"), unit="pcs", tax_rate=Decimal("0.12")),
        ],
    )
    return inv


def main():
    invoice = build_sample_invoice()
    out = Path.cwd() / f"invoice_{invoice.invoice_number}.pdf"
    InvoiceRenderer(invoice).build_pdf(out)
    print(f"Generated: {out}")


if __name__ == "__main__":
    main()
