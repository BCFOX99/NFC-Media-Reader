import nfc
import subprocess
import binascii
import os
import time
import socket
import platform
import sys
import pygame
import usb1
import win32con
import ctypes
import threading
import warnings
import psutil
from nfc.clf import acr122
import nfc.clf.acr122


# Update these imports at the top of your file
import win32gui
import win32con
import win32api
import ctypes
import threading

# Required for console handling
kernel32 = ctypes.WinDLL('kernel32')
user32 = ctypes.WinDLL('user32')

def is_caps_lock_on():
    return user32.GetKeyState(win32con.VK_CAPITAL) & 1 != 0

def get_console_window():
    return kernel32.GetConsoleWindow()

def toggle_console_visibility():
    hwnd = get_console_window()
    if hwnd:
        last_state = None
        while True:
            current_state = is_caps_lock_on()
            if current_state != last_state:
                if current_state:
                    # CapsLock ON = Show console
                    user32.ShowWindow(hwnd, win32con.SW_SHOW)
                else:
                    # CapsLock OFF = Hide console
                    user32.ShowWindow(hwnd, win32con.SW_HIDE)
                last_state = current_state
            time.sleep(0.1)


warnings.filterwarnings("ignore", message=".*nfc.clf.acr122.*")
warnings.filterwarnings("ignore")

# Initialize pygame mixer for sound
pygame.mixer.init()

# Load sound effect
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sound_file = os.path.join(current_dir, "device.mp3")
    startup_sound = pygame.mixer.Sound(sound_file)
except Exception as e:
    print(f"Error loading sound file: {e}")
    startup_sound = None

# Track currently active card and process
active_card = {
    'tag_id': None,
    'action': None,
    'process': None,
    'start_time': None
}

# Required for console handling
kernel32 = ctypes.WinDLL('kernel32')
user32 = ctypes.WinDLL('user32')

# Create console at startup
kernel32.AllocConsole()
sys.stdout = open('CONOUT$', 'w')
sys.stderr = open('CONOUT$', 'w')

def is_caps_lock_on():
    return user32.GetKeyState(win32con.VK_CAPITAL) & 1 != 0

def get_console_window():
    return kernel32.GetConsoleWindow()

def toggle_console_visibility():
    hwnd = get_console_window()
    if hwnd:
        last_state = None
        while True:
            current_state = is_caps_lock_on()
            if current_state != last_state:
                if current_state:
                    user32.ShowWindow(hwnd, win32con.SW_SHOW)
                else:
                    user32.ShowWindow(hwnd, win32con.SW_HIDE)
                last_state = current_state
            time.sleep(0.1)

# Dictionary to store the mappings
mappings = {}

def clean_windows_path(path):
    """Clean and normalize Windows file path"""
    path = path.encode('ascii', 'ignore').decode()
    path = os.path.normpath(path)
    return path

def kill_process(process_name):
    """Kill a process and all its subprocesses"""
    print(f"\nAttempting to kill {process_name}...")
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if process_name.lower() in proc.info['name'].lower():
                    print(f"Found {proc.info['name']} (PID: {proc.info['pid']})")
                    process = psutil.Process(proc.info['pid'])
                    for child in process.children(recursive=True):
                        print(f"Killing child process {child.pid}")
                        child.kill()
                    process.kill()
                    print(f"Killed {process_name}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        print(f"Error killing {process_name}: {e}")

def kill_interfering_processes():
    """Kill any processes that might interfere with the NFC reader"""
    if platform.system() == 'Windows':
        processes_to_kill = [
            'AcsNFCTray.exe',
            'ACSccid.exe',
            'APAcsNFCTray.exe',
            'APACSccid.exe',
            'ACR122U_NFC_API.exe'
        ]
        for proc in processes_to_kill:
            try:
                subprocess.run(['taskkill', '/F', '/IM', proc], 
                             creationflags=subprocess.CREATE_NO_WINDOW,
                             stderr=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL)
            except:
                continue
        time.sleep(2)

def initialize_acr122u():
    """Initialize the ACR122U reader"""
    try:
        kill_interfering_processes()
        print("Attempting to connect with generic driver...")
        
        try:
            clf = nfc.ContactlessFrontend('usb:072f:2200')
            if clf is not None:
                print("ACR122U reader initialized with generic driver")
                return clf
        except Exception as generic_error:
            print(f"Generic driver connection failed: {generic_error}")
        
        print("Attempting connection with specific chipset...")
        clf = nfc.ContactlessFrontend('usb:072f:2200:*')
        if clf is not None:
            print("ACR122U reader initialized with specific chipset")
            return clf
            
    except Exception as e:
        print(f"Error initializing reader: {e}")
        return None
        
    return None

def load_mappings():
    print("\nStarting to load mappings...")
    try:
        if getattr(sys, 'frozen', False):
            current_dir = sys._MEIPASS
        else:
            current_dir = os.path.dirname(os.path.abspath(__file__))

        mapping_file = os.getcwd() + r"\mapping.txt"
        print(f"Looking for mapping file at: {mapping_file}")

        if not os.path.exists(mapping_file):
            print("Error: mapping.txt file not found!")
            return
        
        with open(mapping_file, 'r', encoding='utf-8-sig') as file:
            print("Successfully opened mapping file")
            
            for line in file:
                if not line.strip():
                    continue
                
                print(f"\nProcessing line: {repr(line)}")
                parts = line.strip().split(',')
                
                if len(parts) >= 2:  # Only need 2 parts for VLC: tag_id and path
                    tag_id = parts[0]
                    value = parts[1]
                    
                    tag_id = ''.join(c for c in tag_id if c.isalnum()).upper()
                    value = clean_windows_path(value)
                    
                    mappings[tag_id] = ('vlc', value)
                    print(f"Added mapping - Tag ID: {tag_id}, Value: {value}")
        
        print("\nFinished loading mappings")
        print(f"Total mappings loaded: {len(mappings)}")
        
    except Exception as e:
        print(f"Error reading mappings: {type(e).__name__}: {str(e)}")
        import traceback
        print(traceback.format_exc())

def get_media_type(file_path):
    """Determine if path is audio, video, or a folder"""
    audio_extensions = {'.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg', '.wma'}
    video_extensions = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg'}
    
    if os.path.isdir(file_path):
        return 'folder'
    
    ext = os.path.splitext(file_path)[1].lower()
    if ext in audio_extensions:
        return 'audio'
    elif ext in video_extensions:
        return 'video'
    return 'unknown'

def play_vlc_media(file_path):
    """Launch VLC media player with proper process tracking"""
    global active_card
    
    try:
        print("\nStarting VLC playback...")
        print(f"Media path: {file_path}")
        
        # Fix URL formatting for network streams
        if file_path.startswith(('http:', 'https:', 'dlna:', 'plex:')):
            file_path = file_path.replace('\\', '/').replace('//', '/')
            if file_path.startswith('http:/'):
                file_path = 'http://' + file_path[6:]
            media_type = 'video'
        else:
            media_type = get_media_type(file_path)
        
        # Kill any existing VLC processes
        kill_process('vlc.exe')
        time.sleep(1)

        # Build command based on media type
        if media_type == 'folder':
            folder_path = file_path
            files = []
            for f in os.listdir(folder_path):
                full_path = os.path.join(folder_path, f)
                file_type = get_media_type(full_path)
                if file_type in ['audio', 'video']:
                    files.append(full_path)
            
            if not files:
                print("No media files found in folder")
                return None
                
            cmd = [
                'vlc',
                *files,
                '--play-and-exit',
                '--quiet',
                '--fullscreen',
                '--no-video-title-show',
                '--no-qt-privacy-ask',
                '--no-qt-error-dialogs',
                '--no-repeat'
            ]
        else:
            cmd = [
                'vlc',
                file_path,
                '--play-and-exit',
                '--quiet',
                '--fullscreen',
                '--no-video-title-show',
                '--no-qt-privacy-ask',
                '--no-qt-error-dialogs',
                '--no-repeat'
            ]
        
        # Start process
        vlc_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        print(f"VLC started with PID: {vlc_process.pid}")
        return vlc_process

    except Exception as e:
        print(f"\nVLC Error: {type(e).__name__}: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None

def format_tag_id(tag):
    try:
        if isinstance(tag, str):
            tag_id = ''.join(c for c in tag if c.isalnum()).upper()
        elif hasattr(tag, 'identifier'):
            tag_id = binascii.hexlify(tag.identifier).decode('utf-8').upper()
        else:
            tag_id = ''.join(c for c in str(tag) if c.isalnum()).upper()
        print(f"Formatted tag ID: {tag_id}")
        return tag_id
    except Exception as e:
        print(f"Error formatting tag ID: {e}")
        return None

def play_sound():
    """Play the startup/interaction sound effect"""
    try:
        if startup_sound:
            startup_sound.play()
    except Exception as e:
        print(f"Error playing sound: {e}")

def stop_current_process():
    """Stop the currently running process"""
    print("\n=== Stopping Current Process ===")
    
    try:
        if active_card['process']:
            try:
                parent = psutil.Process(active_card['process'].pid)
                children = parent.children(recursive=True)
                
                for child in children:
                    print(f"Killing child process {child.pid}")
                    child.kill()
                
                print(f"Killing parent process {parent.pid}")
                parent.kill()
                
            except psutil.NoSuchProcess:
                print("Process already terminated")
            except Exception as e:
                print(f"Error killing process tree: {e}")
                kill_process('vlc.exe')
                
    except Exception as e:
        print(f"Error in process termination: {e}")
        subprocess.run(['taskkill', '/F', '/IM', 'vlc.exe'], 
                      creationflags=subprocess.CREATE_NO_WINDOW)

    active_card.update({
        'tag_id': None,
        'action': None,
        'process': None,
        'start_time': None
    })
    print("=== Process Stop Complete ===\n")

def nfc_read(tag):
    global active_card
    print("\nTag detected!")
    tag_id = format_tag_id(tag)
    
    if not tag_id:
        print("Invalid tag ID format")
        return

    print(f"Processing tag: {tag_id}")
    
    # If same tag is tapped again, stop current content
    if tag_id == active_card['tag_id']:
        print("Same tag tapped - stopping playback")
        stop_current_process()
        play_sound()
        return

    # If different tag tapped while content is playing
    if active_card['tag_id'] is not None and active_card['tag_id'] != tag_id:
        print("Different tag detected - switching content")
        stop_current_process()
        time.sleep(1)

    # Process new tag
    play_sound()
    
    if tag_id in mappings:
        action, value = mappings[tag_id]
        print(f"Starting playback for tag {tag_id}")
        
        active_card.update({
            'tag_id': tag_id,
            'action': 'vlc',
            'start_time': time.time()
        })

        try:
            active_card['process'] = play_vlc_media(value)
            if not active_card['process']:
                print("Failed to start VLC process")
                active_card.update({
                    'tag_id': None,
                    'action': None,
                    'process': None,
                    'start_time': None
                })
        except Exception as e:
            print(f"Error starting playback: {e}")
            active_card.update({
                'tag_id': None,
                'action': None,
                'process': None,
                'start_time': None
            })
    else:
        print(f"No mapping found for tag: {tag_id}")

def main():
    # Start console visibility monitor
    console_thread = threading.Thread(target=toggle_console_visibility, daemon=True)
    console_thread.start()

    print("Starting ACR122U NFC Reader application...")
    play_sound()
    
    print("Loading mappings...")
    load_mappings()
    
    if not mappings:
        print("\nWarning: No mappings were loaded! Please check your mapping.txt file.")
        print("Continuing without mappings...")

    print("\nInitializing ACR122U reader...")
    max_retries = 3
    retry_count = 0
    
    while True:
        try:
            if retry_count >= max_retries:
                print("\nMaximum retry attempts reached.")
                print("Please ensure:")
                print("1. WinUSB driver is installed using Zadig")
                print("2. No ACS drivers are installed")
                print("3. Program is run as administrator")
                print("4. No other NFC programs are running")
                print("\nAutomatically retrying in 5 seconds...")
                time.sleep(5)
                retry_count = 0
            
            clf = initialize_acr122u()
            if clf is None:
                retry_count += 1
                print(f"\nRetrying in 3 seconds... (Attempt {retry_count} of {max_retries})")
                time.sleep(3)
                continue
                
            print("Waiting for tags... (Press Ctrl+C to exit)")
            retry_count = 0
            
            while True:
                try:
                    clf.connect(rdwr={'on-connect': nfc_read, 'timeout': 0.3})
                except nfc.clf.TimeoutError:
                    continue
                except socket.timeout:
                    continue
                except Exception as e:
                    if "timeout" in str(e).lower():
                        continue
                    if isinstance(e, (usb1.USBErrorNotSupported, usb1.USBErrorAccess)):
                        print("USB error detected, attempting to reinitialize...")
                        break
                    else:
                        raise
                    
        except (OSError, usb1.USBErrorNotSupported, usb1.USBErrorAccess) as e:
            error_code = getattr(e, 'errno', None)
            if error_code in [5, 19] or isinstance(e, usb1.USBErrorNotSupported):
                print("\nAttempting to reconnect with generic driver...")
            kill_interfering_processes()
            retry_count += 1
            print(f"Retrying in 3 seconds... (Attempt {retry_count} of {max_retries})")
            time.sleep(3)
            
        except KeyboardInterrupt:
            print("\nApplication stopped by user")
            break
            
        except Exception as e:
            print(f"\nError occurred: {type(e).__name__}: {str(e)}")
            retry_count += 1
            print(f"Attempting to recover... Retrying in 3 seconds...")
            time.sleep(3)
            
if __name__ == "__main__":
    # Initialize console state - start hidden
    hwnd = get_console_window()
    if hwnd:
        if not is_caps_lock_on():
            user32.ShowWindow(hwnd, win32con.SW_HIDE)
    
    # Start console visibility monitor in a separate thread
    console_thread = threading.Thread(target=toggle_console_visibility, daemon=True)
    console_thread.start()
    
    main()