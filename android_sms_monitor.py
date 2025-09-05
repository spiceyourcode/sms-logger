# Android SMS Monitoring Integration
# This requires additional setup with Android ADB or SMS monitoring apps

import subprocess
import time
import re
from mpesa_logger import MPESATransactionLogger  # Import our main logger

class AndroidSMSMonitor:
    def __init__(self, excel_file="mpesa_transactions.xlsx"):
        self.logger = MPESATransactionLogger(excel_file)
        self.mpesa_keywords = ['confirmed', 'ksh', 'm-pesa', 'transaction', 'balance']
        
    def is_mpesa_message(self, message):
        """Check if the message is likely an M-PESA transaction"""
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in self.mpesa_keywords)
    
    def monitor_sms_adb(self):
        """Monitor SMS using ADB (requires USB debugging enabled)"""
        print("🔍 Starting SMS monitoring via ADB...")
        print("📱 Make sure your Android device is connected with USB debugging enabled")
        
        # This is a simplified approach - you might need to use specific ADB commands
        # depending on your Android version and permissions
        
        try:
            while True:
                # Get SMS messages (this is a placeholder - actual implementation depends on device)
                # You may need to use: adb shell content query --uri content://sms/inbox
                result = subprocess.run([
                    'adb', 'shell', 'content', 'query',
                    '--uri', 'content://sms/inbox',
                    '--projection', 'address,body,date',
                    '--where', 'read=0'
                ], capture_output=True, text=False)

                if result.returncode == 0 and result.stdout:
                    # Decode the output to handle encoding issues
                    stdout = result.stdout.decode('utf-8', errors='replace')
                    # Parse the output and look for new M-PESA messages
                    print("📨 New SMS detected, checking for M-PESA...")
                    print(f"ADB Output: {stdout[:200]}...")  # Debug: show first 200 chars

                    # Parse ADB output to extract SMS body
                    body_match = re.search(r'body=(.+)', stdout)
                    if body_match:
                        body = body_match.group(1).strip()
                        if self.is_mpesa_message(body):
                            print("🆕 M-PESA message found, processing...")
                            self.logger.process_message(body)
                        else:
                            print("📨 SMS detected but not M-PESA")
                    else:
                        print("❌ Could not extract SMS body from ADB output")
                
                time.sleep(10)  # Check every 10 seconds
                
        except KeyboardInterrupt:
            print("\n⏹️ SMS monitoring stopped")
        except FileNotFoundError:
            print("❌ ADB not found. Please install Android SDK platform-tools")
    
    def monitor_sms_file(self, file_path):
        """Monitor SMS from a text file (for testing or manual input)"""
        print(f"📁 Monitoring SMS from file: {file_path}")
        
        processed_lines = set()
        
        try:
            while True:
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        lines = f.readlines()
                    
                    for i, line in enumerate(lines):
                        line = line.strip()
                        if line and i not in processed_lines and self.is_mpesa_message(line):
                            print(f"\n🆕 New M-PESA message detected!")
                            self.logger.process_message(line)
                            processed_lines.add(i)
                
                time.sleep(5)  # Check every 5 seconds
                
        except KeyboardInterrupt:
            print("\n⏹️ File monitoring stopped")

# Alternative approach using Tasker (Android automation app)
class TaskerIntegration:
    """
    Instructions for using Tasker to monitor M-PESA SMS:
    
    1. Install Tasker app on Android
    2. Create a new Profile:
       - Event → Phone → Received Text
       - Sender: MPESA (or leave blank for all)
    3. Create a Task:
       - Action → File → Write File
       - File: /sdcard/mpesa_messages.txt
       - Text: %SMSRF: %SMSRB (sender: message body)
       - Append: Checked
    4. Run the Python monitor pointing to this file
    """
    
    def __init__(self, tasker_file="/sdcard/mpesa_messages.txt"):
        self.tasker_file = tasker_file
        self.logger = MPESATransactionLogger()
    
    def setup_instructions(self):
        print("""
🤖 TASKER SETUP INSTRUCTIONS:
=============================

1. Install Tasker app from Google Play Store
2. Enable Tasker accessibility permissions in Settings
3. Create a new Profile in Tasker:
   - Event → Phone → Received Text
   - Sender: MPESA (or leave blank)
   
4. Create a Task for this Profile:
   - Action → File → Write File
   - File: /sdcard/mpesa_messages.txt
   - Text: %SMSRB
   - Append: Checked
   - Add Newline: Checked
   
5. Save and enable the profile
6. Run this Python script to monitor the file

📱 Alternative: Use SMS Backup apps that export to CSV/TXT
        """)

# Main execution
if __name__ == "__main__":
    import os
    
    print("📱 M-PESA Real-time SMS Monitor")
    print("=" * 40)
    
    monitor = AndroidSMSMonitor()
    
    print("\nChoose monitoring method:")
    print("1. ADB Method (requires Android SDK)")
    print("2. File Method (manual/Tasker integration)")
    print("3. Show Tasker setup instructions")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        monitor.monitor_sms_adb()
    elif choice == "2":
        file_path = input("Enter path to SMS file (or press Enter for 'sms_messages.txt'): ").strip()
        if not file_path:
            file_path = "sms_messages.txt"
            # Create sample file if it doesn't exist
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    f.write("THK04TF1W4 Confirmed. Ksh250.00 sent to Antony Kiumbe on 20/8/25 at 10:15 AM. New M-PESA balance is Ksh93.09. Transaction cost, Ksh7.00.\n")
                print(f"📄 Created sample file: {file_path}")
        
        monitor.monitor_sms_file(file_path)
    elif choice == "3":
        tasker = TaskerIntegration()
        tasker.setup_instructions()
    else:
        print("❌ Invalid choice")