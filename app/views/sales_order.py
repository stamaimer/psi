# coding=utf-8
from datetime import datetime

from app import app_provider
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.model import InlineFormAdmin
from flask.ext.babelex import lazy_gettext
from app.models import Preference, Incoming, Expense, Shipping, ShippingLine, EnumValues
from app.views import ModelViewWithAccess, DisabledStringField
from formatter import expenses_formatter, incoming_formatter, shipping_formatter, default_date_formatter


class SalesOrderLineInlineAdmin(InlineFormAdmin):
    form_args = dict(
        product=dict(label=lazy_gettext('Product')),
        unit_price=dict(label=lazy_gettext('Unit Price')),
        quantity=dict(label=lazy_gettext('Quantity')),
        remark=dict(label=lazy_gettext('Remark')),
    )

    def postprocess_form(self, form):
        form.retail_price = DisabledStringField(label=lazy_gettext('Retail Price'))
        form.price_discount = DisabledStringField(label=lazy_gettext('Price Discount'))
        form.original_amount = DisabledStringField(label=lazy_gettext('Original Amount'))
        form.actual_amount = DisabledStringField(label=lazy_gettext('Actual Amount'))
        form.discount_amount = DisabledStringField(label=lazy_gettext('Discount Amount'))
        form.remark = None
        form.sol_shipping_line = None
        return form


class SalesOrderAdmin(ModelViewWithAccess):
    from app.models import SalesOrderLine

    column_list = ('id', 'logistic_amount', 'actual_amount', 'original_amount',
                   'discount_amount', 'order_date', 'incoming', 'expense', 'so_shipping', 'remark')
    # column_filters = ('order_date', 'remark', 'logistic_amount')

    form_columns = ('logistic_amount', 'order_date', 'remark', 'actual_amount', 'original_amount',
                    'discount_amount', 'lines')
    form_edit_rules = ('logistic_amount', 'order_date', 'remark', 'actual_amount',
                       'original_amount', 'discount_amount', 'lines')
    form_create_rules = ('logistic_amount', 'order_date', 'remark', 'lines',)
    column_editable_list = ('remark',)

    form_extra_fields = {
        'actual_amount': DisabledStringField(label=lazy_gettext('Actual Amount')),
        'original_amount': DisabledStringField(label=lazy_gettext('Original Amount')),
        'discount_amount': DisabledStringField(label=lazy_gettext('Discount Amount'))
    }
    form_args = dict(
        logistic_amount=dict(default=0),
        order_date=dict(default=datetime.now())
    )
    form_excluded_columns = ('incoming', 'expense', 'so_shipping')
    column_sortable_list = ('id', 'logistic_amount', 'actual_amount', 'original_amount', 'discount_amount',
                            'order_date')
    inline_models = (SalesOrderLineInlineAdmin(SalesOrderLine),)

    column_formatters = {
        'expense': expenses_formatter,
        'incoming': incoming_formatter,
        'so_shipping': shipping_formatter,
        'order_date': default_date_formatter,
    }

    column_labels = {
        'id': lazy_gettext('id'),
        'logistic_amount': lazy_gettext('Logistic Amount'),
        'order_date': lazy_gettext('Order Date'),
        'remark': lazy_gettext('Remark'),
        'actual_amount': lazy_gettext('Actual Amount'),
        'original_amount': lazy_gettext('Original Amount'),
        'discount_amount': lazy_gettext('Discount Amount'),
        'incoming': lazy_gettext('Related Incoming'),
        'expense': lazy_gettext('Related Expense'),
        'so_shipping': lazy_gettext('Related Shipping'),
        'lines': lazy_gettext('Lines'),
    }

    def create_form(self, obj=None):
        form = super(ModelView, self).create_form(obj)
        form.lines.form.actual_amount = None
        form.lines.form.discount_amount = None
        form.lines.form.original_amount = None
        form.lines.form.price_discount = None
        form.lines.form.retail_price = None
        return form

    @staticmethod
    def create_or_update_incoming(model):
        incoming = model.incoming
        preference = Preference.get()
        incoming = SalesOrderAdmin.create_associated_obj(incoming, model, default_obj=Incoming(),
                                                         value=model.actual_amount,
                                                         status_id=preference.def_so_incoming_status_id,
                                                         type_id=preference.def_so_incoming_type_id)
        return incoming

    @staticmethod
    def create_or_update_expense(model):
        expense = model.expense
        preference = Preference.get()
        if (model.logistic_amount is not None) and (model.logistic_amount > 0):
            default_obj = Expense(model.logistic_amount, model.order_date,
                                  preference.def_so_exp_status_id, preference.def_so_exp_type_id)
            expense = SalesOrderAdmin.create_associated_obj(expense, model,
                                                            default_obj=default_obj,
                                                            value=model.logistic_amount,
                                                            status_id=preference.def_so_exp_status_id,
                                                            type_id=preference.def_so_exp_type_id)
        return expense

    @staticmethod
    def create_associated_obj(obj, model, default_obj, value, status_id, type_id):
        if obj is None:
            obj = default_obj
            obj.status_id = status_id
            obj.category_id = type_id
        obj.amount = value
        obj.sales_order_id = model.id
        obj.date = model.order_date
        return obj

    @staticmethod
    def create_or_update_shipping(model):
        status = EnumValues.find_one_by_code('SHIPPING_COMPLETE')
        shipping = model.so_shipping
        if shipping is None:
            shipping = Shipping()
        shipping.date = model.order_date
        shipping.sales_order = model
        shipping.status = status
        for line in model.lines:
            new_sl = None
            for old_sl in shipping.lines:
                if old_sl.sales_order_line_id == line.id:
                    new_sl = old_sl
                    break
            new_sl = SalesOrderAdmin.copy_sales_order_line_to_shipping_line(line, new_sl)
            new_sl.shipping = shipping
        shipping.create_or_update_inventory_transaction()
        return shipping

    @staticmethod
    def copy_sales_order_line_to_shipping_line(sales_order_line, sl):
        if sl is None:
            sl = ShippingLine()
        sl.quantity = sales_order_line.quantity
        sl.price = sales_order_line.unit_price
        sl.product_id = sales_order_line.product_id
        sl.sales_order_line_id = sales_order_line.id
        return sl

    def after_model_change(self, form, model, is_created):
        incoming = SalesOrderAdmin.create_or_update_incoming(model)
        expense = SalesOrderAdmin.create_or_update_expense(model)
        shipping = SalesOrderAdmin.create_or_update_shipping(model)
        db = app_provider.AppInfo.get_db()
        if expense is not None:
            db.session.add(expense)
        if incoming is not None:
            db.session.add(incoming)
        if shipping is not None:
            db.session.add(shipping)
        db.session.commit()
