/* Copyright 2016 LasLabs Inc.
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */


odoo.define('web_stock_picking.web_stock_picking_tour', function(require) {
    'use strict';
    
    var Tour = require('web.Tour');

    Tour.register({
        id: "web_stock_picking_main",
        name: "Check Website Stock Picking Functionality",
        path: "/web/stock/",
        mode: "test",
        steps: [
            {
                title: "Query box shows up",
                waitFor: "#search_query",
                element: "#search_query",
            },
            {
                title: "Stock picking header is visible",
                waitFor: "div.panel_heading:contains('Chic/IN/00004')",
                element: "div.panel_heading:contains('Chic/IN/00004')",
            }
        ],
    });

    Tour.register({
        id: "web_stock_picking_detail",
        name: "Check Website Stock Picking Detail Functionality",
        path: "/web/stock/1",
        mode: "test",
        steps: [
            {
                title: "Main Header Is Visible",
                waitFor: "h1:contains('WH/OUT/00001')",
                element: "h1:contains('WH/OUT/00001')",
            },
            {
                title: "Table Header Is Visible",
                waitFor: "th:contains('Done')",
                element: "th:contains('Done')",
            },
            {
                title: "Save Button Is Visible",
                waitFor: "input:contains('Save')",
                element: "input:contains('Save')",
            },
        ],
    });
    
});
