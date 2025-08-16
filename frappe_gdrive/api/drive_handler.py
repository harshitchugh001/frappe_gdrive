import frappe, os, json, requests
from frappe import enqueue
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials


def get_drive_settings():
    """Fetch latest Drive Settings record (non-single doctype support)."""
    print("🔍 [get_drive_settings] Fetching latest Drive Settings...")
    settings = frappe.get_all(
        "Drive Settings",
        fields=["name"],
        order_by="modified desc",
        limit=1
    )
    print("✅ [get_drive_settings] Got settings:", settings)
    return settings[0]["name"] if settings else None


def enqueue_upload_to_drive(doc, method=None):
    """Trigger upload to Google Drive in background queue."""
    print("🚀 [enqueue_upload_to_drive] Triggered after file insert:", doc.name)
    settings_name = get_drive_settings()
    print("⚙️ [enqueue_upload_to_drive] Using settings:", settings_name)

    if not settings_name:
        print("❌ [enqueue_upload_to_drive] No Drive Settings found.")
        return

    settings = frappe.get_doc("Drive Settings", settings_name)
    print("📦 [enqueue_upload_to_drive] Settings loaded:", settings.as_dict())

    if not settings.enable_drive_upload:
        print("❌ [enqueue_upload_to_drive] Drive upload disabled in settings.")
        return

    print("📤 [enqueue_upload_to_drive] Queuing upload_to_drive for:", doc.name)
    enqueue(upload_to_drive, queue="long", docname=doc.name)




def refresh_access_token(settings):
    """Refresh access token using refresh_token."""
    print("🔄 [refresh_access_token] Refreshing access token...")

    data = {
        "client_id": settings.outh_client_id,
        "client_secret": settings.outh_client_secret,
        "refresh_token": settings.refresh_token,
        "grant_type": "refresh_token"
    }

    res = requests.post("https://oauth2.googleapis.com/token", data=data)
    res_json = res.json()
    print("📥 [refresh_access_token] Response:", res_json)

    if "access_token" in res_json:
        access_token = res_json["access_token"]
        expires_in = res_json.get("expires_in", 3600)

        # Calculate expiry
        expiry_time = datetime.utcnow() + timedelta(seconds=expires_in)
        expiry_str = expiry_time.strftime("%Y-%m-%d %H:%M:%S")

        # Save in Drive Settings
        frappe.db.set_value("Drive Settings", settings.name, {
            "access_token": access_token,
            "token_expiry": expiry_str
        })
        frappe.db.commit()
        print("✅ [refresh_access_token] Access token updated in DB")

        return access_token
    else:
        raise Exception(f"Failed to refresh token: {res_json}")
def upload_to_drive(docname):
    """Upload a file to Google Drive using OAuth tokens."""
    print("🚀 [upload_to_drive] Starting for File:", docname)
    file_doc = frappe.get_doc("File", docname)
    print("📄 [upload_to_drive] File Doc:", file_doc.as_dict())

    settings_name = frappe.get_all("Drive Settings", fields=["name"], order_by="modified desc", limit=1)[0].name
    settings = frappe.get_doc("Drive Settings", settings_name)
    print("⚙️ [upload_to_drive] Settings:", settings.as_dict())

    try:
        local_path = frappe.get_site_path("public", "files", file_doc.file_name)
        if not os.path.exists(local_path):
            frappe.log_error(f"File not found: {local_path}", "Drive Upload Failed")
            return

        # ✅ Ensure we have a valid access token
        if not settings.access_token:
            access_token = refresh_access_token(settings)
        else:
            access_token = settings.access_token

        # Build credentials from stored tokens
        creds = Credentials(
            token=access_token,
            refresh_token=settings.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.outh_client_id,
            client_secret=settings.outh_client_secret,
            scopes=["https://www.googleapis.com/auth/drive.file"]
        )

        drive_service = build("drive", "v3", credentials=creds)
        print("🚗 [upload_to_drive] Google Drive service built successfully")

        # File metadata
        metadata = {"name": file_doc.file_name}
        if settings.google_drive_folder_id:
            metadata["parents"] = [settings.google_drive_folder_id]

        media = MediaFileUpload(local_path, resumable=True)

        # Upload file
        drive_file = drive_service.files().create(
            body=metadata,
            media_body=media,
            fields="id, webViewLink"
        ).execute()
        print("✅ [upload_to_drive] File uploaded:", drive_file)

        # Set sharing permissions
        if settings.share_type == "Anyone with link":
            drive_service.permissions().create(
                fileId=drive_file["id"],
                body={"type": "anyone", "role": "reader"}
            ).execute()

        # Update Frappe File Doc
        file_doc.file_url = drive_file["webViewLink"]
        file_doc.uploaded_to_google_drive = 1
        file_doc.save(ignore_permissions=True)

        # Delete local copy if enabled
        if settings.delete_local_copy and os.path.exists(local_path):
            os.remove(local_path)

        # Log success
        settings.last_synced = frappe.utils.now_datetime()
        settings.log_messages = f"✅ Uploaded: {drive_file['webViewLink']}"
        settings.save(ignore_permissions=True)

    except Exception as e:
        frappe.log_error(f"Drive upload failed for {docname}: {e}", "Drive Upload Error")
        settings.log_messages = f"❌ Error: {str(e)}"
        settings.save(ignore_permissions=True)
        print("❌ [upload_to_drive] Exception:", str(e))