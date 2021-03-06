//With bootbox

String.prototype.format = function(args) {
    var reg;
    var result = this;
    if (arguments.length > 0) {
        if (arguments.length == 1 && typeof (args) == "object") {
            for (var key in args) {
                if(args.hasOwnProperty(key)) {
                    if(args[key]!=undefined){
                        reg = new RegExp("({" + key + "})", "g");
                        result = result.replace(reg, args[key]);
                    }
                }
            }
        }
        else {
            for (var i = 0; i < arguments.length; i++) {
                if (arguments[i] != undefined) {
                    reg = new RegExp("({[" + i + "]})", "g");
                    result = result.replace(reg, arguments[i]);
                }
            }
        }
    }
    return result;
};

bootbox.addLocale('zh_CN', {
    OK: '确定',
    CANCEL: '取消',
    CONFIRM: '确定'
});

$(document).ready(function () {
    $('[data-toggle="popover"]').popover({
        html: true, placement: "auto",
        viewport: {selector: 'body', padding: 5}
    })
});
$('body').on('click', function (e) {
    $('[data-toggle="popover"]').each(function () {
        //the 'is' for buttons that trigger popups
        //the 'has' for icons within a button that triggers a popup
        if (!$(this).is(e.target) && $(this).has(e.target).length === 0
                && $('.popover').has(e.target).length === 0) {
            $(this).popover('hide');
        }
    });
});

/* Hide a column of a table if all cells of the column is empty*/
$('table').each(function (a, tbl) {
    var currentTableRows = $(tbl).find('tbody tr').length;
    $(tbl).find('th').each(function (i) {
        var remove = 0;
        var currentTable = $(this).parents('table');

        var tds = currentTable.find('tr td:nth-child(' + (i + 1) + ')');
        tds.each(function () {
            if ($(this).html().trim() === '') remove++;
        });
        if (remove === currentTableRows) {
            $(this).hide();
            tds.hide();
        }
    });
});

$("input[name^='del-']").change(function(target){
    if (this.checked){
        $(this).parent().parent().addClass('delete-indicate') ;
    } else {
        $(this).parent().parent().removeClass('delete-indicate') ;
    }
})

function addInlineField(parent_id) {
    parent = $("#" + parent_id);
    $trs = parent.find(".inline-field");
    var prefix = parent_id + '-' + $trs.length;

    // Get template
    var $template = $($('.inline-field-template-' + parent_id).text());

    // Set form ID
    $template.attr('id', prefix);

    // Mark form that we just created
    $template.addClass('fresh');
    $template.removeClass('hide');
    // Fix form IDs
    $('[name]', $template).each(function (e) {
        var me = $(this);

        var id = me.attr('id');
        var name = me.attr('name');

        id = prefix + (id !== '' ? '-' + id : '');
        name = prefix + (name !== '' ? '-' + name : '');

        me.attr('id', id);
        me.attr('name', name);
    });

    $template.appendTo(parent);

    // Select first field
    $('input:first', $template).focus();

    // Apply styles
    faForm.applyGlobalStyles($template);
}

function MarkInvalidRowAction(id, status_id) {
    markRowAction(id, status_id, "mark_invalid_row_action_" + id, 'invalid');
}

function MarkShipRowAction(id, status_id) {
    markRowAction(id, status_id, "mark_ship_row_action_" + id, 'shipped');
}

function markRowAction(id, status_id, iconElem, message) {
    var icon = $("#" + iconElem), displayElem, errorMsg;

    function prepare_error_message(message) {
        icon.attr('class', 'fa fa-exclamation-triangle');
        icon.attr('style', 'color:red;cursor:help');
        icon.parent().attr('href', "#");
        icon.parent().tooltip({
            title: message,
            placement: 'top',
            trigger: 'hover'
        });
    }

    bootbox.confirm('Confirm to mark this sales order as ' + message + '?', function (result) {
        if (result == true) {
            icon.attr('class', 'fa fa-spin fa-spinner');
            $.ajax({
                url: '/api/sales_order/' + id + '?status_id=' + status_id,
                type: 'PUT',
                success: function (response) {
                    errorMsg = response.message;
                    if (response.status == 'success') {
                        icon.attr('class', 'glyphicon glyphicon-ok');
                        icon.fadeOut(5000);
                        displayElem = $("#ajax-message-success");
                    } else if (response.status == 'error') {
                        prepare_error_message(errorMsg);
                        displayElem = $("#ajax-message-error");
                    }
                    displayElem.html(errorMsg);
                    displayElem.show().delay(4000).fadeOut();
                },
                error: function (response) {
                    errorMsg = response.responseJSON.message;
                    prepare_error_message(errorMsg);
                    displayElem = $("#ajax-message-error");
                    displayElem.html(errorMsg);
                    displayElem.show().delay(4000).fadeOut();
                }
            });
        }
    });
}

