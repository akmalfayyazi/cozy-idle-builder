from .shop import SHOP_SIZE # *** BARU: Impor ukuran grid toko ***

class Mall:
    def __init__(self, width, height):
        # Pastikan ukuran awal sesuai dengan grid
        self.width = (width // SHOP_SIZE) * SHOP_SIZE
        self.height = (height // SHOP_SIZE) * SHOP_SIZE
        self.entrance_x = self.width // 2
        self.entrance_y = 0
        self.level = 1
        
    def get_total_area(self):
        return self.width * self.height
    
    def get_shop_slots(self):
        """ *** BARU: Mendapatkan slot toko saat ini (misal: 8, 5) *** """
        return (self.width // SHOP_SIZE, self.height // SHOP_SIZE)

    def can_expand(self):
        """ *** DIUBAH: Batasi berdasarkan level/ukuran *** """
        slots_x, slots_y = self.get_shop_slots()
        return slots_x < 20 or slots_y < 20 # Batas maks 20x20 slot
    
    def get_expand_cost(self):
        """ *** DIUBAH: Biaya berdasarkan level/total slot *** """
        slots_x, slots_y = self.get_shop_slots()
        total_slots = slots_x * slots_y
        return 500 + (total_slots * 150) # Biaya meningkat seiring ukuran
    
    def get_next_expansion_slots(self):
        """ *** BARU: Menghitung string untuk slot berikutnya (misal: "8x5" -> "9x5") *** """
        slots_x, slots_y = self.get_shop_slots()
        
        # Logika ekspansi: tambahkan ke sisi yang lebih pendek agar lebih persegi
        if slots_x <= slots_y:
            return f"{slots_x+1}x{slots_y}"
        else:
            return f"{slots_x}x{slots_y+1}"

    def expand(self):
        """ *** DIUBAH: Logika ekspansi berdasarkan grid 100px *** """
        if not self.can_expand():
            return
            
        slots_x, slots_y = self.get_shop_slots()
        
        # Tambahkan ke sisi yang lebih pendek
        if slots_x <= slots_y:
            self.width += SHOP_SIZE
        else:
            self.height += SHOP_SIZE
            
        self.level += 1
        # Selalu pusatkan kembali pintu masuk
        self.entrance_x = self.width // 2