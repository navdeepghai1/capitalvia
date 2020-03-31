'''
    Developer Navdeep
    Email navdeepghai1@gmail.com
'''
from __future__ import unicode_literals

import frappe
from frappe import _
import json
from six import string_types, itervalues
from frappe.modules import get_module_path, scrub
import os
import randomcolor
import re
from past.builtins import cmp
import functools
import erpnext
from erpnext.accounts.utils import get_fiscal_year
from erpnext.accounts.report.utils import get_currency, convert_to_presentation_currency
from frappe.utils import (flt, cint, getdate, get_first_day, add_months, add_days, formatdate, datetime, date_diff)

from calendar import monthrange

APP_NAME = "capitalvia"

@frappe.whitelist()
def execute(args):
    if(args and isinstance(args, string_types)):
        args = json.loads(args)
    args = frappe._dict(args)

    page = frappe.get_doc("Page", args.get("page_name"))
    del args['page_name']
    page_name = scrub(page.name)
    file_path = os.path.join(get_module_path(page.module), 'page', page_name, "%s.py"%(page_name))
    if(os.path.exists(file_path)):
        path = ".".join([APP_NAME, scrub(page.module), 'page', page_name, "%s"%(page_name)])
        module = frappe.get_module(path)
        if(hasattr(module, "get_data")):
            return module.get_data(args)
    else:
        frappe.msgprint(_("Please create controller with same name of page."))

    # Return default response
    return fapppe._dict()

def get_period_list(filters, periodicity, accumulated_values=False):
    """Get a list of dict {"from_date": from_date, "to_date": to_date, "key": key, "label": label}
    	Periodicity can be (Yearly, Quarterly, Monthly)"""

    # start with first day, so as to avoid year to_dates like 2-April if ever they occur]
    year_start_date = getdate(filters.get("from_date"))
    year_end_date = getdate(filters.get("to_date"))
    company = filters.get("company")
    months_to_add = cint({
    	"Yearly": 12,
    	"Half-Yearly": 6,
    	"Quarterly": 3,
    	"Monthly": 1
    }[periodicity])

    period_list = []

    starting_date = year_start_date
    months = get_months_frequency(year_start_date, year_end_date)
    r =  months//months_to_add
    if(not (months/months_to_add).is_integer()):
        r += 1

    for i in range(r):
        period = frappe._dict({
        	"from_date": starting_date
        })

        to_date = add_months(starting_date, months_to_add)
        if to_date == get_first_day(to_date):
        	# if to_date is the first day, get the last day of previous month
        	to_date = add_days(to_date, -1)

        starting_date = getdate(to_date)

        if to_date <= year_end_date:
            # the normal case
            period.to_date = to_date
        else:
            # if a fiscal year ends before a 12 month period
            period.to_date = year_end_date

        #period.to_date_fiscal_year = get_fiscal_year(period.to_date, company=company)[0]
        #period.from_date_fiscal_year_start_date = get_fiscal_year(period.from_date, company=company)[1]
        period_list.append(period)
        if period.to_date == year_end_date:
        	break

    # common processing
    for opts in period_list:
    	key = opts["to_date"].strftime("%b_%Y").lower()
    	if periodicity == "Monthly" and not accumulated_values:
    		label = formatdate(opts["to_date"], "MMM YYYY")
    	else:
    		if not accumulated_values:
    			label = get_label(periodicity, opts["from_date"], opts["to_date"])
    		else:
    			if reset_period_on_fy_change:
    				label = get_label(periodicity, opts.from_date_fiscal_year_start_date, opts["to_date"])
    			else:
    				label = get_label(periodicity, period_list[0].from_date, opts["to_date"])

    	opts.update({
    		"key": key.replace(" ", "_").replace("-", "_"),
    		"label": label,
    		"year_start_date": year_start_date,
    		"year_end_date": year_end_date
    	})

    return period_list

def get_months_frequency(start_date, end_date):
	diff = (12 * end_date.year + end_date.month) - (12 * start_date.year + start_date.month)
	return diff + 1

def get_label(periodicity, from_date, to_date):
    if periodicity == "Yearly":
        if formatdate(from_date, "YYYY") == formatdate(to_date, "YYYY"):
            label = formatdate(from_date, "YYYY")
        else:
            label = formatdate(from_date, "YYYY") + "-" + formatdate(to_date, "YYYY")
    else:
        label = formatdate(from_date, "MMM YY") + "-" + formatdate(to_date, "MMM YY")

    return label
