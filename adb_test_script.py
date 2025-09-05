import subprocess
import sys
import time

def test_adb_installation():
    """Test if ADB is properly installed and accessible"""
    print("🔍 Testing ADB Installation...")
    print("=" * 50)
    
    try:
        # Test ADB version
        result = subprocess.run(['adb', '--version'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ ADB is installed!")
            print(f"   Version: {result.stdout.strip()}")
            return True
        else:
            print("❌ ADB command failed")
            return False
            
    except FileNotFoundError:
        print("❌ ADB not found in PATH")
        print("\n💡 Installation Instructions:")
        print("   Windows: Download Android SDK Platform Tools")
        print("   macOS: brew install android-platform-tools")
        print("   Linux: sudo apt install android-tools-adb")
        return False
    except subprocess.TimeoutExpired:
        print("❌ ADB command timed out")
        return False

def test_device_connection():
    """Test if Android device is properly connected"""
    print("\n📱 Testing Device Connection...")
    print("=" * 50)
    
    try:
        # List connected devices
        result = subprocess.run(['adb', 'devices'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            output_lines = result.stdout.strip().split('\n')
            print("ADB Devices Output:")
            print(result.stdout)
            
            # Check for connected devices
            devices = [line for line in output_lines[1:] if line.strip() and 'device' in line]
            
            if devices:
                print(f"✅ Found {len(devices)} connected device(s)")
                for device in devices:
                    device_id = device.split()[0]
                    print(f"   Device ID: {device_id}")
                return True
            else:
                print("❌ No devices found")
                print("\n🔧 Troubleshooting Steps:")
                print("   1. Connect phone via USB cable")
                print("   2. Enable Developer Options (tap Build Number 7 times)")
                print("   3. Enable USB Debugging in Developer Options")
                print("   4. Accept the USB debugging prompt on your phone")
                print("   5. Try running: adb kill-server && adb start-server")
                return False
        else:
            print("❌ Failed to list devices")
            return False
            
    except Exception as e:
        print(f"❌ Error testing device connection: {e}")
        return False

def test_sms_permissions():
    """Test if we can access SMS content"""
    print("\n📨 Testing SMS Access...")
    print("=" * 50)
    
    try:
        # Try to query SMS inbox
        result = subprocess.run([
            'adb', 'shell', 'content', 'query',
            '--uri', 'content://sms/inbox',
            '--projection', 'address,body,date',
            '--where', 'address LIKE "%MPESA%" OR body LIKE "%confirmed%"',
            '--limit', '5'
        ], capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            if result.stdout.strip():
                print("✅ SMS access successful!")
                print("📋 Sample SMS data:")
                print(result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout)
                return True
            else:
                print("⚠️  SMS access works but no M-PESA messages found")
                print("   This could mean:")
                print("   - No M-PESA messages in inbox")
                print("   - Messages are stored differently on your device")
                return True
        else:
            print("❌ Cannot access SMS content")
            print(f"Error: {result.stderr}")
            print("\n💡 Possible Solutions:")
            print("   1. Grant SMS permissions to shell: adb shell pm grant com.android.shell android.permission.READ_SMS")
            print("   2. Some devices block SMS access via ADB for security")
            print("   3. Consider using Tasker app method instead")
            return False
            
    except Exception as e:
        print(f"❌ Error testing SMS access: {e}")
        return False

def setup_sms_permissions():
    """Try to grant SMS permissions"""
    print("\n🔐 Setting up SMS Permissions...")
    print("=" * 50)
    
    try:
        # Try to grant SMS read permission
        result = subprocess.run([
            'adb', 'shell', 'pm', 'grant', 'com.android.shell', 'android.permission.READ_SMS'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ SMS permissions granted successfully")
            return True
        else:
            print("⚠️  Could not grant SMS permissions automatically")
            print("   This is normal on some devices for security reasons")
            return False
            
    except Exception as e:
        print(f"⚠️  Error setting up permissions: {e}")
        return False

def main():
    print("🚀 M-PESA ADB Setup and Test Tool")
    print("=" * 60)
    
    # Step 1: Test ADB installation
    if not test_adb_installation():
        print("\n🛑 Please install ADB first, then run this script again.")
        sys.exit(1)
    
    # Step 2: Test device connection
    if not test_device_connection():
        print("\n🛑 Please connect your Android device and enable USB debugging.")
        sys.exit(1)
    
    # Step 3: Setup permissions
    setup_sms_permissions()
    
    # Step 4: Test SMS access
    sms_works = test_sms_permissions()
    
    print("\n" + "=" * 60)
    print("📋 SETUP SUMMARY:")
    print("=" * 60)
    print("✅ ADB: Working")
    print("✅ Device: Connected")
    print(f"{'✅' if sms_works else '⚠️ '} SMS Access: {'Working' if sms_works else 'Limited'}")
    
    if sms_works:
        print("\n🎉 Great! You're ready to use ADB SMS monitoring!")
        print("   Run the main M-PESA logger script now.")
    else:
        print("\n💡 Alternative Options:")
        print("   1. Use Tasker app method (more reliable)")
        print("   2. Use file-based monitoring")
        print("   3. Try the web interface for manual entry")
    
    print("\n🔧 Useful ADB Commands:")
    print("   adb devices                     # List connected devices")
    print("   adb kill-server                 # Restart ADB server")
    print("   adb start-server                # Start ADB server")
    print("   adb shell                       # Open device shell")

if __name__ == "__main__":
    main()