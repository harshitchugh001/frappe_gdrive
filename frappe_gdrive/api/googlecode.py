# frappe_gdrive/api/googlecode.py
import frappe
import requests
from datetime import datetime, timedelta


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


@frappe.whitelist(allow_guest=True)
def capture_code(code=None, **kwargs):
    
    if not code:
        return {"status": "failed", "message": "No code received"}

    settings_name = get_drive_settings()
    if not settings_name:
        print("❌ No Drive Settings found.")
        return {"status": "failed", "message": "No Drive Settings configured"}

    settings = frappe.get_doc("Drive Settings", settings_name)
    print("📦 Drive Settings loaded:", settings.as_dict())

    client_id = settings.outh_client_id
    client_secret = settings.outh_client_secret
    redirect_uri = settings.oauth_redirect_uri

    if not client_id or not client_secret or not redirect_uri:
        return {"status": "failed", "message": "Missing OAuth credentials in Drive Settings"}

    token_url = "https://oauth2.googleapis.com/token"

    # Request payload
    data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }
    
    
    print(data,"data")

    try:
        res = requests.post(token_url, data=data)
        res_json = res.json()
        
        
        print(res_json,"response")

        if "error" in res_json:
            return {"status": "failed", "response": res_json}

        # Tokens mil gaye
        access_token = res_json.get("access_token")
        refresh_token = res_json.get("refresh_token")
        expires_in = res_json.get("expires_in")

        expiry_time = datetime.utcnow() + timedelta(seconds=expires_in)

        # DB me string format me save karo (Frappe preferred format)
        expiry_str = expiry_time.strftime("%Y-%m-%d %H:%M:%S")

        # Store in Drive Settings
        frappe.db.set_value("Drive Settings", settings_name, {
            "access_token": access_token,
            "refresh_token": refresh_token,
            # "token_expiry": expiry_str
        })
        frappe.db.commit()

        return {
            "status": "success",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": expires_in
        }

    except Exception as e:
        frappe.logger().error(f"Error exchanging code for token: {str(e)}")
        return {"status": "failed", "message": str(e)}
