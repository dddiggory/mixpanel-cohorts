#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START app]
import logging
from flask import Flask, render_template, request, url_for, redirect
import json
import urllib
import urllib2
import urlparse
import base64

app = Flask(__name__)

@app.route('/')
def index():
	url_for('static', filename='img/filters.png')
	url_for('static', filename='img/GitHub_Logo.png')
	url_for('static', filename='img/Octocat.png')
	return render_template('index.html')


@app.errorhandler(500)
def server_error(e):
	logging.exception("An error occurred during a request.")
	return "An internal error occurred.", 500
# [END app]

@app.route('/add', methods=['POST', 'GET'])
@app.route('/cohorts', methods=['POST', 'GET'])
@app.route('/remove', methods=['POST', 'GET'])
@app.route('/delete', methods=['POST', 'GET'])
@app.route('/clearall', methods=['POST', 'GET'])
def parse_data():
	if request.method == "GET":
		return redirect(url_for('index'))
	params = request.args

	if params.get('cohort'):
		Cohort_Name, Token = urllib.unquote_plus(params['cohort']), params['token']
	else:
		Token = urllib.unquote_plus(params['token'])

	userData = (json.loads(request.form.get('users')))

	if "add" in request.path.lower() or "cohorts" in request.path.lower():
		updateAction = {"$union": {"Cohorts": [Cohort_Name]}}
	elif "remove" in request.path.lower() or "delete" in request.path.lower():
		updateAction = {"$remove": {"Cohorts": Cohort_Name}}
	elif "clearall" in request.path.lower():
		updateAction = {"$unset": ["Cohorts"]}
		Cohort_Name = None

	#Usage tracking. Please remove if rehosting.
	mpTrackingObject = {"event": "Cohort Script Run", "properties": {"token": "diggstoken", "distinct_id": Token, "Customer Token": Token, "Customer Cohort Name": Cohort_Name}}
	mpTrackingURL = "http://api.mixpanel.com/track/?data="+base64.b64encode(json.dumps(mpTrackingObject))
	urllib2.urlopen(mpTrackingURL)

	updateTemplate = {
		"token": Token,
		"$ignore_time": True,
		"$ip": 0
	}
	updateTemplate.update(updateAction)

	mpURL = "http://api.mixpanel.com/engage/?verbose=1"
	batch = []

	totalUsers = len(userData)
	for user in userData:
		update = updateTemplate.copy()
		update["$distinct_id"] = user["$distinct_id"]
		batch.append(update)
		if len(batch):
			req = urllib2.Request(mpURL,'data='+base64.b64encode(json.dumps(batch)))
			response = urllib2.urlopen(req)
			batch = []

	req = urllib2.Request(mpURL,'data='+base64.b64encode(json.dumps(batch)))
	response = urllib2.urlopen(req)

	return '200 OK'


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)







