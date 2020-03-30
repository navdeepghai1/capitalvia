frappe.pages['sales-dashboard'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Sales Dashboard',
		single_column: true
	});

	let args = {
		"filters":[{
				"fieldname": "company", "fieldtype": "Link", "options": "Company",
				"default": frappe.sys_defaults.company, "reqd":1, "label": __("Sales Person")
		},{
				"fieldname": "from_date", "fieldtype": "Date", "label":__("From Date"), "reqd": 1
		},{
				"fieldname": "to_date", "fieldtype": "Date", "label": __("To Date"), "reqd": 1,
		},{
			  "fieldname": "group_by", "fieldtype": "Select", "options": ["Sales Person"],
				"default": "Sales Person", "reqd": 1, "read_only":1, "label": __("Group By")
		}],
		"page": page,
		"wrapper": wrapper,
		"page_name": "sales-dashboard",
		"title": __("Top 10 Sales Person"),
		"callback": function(res, chart){
			if(res.message){
				var yearly_data = res.message.yearly_data;
				var monthly_data = res.message.monthly_data;
				var yearly_canvas = chart.make_canvas_tag("yearly_canvas", "col-md-6");
				var monthly_canvas = chart.make_canvas_tag("monthly_canvas", "col-md-12	");
				chart.render_chart("yearly_canvas", yearly_canvas, yearly_data[0], yearly_data[1], yearly_data[2]);
				chart.render_chart("monthly_canvas", monthly_canvas, monthly_data[0], monthly_data[1], monthly_data[2]);
			}
		}
	};

	window.page = page;
	new capitalvia.MakeBarChart(args)

}
