import json
import os
from datetime import datetime

class SaveManager:
    def __init__(self):
        # Buat folder saves jika belum ada
        self.save_dir = "saves"
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        
        self.max_slots = 3
    
    def get_save_path(self, slot):
        """Mendapatkan path file save untuk slot tertentu"""
        return os.path.join(self.save_dir, f"save_slot_{slot}.json")
    
    def save_exists(self, slot):
        """Cek apakah save slot sudah ada"""
        return os.path.exists(self.get_save_path(slot))
    
    def save_game(self, game_data, slot):
        """
        Menyimpan data game ke slot tertentu
        
        game_data structure:
        {
            'coins': int,
            'gems': int,
            'level': int,
            'xp': int,
            'xp_to_next_level': int,
            'mall': {
                'width': int,
                'height': int,
                'level': int
            },
            'shops': [
                {'type': str, 'x': int, 'y': int, 'level': int, ...}
            ],
            'decorations': [
                {'type': str, 'x': int, 'y': int}
            ],
            'quests': [
                {'description': str, 'progress': int, 'completed': bool, ...}
            ],
            'timestamp': str
        }
        """
        try:
            # Tambahkan timestamp
            game_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            game_data['slot'] = slot
            
            save_path = self.get_save_path(slot)
            with open(save_path, 'w') as f:
                json.dump(game_data, f, indent=4)
            
            print(f"✓ Game saved to slot {slot}")
            return True
        except Exception as e:
            print(f"✗ Error saving game: {e}")
            return False
    
    def load_game(self, slot):
        """Memuat data game dari slot tertentu"""
        try:
            save_path = self.get_save_path(slot)
            if not os.path.exists(save_path):
                print(f"✗ No save found in slot {slot}")
                return None
            
            with open(save_path, 'r') as f:
                game_data = json.load(f)
            
            print(f"✓ Game loaded from slot {slot}")
            return game_data
        except Exception as e:
            print(f"✗ Error loading game: {e}")
            return None
    
    def get_save_info(self, slot):
        """Mendapatkan info preview dari save slot"""
        try:
            game_data = self.load_game(slot)
            if game_data:
                return {
                    'exists': True,
                    'level': game_data.get('level', 1),
                    'coins': game_data.get('coins', 0),
                    'gems': game_data.get('gems', 0),
                    'shops_count': len(game_data.get('shops', [])),
                    'timestamp': game_data.get('timestamp', 'Unknown'),
                    'slot': slot
                }
            else:
                return {
                    'exists': False,
                    'slot': slot
                }
        except:
            return {
                'exists': False,
                'slot': slot
            }
    
    def delete_save(self, slot):
        """Menghapus save dari slot tertentu"""
        try:
            save_path = self.get_save_path(slot)
            if os.path.exists(save_path):
                os.remove(save_path)
                print(f"✓ Save slot {slot} deleted")
                return True
            return False
        except Exception as e:
            print(f"✗ Error deleting save: {e}")
            return False
    
    def get_all_saves_info(self):
        """Mendapatkan info semua slot save"""
        return [self.get_save_info(i) for i in range(1, self.max_slots + 1)]