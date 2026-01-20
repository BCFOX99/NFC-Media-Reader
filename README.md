I've long admired some of these NFC game consoles and media players that I have seen online however I wanted something that could do both as I wanted my newborn son to grow up with a device where they aren't having to navigate a streaming service
and rather have a curated selection of games and movies that they can physically grab, a bit like the physical media that I grew up with. With little coding experience I got some help from someone on Fiverr who made this piece of code (Big shout out to arham_ali2423, an excellent coder for your Python needs). 
To use it you will either need to download the code known as 'full_one' or 'media_one'. The full version has the ability to play games on top of everything else whereas the media version doesn't have functionality with RetroArch for those who only want music and video content.

To use this, simply plug in your NFC reader (I used the ACR122U but other NFC readers should work) and then download which version you want to use (full or media) and the mapping text. Make sure the mapping text is in the same folder as the python script.
I have left the mapping text with some examples of how the format should be, the first example is what it looks like playing through Plex, you must enable DLNA on your Plex Server to enable functionality and it will play the content in VLC so make sure you have that installed.
To find the directory to paste into your mapping text for Plex files, turn on DLNA on your Plex Server and from your device open VLC and under 'Local Network' go to 'Universal Plug 'n' Play' and you should see your Plex Server on there. Then navigate through your directory until you
find the file you want to play. From here right click it and choose 'Information' you'll then see at the bottom of the window it will have a section called 'Location' which will reveal the path for the file. Simply copy and paste this into your mapping text.

The first set of characters on the mapping text is the NFC Tag ID, you can find this by starting the script and tapping your NFC Card on and it will tell you what the Tag ID is. The other examples show audio and video files that are stored locally on the device and the last one highlights RetroArch.
With this one you must specify what RetroArch core you would like to use. Not all cores are supported but feel free to add extra cores. Currently this is what is supported and in what format, see below

'snes9x_libretro.dll': ['.sfc', '.smc'],
'dolphin_libretro.dll': ['.gcm', '.iso', '.wbfs', '.ciso', '.gcz'],
'dosbox_pure_libretro.dll': ['.exe', '.bat', '.com'],
'fbalpha2012_libretro.dll': ['.zip', '.7z'],
'fbneo_libretro.dll': ['.zip', '.7z'],
'fceumm_libretro.dll': ['.nes', '.fds'],
'flycast_libretro.dll': ['.cdi', '.gdi', '.chd'],
'gambatte_libretro.dll': ['.gb', '.gbc'],
'gpsp_libretro.dll': ['.gba'],
'mame2003_plus_libretro.dll': ['.zip'],
'mednafen_pce_libretro.dll': ['.pce'],
'mednafen_saturn_libretro.dll': ['.cue', '.iso'],
'mednafen_vb_libretro.dll': ['.vb'],
'melondsds_libretro.dll': ['.nds'],
'parallel_n64_libretro.dll': ['.n64', '.v64', '.z64'],
'pcsx2_libretro.dll': ['.iso', '.bin'],
'pcsx_rearmed_libretro.dll': ['.bin', '.iso', '.img', '.cue'],
'picodrive_libretro.dll': ['.bin', '.gen', '.smd', '.md'],
'ppsspp_libretro.dll': ['.iso', '.cso', '.pbp'],
'puae_libretro.dll': ['.adf', '.adz', '.dms'],
'scummvm_libretro.dll': ['.scummvm'],
'snes9x_libretro.dll': ['.sfc', '.smc']


  So once you have RetroArch, VLC, your mapping text set up and your NFC Reader plugged in you double click the script you want to use. It will make a sound like a device is being plugged in, feel free to change this. The script is hidden but if you press 'Caps Lock' on your keyboard you will see the script.
  Sometimes the NFC Reader doesn't get picked up by the script so I would suggest plugging it into a different USB socket and that usually fixes the issue. Simply tap the NFC Tag once on to your reader and it will open up the relevant media, If you want to kill the media you're using
  simply tap the card on it again and it will stop it. 

  In it's current state I know it's not perfect as my goal is for it to be plug and play something that a child could use, simply turning on a box and maybe have a message say 'Tap Card To Play Media', I've seen some people just have a message like that as their Desktop Background and hidden all other icons on their desktop
  but I wonder if this could be improved? I want it to immediately start after tapping the card and having something boot up without having to see any code or navigate any OS, just a tap and play scenario. The media script I think has the potential to work in a museum for visitors to tap different cards to have different videos play
  rather than having the same one loop over and over. I've also only tested this on Windows but would love to see this work on other OS like Linux, Mac and maybe Android too!
    

  I encourage you all to enjoy this and please modify as there is a lot of room for improvement. If you do make any changes do let me know as I would love to see them! :)

  Again big thanks to arham_ali2423 on Fiverr who was able to bring this to life, please feel free to reach out to him for any Python needs, he is very efficient!
