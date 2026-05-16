import os
import sys
import subprocess
import logging

def create_self_signed_cert():
    """
    Creates a self-signed certificate for development signing.
    Requires OpenSSL to be installed.
    """
    cert_dir = "certs"
    os.makedirs(cert_dir, exist_ok=True)
    
    pfx_path = os.path.join(cert_dir, "dev_certificate.pfx")
    if os.path.exists(pfx_path):
        print(f"Certificate already exists at {pfx_path}")
        return pfx_path
    
    print("Generating self-signed certificate for development...")
    try:
        # 1. Generate private key and certificate
        # Using a simple subject for development
        subj = "/C=US/ST=State/L=City/O=TravelMate AI/CN=TravelMate Dev"
        
        # Generate key and cert
        subprocess.check_call([
            "openssl", "req", "-x509", "-newkey", "rsa:4096", 
            "-keyout", os.path.join(cert_dir, "key.pem"), 
            "-out", os.path.join(cert_dir, "cert.pem"), 
            "-days", "365", "-nodes", "-subj", subj
        ])
        
        # 2. Export to PFX (Windows standard for signing)
        # We use an empty password for this dev cert
        subprocess.check_call([
            "openssl", "pkcs12", "-export", 
            "-out", pfx_path, 
            "-inkey", os.path.join(cert_dir, "key.pem"), 
            "-in", os.path.join(cert_dir, "cert.pem"), 
            "-passout", "pass:"
        ])
        
        # Cleanup temporary pem files
        os.remove(os.path.join(cert_dir, "key.pem"))
        os.remove(os.path.join(cert_dir, "cert.pem"))
        
        print(f"Success! Self-signed certificate created: {pfx_path}")
        print("Note: This certificate will show as 'Not Trusted' unless manually installed to the Trusted Root Certification Authorities store.")
        return pfx_path
    except Exception as e:
        print(f"Failed to generate certificate: {e}")
        print("Ensure OpenSSL is installed and in your PATH.")
        return None

if __name__ == "__main__":
    create_self_signed_cert()
