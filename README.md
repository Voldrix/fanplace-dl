# FanPlace Profile Downloader
This tool downloads all photos/videos from FanPlace profiles\
You must be subscribed to the profile to download their content.

fanplace-dl.py will create a directory named after each profile in the `DLDIR` or current working directory if not set.\
Any existing media will be skipped, not re-downloaded.\
Will only download newest posts from where you last left off (determined by finding the latest post ID amongst photos and videos in the profile's folder)

#### Requires
Requires Python3 and 'requests': `python -m pip install requests`

## Features
* Downloads photos and videos (purchased content included)
* Specify multiple profiles at once or use "all" keyword to get subscriptions dynamically
* Bypass list to skip unwanted profiles

## Usage
First make sure to set your auth token in the script.

`./fanplace-dl.py <profiles> OR all`

### Authorization Token
You need your fanplace.com authorization token from your browser.\
This token changes every time you login, and will need to be updated in the script each time.

- Login to FanPlace
- Open dev console `F12` -> Network tab
- Click on one of the JSON elements (may need to refresh page)
- Click __Headers__ sub-tab (default)
- Copy the value of the __Authorization__ header (including the word bearer) under __request headers__ on the right
- Paste into script

#### OnlyFans
[OnlyFans Downloader](https://github.com/Voldrix/onlyfans-dl-2)

