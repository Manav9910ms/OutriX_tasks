from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from datetime import datetime
import os
import re

# ====== CONFIGURATION ======
BASE_PATH = "/storage/emulated/0/Download"  # Save location on Android
CURRENCY = "INR"
COUNTER_FILE = os.path.join(BASE_PATH, "invoice_counter.txt")   # Tracks latest number
HISTORY_FILE = os.path.join(BASE_PATH, "invoice_history.txt")   # Tracks all numbers
# ===========================


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def sanitize_for_filename(text: str) -> str:
    text = text.strip().replace(" ", "_")
    return re.sub(r"[^A-Za-z0-9._-]", "_", text)


def read_counter():
    try:
        with open(COUNTER_FILE, "r") as f:
            content = f.read().strip()
            return int(content) if content else 0
    except (FileNotFoundError, ValueError):
        return 0


def write_counter(counter: int):
    tmp = COUNTER_FILE + ".tmp"
    with open(tmp, "w") as f:
        f.write(str(counter))
    os.replace(tmp, COUNTER_FILE)


def log_invoice_number(invoice_no: str):
    with open(HISTORY_FILE, "a") as f:
        f.write(invoice_no + "\n")


def get_next_invoice_number():
    last_counter = read_counter()
    counter = last_counter + 1
    write_counter(counter)
    invoice_no = f"INV-{counter:06d}"
    log_invoice_number(invoice_no)
    return invoice_no


def create_invoice(filename, company, client, invoice_no, items, tax_rate=0.18):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # Header
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 50, company)

    # Invoice details
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 100, f"Invoice #: {invoice_no}")
    c.drawString(50, height - 115, f"Date: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    c.drawString(50, height - 130, f"Billed To: {client}")

    # Table header (shaded)
    y = height - 170
    headers = ["Description", "Qty", "Unit Price", "Line Total"]
    c.setFillColor(colors.lightgrey)
    c.rect(50, y, 430, 20, fill=1)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(55, y + 5, headers[0])
    c.drawRightString(300, y + 5, headers[1])
    c.drawRightString(400, y + 5, headers[2])
    c.drawRightString(480, y + 5, headers[3])

    # Items
    y -= 25
    c.setFont("Helvetica", 12)
    subtotal = 0.0
    for desc, qty, price in items:
        line_total = qty * price
        subtotal += line_total
        c.drawString(55, y, str(desc))
        c.drawRightString(300, y, str(qty))
        c.drawRightString(400, y, f"{CURRENCY}{price:,.2f}")
        c.drawRightString(480, y, f"{CURRENCY}{line_total:,.2f}")
        y -= 20

    # Totals
    tax = subtotal * tax_rate
    grand_total = subtotal + tax
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(400, y - 10, "Subtotal:")
    c.drawRightString(480, y - 10, f"{CURRENCY}{subtotal:,.2f}")
    c.drawRightString(400, y - 30, f"Tax ({tax_rate*100:.0f}%):")
    c.drawRightString(480, y - 30, f"{CURRENCY}{tax:,.2f}")
    c.drawRightString(400, y - 50, "Grand Total:")
    c.drawRightString(480, y - 50, f"{CURRENCY}{grand_total:,.2f}")

    # Footer
    c.setFont("Helvetica", 10)
    c.drawCentredString(width / 2, 30, "Thank you for your business!")
    c.showPage()
    c.save()


if __name__ == "__main__":
    ensure_dir(BASE_PATH)

    company = input("Enter company name: ").strip()
    client = input("Enter client name: ").strip()
    invoice_no = get_next_invoice_number()

    items = []
    while True:
        desc = input("Item description (leave blank to finish): ").strip()
        if not desc:
            break
        qty = int(input("Quantity: "))
        price = float(input("Unit price: "))
        items.append((desc, qty, price))

    try:
        tax_input = input("Tax rate in % (default 18): ").strip()
        tax_rate = float(tax_input) / 100 if tax_input else 0.18
    except ValueError:
        tax_rate = 0.18

    safe_client = sanitize_for_filename(client)
    filename = f"{invoice_no}_{safe_client}.pdf"
    save_path = os.path.join(BASE_PATH, filename)

    create_invoice(save_path, company, client, invoice_no, items, tax_rate)
    print(f"✅ Invoice saved to: {save_path}")
    print(f"🗂 Latest invoice number stored in: {COUNTER_FILE}")
    print(f"📜 Full history logged in: {HISTORY_FILE}")