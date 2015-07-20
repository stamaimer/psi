# encoding: utf-8

from app_provider import AppInfo
import const
from models.enum_values import EnumValues
from sqlalchemy import Column, Integer, ForeignKey, Numeric, Boolean, Text, DateTime
from sqlalchemy.orm import backref, relationship

db = AppInfo.get_db()


class Expense(db.Model):
    __tablename__ = 'expense'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    amount = Column(Numeric(precision=8, scale=2, decimal_return_scale=2), nullable=False)
    has_invoice = Column(Boolean)

    status_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    status = relationship('EnumValues', foreign_keys=[status_id])

    category_id = Column(Integer, ForeignKey('enum_values.id'), nullable=False)
    category = relationship('EnumValues', foreign_keys=[category_id])

    purchase_order_id = Column(Integer, ForeignKey('purchase_order.id'))
    purchase_order = relationship('PurchaseOrder', backref=backref('expenses',
                                                                   uselist=True, cascade='all, delete-orphan'))
    sales_order_id = Column(Integer, ForeignKey('sales_order.id'))
    sales_order = relationship('SalesOrder', backref=backref('expense',
                                                             uselist=False, cascade='all, delete-orphan'))

    remark = Column(Text)

    def __init__(self, amount=0, exp_date=None, status_id=None, category_id=None):
        self.amount = amount
        self.date = exp_date
        self.status_id = status_id
        self.category_id = category_id
        self.has_invoice = False

    @staticmethod
    def status_filter():
        return EnumValues.type_filter(const.EXP_STATUS_KEY)

    @staticmethod
    def type_filter():
        return EnumValues.type_filter(const.EXP_TYPE_KEY)

    def __unicode__(self):
        return str(self.id) + ' - ' + str(self.amount)