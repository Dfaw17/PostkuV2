from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.signals import *
from django.dispatch import receiver
from django.db.models import Sum
from model_utils import FieldTracker
from ckeditor.fields import RichTextField


# Create your models here.

def validate_at_value(value):
    if "@" in value:
        return value
    else:
        raise ValidationError("@ required for username")


def validate_data(value):
    if value > 2:
        return value
    else:
        raise ValidationError("data harus lebih 1")


class Toko(models.Model):
    nama = models.CharField(max_length=255, null=True, blank=True)
    alamat = models.TextField(null=True, blank=True)
    add_provinsi = models.CharField(null=True, blank=True, max_length=255)
    add_kab_kot = models.CharField(null=True, blank=True, max_length=255)
    add_kecamatan = models.CharField(null=True, blank=True, max_length=255)
    add_kel_des = models.CharField(null=True, blank=True, max_length=255)
    logo = models.ImageField(null=True, blank=True)
    kategori = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nama


class Banner(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    body = RichTextField(blank=True, null=True)
    image = models.ImageField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Article(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    body = RichTextField(blank=True, null=True)
    image = models.ImageField(null=True, blank=True)
    count_seen = models.IntegerField(null=False, blank=False, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Account(models.Model):
    username = models.CharField(max_length=255, unique=True, null=False, blank=False, validators=[validate_at_value])
    email = models.CharField(max_length=255, null=True, blank=True, unique=True)
    nama = models.CharField(max_length=255, null=True, blank=True)
    phone = models.BigIntegerField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    is_owner = models.BooleanField(null=True, blank=True)
    is_subs = models.BooleanField(null=True, blank=True)
    subs_date = models.DateTimeField(null=True, blank=True)
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    toko = models.ManyToManyField(Toko, blank=True)
    no_rekening = models.CharField(max_length=255, null=True, blank=True)
    jenis_bank = models.CharField(max_length=255, null=True, blank=True)
    profile_pic = models.ImageField(null=True, blank=True)
    rekening_book_pic = models.ImageField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class KategoriMenu(models.Model):
    label = models.CharField(max_length=255, null=False, blank=False, )
    is_active = models.BooleanField(default=True)
    toko = models.ForeignKey(Toko, null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.label


class KritikSaran(models.Model):
    label = models.CharField(max_length=255, null=False, blank=False, )
    isi = models.CharField(max_length=255, null=False, blank=False, )
    account = models.ForeignKey(Account, null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.label


class Pelanggan(models.Model):
    nama = models.CharField(max_length=255, null=False, blank=False, )
    phone = models.BigIntegerField(null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    toko = models.ForeignKey(Toko, null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nama


class TableManagement(models.Model):
    nama = models.CharField(max_length=255, null=False, blank=False, )
    note = models.CharField(max_length=255, null=True, blank=True, )
    is_active = models.BooleanField(default=True)
    is_booked = models.BooleanField(default=False)
    toko = models.ForeignKey(Toko, null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nama


class OrderType(models.Model):
    nama = models.CharField(max_length=255, null=False, blank=False)
    desc = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nama


class LabelOrder(models.Model):
    nama = models.CharField(max_length=255, null=False, blank=False)
    desc = models.TextField(null=True, blank=True)
    logo = models.ImageField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nama


class Discount(models.Model):
    nama = models.CharField(max_length=255, null=False, blank=False, )
    is_active = models.BooleanField(default=True)
    toko = models.ForeignKey(Toko, null=True, blank=True, on_delete=models.CASCADE)
    type = models.IntegerField(null=False, blank=False, default=1)
    nominal = models.IntegerField(null=False, blank=False, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nama


class Pajak(models.Model):
    nama = models.CharField(max_length=255, null=False, blank=False, )
    is_active = models.BooleanField(default=True)
    toko = models.ForeignKey(Toko, null=True, blank=True, on_delete=models.CASCADE)
    type = models.IntegerField(null=False, blank=False, default=1)
    nominal = models.IntegerField(null=False, blank=False, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nama


class Bank(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False, )
    code = models.IntegerField(null=False, blank=False, default=0)
    created_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class ServiceFee(models.Model):
    nama = models.CharField(max_length=255, null=False, blank=False, )
    is_active = models.BooleanField(default=True)
    toko = models.ForeignKey(Toko, null=True, blank=True, on_delete=models.CASCADE)
    nominal = models.IntegerField(null=False, blank=False, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nama


class Menu(models.Model):
    nama = models.CharField(max_length=255, null=True, blank=True)
    harga = models.PositiveIntegerField(null=True, blank=True)
    harga_modal = models.PositiveIntegerField(null=True, blank=True)
    desc = models.TextField(null=True, blank=True)
    toko = models.ForeignKey(Toko, on_delete=models.DO_NOTHING, blank=True, null=True)
    menu_pic = models.ImageField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    kategori = models.ForeignKey(KategoriMenu, null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nama


class ChanelPayment(models.Model):
    jenis_pembayaran = models.CharField(max_length=255, null=True, blank=True)
    nama = models.CharField(max_length=255, null=True, blank=True)
    nomer = models.CharField(max_length=255,null=True, blank=True)
    logo = models.ImageField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.jenis_pembayaran


class StockMenu(models.Model):
    nama = models.CharField(max_length=255, null=True, blank=True)
    current_stock = models.BigIntegerField(default=0)
    menu = models.ForeignKey(Menu, null=True, blank=True, on_delete=models.CASCADE)
    toko = models.ForeignKey(Toko, null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.nama) + " - " + str(self.toko) + " - " + str(self.current_stock)


class TrxStockMenu(models.Model):
    nama = models.CharField(max_length=255, null=True, blank=True)
    type_adjustment = models.IntegerField(default=0)
    adjustment_stock = models.BigIntegerField(default=0)
    note = models.CharField(max_length=255, null=True, blank=True)
    stock = models.ForeignKey(StockMenu, null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nama


class Cart(models.Model):
    cart_code = models.CharField(max_length=20, null=True, blank=True, editable=False)
    nama_cart = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    toko = models.ForeignKey(Toko, on_delete=models.CASCADE)
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE, null=True, blank=True)
    pajak = models.ForeignKey(Pajak, on_delete=models.CASCADE, null=True, blank=True)
    tipe_order = models.ForeignKey(OrderType, on_delete=models.CASCADE, null=True, blank=True)
    label_order = models.ForeignKey(LabelOrder, on_delete=models.CASCADE, null=True, blank=True)
    table = models.ForeignKey(TableManagement, on_delete=models.CASCADE, null=True, blank=True)
    pelanggan = models.ForeignKey(Pelanggan, on_delete=models.CASCADE, null=True, blank=True)
    service_fee = models.ManyToManyField(ServiceFee, blank=True, null=True)
    ordered = models.BooleanField(default=False)
    total_price = models.FloatField(default=0, null=True, blank=True)
    total_disc = models.FloatField(default=0, null=True, blank=True)
    total_pajak = models.FloatField(default=0, null=True, blank=True)
    total_service_fee = models.FloatField(default=0, null=True, blank=True)
    grand_total_price = models.FloatField(default=0, null=True, blank=True)
    total_item = models.IntegerField(blank=True, null=True)
    is_canceled = models.BooleanField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, )

    tracker = FieldTracker()

    def __str__(self):
        return str(self.cart_code) + " - " + str(self.grand_total_price)


class CartItems(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    menu_kategori = models.ForeignKey(KategoriMenu, on_delete=models.CASCADE, null=True, blank=True)
    qty = models.PositiveIntegerField(default=1)
    toko = models.ForeignKey(Toko, on_delete=models.CASCADE, null=True, blank=True)
    ordered = models.BooleanField(default=False)
    ordered_at = models.DateTimeField(null=True, blank=True)
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE, null=True, blank=True)
    price = models.FloatField(default=0)
    hpp = models.FloatField(default=0)
    total_disc = models.FloatField(default=0)
    grand_total_price = models.FloatField(default=0)
    is_canceled = models.BooleanField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.grand_total_price) + " - " + str(self.menu.nama)


class Payment(models.Model):
    paymnet = models.CharField(max_length=255, null=False, blank=False, )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.paymnet


class Transaction(models.Model):
    reff_code = models.CharField(max_length=20, null=True, blank=True)
    payment_type = models.ForeignKey(Payment, null=False, blank=False, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, null=False, blank=False, on_delete=models.CASCADE)
    pegawai = models.ForeignKey(Account, null=False, blank=False, on_delete=models.CASCADE)
    toko = models.ForeignKey(Toko, null=True, blank=True, on_delete=models.CASCADE)
    total = models.BigIntegerField(default=0)
    pajak = models.BigIntegerField(default=0)
    grand_total = models.BigIntegerField(default=0)
    is_settelement = models.BooleanField(default=0)
    is_canceled = models.BooleanField(default=0)
    uang_bayar = models.BigIntegerField(null=True, blank=True)
    uang_kembalian = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.reff_code


class Settlement(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    data = models.ManyToManyField(Transaction, blank=True)
    status_settelement = models.BooleanField(default=0)
    total = models.BigIntegerField(null=False, blank=False)
    toko = models.ForeignKey(Toko, null=False, blank=False, on_delete=models.CASCADE)
    pic_claim = models.ImageField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class CallbackXendit(models.Model):
    event = models.CharField(max_length=255, null=True, blank=True)
    external_id = models.CharField(max_length=20, null=True, blank=True)
    amount = models.BigIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, null=True, blank=True)


class Absensi(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=False, blank=False)
    toko = models.ForeignKey(Toko, on_delete=models.CASCADE, null=False, blank=False)
    pic1 = models.ImageField(null=True, blank=True)
    pic2 = models.ImageField(null=True, blank=True)
    time1 = models.DateTimeField(null=True, blank=True)
    time2 = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ProductPPOB(models.Model):
    product_code = models.CharField(max_length=255, null=True, blank=True)
    product_description = models.CharField(max_length=255, null=True, blank=True)
    product_nominal = models.CharField(max_length=255, null=True, blank=True)
    product_details = models.CharField(max_length=255, null=True, blank=True)
    product_price = models.BigIntegerField(null=True, blank=True)
    product_type = models.CharField(max_length=255, null=True, blank=True)
    active_period = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    icon_url = models.CharField(max_length=255, null=True, blank=True)
    POSTKU_price = models.BigIntegerField(null=True, blank=True)
    last_sync_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product_code


class ProductPPOBPostpaid(models.Model):
    code = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    fee = models.BigIntegerField(null=True, blank=True)
    komisi = models.BigIntegerField(null=True, blank=True)
    type = models.CharField(max_length=255, null=True, blank=True)
    komisi_merchant = models.BigIntegerField(null=True, blank=True)
    komisi_postku = models.BigIntegerField(null=True, blank=True)
    last_sync_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ProductPPOBDigi(models.Model):
    product_name = models.CharField(max_length=255, null=True, blank=True)
    category = models.CharField(max_length=255, null=True, blank=True)
    brand = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=255, null=True, blank=True)
    seller_name = models.CharField(max_length=255, null=True, blank=True)
    buyer_sku_code = models.CharField(max_length=255, null=True, blank=True)
    start_cut_off = models.CharField(max_length=255, null=True, blank=True)
    end_cut_off = models.CharField(max_length=255, null=True, blank=True)
    desc = models.CharField(max_length=255, null=True, blank=True)
    buyer_product_status = models.BooleanField()
    seller_product_status = models.BooleanField()
    unlimited_stock = models.BooleanField()
    multi = models.BooleanField()
    price = models.BigIntegerField(null=True, blank=True)
    price_postku = models.BigIntegerField(null=True, blank=True)
    stock = models.BigIntegerField(null=True, blank=True)
    last_sync_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product_name


class CategoryPPOB(models.Model):
    category_ppob_name = models.CharField(max_length=255, null=True, blank=True)
    category_ppob_key = models.CharField(max_length=255, null=True, blank=True)
    category_ppob_image = models.ImageField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.category_ppob_name


class BrandPPOB(models.Model):
    brand_ppob_name = models.CharField(max_length=255, null=True, blank=True)
    brand_ppob_key = models.CharField(max_length=255, null=True, blank=True)
    category_ppob = models.ForeignKey(CategoryPPOB, null=True, blank=True, on_delete=models.CASCADE)
    brand_ppob_image = models.ImageField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.brand_ppob_name


class CallbackMobileData(models.Model):
    ref_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    product_code = models.CharField(max_length=255, null=True, blank=True)
    customer_id = models.CharField(max_length=255, null=True, blank=True)
    price = models.CharField(max_length=255, null=True, blank=True)
    message = models.CharField(max_length=255, null=True, blank=True)
    sn = models.CharField(max_length=255, null=True, blank=True)
    pin = models.CharField(max_length=255, null=True, blank=True)
    balance = models.CharField(max_length=255, null=True, blank=True)
    tr_id = models.CharField(max_length=255, null=True, blank=True)
    rc = models.CharField(max_length=255, null=True, blank=True)
    sign = models.CharField(max_length=255, null=True, blank=True)


class CallDIGI(models.Model):
    trx_id = models.CharField(max_length=255, null=True, blank=True)
    ref_id = models.CharField(max_length=255, null=True, blank=True)
    customer_no = models.CharField(max_length=255, null=True, blank=True)
    buyer_sku_code = models.CharField(max_length=255, null=True, blank=True)
    message = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    rc = models.CharField(max_length=255, null=True, blank=True)
    sn = models.CharField(max_length=255, null=True, blank=True)
    buyer_last_saldo = models.BigIntegerField(null=True, blank=True)
    price = models.BigIntegerField(null=True, blank=True)


class WalletToko(models.Model):
    # Status Request (0=available to request topup, 1=has been request topup, 2=request topup on checking admin)
    wallet_code = models.CharField(max_length=255, null=True, blank=True)
    balance = models.BigIntegerField(default=0)
    status_req_deposit = models.BigIntegerField(default=0)
    balance_req = models.BigIntegerField(default=0)
    toko = models.ForeignKey(Toko, null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.wallet_code) + " - " + str(self.toko)


class TrxWallet(models.Model):
    # type TrxWallet = (1= Debit, 2= Kredit, 3=Refund)
    wallet_code = models.CharField(max_length=255, null=True, blank=True)
    reff_id = models.CharField(max_length=255, null=True, blank=True)
    type = models.IntegerField(default=0)
    adjustment_balance = models.BigIntegerField(default=0)
    note = models.TextField(null=True, blank=True)
    wallet = models.ForeignKey(WalletToko, null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.wallet_code


class ConfirmWallet(models.Model):
    # Status Confirm (1=checking admin, 2=approve, 3=cancel)
    wallet_code = models.CharField(max_length=255, null=True, blank=True)
    reason = models.CharField(max_length=255, null=True, blank=True)
    status_confirm = models.BigIntegerField(null=True, blank=True)
    pic = models.ImageField(null=True, blank=True)
    wallet = models.ForeignKey(WalletToko, null=True, blank=True, on_delete=models.CASCADE)
    toko = models.ForeignKey(Toko, null=True, blank=True, on_delete=models.CASCADE)
    balance = models.BigIntegerField(default=0)
    chanel = models.ForeignKey(ChanelPayment, null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.wallet_code


class PPOBPrepaidTransaction(models.Model):
    ref_id = models.CharField(max_length=255, null=True, blank=True)
    toko = models.ForeignKey(Toko, null=True, blank=True, on_delete=models.CASCADE)
    wallet = models.ForeignKey(WalletToko, null=True, blank=True, on_delete=models.CASCADE)
    customer_no = models.CharField(max_length=255, null=True, blank=True)
    buyer_sku_code = models.CharField(max_length=255, null=True, blank=True)
    product_name = models.CharField(max_length=255, null=True, blank=True)
    category = models.CharField(max_length=255, null=True, blank=True)
    brand = models.CharField(max_length=255, null=True, blank=True)
    desc = models.CharField(max_length=255, null=True, blank=True)
    message = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    buyer_last_saldo = models.BigIntegerField(null=True, blank=True)
    price = models.BigIntegerField(null=True, blank=True)
    price_postku = models.BigIntegerField(null=True, blank=True)
    is_refunded = models.BooleanField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ref_id


class TrxSubs(models.Model):
    ref_id = models.CharField(max_length=255, null=True, blank=True)
    account = models.ForeignKey(Account, null=True, blank=True, on_delete=models.CASCADE)
    date_subs = models.BigIntegerField(null=True, blank=True)
    invoice = models.BigIntegerField(null=True, blank=True)
    status = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ref_id


# =========================================== SIGNAL ===========================================

@receiver(pre_save, sender=TrxSubs)
def correct_trx_subs(sender, **kwargs):
    trx_subs = kwargs['instance']

    if trx_subs.ref_id == None:
        trx_subs.ref_id = "WLT-" + datetime.today().strftime('%Y%m%d%H%M%S')
    else:
        trx_subs.ref_id = trx_subs.ref_id


@receiver(pre_save, sender=Settlement)
def correct_trx_ppob(sender, **kwargs):
    settelement = kwargs['instance']

    settelement.name = "STL-" + datetime.today().strftime('%Y%m%d%H%M%S')


@receiver(pre_save, sender=ConfirmWallet)
def correct_confirm_wallet(sender, **kwargs):
    confirm_wallet = kwargs['instance']

    wallet = WalletToko.objects.get(id=confirm_wallet.wallet.id)
    confirm_wallet.wallet_code = wallet.wallet_code
    confirm_wallet.toko = wallet.toko
    confirm_wallet.status_confirm = 1
    confirm_wallet.balance = wallet.balance_req


@receiver(post_save, sender=ConfirmWallet)
def correct_confirm_wallet(sender, **kwargs):
    confirm_wallet = kwargs['instance']

    wallet = WalletToko.objects.get(id=confirm_wallet.wallet.id)
    wallet.status_req_deposit = 2
    wallet.save()


@receiver(pre_save, sender=WalletToko)
def correct_data_wallettoko(sender, **kwargs):
    wallet_toko = kwargs['instance']

    # Chart->cart_code
    if wallet_toko.wallet_code == None:
        wallet_toko.wallet_code = "WLT-" + datetime.today().strftime('%Y%m%d%H%M%S')
    else:
        wallet_toko.wallet_code = wallet_toko.wallet_code


@receiver(pre_save, sender=TrxWallet)
def correct_trx_wallet(sender, **kwargs):
    trx_wallet = kwargs['instance']

    wallet_toko = WalletToko.objects.get(id=trx_wallet.wallet.id)
    trx_wallet.wallet_code = wallet_toko.wallet_code

    trx_wallet.reff_id = "TRX-WLT-" + datetime.today().strftime('%Y%m%d%H%M%S')


@receiver(post_save, sender=TrxWallet)
def correct_trx_wallet(sender, **kwargs):
    trx_wallet = kwargs['instance']

    # 1= Debit, 2= Kredit, 3=Refund

    wallet = WalletToko.objects.get(id=trx_wallet.wallet.id)
    if trx_wallet.type == 1:
        wallet.balance = wallet.balance + trx_wallet.adjustment_balance
        wallet.save()
    elif trx_wallet.type == 2:
        wallet.balance = wallet.balance - trx_wallet.adjustment_balance
        wallet.save()
    elif trx_wallet.type == 3:
        wallet.balance = wallet.balance + trx_wallet.adjustment_balance
        wallet.save()


@receiver(pre_save, sender=StockMenu)
def correct_data_stockmenu(sender, **kwargs):
    stock_menu = kwargs['instance']

    # edit nama menu & Toko
    menu = Menu.objects.get(id=stock_menu.menu.id)
    stock_menu.nama = menu.nama
    stock_menu.toko = menu.toko


@receiver(pre_save, sender=TrxStockMenu)
def correct_trx_stockmenu(sender, **kwargs):
    trx_stock_menu = kwargs['instance']

    # edit nama menu
    stock_menu = StockMenu.objects.get(id=trx_stock_menu.stock.id)
    trx_stock_menu.nama = stock_menu.nama


@receiver(post_save, sender=TrxStockMenu)
def correct_trx_stockmenu(sender, **kwargs):
    trx_stock_menu = kwargs['instance']

    # 1= Penambahan, 2= Pengurangan, 3=Reset Stock, 4=Penjualan

    stock = StockMenu.objects.get(id=trx_stock_menu.stock.id)
    if trx_stock_menu.type_adjustment == 1:
        stock.current_stock = stock.current_stock + trx_stock_menu.adjustment_stock
        stock.save()
    elif trx_stock_menu.type_adjustment == 2:
        stock.current_stock = stock.current_stock - trx_stock_menu.adjustment_stock
        stock.save()
    elif trx_stock_menu.type_adjustment == 3:
        stock.current_stock = trx_stock_menu.adjustment_stock
        stock.save()
    elif trx_stock_menu.type_adjustment == 4:
        stock.current_stock = stock.current_stock - trx_stock_menu.adjustment_stock
        stock.save()


@receiver(pre_save, sender=Cart)
def correct_price_cart(sender, **kwargs):
    cart = kwargs['instance']

    # Chart->cart_code
    if cart.cart_code == None:
        cart.cart_code = "PKU-" + datetime.today().strftime('%Y%m%d%H%M%S')
    else:
        cart.cart_code = cart.cart_code

    # Cart-> Disc-> Price
    try:
        disc = Discount.objects.get(id=cart.discount.id)
        type = Discount.objects.get(id=disc.id).type

        if type == 2:
            cart.grand_total_price = cart.total_price - (cart.total_price * float(disc.nominal) / 100)
            cart.total_disc = (cart.total_price * float(disc.nominal) / 100)
        else:
            cart.grand_total_price = cart.total_price - float(disc.nominal)
            cart.total_disc = float(disc.nominal)
    except:
        cart.grand_total_price = cart.total_price

    # Cart -> Table
    try:
        table2 = TableManagement.objects.get(id=cart.tracker.previous('table_id'))
        table2.is_booked = 0
        table2.save()
    except:
        print("")

    # Cart -> Pajak
    try:
        pajak = Pajak.objects.get(id=cart.pajak.id)
        type_pajak = Pajak.objects.get(id=pajak.id).type

        a = CartItems.objects.filter(cart_id=cart.id).aggregate(Sum('price'))
        price_item = a.get("price__sum")

        if type_pajak == 2:
            cart.grand_total_price = cart.grand_total_price + (price_item * float(pajak.nominal) / 100)
            cart.total_pajak = (price_item * float(pajak.nominal) / 100)
        else:
            cart.grand_total_price = cart.grand_total_price + float(pajak.nominal)
            cart.total_pajak = float(pajak.nominal)
    except:
        cart.grand_total_price = cart.grand_total_price

    # Cart -> Service Fee
    try:
        data_service = cart.service_fee.all().aggregate(Sum('nominal'))
        print(data_service)
        price_service_fee = data_service.get("nominal__sum")
        cart.grand_total_price = cart.grand_total_price + price_service_fee
        cart.total_service_fee = price_service_fee

    except:
        cart.grand_total_price = cart.grand_total_price
        cart.total_service_fee = 0


@receiver(post_save, sender=Cart)
def correct_price_cart(sender, **kwargs):
    cart = kwargs['instance']

    try:
        table = TableManagement.objects.get(id=cart.table.id)
        table.is_booked = 1
        table.save()
    except:
        print("")


@receiver(pre_save, sender=CartItems)
def correct_price_cart_item(sender, **kwargs):
    cart_items = kwargs['instance']

    # ChartItems->price
    menu = Menu.objects.get(id=cart_items.menu.id)
    cart_items.price = cart_items.qty * float(menu.harga)

    # ChartItems->hpp
    menu = Menu.objects.get(id=cart_items.menu.id)
    cart_items.hpp = cart_items.qty * float(menu.harga_modal)

    # ChartItems->disc
    try:
        disc = Discount.objects.get(id=cart_items.discount.id)
        type = Discount.objects.get(id=disc.id).type

        if type == 2:
            cart_items.grand_total_price = cart_items.price - (cart_items.price * float(disc.nominal) / 100)
            cart_items.total_disc = (cart_items.price * float(disc.nominal) / 100)
        else:
            cart_items.grand_total_price = cart_items.price - float(disc.nominal)
            cart_items.total_disc = float(disc.nominal)
    except:
        cart_items.grand_total_price = cart_items.price

    # ChartItems->menu_kategori
    menu = Menu.objects.get(id=cart_items.menu.id)
    cart_items.menu_kategori = menu.kategori

    # ChartItems->toko
    cart_items.toko = menu.toko


@receiver(post_save, sender=CartItems)
def correct_total_price_cart(sender, **kwargs):
    cart_items = kwargs['instance']

    cart = Cart.objects.get(id=cart_items.cart.id)
    a = CartItems.objects.filter(cart_id=cart_items.cart.id).aggregate(Sum('grand_total_price'))
    b = CartItems.objects.filter(cart_id=cart_items.cart.id).aggregate(Sum('qty'))
    cart.total_price = a.get("grand_total_price__sum")
    cart.total_item = b.get("qty__sum")
    cart.save()


@receiver(post_delete, sender=CartItems)
def correct_total_price_cart(sender, **kwargs):
    cart_items = kwargs['instance']

    cart = Cart.objects.get(id=cart_items.cart.id)
    a = CartItems.objects.filter(cart_id=cart_items.cart.id).aggregate(Sum('price'))
    b = CartItems.objects.filter(cart_id=cart_items.cart.id).count()
    cart.total_price = a.get("price__sum")
    cart.total_item = b
    cart.save()


@receiver(pre_save, sender=Transaction)
def correct_price(sender, **kwargs):
    transactions = kwargs['instance']

    # Transaction->Total
    cart = Cart.objects.get(id=transactions.cart.id)
    transactions.total = float(cart.grand_total_price)

    # Transaction->Pajak
    check_pajak = Payment.objects.get(id=transactions.payment_type.id).id
    if check_pajak == 2:
        transactions.pajak = (float(cart.total_price) * 5) / 100
    else:
        transactions.pajak = 0

    # Transaction->Grand Total
    transactions.grand_total = transactions.total - transactions.pajak

    # Transaction->Cart_code
    transactions.reff_code = cart.cart_code

    # Transaction->Toko
    transactions.toko = cart.toko

    if transactions.uang_bayar == None:
        print('')
    else:
        transactions.uang_kembalian = transactions.uang_bayar - (transactions.total - transactions.pajak)


@receiver(post_save, sender=Transaction)
def correct_price(sender, **kwargs):
    transactions = kwargs['instance']

    # Cart->Ordered
    cart = Cart.objects.get(id=transactions.cart.id)
    cart.ordered = 1
    cart.save()

    # CartItems->Ordered
    cartitems = CartItems.objects.filter(cart_id=transactions.cart.id)
    for i in cartitems:
        i.ordered_at = transactions.created_at
        i.ordered = 1
        i.save()

    # Table->Is Booked
    try:
        table = TableManagement.objects.get(id=transactions.cart.table.id)
        table.is_booked = 0
        table.save()
    except:
        print("")

    # Stock trx menu
    cartitems = CartItems.objects.filter(cart_id=transactions.cart.id)
    for i in cartitems:
        try:
            stock_menu = StockMenu.objects.get(menu_id=i.menu.id)

            stock_id = stock_menu.id
            adjustment_stock = i.qty
            nama = stock_menu.nama

            TrxStockMenu.objects.create(
                nama=nama,
                type_adjustment=4,
                adjustment_stock=adjustment_stock,
                stock_id=stock_id,

            )
            print("success")
        except:
            print("something went wrong")
