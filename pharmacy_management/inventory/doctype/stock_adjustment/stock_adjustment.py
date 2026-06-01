import frappe
from frappe.model.document import Document

class StockAdjustment(Document):
    def validate(self):
        self.calculate_totals()

    def calculate_totals(self):
        total_qty = sum(item.qty for item in self.items)
        total_value = sum((item.qty or 0) * (item.rate or 0) for item in self.items)
        self.total_qty = total_qty
        self.total_value = total_value

    def on_submit(self):
        self.create_stock_entry()

    def create_stock_entry(self):
        se = frappe.new_doc("Stock Entry")
        se.stock_entry_type = "Material Issue"
        se.posting_date = self.posting_date
        for item in self.items:
            se.append("items", {
                "item_code": item.medicine,
                "qty": item.qty,
                "s_warehouse": self.warehouse,
                "batch_no": item.batch_no,
                "basic_rate": item.rate,
            })
        se.insert(ignore_permissions=True)
        se.submit()
