/*
  Developer navdeep
  Email navdeepghai1@gmail.com
*/

frappe.provide('capitalvia');

// add toolbar icon
$(document).bind('toolbar_setup', function() {
	frappe.app.name = "Capitalvia";
});
