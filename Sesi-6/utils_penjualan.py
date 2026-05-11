from datetime import datetime
import math

def tambahkan_timestamp(laporan:dict) -> dict:
    """
    Menambahkan key "dibuat_pada" yang berisikan timestamp laporan dibuat.
    Format timestamp. cth, "27 April 2026, 14:30:05".
    Arg:
        laporan (dict): Laporan penjualan berisi detail penjualan, 
                        grand_total, dan rata unit yang terjual.
    Return:
        dict: Laporan dengan tambahan key "dibuat_pada".
    """
    timestamp = datetime.now().strftime("%d %B %Y, %H:%M:%S")
    laporan['dibuat_pada'] = timestamp
    return laporan


def hitung_mean(list_subtotal:list[int]) -> float:
    """
    Kalkulasi mean subtotal.
    Arg:
        list_subtotal (list[int]): List harga subtotal.
    Return:
        float: Rata - rata subtotal.
    """
    total = 0
    for i in list_subtotal:
        total += i
    
    mean = total / len(list_subtotal)
    return mean


def hitung_standar_deviasi(list_subtotal:list[int]) -> float:
    """
    Kalkulasi standar deviasi dari list harga subtotal.
    Arg:
        list_subtotal (list[int]): List harga subtotal.
    Return:
        float: Standar deviasi dari harga subtotal.
    """
    mean = hitung_mean(list_subtotal)
    x_ = 0
    
    for i in list_subtotal:
        x_ += (i - mean)**2
    
    std_dev = math.sqrt(x_)
    return std_dev


def statistik_penjualan(data_penjualan:list[dict]) -> dict:
    """
    Menyediakan informasi terkait total unit terjual, maksimum harga subtotal,
    minimum harga subtotal, dan standar deviasi harga subtotal.
    Arg:
        data_penjualan (list[dict]): Data penjualan.
    Return:
        dict: Informasi statistik data penjualan. 
              Berisikan total unit terjual, maksimum harga subtotal,
              minimum harga subtotal, dan standar deviasi harga subtotal.
    """
    list_subtotal:list[int] = [] # List harga subtotal
    total_unit:int = 0 # Total semua unit barang yang ada di data penjualan

    for data in data_penjualan:
        subtotal:int = hitung_subtotal(data["unit"], data["harga_satuan"])
        list_subtotal.append(subtotal)
        total_unit += data["unit"]
    
    return {
        "total_unit": total_unit,
        "max_subtotal": max(list_subtotal),
        "min_subtotal": min(list_subtotal),
        "std_subtotal": hitung_standar_deviasi(list_subtotal)
    }

def buat_laporan(data_penjualan:list[dict], persen_diskon:int = 0) -> dict:
   """
    Penyusun laporan dari data penjualan.
    Args:
        data_penjualan (list[dict]): Data penjualan.
        persen_diskon (int): Besar diskon dalam persentase (%). 
                             Defaults to 0.
    Return:
        dict: Laporan penjualan berisi detail penjualan, 
              grand_total, dan rata unit yang terjual.
    """
   item:list[dict] = [] # untuk kolom detail
   grand_total:int = 0 # Total semua harga barang yang ada di data penjualan
   total_unit:int = 0 # Total semua unit barang yang ada di data penjualan

   for data in data_penjualan:
      subtotal:int = hitung_subtotal(data["unit"], data["harga_satuan"])
      diskon:int = hitung_diskon(subtotal, persen_diskon)
      total:int = hitung_total(subtotal, persen_diskon)

      data["subtotal"] = subtotal
      data["diskon"] = diskon
      data["total"] = total

      item.append(data)
      grand_total += total
      total_unit += data["unit"]
      
   return {
       "detail": item,
       "grand_total":grand_total,
       "rata_unit": f"{total_unit/len(data_penjualan):.2f}"
   }

def hitung_subtotal(unit:int, harga_satuan:int) -> int:
    """
    Hitung subtotal = unit * harga_satuan.
    Args:
        unit (int): Banyak unit barang.
        harga_satuan (int): Harga satuan barang.
    Return:
        int: Hasil perkalian unit dan harga_satuan.
    """
    return int(unit * harga_satuan)

def hitung_diskon(subtotal:int, persen_diskon:int = 0) -> int:
    """
    Hitung harga diskon = subtotal * (persen_diskon / 100).
    Args:
        subtotal (int): Harga subtotal.
        persen_diskon (int): Besar diskon dalam persentase (%). 
                             Defaults to 0.
    Return:
        int: Harga diskon.
    """
    total_diskon:float = persen_diskon / 100
    return int(subtotal * total_diskon)

def hitung_total(subtotal:int, persen_diskon:int = 0) -> int:
    """
    Hitung harga diskon = subtotal - harga_diskon.
    Args:
        subtotal (int): Harga subtotal.
        persen_diskon (int): Besar diskon dalam persentase (%). 
                             Defaults to 0.
    Return:
        int: Harga setelah diskon.
    """
    return int(subtotal - hitung_diskon(subtotal, persen_diskon))
    