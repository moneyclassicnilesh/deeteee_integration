import frappe
import json
import re

def drop_custom_field():

    deleted_documents = frappe.get_all("Deleted Document",filters={},fields=["name"])
    for row in deleted_documents:
        deleted_document_doc = frappe.get_doc("Deleted Document",row.get("name"))
        data = deleted_document_doc.get("data")
        if isinstance(data,str):
            data = json.loads(data)
        if data.get("dt") == "Sales Invoice":
            try:
                frappe.db.sql("""ALTER TABLE `tabSales Invoice` DROP COLUMN {0}""".format(data.get("fieldname")))
                print(f"{data.get('fieldname')} deleted")
            except Exception as e:
                print(e)


import frappe
import json
import re

def drop_custom_field():

    deleted_documents = frappe.get_all("Deleted Document",filters={},fields=["name"])
    for row in deleted_documents:
        deleted_document_doc = frappe.get_doc("Deleted Document",row.get("name"))
        data = deleted_document_doc.get("data")
        if isinstance(data,str):
            data = json.loads(data)
        if data.get("dt") == "Sales Invoice":
            try:
                frappe.db.sql("""ALTER TABLE `tabSales Invoice` DROP COLUMN {0}""".format(data.get("fieldname")))
                print(f"{data.get('fieldname')} deleted")
            except Exception as e:
                print(e)


def parse_address(address_display):
    if not address_display:
        return {
            "address_line1": "",
            "address_line2": "",
            "new_city": "",
            "gst_state": "",
            "gst_state_number": "",
            "pincode": "",
            "country": "",
            "phone": "",
            "email_id": ""
        }
    
    address_lines = [line.strip() for line in address_display.split("<br>") if line.strip()]
    
    address_info = {
        "address_line1": address_lines[0] if len(address_lines) > 0 else "",
        "address_line2": "",
        "new_city": "",
        "gst_state": "",
        "gst_state_number": "",
        "pincode": "",
        "country": "",
        "phone": "",
        "email_id": ""
    }

    if len(address_lines) > 1:
        if "State Code:" in address_lines[1] or "PIN:" in address_lines[1] or "Phone:" in address_lines[1] or "Email:" in address_lines[1]:
            address_info["new_city"] = address_lines[1] or ""
        else:
            address_info["address_line2"] = address_lines[1] or ""

    if len(address_lines) > 2:
        if "State Code:" in address_lines[2] or "PIN:" in address_lines[2] or "Phone:" in address_lines[2] or "Email:" in address_lines[2]:
            address_info["new_city"] = address_lines[1] or ""
        else:
            address_info["new_city"] = address_lines[2] or ""

    for line in address_lines:
        if "State Code:" in line:
            address_info["gst_state"] = line.split(",")[0].strip()
            address_info["gst_state_number"] = re.search(r'\d+', line).group() if re.search(r'\d+', line) else ""
        elif "PIN:" in line:
            address_info["pincode"] = re.search(r'\d+', line).group() if re.search(r'\d+', line) else ""
        elif "Phone:" in line:
            address_info["phone"] = re.search(r'\+\d+', line).group() if re.search(r'\+\d+', line) else ""
        elif "Email:" in line:
            address_info["email_id"] = line.split(":")[1].strip()
        elif "India" in line:
            address_info["country"] = "India"
        else:
            address_info["country"] = line

    return address_info

def create_address(address_display, row, name, address_type):
    try:
        address_info = parse_address(address_display)
        new_address = frappe.new_doc("Address")
        if address_type == "supplier":
            new_address.address_title = row.supplier
        else:
            new_address.address_title = name
        new_address.update(address_info)
        
        if address_type == "shipping":
            new_address.is_shipping_address = 1
            new_address.gstin = row.get("company_gstin")
        elif address_type == "billing":
            new_address.is_primary_address = 1
            new_address.gstin = row.get("company_gstin")
        elif address_type == "supplier":
            new_address.is_primary_address = 1
            new_address.gstin = row.get("supplier_gstin")
        new_address.append("links",{
            "link_doctype":"Supplier",
            "link_name":row.supplier
        })
        new_address.insert(ignore_permissions=True)
    except Exception as e:
        print(row.supplier)

def handle_addresses():
    pos = frappe.get_all("Purchase Order", filters={}, fields=["*"])
    
    for row in pos:
        # if row.shipping_address:
        #     if not frappe.db.exists("Address", row.shipping_address):
        #         create_address(row.shipping_address_display, row, row.shipping_address, "shipping")
        #     else:
        #         frappe.db.set_value("Address", row.shipping_address, "is_shipping_address", 1)

        # if row.billing_address:
        #     if not frappe.db.exists("Address", row.billing_address):
        #         create_address(row.billing_address_display, row, row.billing_address, "billing")
        #     else:
        #         frappe.db.set_value("Address", row.billing_address, "is_primary_address", 1)

        if row.supplier_address:
            if not frappe.db.exists("Address", {"address_title":row.supplier}):
                create_address(row.address_display, row, row.supplier_address, "supplier")
            else:
                frappe.db.set_value("Address", row.supplier_address, "is_primary_address", 1)