"""
Invoice Generator Web App - Streamlit UI

Run locally:
  streamlit run app.py

Deploy:
  Push to GitHub and deploy via streamlit.io/cloud
"""

import streamlit as st
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
import base64

from invoice import (
    Invoice, Party, LineItem, InvoiceRenderer, D
)


def main():
    st.set_page_config(page_title="Invoice Generator", page_icon="📄", layout="wide")
    
    st.title("📄 Invoice Generator")
    st.markdown("Generate professional invoices for your business")
    
    # Initialize session state for line items
    if 'line_items' not in st.session_state:
        st.session_state.line_items = [{"description": "", "quantity": 1, "unit_price": 0.0, "unit": "pcs", "tax_rate": 0.0}]
    
    # ==================== CHECK FOR LOGO ====================
    # Look for logo file in project folder
    logo_path = None
    for logo_name in ["logo.png", "logo.jpg", "logo.jpeg", "company_logo.png", "company_logo.jpg"]:
        potential_logo = Path.cwd() / logo_name
        if potential_logo.exists():
            logo_path = potential_logo
            break
    
    if logo_path:
        st.info(f"🎨 Using company logo: {logo_path.name}")
    
    # Two column layout
    col1, col2 = st.columns([1, 1])
    
    # ==================== SELLER INFORMATION ====================
    with col1:
        st.subheader("🏢 Seller Information")
        seller_name = st.text_input("Company Name*", value="DAFUEL INNOVATION PVT. LTD.")
        seller_address1 = st.text_input("Address Line 2", value="Chandigarh, India 160017")
        
        s_col1, s_col2 = st.columns(2)
        with s_col1:
            seller_phone = st.text_input("Phone", value="+91-89888 04848")
            seller_gstin = st.text_input("GSTIN", value="04AALCD7751R1ZX")
        with s_col2:
            seller_email = st.text_input("Email", value="dafuelinnovationspvtltd@gmail.com")
            seller_website = st.text_input("Website (optional)", value="www.truyerba.in")
    
    # ==================== BUYER INFORMATION ====================
    with col2:
        st.subheader("👤 Bill To")
        buyer_name = st.text_input("Client Name*", value="Client Company Ltd.")
        buyer_address1 = st.text_input("Client Address Line 1*", value="45 Client Street")
        buyer_address2 = st.text_input("Client Address Line 2", value="Gurugram, India 122001")
        
        b_col1, b_col2 = st.columns(2)
        with b_col1:
            buyer_phone = st.text_input("Client Phone", value="+91-99999-11111")
            buyer_gstin = st.text_input("Client GSTIN", value="07PQRSX5678L1Z2")
        with b_col2:
            buyer_email = st.text_input("Client Email", value="ap@client.example")
    
    st.divider()
    
    # ==================== INVOICE META ====================
    st.subheader("📋 Invoice Details")
    meta_col1, meta_col2, meta_col3 = st.columns(3)
    
    with meta_col1:
        invoice_number = st.text_input("Invoice Number*", value=f"INV-{date.today().year}-0001")
        invoice_date = st.date_input("Invoice Date", value=date.today())
    
    with meta_col2:
        due_date = st.date_input("Due Date", value=date.today() + timedelta(days=15))
        payment_terms = st.text_input("Payment Terms", value="Net 15")
    
    with meta_col3:
        purchase_order = st.text_input("PO Number (optional)", value="")
        place_of_supply = st.text_input("Place of Supply", value="Haryana")
    
    st.divider()
    
    # ==================== LINE ITEMS ====================
    st.subheader("🛒 Items / Services")
    
    # Display existing line items
    for idx, item in enumerate(st.session_state.line_items):
        with st.expander(f"Item {idx + 1}: {item['description'][:30] if item['description'] else 'New Item'}", expanded=True):
            cols = st.columns([3, 1, 1, 1.5, 1, 0.5])
            
            with cols[0]:
                item['description'] = st.text_input(
                    "Description*",
                    value=item['description'],
                    key=f"desc_{idx}",
                    placeholder="Enter product/service name"
                )
            
            with cols[1]:
                item['quantity'] = st.number_input(
                    "Quantity*",
                    min_value=0.0,
                    value=float(item['quantity']),
                    step=1.0,
                    key=f"qty_{idx}"
                )
            
            with cols[2]:
                item['unit'] = st.selectbox(
                    "Unit",
                    options=["pcs", "hrs", "days", "service", "kg", "box", "unit"],
                    index=["pcs", "hrs", "days", "service", "kg", "box", "unit"].index(item['unit']) if item['unit'] in ["pcs", "hrs", "days", "service", "kg", "box", "unit"] else 0,
                    key=f"unit_{idx}"
                )
            
            with cols[3]:
                item['unit_price'] = st.number_input(
                    "Unit Price (₹)*",
                    min_value=0.0,
                    value=float(item['unit_price']),
                    step=100.0,
                    key=f"price_{idx}"
                )
            
            with cols[4]:
                item['tax_rate'] = st.number_input(
                    "Tax Rate (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(item['tax_rate'] * 100),
                    step=1.0,
                    key=f"tax_{idx}"
                ) / 100.0
            
            with cols[5]:
                if st.button("🗑️", key=f"del_{idx}", help="Delete this item"):
                    if len(st.session_state.line_items) > 1:
                        st.session_state.line_items.pop(idx)
                        st.rerun()
    
    # Add item button
    if st.button("➕ Add Another Item"):
        st.session_state.line_items.append({
            "description": "",
            "quantity": 1,
            "unit_price": 0.0,
            "unit": "pcs",
            "tax_rate": 0.0
        })
        st.rerun()
    
    st.divider()
    
    # ==================== ADDITIONAL DETAILS ====================
    add_col1, add_col2 = st.columns(2)
    
    with add_col1:
        st.subheader("💰 Additional Charges")
        shipping = st.number_input("Shipping Charges (₹)", min_value=0.0, value=0.0, step=50.0)
        discount_rate = st.number_input("Discount (%)", min_value=0.0, max_value=100.0, value=0.0, step=1.0) / 100.0
        global_tax_rate = st.number_input("Global Tax Rate (%) - Applied to items with 0% tax", min_value=0.0, max_value=100.0, value=18.0, step=1.0) / 100.0
    
    with add_col2:
        st.subheader("📝 Notes & Terms")
        notes = st.text_area("Notes", value="Please review the invoice and pay by the due date.", height=100)
        terms = st.text_area("Terms & Conditions", value="1) Late payments may incur a fee.\n2) Goods once sold are not returnable.", height=100)
    
    # ==================== BANK DETAILS ====================
    with st.expander("🏦 Bank / Payment Details (Optional)"):
        bank_enabled = st.checkbox("Include bank details", value=True)
        if bank_enabled:
            bank_col1, bank_col2 = st.columns(2)
            with bank_col1:
                bank_account_name = st.text_input("Account Name", value="ACME Solutions Pvt. Ltd.")
                bank_account_number = st.text_input("Account Number", value="1234567890")
                bank_ifsc = st.text_input("IFSC Code", value="HDFC0001234")
            with bank_col2:
                bank_name = st.text_input("Bank Name", value="HDFC Bank")
                bank_upi = st.text_input("UPI ID", value="acme@upi")
    
    st.divider()
    
    # ==================== GENERATE INVOICE ====================
    if st.button("🎯 Generate Invoice PDF", type="primary", use_container_width=True):
        # Validate required fields
        if not seller_name or not buyer_name or not invoice_number:
            st.error("⚠️ Please fill in all required fields marked with *")
            return
        
        if not any(item['description'] and item['quantity'] > 0 and item['unit_price'] > 0 for item in st.session_state.line_items):
            st.error("⚠️ Please add at least one valid item with description, quantity, and price")
            return
        
        with st.spinner("Generating invoice..."):
            try:
                # Build seller party
                seller_addresses = [seller_address1]
                
                seller_extra = []
                if seller_website:
                    seller_extra.append(seller_website)
                
                seller = Party(
                    name=seller_name,
                    address_lines=seller_addresses,
                    phone=seller_phone,
                    email=seller_email,
                    tax_id_label="GSTIN",
                    tax_id_value=seller_gstin,
                    extra=seller_extra
                )
                
                # Build buyer party
                buyer_addresses = [buyer_address1]
                if buyer_address2:
                    buyer_addresses.append(buyer_address2)
                
                buyer = Party(
                    name=buyer_name,
                    address_lines=buyer_addresses,
                    phone=buyer_phone,
                    email=buyer_email,
                    tax_id_label="GSTIN",
                    tax_id_value=buyer_gstin
                )
                
                # Build line items
                items = []
                for item in st.session_state.line_items:
                    if item['description'] and item['quantity'] > 0:
                        items.append(LineItem(
                            description=item['description'],
                            quantity=D(item['quantity']),
                            unit_price=D(item['unit_price']),
                            unit=item['unit'],
                            tax_rate=D(item['tax_rate'])
                        ))
                
                # Build bank details
                bank_details = {}
                if bank_enabled:
                    if bank_account_name:
                        bank_details["Account Name"] = bank_account_name
                    if bank_account_number:
                        bank_details["Account Number"] = bank_account_number
                    if bank_ifsc:
                        bank_details["IFSC"] = bank_ifsc
                    if bank_name:
                        bank_details["Bank"] = bank_name
                    if bank_upi:
                        bank_details["UPI"] = bank_upi
                
                # Create invoice
                invoice = Invoice(
                    invoice_number=invoice_number,
                    invoice_date=invoice_date,
                    due_date=due_date,
                    currency_symbol="₹",
                    seller=seller,
                    buyer=buyer,
                    items=items,
                    shipping=D(shipping),
                    discount_rate=D(discount_rate),
                    global_tax_rate=D(global_tax_rate),
                    payment_terms=payment_terms,
                    purchase_order=purchase_order,
                    place_of_supply=place_of_supply,
                    notes=notes,
                    terms_and_conditions=terms,
                    bank_details=bank_details,
                    logo_path=str(logo_path) if logo_path else None
                )
                
                # Generate PDF
                output_path = Path.cwd() / f"invoice_{invoice.invoice_number}.pdf"
                InvoiceRenderer(invoice).build_pdf(output_path)
                
                # Read PDF and offer download
                with open(output_path, "rb") as pdf_file:
                    pdf_bytes = pdf_file.read()
                
                st.success(f"✅ Invoice generated successfully!")
                
                # Display summary
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Subtotal", f"₹{invoice.subtotal():,.2f}")
                with col_b:
                    st.metric("Total Tax", f"₹{invoice.total_tax():,.2f}")
                with col_c:
                    st.metric("Grand Total", f"₹{invoice.total():,.2f}")
                
                # Download button
                st.download_button(
                    label="⬇️ Download Invoice PDF",
                    data=pdf_bytes,
                    file_name=f"invoice_{invoice.invoice_number}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
            except Exception as e:
                st.error(f"❌ Error generating invoice: {str(e)}")
                import traceback
                st.code(traceback.format_exc())


if __name__ == "__main__":
    main()
