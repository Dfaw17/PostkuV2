from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views
from . import api
from .apis import toko

urlpatterns = [
    # ======================================WEB================================

    path('', views.home, name='home'),
    path('wrong_access', views.wrong_access, name='wrong_access'),
    path('accounts/login/', views.loginpage, name='login'),
    path('accounts/register/', views.registerpage, name='register'),
    path('logout', views.logoutpage, name='logout'),

    path('reset_password/', auth_views.PasswordResetView.as_view(), name="reset_password"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),

    path('account', views.account, name='account'),
    path('account/<str:id>/', views.detail_account, name='detail_account'),

    path('pegawai', views.pegawai, name='pegawai'),
    path('pegawai/<str:id>/', views.detail_pegawai, name='detail_pegawai'),

    path('toko', views.toko, name='toko'),
    path('toko/<str:id>/', views.detail_toko, name='detail_toko'),

    path('menu', views.menu, name='menu'),
    path('menu/<str:id>/', views.detail_menu, name='detail_menu'),

    path('absen', views.absen, name='absen'),

    path('kategori_menu', views.kategori_menu, name='kategori_menu'),
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

    path('report/merchant', views.report_merchant, name='report_merchant'),
    path('report/menu', views.report_menu, name='report_menu'),
    path('report/pegawai', views.report_pegawai, name='report_pegawai'),
    path('report/disc', views.report_disc, name='report_disc'),
    path('report/table', views.report_table, name='report_table'),
    path('report/pelanggan', views.report_pelanggan, name='report_pelanggan'),

    path('ppob_digi', views.ppob_digi, name='ppob_digi'),
    path('ppob_digi/sync', views.sync_ppob_digi, name='sync_ppob_digi'),

    # path('ppob/sync', views.sync_ppob, name='sync_ppob'),
    # path('ppob', views.ppob, name='ppob'),
    # path('ppob_postpaid', views.ppob_postpaid, name='ppob_postpaid'),
    # path('ppob_postpaid/sync', views.sync_ppob_postpaid, name='sync_ppob_postpaid'),

    path('subs', views.subs, name='subs'),
    path('subs/sync', views.sync_subs, name='sync_subs'),

    # ======================================API================================

    path('api/token', TokenObtainPairView.as_view()),
    path('api/token/refresh', TokenRefreshView.as_view()),
    path('api/token/register', api.Register.as_view()),
    path('api/token/login', api.Login.as_view()),
    path('api/token/logout', api.Logout.as_view()),

    path('api/updateowner', api.UpdateProfileOwner.as_view()),
    path('api/updatepegawai', api.UpdateProfilePegawai.as_view()),
    path('api/account/', api.DetailAccount.as_view()),

    path('api/toko', toko.CRUDToko.as_view()),
    path('api/toko/detail/<str:id>/', toko.DetailToko.as_view()),

    path('api/menu', api.CRUDMenu.as_view()),
    path('api/menu/detail/<str:id>/', api.DetailMenu.as_view()),

    path('api/kategorimenu', api.CRUDKategoriMenu.as_view()),
    path('api/kategorimenu/detail/<str:id>/', api.DetailKategoriMenu.as_view()),

    path('api/cart', api.CartAPI.as_view()),
    path('api/cart/detail/<str:id>/', api.CartAPIDetail.as_view()),
    path('api/cartitem', api.CartItem.as_view()),

    path('api/table', api.CRUDTableManagement.as_view()),
    path('api/table/detail/<str:id>/', api.DetailTableManagement.as_view()),
    path('api/cart/table', api.InsertTable.as_view()),

    path('api/pelanggan', api.CRUDPelanggan.as_view()),
    path('api/pelanggan/detail/<str:id>/', api.DetailPelanggan.as_view()),
    path('api/cart/pelanggan', api.InsertPelanggan.as_view()),

    path('api/cart/discount', api.InsertDiscount.as_view()),
    path('api/cart_item/discount', api.InsertDiscountCartItem.as_view()),
    path('api/discount', api.CRUDDiscount.as_view()),
    path('api/discount/detail/<str:id>/', api.DetailDiscount.as_view()),

    path('api/pajak', api.CRUDPajak.as_view()),
    path('api/pajak/detail/<str:id>/', api.DetailPajak.as_view()),
    path('api/cart/pajak', api.InsertPajak.as_view()),

    path('api/cart/servicefee', api.InsertServiceFee.as_view()),
    path('api/servicefee', api.CRUDServiceFee.as_view()),
    path('api/servicefee/detail/<str:id>/', api.DetailServiceFee.as_view()),

    path('api/transaction', api.Transactions.as_view()),
    path('api/transaction/detail/<str:id>/', api.DetailTransactions.as_view()),
    path('api/transaction/ppob', api.TransactionPPOB.as_view()),

    path('api/absen', api.Absen.as_view()),
    path('api/absen/check/<str:id>/', api.CheckAbsen.as_view()),
    path('api/absen/detail/<str:id>/', api.DetailAbsen.as_view()),

    path('api/tipe_order', api.TipeOrders.as_view()),
    path('api/label_order', api.LabelsOrder.as_view()),
    path('api/bank', api.Banks.as_view()),

    path('api/articles', api.Articles.as_view()),
    path('api/articles/<str:id>/', api.DetailArticles.as_view()),

    path('api/report/menu', api.ReportByMenu.as_view()),
    path('api/report/kategori', api.ReportByMenuKategori.as_view()),
    path('api/report/employee', api.ReportByEmployee.as_view()),
    path('api/report/disc', api.ReportByDisc.as_view()),
    path('api/report/table', api.ReportByTable.as_view()),
    path('api/report/pelanggan', api.ReportByPelanggan.as_view()),
    path('api/report/order_tipe', api.ReportByOrderType.as_view()),
    path('api/report/label_order', api.ReportByLabelOrder.as_view()),

    path('api/settlement', api.CreateSettlement.as_view()),
    path('api/settlement/<str:id>/', api.DetailHistoryettlement.as_view()),
    path('api/settlement/history', api.Historyettlement.as_view()),

    path('api/qris', api.XenditQris.as_view()),
    path('api/qris/check/<str:id>/', api.XenditQris.as_view()),
    path('api/qris/callback', api.XenditCallback.as_view()),

    path('api/ppob/pricelist', api.MobileDataPrice.as_view()),
    path('api/ppob/callback', api.MobileDataCallback.as_view()),
    path('api/postpaid', api.Postpaid.as_view()),
    path('api/ppob', api.Prepaid.as_view()),

    path('api/ppob_digi', api.DIGI.as_view()),
    path('api/ppob_digi/callback', api.DIGICallback.as_view()),
    path('api/kategori/ppob', api.KategoriPPOB.as_view()),
    path('api/brand/ppob', api.MerekPPOB.as_view()),

    path('api/stock', api.StockMenus.as_view()),
    path('api/stock/trx', api.TrxStock.as_view()),

    path('api/stock/detail/<str:id>/', api.DetailStockMenus.as_view()),
    path('api/stock/trx/detail/<str:id>/', api.TrxStockDetail.as_view()),

    path('api/wallet', api.WalletsToko.as_view()),
    path('api/wallet/trx', api.TrxWallets.as_view()),
    path('api/wallet/konfirmasi', api.KonfirmasiWallets.as_view()),
    path('api/wallet/history-topup', api.HistoryTopupWallets.as_view()),

    path('api/subs', api.Subs.as_view()),

    path('api/beranda/<str:id>/', api.Beranda.as_view()),
    path('api/banner/<str:id>/', api.DetailBanner.as_view()),
    path('api/laporanbisnis', api.LaporanBisnis.as_view()),
    path('api/kritiksaran', api.CreateSaranKritik.as_view()),

    path('api/v2/cart', api.CartAPIV2.as_view()),
    path('api/v2/cartitem', api.CartItemAPIV2.as_view()),

    path('api/channel_payment', api.ChannelPayments.as_view()),

]
