#!/usr/bin/env python3

import os
import sys
import json
import shutil
import pathlib
import requests
requests.urllib3.disable_warnings()

######################
# CONFIGURATIONS     #
######################

#Auth Token (update every time you login)
AUTHORIZATION = ""

#Download Directory. Uses CWD if null
DLDIR = ''
#List of accounts to skip
ByPass = ['']

#Content Types to Download
PHOTOS = True
VIDEOS = True
MESSAGES = True

######################
# END CONFIGURATIONS #
######################


def get_subscriptions():
	status = requests.get("https://dashboard11.v4.fanplace.com/dashboard/subscriptions", headers={"Authorization": AUTHORIZATION})
	if not status.ok:
		print("\nSUBSCRIPTIONS ERROR")
		return
	subs = status.json()
	return [row['username'] for row in subs['subscriptions'] if row['active']]


def get_user_info(profile):
	status = requests.get("https://member10.v4.fanplace.com/user/" + profile, headers={"Authorization": AUTHORIZATION})
	if not status.ok:
		print("\nUSER INFO ERROR")
		return
	info = status.json()
	if not info['success']:
		print("\nUSER NOT FOUND: " + profile)
		return
	return info['user']


def getLastPost(profile):
	latest = 0;
	for dirpath, dirs, files in os.walk(profile):
		for f in files:
			post = f.split('.')[0]
			post = post.split('_')
			if len(post) != 2 or not post[0].isdigit() or not post[1].isdigit() or int(post[0]) > 10000000:
				continue
			post = int(post[0])
			latest = post if post > latest else latest
	return latest


def get_photos(PROFILE, profile_id, lastPost):
	status = requests.get("https://member10.v4.fanplace.com/user/" + profile_id + "/image", headers={"Authorization": AUTHORIZATION})
	if not status.ok:
		print("\nget_images ERROR")
		return
	images = status.json()
	if not images['success']:
		print("\nget_images FAIL")
		return

	if len(images['media']) > 0:
		if not os.path.isdir(PROFILE + '/photos'):
			pathlib.Path(PROFILE + '/photos').mkdir(parents=True, exist_ok=True)

	for img in reversed(images['media']):
		if img['post'] < lastPost:
			continue
		filename = PROFILE + '/photos/' + str(img['post']) + '_' + str(img['id']) + '.' + (img['extension'] or 'jpg')

		download_media("https://cdn.fanplace.com/" + img['preview'], filename)


def get_videos(PROFILE, profile_id, lastPost):
	status = requests.get("https://member10.v4.fanplace.com/user/" + profile_id + "/video", headers={"Authorization": AUTHORIZATION})
	if not status.ok:
		print("\nget_videos ERROR")
		return
	videos = status.json()
	if not videos['success']:
		print("\nget_videos FAIL")
		return

	if len(videos['media']) > 0:
		if not os.path.isdir(PROFILE + '/videos'):
			pathlib.Path(PROFILE + '/videos').mkdir(parents=True, exist_ok=True)

	for vid in reversed(videos['media']):
		if vid['post'] < lastPost:
			continue
		filename = PROFILE + '/videos/' + str(vid['post']) + '_' + str(vid['id']) + '.' + (vid['extension'] or 'mp4')
		quailty = '480' if vid['q480'] else '240'
		quailty = '720' if vid['q720'] else quailty
		quailty = '1080' if vid['q1080'] else quailty
		quailty = '1440' if vid['q1440'] else quailty
		quailty = '2160' if vid['q2160'] else quailty
		source = "https://cdn.fanplace.com/media/" + profile_id + '/v/' + vid['load_id'] + '/' + quailty + '.' + (vid['extension'] or 'mp4')

		download_media(source, filename)


def get_messages(PROFILE, profile_id):
	paginate = 9999999999
	status = requests.get("https://chat18.v4.fanplace.com/conversation/" + profile_id + "/" + str(paginate), headers={"Authorization": AUTHORIZATION})
	if not status.ok:
		print("\nget_messages ERROR")
		return
	msgThread = status.json()
	if not msgThread['success']:
		print("\nget_messages FAIL")
		return

	messages = msgThread['thread']['messages']

	#paginate
	while len(msgThread['thread']['messages']) == 20:
		paginate = msgThread['thread']['messages'][19]['id']
		status = requests.get("https://chat18.v4.fanplace.com/conversation/" + profile_id + "/" + str(paginate), headers={"Authorization": AUTHORIZATION})
		if not status.ok:
			break
		msgThread = status.json()
		messages.extend(msgThread['thread']['messages'])

	if len(messages) > 0:
		if not os.path.isdir(PROFILE + '/messages'):
			pathlib.Path(PROFILE + '/messages').mkdir(parents=True, exist_ok=True)

	for msg in messages:
		if msg['preview']:
			msg['media'].append(msg['preview'])
		for media in msg['media']:
			filename = PROFILE + '/messages/' + str(msg['id']) + '-' + str(media['id']) + '.' + (media['extension'] or 'jpg')

			download_media(media['image'], filename)


def download_media(sourceURL, destFileName):
	if os.path.isfile(destFileName):
		return
	try:
		r = requests.get(sourceURL, stream=True, timeout=(4,None), verify=False)
	except:
		print('Error getting: ' + sourceURL + ' (skipping)')
		return
	if r.status_code != 200:
		print(r.url + ' :: ' + str(r.status_code))
		return

	with open(destFileName, 'wb') as f:
		r.raw.decode_content = True
		shutil.copyfileobj(r.raw, f)
		print(destFileName)
	r.close()


if len(sys.argv) < 2:
	print("\nUsage: " + sys.argv[0] + " <list of profiles> OR all\n")
	print("Make sure to update the auth token at the top of this script (See readme)\n")
	exit()

if DLDIR:
	try: os.chdir(DLDIR)
	except: print('Unable to use DIR: ' + DLDIR)
print("CWD = " + os.getcwd())
PROFILE_LIST = sys.argv
PROFILE_LIST.pop(0)

if PROFILE_LIST[0] == "all":
	PROFILE_LIST = get_subscriptions()

for PROFILE in PROFILE_LIST:
	if PROFILE in ByPass:
		continue

	user_info = get_user_info(PROFILE)
	if not user_info:
		continue
	if not user_info['my_subscription']['active']:
		print("subscription inactive: " + PROFILE)
		continue

	PROFILE_ID = str(user_info["id"])

	lastPost = getLastPost(PROFILE)

	print("\nDownloading profile: " + PROFILE + " " + str(lastPost) + "\n")

	if PHOTOS:
		get_photos(PROFILE, PROFILE_ID, lastPost)
	if VIDEOS:
		get_videos(PROFILE, PROFILE_ID, lastPost)
	if MESSAGES:
		get_messages(PROFILE, PROFILE_ID)

