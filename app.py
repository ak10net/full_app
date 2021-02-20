import os
import requests
import operator
import re
import nltk
from stop_words import stops
from collections import Counter
from bs4 import BeautifulSoup
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

#from rq import Queue
#from rq.job import Job
#from worker import conn

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app) 

#q = Queue(connection=conn)
from models import *

'''
def count_and_save_words(url):
	errors = []
	try:
		r = requests.get(url)
	except:
		errors.append('Unable to get URL')
		return {'error': errors}

	raw = BeautifulSoup(r.text, 'html.parser').get_text()
	nltk.data.path.append('./nltk_data')
	tokens = nltk.word_tokenize(raw)
	text = nltk.Text(tokens)
	nonPunct = re.compile('.[A_Za-z].*')
	raw_words = [w for w in text if nonPunct.match(w)]
	raw_word_count = Counter(raw_words)
	no_stop_words = [w for w in raw_words if w.lower() not in stops]
	no_stop_words_count = Counter(no_stop_words)

	try:
		from models import Result
		result = Result(
			url=url,
			result_all=raw_word_count,
			result_no_stop_words=no_stop_words_count
		)
		db.session.add(result)
		db.session.commit()
		return result.id
	except:
		errors.append()
		return {'error': errors}
'''
@app.route('/', methods=['GET', 'POST'])
def index():
	errors = []
	results = {}
	if request.method == 'POST':
		'''
		url = request.form['url']
		if not url[:8].startswith(('https://', 'http://')):
			url = 'http://' + url
		job = q.enqueue_call(
			func=count_and_save_words, args=(url,), result_ttl=5000
		)
		print(job.get_id())
		'''
		try:
			url = request.form['url']
			r = requests.get(url)
		except:
			errors.append('Unable to get URL')
		if r:
			raw = BeautifulSoup(r.text, 'html.parser').get_text()
			nltk.data.path.append('./nltk_data')
			tokens = nltk.word_tokenize(raw)
			text = nltk.Text(tokens)
			nonPunct = re.compile('.[A_Za-z].*')
			raw_words = [w for w in text if nonPunct.match(w)]
			raw_word_count = Counter(raw_words)
			no_stop_words = [w for w in raw_words if w.lower() not in stops]
			no_stop_words_count = Counter(no_stop_words)
			# save the results
			results = sorted(
				no_stop_words_count.items(),
				key=operator.itemgetter(1),
				reverse=True
			)
			try:
				result = Result(
					url=url,
					result_all=raw_word_count,
					result_no_stop_words=no_stop_words_count
				)
				db.session.add(result)
				db.session.commit()
			except:
				errors.append('Unable to add item to database')
	return render_template('index.html', results=results)

'''
@app.route('/results/<job_key>', methods=['GET'])
def get_results(job_key):
	job = Job.fetch(job_key, connection=conn)

	if job.is_finished:
		return str(job.result), 200
	else:
		return 'Nay!', 202
'''
'''
@app.route('/')
def hello():
	return 'Hello World!'


@app.route('/<name>')
def hello_name(name):
	return 'Hello {}!'.format(name)

#print(os.environ['APP_SETTINGS'])
'''

if __name__ == '__main__':
	app.run()


