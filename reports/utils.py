from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from io import BytesIO

def generate_receipt_pdf(order):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Company header
    p.setFont("Helvetica-Bold", 16)
    p.drawString(1*inch, 10.5*inch, "Clean & Fresh Laundry")
    
    # Order details
    p.setFont("Helvetica", 10)
    p.drawString(1*inch, 10*inch, f"Receipt #: {order.order_number}")
    p.drawString(1*inch, 9.7*inch, f"Date: {order.registered_at.strftime('%Y-%m-%d %H:%M')}")
    p.drawString(1*inch, 9.4*inch, f"Customer: {order.customer.name}")
    
    # Items table
    y = 9*inch
    p.drawString(1*inch, y, "Item")
    p.drawString(4*inch, y, "Qty")
    p.drawString(5*inch, y, "Price")
    p.drawString(7*inch, y, "Total")
    
    y -= 0.3*inch
    for item in order.items.all():
        p.drawString(1*inch, y, item.clothing_type.name)
        p.drawString(4*inch, y, str(item.quantity))
        p.drawString(5*inch, y, f"${item.unit_price}")
        p.drawString(7*inch, y, f"${item.subtotal}")
        y -= 0.3*inch
    
    # Totals
    y -= 0.3*inch
    p.drawString(5*inch, y, "Subtotal:")
    p.drawString(7*inch, y, f"${order.total_amount - order.express_charge}")
    
    if order.express_service:
        y -= 0.3*inch
        p.drawString(5*inch, y, "Express Charge:")
        p.drawString(7*inch, y, f"${order.express_charge}")
    
    y -= 0.3*inch
    p.setFont("Helvetica-Bold", 12)
    p.drawString(5*inch, y, "TOTAL:")
    p.drawString(7*inch, y, f"${order.total_amount}")
    
    p.save()
    buffer.seek(0)
    return buffer