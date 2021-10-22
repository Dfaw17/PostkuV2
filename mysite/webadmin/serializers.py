from rest_framework import serializers
from xendit.models.qrcode import QRCode

from .models import *
from xendit import *


# =======================================MAIN SERIALIZERS=======================================
class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(max_length=128, min_length=6)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class ExtendsUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('__all__')


class TokoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Toko
        fields = ('__all__')


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ('__all__')


class CustomMenuSerializer(serializers.ModelSerializer):
    kategori = serializers.SlugRelatedField(read_only=True, slug_field='label')

    class Meta:
        model = Menu
        fields = ('__all__')


class KategoriMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = KategoriMenu
        fields = ('__all__')


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        # service_fee = serializers.SlugRelatedField(
        #     many=True,
        #     queryset=ServiceFee.objects.all(),
        #     slug_field='id'
        # )
        model = Cart
        fields = ('__all__')


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('__all__')


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = ('__all__')


class PajakSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pajak
        fields = ('__all__')


class TableManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = TableManagement
        fields = ('__all__')


class PelangganSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pelanggan
        fields = ('__all__')


class AbsenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Absensi
        fields = ('__all__')


class TipeOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderType
        fields = ('__all__')


class LabelOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabelOrder
        fields = ('__all__')


class PPOBProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPPOB
        fields = ('__all__')


class PPOBProducPostpaidtSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPPOBPostpaid
        fields = ('__all__')


class StockMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMenu
        fields = ('__all__')


class TrxStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrxStockMenu
        fields = ('__all__')


class DIGICallbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallDIGI
        fields = ('__all__')


class ProductDIGISerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPPOBDigi
        fields = ('__all__')


class KatPPOBProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryPPOB
        fields = ('__all__')


class BrandPPOBProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandPPOB
        fields = ('__all__')


class WalletTokoSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletToko
        fields = ('__all__')


class TrxWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrxWallet
        fields = ('__all__')


class ConfirmWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfirmWallet
        fields = ('__all__')


class TrxSubsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrxSubs
        fields = ('__all__')


class KritikSaranSerializer(serializers.ModelSerializer):
    class Meta:
        model = KritikSaran
        fields = ('__all__')


class ServiceFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceFee
        fields = ('__all__')


class PPOBPrepaidTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PPOBPrepaidTransaction
        fields = ('__all__')


class ListBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ('id', 'title', 'image')


class DetailBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ('__all__')


class ListArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ('id', 'title', 'image', 'count_seen', 'created_at')


class DetailArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ('__all__')


class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = ('__all__')


class ChannelPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChanelPayment
        fields = ('__all__')


# =======================================CUSTOM SERIALIZERS=======================================
class custom_trx_for_settelement(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('__all__')


class custom_toko_for_login(serializers.ModelSerializer):
    class Meta:
        model = Toko
        fields = ('__all__')


class custom_menu_for_cartitem(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ('nama', 'harga')


class custom_disc_for_cartitem(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = ('nama',)


class XenditQrisSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRCode
        fields = ('__all__')


class XenditCallbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallbackXendit
        fields = ('__all__')


class MobileDataCallbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallbackMobileData
        fields = ('__all__')


class CartItemsSerializer(serializers.ModelSerializer):
    menu_name = custom_menu_for_cartitem(source='menu', read_only=True)
    disc_name = custom_disc_for_cartitem(source='discount', read_only=True)

    class Meta:
        model = CartItems
        fields = ('__all__')


class SettlementnSerializer(serializers.ModelSerializer):
    data_trx = custom_trx_for_settelement(source='data', many=True, read_only=True)

    class Meta:
        model = Settlement
        fields = ('__all__')


class CustomAbsenSerializer(serializers.ModelSerializer):
    nama = serializers.CharField(source='user.nama', read_only=True)
    no_telp = serializers.CharField(source='user.phone', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Absensi
        fields = ('__all__')
