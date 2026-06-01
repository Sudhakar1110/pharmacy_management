import frappe
from frappe.model.document import Document

class StockTransfer(Document):
    def validate(self):
        if self.from_warehouse == self.to_warehouse:
            frappe.throw("From and To Warehouse cannot be the same")
        self.total_qty = sum(item.qty or 0 for item in self.items)

    def on_submit(self):
        se = frappe.new_doc("Stock Entry")
        se.stock_entry_type = "Material Transfer"
        se.posting_date = self.posting_date
        for item in self.items:
            se.append("items", {
                "item_code": item.medicine,
                "qty": item.qty,
                "s_warehouse": self.from_warehouse,
                "t_warehouse": self.to_warehouse,
                "batch_no": item.batch_no,
            })
        se.insert(ignore_permissions=True)
        se.submit()
