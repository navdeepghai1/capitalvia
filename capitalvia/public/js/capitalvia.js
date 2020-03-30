/*
Developer Navdeep
Email navdeepghai1@gmail.com
*/

frappe.provide("capitalvia");

capitalvia.MakeBarChart = Class.extend({
  init: function(args){
    $.extend(this, args);
    this.make();
    this.canvas_tags = {};
    this.charts = {};
  },
  make: function(){
    this.$wrapper = $(".layout-main-section");
    this.make_filters();
  },
  make_filters: function(){
    this.filter_controller =  new capitalvia.Filters({
      "filters": this.filters,
      "page": this.page,
      "wrapper": this.wrapper,
      "parent": this
    });
  },
  get_data: function(values){
    if(!this.filter_controller.validate_filter()){
      return;
    }
    let me = this;
    $.extend(values, {
      "page_name": me.page_name
    });
    frappe.call({
        "method": "capitalvia.dashboards.dashboard.execute",
        "args": {"args": values},
        "callback": function(res){
          if(!(res && res.message))
            return false;
          // handle response by end user callback
          if(me.callback){
            me.callback(res, me);
          }else{
            // handle and make chart
            // HACK IT
          }
        }
    });
  },
  render_chart: function(label, canvas, labels, data, options){
    if(label in this.charts){
        this.charts[label].destroy();
    }
    this.charts[label] = new Chart(canvas, {
      "type": "bar",
      "data":{
        "labels": labels,
        "datasets": data
      },
      "options": options
     });

  },
  make_canvas_tag: function(label, col, width, height){
     if(label in this.canvas_tags){
         return document.getElementById(this.canvas_tags[label].find("canvas").attr("id"));
     }
     let $canvas = $(`<div class="${col}">
        <canvas class="chartjs" id="${frappe.utils.get_random(10)}"  width="${width}" height="${height}"></canvas>
        </div>`).appendTo(this.$wrapper);
     this.canvas_tags[label] = $canvas;
     return document.getElementById($canvas.find("canvas").attr("id"));
 },

});

capitalvia.Filters = Class.extend({
  init: function(args){
    $.extend(this, args);
    this.values = {};
    this.make()
  },
  make: function(){
    let me = this;
    let filters = this.filters || [];
    for(var i=0;i<filters.length; i++){
      this.make_filter(filters[i]);
    }
  },
  make_filter: function(field_df){
    let filter = this.page.add_field(field_df);
    this.init_handler(filter);
  },
  init_handler: function(filter){
    var me = this;
    this.values[filter.df.fieldname] = filter.value;
    filter.$input.on("change", function(event){
      let fieldname = $(this).attr("data-fieldname");
      me.values[fieldname] = me.page.fields_dict[fieldname].get_value();
      me.parent.get_data(me.values);
    });
  },
  validate_filter: function(){
    let flag = true;
    for(var fieldname in this.page.fields_dict){
      let field = this.page.fields_dict[fieldname];
      if(field.df.reqd && !this.values[fieldname]){
        frappe.msgprint(__(frappe.utils.format("{0} is required", [field.df.label])));
        flag = false;
        break;
      }
    }
    return flag;
  }
});
