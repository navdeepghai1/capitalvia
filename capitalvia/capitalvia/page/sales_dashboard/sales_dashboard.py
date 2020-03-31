'''
    Developer Navdeep
    Email navdeepghai1@gmail.com
'''
from __future__ import unicode_literals
import frappe
from frappe import _
import re
from erpnext.accounts.report.gross_profit.gross_profit import execute
from capitalvia.dashboards.dashboard import get_period_list

from six import itervalues
from calendar import monthrange

from frappe.utils import flt
import randomcolor

def get_data(filters=None):
    columns, results  = execute(filters)
    months = get_period_list(filters, "Monthly")
    years = get_period_list(filters, "Yearly")
    conditions = get_conditions(filters)
    monthly_data_map = frappe._dict()
    yearly_data_map  = frappe._dict()

    monthly_data_map = frappe._dict()
    yearly_data_map = frappe._dict()
    random_controller = randomcolor.RandomColor()
    for item in frappe.db.sql("""SELECT `tabSales Invoice`.name, `tabSales Invoice`.net_total,
                    `tabSales Invoice`.grand_total,  `tabSales Team`.sales_person,
                    `tabSales Invoice`.posting_date,
                    `tabSales Team`.allocated_amount, `tabSales Team`.allocated_percentage
                    FROM `tabSales Invoice`
                    INNER JOIN `tabSales Team` ON `tabSales Invoice`.name = `tabSales Team`.parent
                WHERE
                    `tabSales Invoice`.docstatus = 1 AND `tabSales Team`.parenttype = 'Sales Invoice'
                    %s
        """%(conditions), as_dict=True):
        sales_person = item.sales_person or "Other"
        monthly_data_map.setdefault(sales_person, init_sales_person_data(months))
        yearly_data_map.setdefault(sales_person, init_sales_person_data(years))

        update_data(monthly_data_map, sales_person, item)
        update_data(yearly_data_map, sales_person, item)

    yearly_labels, yearly_data, yearly_options = process_and_get_data("Yearly Sales Person Data", yearly_data_map, years, random_controller)
    monthly_labels, monthly_data, monthly_options = process_and_get_data("Monthly Sales Person Data", monthly_data_map, months, random_controller)

    # Reverse to get best sales person records at first
    yearly_data = sorted(yearly_data, key=lambda i: i['total'], reverse=True)
    monthly_data = sorted(monthly_data, key=lambda i: i['total'], reverse=True)

    data = frappe._dict({
        "yearly_data": [yearly_labels,
            yearly_data if(len(yearly_data) <= 10) else yearly_data[:9], yearly_options],
        "monthly_data": [monthly_labels,
            monthly_data if(len(monthly_data) <= 10) else monthly_data[:9], monthly_options],
    })
    return data




def process_and_get_data(title, data_map, period_list, random_controller):
    labels = [m.get("label") for m in period_list]
    data  = []
    options = {
		"responsive": True,
		"legend": {
			"position": 'top',
		},
		"title": {
			"display": True,
			"text": _(title)
		}
	}
    for sales_person, date_wise_data in data_map.items():
        dataset = frappe._dict({
            "label": sales_person,
            "total": 0.0,
            "data": [],
            "backgroundColor": [],
            "borderColor": "white",
            "borderWidth":1
        })
        color = random_controller.generate()[0]
        for period in period_list:
            key = (period.from_date, period.to_date)
            dataset['total'] += flt(date_wise_data[key])
            dataset.data.append(date_wise_data[key])
            dataset.backgroundColor.append(color)
        data.append(dataset)

    return labels, data, options

# UPDATE DATA
def update_data(data, sales_person, item):
    data[sales_person]['total'] += flt(item.net_total)
    for from_to_date in data[sales_person]:
        if(from_to_date == 'total'):
            continue
        elif(item.posting_date >= from_to_date[0]
                and item.posting_date <= from_to_date[1]):
            data[sales_person][from_to_date] += flt(item.net_total)


# INIT SALES PERSON DATA
def init_sales_person_data(period_list):
    temp = frappe._dict({"total": 0.0})
    for period in period_list:
        temp[(period.from_date, period.to_date)] = 0.0
    return temp

def get_conditions(filters):
    conditions = ""
    if filters.get("company"):
        conditions += " AND `tabSales Invoice`.company='%s' "%(filters.get("company"))
    if(filters.get("from_date") and filters.get("to_date")):
        conditions += " AND `tabSales Invoice`.posting_date BETWEEN '%s' AND '%s' "%(
                            filters.get("from_date"), filters.get("to_date"))
    return conditions
