// Copyright (c) 2025, Harshit Chugh
// For license information, please see license.txt

frappe.ui.form.on("Drive Settings", {
    refresh(frm) {
        // Add custom button dynamically (agar server side button add nahi kiya)
        frm.add_custom_button(__('Authorize Account'), function() {
            frm.trigger("authorize_account");
        });
    },

    authrize_account(frm) {
        // DocType ke fields se values lena
        let client_id = frm.doc.outh_client_id;
        let client_secret = frm.doc.outh_client_secret;
        let redirect_uri = frm.doc.oauth_redirect_uri;

        // Console check
        console.log("Client ID:", client_id);
        console.log("Client Secret:", client_secret);
        console.log("Redirect URI:", redirect_uri);

        // Example: auth url banake open karna
        let scope = "https://www.googleapis.com/auth/drive.file"; // drive ke liye scope
       let auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + 
                    "response_type=code" +
                    "&access_type=offline" +
                    "&prompt=consent" +
                    "&client_id=" + encodeURIComponent(client_id) +
                    "&redirect_uri=" + encodeURIComponent(redirect_uri) +
                    "&scope=" + encodeURIComponent(scope);

                console.log("Redirecting to:", auth_url);

                // Redirect browser to Google OAuth consent screen
                window.open(auth_url, "_blank");
        // Browser window me open kare
        window.open(authUrl, "_blank");
    }
});
