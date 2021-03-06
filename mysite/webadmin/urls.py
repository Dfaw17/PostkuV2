from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views
from . import api
from .apis import toko, articles, menu, kategori_menu, stock_menu, absen, man_table, discount, service_fee, pajak, \
    pelanggan, kritik_saran, beranda, laporan_bisnis, label_order, tipe_order, transaction, qris, reports

from .viewss import views_auth, views_home, views_account, views_toko, views_menu, views_reports

urlpatterns = [
    # ======================================WEB================================

    path('', views_home.home, name='home'),
    path('wrong_access', views_auth.wrong_access, name='wrong_access'),
    path('accounts/login/', views_auth.loginpage, name='login'),
    path('accounts/register/', views_auth.registerpage, name='register'),
    path('logout', views_auth.logoutpage, name='logout'),

    path('reset_password/', auth_views.PasswordResetView.as_view(), name="reset_password"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),

    path('account', views_account.account, name='account'),
    path('account/<str:id>/', views_account.detail_account, name='detail_account'),

    path('pegawai', views_account.pegawai, name='pegawai'),
    path('pegawai/<str:id>/', views_account.detail_pegawai, name='detail_pegawai'),

    path('toko', views_toko.toko, name='toko'),
    path('toko/<str:id>/', views_toko.detail_toko, name='detail_toko'),

    path('menu', views_menu.menu, name='menu'),
    path('menu/<str:id>/', views_menu.detail_menu, name='detail_menu'),

    path('absen', views.absen, name='absen'),

    path('kategori_menu', views_menu.kategori_menu, name='kategori_menu'),
    path('discount', views.discount, name='discount'),
    path('table', views.table, name='table'),
    path('stock', views.stock, name='stock'),
    path('history_stock/<str:id>/', views.history_stock, name='history_stock'),
    path('pelanggan', views.pelanggan, name='pelanggan'),
    path('tipe_order', views.tipe_order, name='tipe_order'),
    path('label_order', views.label_order, name='label_order'),

    path('wallets', views.wallets, name='wallets'),
    path('wallets/<str:id>/', views.detail_wallets, name='detail_wallets'),

    path('transaction', views.transaction, name='transaction'),
    path('transaction/tunai', views.transaction_tunai, name='transaction_tunai'),
    path('transaction/qris', views.transaction_qris, name='transaction_qris'),
    path('transaction/<str:id>/', views.detail_transaction, name='detail_transaction'),
    path('transaction/ppob', views.transaction_ppob, name='transaction_ppob'),

    path('transaction/settlement', views.settlement, name='settlement'),
    path('settlement/<str:id>/', views.settlement_detail, name='detail_settlement'),
    path('transaction/settlement/done', views.settlement_done, name='settlement_done'),
    path('settlement/done/<str:id>/', views.settlement_detail_done, name='detail_settlement_done'),
    path('confirm/settlement/<str:id>/', views.confirm_settlement, name='confirm_settlement'),

    path('request_topup', views.request_topup, name='request_topup'),
    path('request_topup_approve', views.request_topup_approve, name='request_topup_approve'),
    path('request_topup_reject', views.request_topup_reject, name='request_topup_reject'),
    path('request_topup', views.request_topup, name='request_topup'),
    path('request_topup/<str:id>/', views.request_topup_detail, name='detail_request_topup'),
    path('confirm/request_topup/<str:id>/', views.confirm_request_topup, name='confirm_request_topup'),
    path('confirm/request_topup_reject/<str:id>/', views.confirm_request_topup_reject,
         name='confirm_request_topup_reject'),

    path('report/merchant', views_reports.report_merchant, name='report_merchant'),
    path('report/menu', views_reports.report_menu, name='report_menu'),
    path('report/pegawai', views_reports.report_pegawai, name='report_pegawai'),
    path('report/disc', views_reports.report_disc, name='report_disc'),
    path('report/table', views_reports.report_table, name='report_table'),
    path('report/pelanggan', views_reports.report_pelanggan, name='report_pelanggan'),

    path('ppob_digi', views.ppob_digi, name='ppob_digi'),
    path('ppob_digi/sync', views.sync_ppob_digi, name='sync_ppob_digi'),

    # path('ppob/sync', views.sync_ppob, name='sync_ppob'),
    # path('ppob', views.ppob, name='ppob'),
    # path('ppob_postpaid', views.ppob_postpaid, name='ppob_postpaid'),
    # path('ppob_postpaid/sync', views.sync_ppob_postpaid, name='sync_ppob_postpaid'),

    path('subs', views.subs, name='subs'),
    path('subs/sync', views.sync_subs, name='sync_subs'),

    # ============================================================================API======================================================================

    path('api/token', TokenObtainPairView.as_view()),
    path('api/token/refresh', TokenRefreshView.as_view()),
    path('api/token/register', api.Register.as_view()),
    path('api/token/login', api.Login.as_view()),
    path('api/token/logout', api.Logout.as_view()),

    path('api/updateowner', api.UpdateProfileOwner.as_view()),
    path('api/updatepegawai', api.UpdateProfilePegawai.as_view()),
    path('api/delete_pegawai', api.DeletedPegawai.as_view()),
    path('api/account/', api.DetailAccount.as_view()),

    path('api/toko', toko.CRUDToko.as_view()),
    path('api/toko/detail/<str:id>/', toko.DetailToko.as_view()),

    path('api/menu', menu.CRUDMenu.as_view()),
    path('api/menu/detail/<str:id>/', menu.DetailMenu.as_view()),

    path('api/kategorimenu', kategori_menu.CRUDKategoriMenu.as_view()),
    path('api/kategorimenu/detail/<str:id>/', kategori_menu.DetailKategoriMenu.as_view()),

    path('api/cart', api.CartAPI.as_view()),
    path('api/cart/detail/<str:id>/', api.CartAPIDetail.as_view()),
    path('api/cartitem', api.CartItem.as_view()),

    path('api/table', man_table.CRUDTableManagement.as_view()),
    path('api/table/detail/<str:id>/', man_table.DetailTableManagement.as_view()),
    path('api/cart/table', api.InsertTable.as_view()),

    path('api/pelanggan', pelanggan.CRUDPelanggan.as_view()),
    path('api/pelanggan/detail/<str:id>/', pelanggan.DetailPelanggan.as_view()),
    path('api/cart/pelanggan', api.InsertPelanggan.as_view()),

    path('api/cart/discount', api.InsertDiscount.as_view()),
    path('api/cart_item/discount', api.InsertDiscountCartItem.as_view()),
    path('api/discount', discount.CRUDDiscount.as_view()),
    path('api/discount/detail/<str:id>/', discount.DetailDiscount.as_view()),

    path('api/pajak', pajak.CRUDPajak.as_view()),
    path('api/pajak/detail/<str:id>/', pajak.DetailPajak.as_view()),
    path('api/cart/pajak', api.InsertPajak.as_view()),

    path('api/cart/servicefee', api.InsertServiceFee.as_view()),
    path('api/servicefee', service_fee.CRUDServiceFee.as_view()),
    path('api/servicefee/detail/<str:id>/', service_fee.DetailServiceFee.as_view()),

    path('api/transaction', transaction.Transactions.as_view()),
    path('api/transaction/detail/<str:id>/', transaction.DetailTransactions.as_view()),
    path('api/transaction/ppob', api.TransactionPPOB.as_view()),
    path('api/transaction/ppob/detail', api.DetailTransactionPPOB.as_view()),

    path('api/absen', absen.Absen.as_view()),
    path('api/absen/check/<str:id>/', absen.CheckAbsen.as_view()),
    path('api/absen/detail/<str:id>/', absen.DetailAbsen.as_view()),

    path('api/tipe_order', tipe_order.TipeOrders.as_view()),
    path('api/label_order', label_order.LabelsOrder.as_view()),
    path('api/bank', api.Banks.as_view()),

    path('api/articles', articles.Articles.as_view()),
    path('api/articles/<str:id>/', articles.DetailArticles.as_view()),

    path('api/report/menu', reports.ReportByMenu.as_view()),
    path('api/report/kategori', reports.ReportByMenuKategori.as_view()),
    path('api/report/employee', reports.ReportByEmployee.as_view()),
    path('api/report/disc', reports.ReportByDisc.as_view()),
    path('api/report/table', reports.ReportByTable.as_view()),
    path('api/report/pelanggan', reports.ReportByPelanggan.as_view()),
    path('api/report/order_tipe', reports.ReportByOrderType.as_view()),
    path('api/report/label_order', reports.ReportByLabelOrder.as_view()),

    path('api/settlement', api.CreateSettlement.as_view()),
    path('api/settlement/<str:id>/', api.DetailHistoryettlement.as_view()),
    path('api/settlement/history', api.Historyettlement.as_view()),

    path('api/qris', qris.XenditQris.as_view()),
    path('api/qris/check/<str:id>/', qris.XenditQris.as_view()),
    path('api/qris/callback', qris.XenditCallback.as_view()),

    path('api/ppob/pricelist', api.MobileDataPrice.as_view()),
    path('api/ppob/callback', api.MobileDataCallback.as_view()),
    path('api/postpaid', api.Postpaid.as_view()),
    path('api/ppob', api.Prepaid.as_view()),

    path('api/ppob_digi', api.DIGI.as_view()),
    path('api/ppob_digi/callback', api.DIGICallback.as_view()),
    path('api/kategori/ppob', api.KategoriPPOB.as_view()),
    path('api/brand/ppob', api.MerekPPOB.as_view()),

    path('api/stock', stock_menu.StockMenus.as_view()),
    path('api/stock/trx', stock_menu.TrxStock.as_view()),

    path('api/stock/detail/<str:id>/', stock_menu.DetailStockMenus.as_view()),
    path('api/stock/trx/detail/<str:id>/', stock_menu.TrxStockDetail.as_view()),

    path('api/wallet', api.WalletsToko.as_view()),
    path('api/wallet/trx', api.TrxWallets.as_view()),
    path('api/wallet/konfirmasi', api.KonfirmasiWallets.as_view()),
    path('api/wallet/history-topup', api.HistoryTopupWallets.as_view()),

    path('api/subs', api.Subs.as_view()),

    path('api/beranda/<str:id>/', beranda.Beranda.as_view()),
    path('api/banner/<str:id>/', beranda.DetailBanner.as_view()),
    path('api/laporanbisnis', laporan_bisnis.LaporanBisnis.as_view()),
    path('api/kritiksaran', kritik_saran.CreateSaranKritik.as_view()),

    path('api/v2/cart', api.CartAPIV2.as_view()),
    path('api/v2/cartitem', api.CartItemAPIV2.as_view()),

    path('api/channel_payment', api.ChannelPayments.as_view()),
    path('api/check_subscribtion', beranda.CheckSubs.as_view()),
    path('api/contact_us', api.ContactUsApi.as_view()),

]
