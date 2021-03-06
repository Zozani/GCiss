#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad

from __future__ import (
    unicode_literals, absolute_import, division, print_function)

from datetime import datetime, date

from PyQt4.QtGui import (QVBoxLayout, QGridLayout, QIcon, QMenu)
from PyQt4.QtCore import Qt, QDate

from configuration import Config
from Common.ui.common import (FormLabel, FWidget, FPeriodHolder, FPageTitle,
                              Button, BttExportXLSX, FormatDate)
from Common.ui.table import FTableWidget, TotalsWidget
from Common.ui.util import formatted_number, is_int, date_to_datetime
from models import Payment
from ui.payment_edit_add import EditOrAddPaymentrDialog


try:
    unicode
except:
    unicode = str


class PaymentViewWidget(FWidget, FPeriodHolder):

    def __init__(self, parent=0, *args, **kwargs):

        super(PaymentViewWidget, self).__init__(
            parent=parent, *args, **kwargs)
        FPeriodHolder.__init__(self, *args, **kwargs)

        self.parentWidget().setWindowTitle(
            Config.APP_NAME + u"   Movements")
        self.parent = parent

        self.title = u"Movements"

        self.on_date = FormatDate(
            QDate(date.today().year, date.today().month, 1))
        self.end_date = FormatDate(QDate.currentDate())
        self.now = datetime.now().strftime("%x")
        self.soldeField = FormLabel("0")
        self.label_balance = FormLabel(u"Solde au {} ".format(self.now))
        balanceBox = QGridLayout()
        balanceBox.addWidget(self.label_balance, 0, 2)
        balanceBox.addWidget(self.soldeField, 0, 3)
        balanceBox.setColumnStretch(0, 1)

        self.table = RapportTableWidget(parent=self)
        self.button = Button(u"Ok")
        self.button.clicked.connect(self.table.refresh_)

        self.btt_export = BttExportXLSX(u"Exporter")
        self.btt_export.clicked.connect(self.export_xls)
        self.add_btt = Button("Créditer")
        self.add_btt.setIcon(QIcon(u"{img_media}{img}".format(img_media=Config.img_media,
                                                              img="in.png")))
        self.add_btt.clicked.connect(self.add_payment)
        self.sub_btt = Button("Débiter")
        self.sub_btt.setIcon(QIcon(u"{img_media}{img}".format(img_media=Config.img_media,
                                                              img="out.png")))
        self.sub_btt.clicked.connect(self.sub_payment)

        editbox = QGridLayout()
        editbox.addWidget(FormLabel(u"Date debut"), 0, 1)
        editbox.addWidget(self.on_date, 0, 2)
        editbox.addWidget(FormLabel(u"Date fin"), 1, 1)
        editbox.addWidget(self.end_date, 1, 2)
        editbox.addWidget(self.button, 1, 3)

        editbox.addWidget(self.sub_btt, 1, 5)
        editbox.addWidget(self.add_btt, 1, 6)
        editbox.addWidget(self.btt_export, 1, 7)
        editbox.setColumnStretch(4, 2)
        vbox = QVBoxLayout()
        vbox.addWidget(FPageTitle(self.title))
        vbox.addLayout(editbox)
        vbox.addWidget(self.table)
        vbox.addLayout(balanceBox)
        self.setLayout(vbox)

    def export_xls(self):
        from Common.exports_xlsx import export_dynamic_data
        dict_data = {
            'file_name': "versements.xlsx",
            'headers': self.table.hheaders[:-1],
            'data': self.table.data,
            "extend_rows": [(1, self.table.label_mov_tt),
                            (2, self.table.totals_debit),
                            (3, self.table.totals_credit), ],
            "footers": [
                ("C", "E", "Solde au {} = {}".format(self.now, self.table.balance_tt)), ],
            'sheet': self.title,
            # 'title': self.title,
            'format_money': ['C:C', 'D:D', 'E:E', ],
            'widths': self.table.stretch_columns,
            'exclude_row': len(self.table.data) - 1,
            "date": "Du {} au {}".format(
                date_to_datetime(self.on_date.text()).strftime(u'%d/%m/%Y'),
                date_to_datetime(self.end_date.text()).strftime(u'%d/%m/%Y'))
        }
        export_dynamic_data(dict_data)

    def add_payment(self):
        print("add_payment")
        self.open_dialog(EditOrAddPaymentrDialog, modal=True,
                         payment=None, type_=Payment.CREDIT, table_p=self.table)

    def sub_payment(self):
        print("sub_payment")
        self.open_dialog(EditOrAddPaymentrDialog, modal=True,
                         payment=None, type_=Payment.DEBIT, table_p=self.table)


class RapportTableWidget(FTableWidget):

    def __init__(self, parent, *args, **kwargs):

        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.hheaders = [
            u"Date", u"Libelle opération", u"Débit", u"Crédit", u"Solde", ""]

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.popup)

        self.parent = parent

        # self.sorter = True
        self.stretch_columns = [0, 1, 4]
        self.align_map = {0: 'l', 1: 'l', 2: 'r', 3: 'r', 4: 'r'}
        self.ecart = -5
        self.display_vheaders = False
        self.refresh_()

    def refresh_(self):
        """ """

        l_date = [date_to_datetime(self.parent.on_date.text()),
                  date_to_datetime(self.parent.end_date.text())]
        self._reset()
        self.set_data_for(l_date)
        self.refresh()
        self.hideColumn(len(self.hheaders) - 1)

        pw = self.parent.parent.page_width() / 5
        self.setColumnWidth(0, pw)
        self.setColumnWidth(1, pw)
        self.setColumnWidth(2, pw)
        self.setColumnWidth(3, pw)
        # self.setColumnWidth(4, pw)

    def set_data_for(self, *args):
        date_ = args[0]
        self.data = [(pay.date, pay.libelle, pay.debit, pay.credit,
                      pay.balance, pay.id) for pay in Payment.filter(Payment.date > date_[
                          0], Payment.date < date_[1]).order_by(Payment.date.desc())]
        self.refresh()

    def popup(self, pos):

        # from ui.ligne_edit import EditLigneViewWidget
        from ui.deleteview import DeleteViewWidget
        from data_helper import check_befor_update_payment

        if (len(self.data) - 1) < self.selectionModel().selection().indexes()[0].row():
            return False
        menu = QMenu()
        editaction = menu.addAction("Modifier cette ligne")
        delaction = menu.addAction("Supprimer cette ligne")
        action = menu.exec_(self.mapToGlobal(pos))
        row = self.selectionModel().selection().indexes()[0].row()
        payment = Payment.get(id=self.data[row][-1])
        if action == editaction:
            self.parent.open_dialog(EditOrAddPaymentrDialog, modal=True,
                                    payment=payment, table_p=self)

        if action == delaction:
            self.parent.open_dialog(DeleteViewWidget, modal=True,
                                    table_p=self, obj=payment)

    def extend_rows(self):

        nb_rows = self.rowCount()
        self.setRowCount(nb_rows + 2)
        self.setSpan(nb_rows + 2, 2, 2, 4)
        self.totals_debit = 0
        self.totals_credit = 0
        self.balance_tt = 0
        cp = 0
        for row_num in range(0, self.data.__len__()):
            mtt_debit = is_int(unicode(self.item(row_num, 2).text()))
            mtt_credit = is_int(unicode(self.item(row_num, 3).text()))
            if cp == 0:
                last_balance = is_int(unicode(self.item(row_num, 4).text()))
            self.totals_debit += mtt_debit
            self.totals_credit += mtt_credit
            cp += 1

        self.balance_tt = last_balance
        # self.balance_tt = self.totals_debit - self.totals_credit

        self.label_mov_tt = u"Totals mouvements: "
        self.setItem(nb_rows, 1, TotalsWidget(self.label_mov_tt))
        self.setItem(
            nb_rows, 2, TotalsWidget(formatted_number(self.totals_debit)))
        self.setItem(
            nb_rows, 3, TotalsWidget(formatted_number(self.totals_credit)))
        self.parent.soldeField.setText(formatted_number(self.balance_tt))
