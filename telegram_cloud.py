import requests

# 🔑 បញ្ចូលព័ត៌មាន Telegram របស់អ្នក
TELEGRAM_BOT_TOKEN = "8940465802:AAFdV3ZimYVkKC2iLq83LbxhaX_0Z0QtzxY"
TELEGRAM_CHAT_ID = "5054218656"

def upload_image_to_telegram(file_path):
    """
    សម្រាប់ Admin App: Upload រូបភាពទៅ Telegram 
    ហើយវានឹង Return លេខកូដ file_id មកវិញ
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    
    print("កំពុង Upload រូបភាពទៅកាន់ Telegram Cloud...")
    try:
        with open(file_path, "rb") as image_file:
            # ផ្ញើទៅកាន់ Channel
            response = requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID}, files={"photo": image_file})
            
        if response.status_code == 200:
            data = response.json()
            # Telegram បំបែករូបភាពជាច្រើនទំហំ, យើងយកទំហំធំបំផុត (index ចុងក្រោយ [-1])
            file_id = data["result"]["photo"][-1]["file_id"]
            print(f"✅ Upload ជោគជ័យ! File ID: {file_id}")
            return file_id
        else:
            print(f"❌ បរាជ័យក្នុងការ Upload: {response.text}")
            return None
    except FileNotFoundError:
        print("❌ រកមិនឃើញហ្វាល់រូបភាពនេះទេ!")
        return None

def get_image_url_from_telegram(file_id):
    """
    សម្រាប់ POS App: យក file_id ទៅប្តូរជា Link (URL) 
    ដើម្បីទាញយក ឬបង្ហាញរូបភាព
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile?file_id={file_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        file_path = response.json()["result"]["file_path"]
        download_link = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
        return download_link
    else:
        print("❌ មិនអាចរក File ID នេះឃើញទេ!")
        return None

# ==========================================
# របៀបសាកល្បង (Testing)
# ==========================================
if __name__ == "__main__":
    # ១. សាកល្បង Upload រូបភាព (ត្រូវប្រាកដថាអ្នកមានរូបភាពឈ្មោះ laptop.jpg ក្នុង Folder)
    # my_file_id = upload_image_to_telegram("laptop.jpg")
    
    # ២. សាកល្បងយក File ID មកបង្កើតជា Link
    # ប្រសិនបើអ្នកមាន File ID រួចហើយ អាចយកមកសាកល្បងបាន
    # test_file_id = "AgACAgUAAxkBAA... (លេខកូដដែលបានពីការ Upload)"
    # image_url = get_image_url_from_telegram(test_file_id)
    # print(f"Link សម្រាប់ Download រូបភាពគឺ: {image_url}")
    pass
