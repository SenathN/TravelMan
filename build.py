import os
import sys
import subprocess
import shutil
import logging
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("build.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

def get_version():
    try:
        with open("VERSION", "r") as f:
            return f.read().strip()
    except Exception as e:
        logging.error(f"Failed to read VERSION file: {e}")
        return "unknown"

def verify_integrity(file_path):
    if not os.path.exists(file_path):
        logging.error(f"Integrity check failed: {file_path} does not exist.")
        return False
    
    file_size = os.path.getsize(file_path)
    if file_size < 1024 * 1024:  # At least 1MB for a bundled app
        logging.warning(f"Integrity check: File size ({file_size} bytes) seems too small for a bundled app.")
    
    # Calculate SHA256 for logging
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    logging.info(f"Integrity check passed: {file_path}")
    logging.info(f"SHA256: {sha256_hash.hexdigest()}")
    return True

def is_docker_available():
    """Checks if docker is installed AND the daemon is running."""
    try:
        # 'docker info' fails if the daemon is not running
        subprocess.check_call(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        return False

def sign_executable(file_path):
    """
    Signs the executable to resolve publisher issues.
    Uses signtool.exe on Windows or osslsigncode on Linux.
    """
    if not os.path.exists(file_path):
        logging.error(f"Cannot sign {file_path}: File not found.")
        return False

    cert_path = os.environ.get("CERT_PATH")
    cert_pass = os.environ.get("CERT_PASSWORD", "")

    if not cert_path:
        # Check if dev certificate exists
        dev_cert = os.path.join("certs", "dev_certificate.pfx")
        if os.path.exists(dev_cert):
            cert_path = dev_cert
            logging.info(f"Using development certificate: {cert_path}")
        else:
            logging.warning("No code signing certificate provided (CERT_PATH not set). The executable will be unsigned.")
            return False

    logging.info(f"Signing {file_path}...")
    
    current_os = sys.platform
    try:
        if current_os == "win32":
            # Windows: use signtool.exe
            # Usually found in Windows SDK
            cmd = [
                "signtool", "sign", "/f", cert_path, 
                "/p", cert_pass, "/t", "http://timestamp.digicert.com", 
                "/v", file_path
            ]
            subprocess.check_call(cmd)
        else:
            # Linux: use osslsigncode
            # This is commonly used in cross-compilation environments
            cmd = [
                "osslsigncode", "sign", "-pkcs12", cert_path,
                "-pass", cert_pass, "-n", "TravelMate AI",
                "-i", "http://travelmate.ai",
                "-t", "http://timestamp.digicert.com",
                "-in", file_path, "-out", f"{file_path}.signed"
            ]
            subprocess.check_call(cmd)
            # Move signed file back to original name
            os.replace(f"{file_path}.signed", file_path)
        
        logging.info("Successfully signed executable.")
        return True
    except Exception as e:
        logging.error(f"Failed to sign executable: {e}")
        logging.info("Continuing without signing...")
        return False

def build(target_os=None, mode="onefile"):
    version = get_version()
    current_os = sys.platform
    is_ci = os.environ.get("GITHUB_ACTIONS") == "true"
    
    # Default to windows if no OS specified
    if not target_os:
        target_os = "windows"
        
    # Check if we can actually build for the target
    if target_os == "windows" and current_os != "win32" and not is_docker_available():
        if is_ci:
            logging.error("Docker required for Windows cross-compilation in CI environment.")
            sys.exit(1)
        else:
            logging.warning("Docker is not available for Windows cross-compilation.")
            logging.info(f"Falling back to local OS build ({current_os}) for development...")
            target_os = current_os

    base_name = f"TravelMate_v{version}"
    output_name = f"{base_name}.exe" if target_os == "windows" else base_name
    
    logging.info(f"Starting build for {output_name} (Target: {target_os}, Mode: {mode})...")

    # 0. Generate seed database
    logging.info("Generating seed database...")
    try:
        subprocess.check_call([sys.executable, "scripts/make_seed_db.py"])
        logging.info("Seed database generated successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to generate seed database: {e}")
        sys.exit(1)

    # PyInstaller command components
    entry_point = "main.py"
    # Assets to include - ensure paths are relative to project root
    assets = [
        ("intents.json", "."),
        ("nltk_data", "nltk_data"),
        ("data/seed_chatbot.db", "data"),
    ]
    
    # Use spec file for consistent builds
    spec_file = "TravelMate_v1.0.0.spec" if mode == "onefile" else "TravelMate_onedir.spec"
    
    if current_os == "win32" and target_os == "windows":
        logging.info("Building for Windows on Windows host...")
        
        if os.path.exists(spec_file):
            logging.info(f"Using spec file: {spec_file}")
            cmd = [sys.executable, "-m", "PyInstaller", "--clean", "--noconfirm", spec_file]
        else:
            logging.warning(f"Spec file {spec_file} not found, using CLI flags.")
            sep = ";"
            add_data_flags = []
            for src, dest in assets:
                if os.path.exists(src):
                    add_data_flags.extend(["--add-data", f"{src}{sep}{dest}"])
            
            cmd = [
                sys.executable, "-m", "PyInstaller", "--onefile", "--windowed",
                "--name", base_name,
                "--version-file", "version_info.txt",
                "--clean", "--noconfirm"
            ] + add_data_flags + [entry_point]
        
        try:
            subprocess.check_call(cmd)
        except subprocess.CalledProcessError as e:
            logging.error(f"Build failed: {e}")
            sys.exit(1)

    elif current_os != "win32" and target_os == "windows":
        if is_docker_available():
            logging.info("Building for Windows on Linux/macOS via Docker...")
            
            # Using a more modern/robust pyinstaller image if possible, 
            # but keeping cdrx as fallback
            docker_image = os.environ.get("DOCKER_IMAGE", "cdrx/pyinstaller-windows")
            
            if os.path.exists(spec_file):
                docker_cmd = [
                    "docker", "run", "--rm",
                    "-v", f"{os.getcwd()}:/src",
                    docker_image,
                    f"pyinstaller --clean --noconfirm {spec_file}"
                ]
            else:
                docker_cmd = [
                    "docker", "run", "--rm",
                    "-v", f"{os.getcwd()}:/src",
                    docker_image,
                    f"pyinstaller --onefile --windowed --name {base_name} --version-file version_info.txt --clean --noconfirm " + \
                    " ".join([f"--add-data {src};{dest}" for src, dest in assets]) + \
                    f" {entry_point}"
                ]
            try:
                subprocess.check_call(docker_cmd)
            except subprocess.CalledProcessError as e:
                logging.error(f"Docker build failed: {e}")
                sys.exit(1)
        else:
            logging.error("Docker required for Windows cross-compilation from Linux.")
            sys.exit(1)
    else:
        # Local OS build (Linux or macOS)
        logging.info(f"Building for local OS ({current_os})...")
        sep = ":" # Linux/macOS uses :
        add_data_flags = []
        for src, dest in assets:
            if os.path.exists(src):
                add_data_flags.extend(["--add-data", f"{src}{sep}{dest}"])
        
        cmd = [
            sys.executable, "-m", "PyInstaller", "--onefile", "--windowed",
            "--name", base_name,
            "--clean", "--noconfirm"
        ] + add_data_flags + [entry_point]
        
        try:
            subprocess.check_call(cmd)
        except subprocess.CalledProcessError as e:
            logging.error(f"Local build failed: {e}")
            sys.exit(1)

    # 4. Signing and Verification
    dist_path = os.path.join("dist", output_name)
    if os.path.exists(dist_path):
        # Sign the executable
        sign_executable(dist_path)
        
        if verify_integrity(dist_path):
            logging.info(f"Build successful! Final Windows executable: {dist_path}")
        else:
            logging.error("Build completed but integrity check failed.")
            sys.exit(1)
    else:
        logging.error(f"Expected output file not found: {dist_path}")
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--os", choices=["windows", "linux", "darwin"], help="Target OS for build")
    parser.add_argument("--mode", choices=["onefile", "onedir"], default="onefile", help="Build mode")
    args = parser.parse_args()
    
    build(target_os=args.os, mode=args.mode)
