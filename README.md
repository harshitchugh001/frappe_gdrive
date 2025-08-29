# ERPNext Google Drive Storage App

A custom Frappe/ERPNext app that automatically stores file attachments in **Google Drive** instead of your ERPNext server.  
This helps save server space, reduce hosting costs, and provides scalable cloud storage.  

---

## 🚀 Features

- 🔄 Automatically uploads ERPNext attachments to Google Drive  
- 💾 Saves server storage (no more server full issues)  
- 📢 Sends notification when Google Drive 15GB limit is about to be reached  
- 🔀 Switch to another Gmail account after 15GB is full  
- 📂 Old files remain accessible while new files go to the new linked Gmail  
- ⚙️ Configurable via **Drive Settings Doctype** in ERPNext  
- 🔐 Secure integration using Google API  

---

## 📋 Requirements

- Frappe/ERPNext installed  
- Google account (Gmail)  
- Google Drive API credentials (Client ID & Secret)  

---

## 🛠️ Installation

1. Go to your bench directory  
   ```bash
   cd bench_name
  ```


    bench get-app github_url
```

Install the app on your site
```
bench --site sitename install-app app_name
```


Migrate & restart

```
    bench migrate
    bench restart
```

⚙️ Configuration

    In ERPNext, search for Drive Settings Doctype

    Enter your Google Client ID, Client Secret, and Refresh Token

    Save settings

    Done ✅ Now all new file attachments will be stored in your Google Drive

📡 How it Works

    When a file is uploaded in ERPNext, instead of saving it on the server, the app uploads it to Google Drive.

    Google Drive’s 15GB free storage is utilized first.

    When nearing storage limits, system sends a notification to admin.

    Admin can switch Gmail account anytime in Drive Settings:

        Old files remain accessible in the old Gmail

        New files will go into the new Gmail

💡 Benefits

    🏷️ Cost Saving → No need to pay for extra server storage

    ♾️ Scalable → Keep switching Gmail accounts for more space

    🔒 Reliable → Google Drive rarely goes down

    📑 Flexible → Change storage account anytime

    📂 Seamless Integration → Attachments work the same way in ERPNext

📌 Example Use Cases

    Companies with limited server space

    Organizations wanting to reduce hosting bills

    Businesses that handle large attachments (images, invoices, designs)

    Easy file backup & migration
