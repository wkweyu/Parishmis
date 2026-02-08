# -*- coding: utf-8 -*-
import frappe
import json
from frappe import _

@frappe.whitelist()
def initiate_stk_push(collection, amount, phone):
    settings = frappe.get_doc("M-Pesa Settings")
    if not settings.enabled:
        frappe.throw(_("M-Pesa is not enabled in M-Pesa Settings"))
        
    # Standard STK Push implementation logic would go here
    # 1. Get Access Token
    # 2. Prepare Payload
    # 3. Request Safaricom API
    
    # Returning a dummy success response for the UI to handle
    return {"ResponseCode": "0", "CustomerMessage": "Success"}

@frappe.whitelist(allow_guest=True)
def callback():
    data = json.loads(frappe.request.data)
    
    # Logic to parse M-Pesa Callback (Validation logic omitted for brevity as per typical boilerplate)
    # This usually involves parsing Body -> stkCallback -> CallbackMetadata -> Item
    
    res = data.get('Body', {}).get('stkCallback', {})
    result_code = res.get('ResultCode')
    checkout_id = res.get('CheckoutRequestID')
    
    if result_code == 0:
        # Success
        items = res.get('CallbackMetadata', {}).get('Item', [])
        amount = 0
        receipt = ""
        phone = ""
        
        for item in items:
            name = item.get('Name')
            value = item.get('Value')
            if name == 'Amount': amount = value
            if name == 'MpesaReceiptNumber': receipt = value
            if name == 'PhoneNumber': phone = str(value)
            
        # Create M-Pesa Transaction
        tx = frappe.new_doc("M-Pesa Transaction")
        tx.transaction_id = receipt
        tx.msisdn = phone
        tx.amount = amount
        tx.status = "Success"
        tx.transaction_time = frappe.utils.now_datetime()
        tx.insert(ignore_permissions=True)
        
        # Create Collection if found linked to checkout_id (In a real system, you'd store CheckoutID in a temp doc)
        # For simplicity, we create a generic Collection record if we can identify the parishioner by phone
        parishioner = frappe.db.get_value("Parishioner", {"phone": ["like", f"%{phone[-9:]}%"]}, "name")
        
        if parishioner:
            col = frappe.new_doc("Collection")
            col.parishioner = parishioner
            col.collection_date = frappe.utils.today()
            col.amount = amount
            col.mode_of_receipt = "M-Pesa"
            col.remarks = f"M-Pesa Receipt: {receipt}"
            col.insert(ignore_permissions=True)
            col.submit()
            
            # Link back
            tx.collection = col.name
            tx.save(ignore_permissions=True)

    return {"status": "ok"}
