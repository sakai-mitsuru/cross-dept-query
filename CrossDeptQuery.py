# -*- coding: utf-8 -*-

import os
import sys
import json
import wave
import itertools
import contextlib
#import urllib2
import six
import datetime

import mimetypes
import types

import codecs
import csv
import re
import time

import io,sys

#from types import *
from six.moves import urllib


proxies = {"https": "http://proxy.toshiba-sol.co.jp:8080/"}
handler = urllib.request.ProxyHandler(proxies)
opener = urllib.request.build_opener(handler)


####利用者設定パラメータ####
class BaseInfo:

	#RECAIUSサービス利用アカウント及びパスワード
	service_id = "iistry-1009"	# AIアシスタント用
	#service_id = "xxxx"

	password   = "!Iis-ySRvKFk3" # AIアシスタント用
	#password   = "xxxx"

	#認証システムのトークンの有効期限
	expiry_sec = 3600  # 1時間

	#ユーザ識別名(例)
	uuName = "aaiUserA00010"	# AIアシスタント用


	#知識ベース名称 (知識ベース作成時に利用)
	dbname = "CrossDept_f1"	#　AIアシスタント 組織横断検索用　

	dbid = "1277"	#AIアシスタント SLC実験用


	#組織横断用不要語リスト
	NeedlessWordList = ["分かる","教え","教えて","教える","知る","知りたい","知っている","人","お問い合わせ","記事","につい","について","詳しい","詳しく","関する","関して","に関数する","に関して","内容"]


	#文書検索用API用入力データ
	inputForSearchDoc = "セキュリティ,ビジネス"




	####以下　参考には不要####
	#検索語取得API用入力データ(例)
	inputForSearchWord = "SQLについて"

	#ドキュメント番号(例)  (指定したdocidによるドキュメント取得APIに利用)
	docid = "316288"

	#文書取得API用出力length(例)
	lengthOfgetDoc = "2000"

	#入力用テキストデータ(例)　短文
	textDocShort = "脆弱性と運用管理について詳しい人知りたい"

	#特徴語取得API用入力データ(例)
	inputForGetSpecific = "docids[]=33151&docids[]=33178"

	#入力用テキストデータ(例)　長文
	textDoc = ""


####利用者依存のパラメータ END####
class MyWebHandler:
	def __init__(self, url, data=None, headers=None, method=None):
		if six.PY2:
			self.req = urllib.request.Request(url, data, headers)
			if method is not None:
				self.req.get_method = lambda: method
		else:
			self.req = urllib.request.Request(url, data, headers, method=method)
		self.response = opener.open(self.req)

	def read(self):
		the_page = self.response.read()
		if isinstance(the_page, six.binary_type):
			the_page = the_page.decode("UTF-8")
		return the_page

	def readlines(self):
		the_pageline = self.response.readlines()
		if isinstance(the_pageline, six.binary_type):
			the_pageline = the_pageline.decode("UTF-8")
		return the_pageline

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, tb):
		self.response.close()
		if isinstance(exc_value, urllib.error.HTTPError):
			six.print_("HTTP Error {0}".format(exc_value.code), file=sys.stderr)
			the_page = exc_value.read()
			six.print_(the_page, file=sys.stderr)

class RecaiusAuth:
	# baseurl = "https://try-api.recaius.jp/auth/v2"
	baseurl = "https://api.recaius.jp/auth/v2"
	def __init__(self, service_id, password):
		url = RecaiusAuth.baseurl + "/tokens"

		# サービスごとのアカウントをここで与える
		user = {"service_id": service_id, "password": password}

		# 知識探索用
		#values = {"knowledge_explorer": user}
		values = {
			"knowledge_explorer": user,
			"expiry_sec": BaseInfo.expiry_sec
		}

		headers = {"Content-Type" : "application/json"}
		data = six.b(json.dumps(values))

		with MyWebHandler(url, data, headers) as handler:
			the_page = handler.read()
		result = json.loads(the_page.strip())
		self.token = result["token"]

		#テスト挿入
		#six.print_("self.token =" + self.token)

		#six.print_("Expiry sec:", result["expiry_sec"], file=sys.stderr)
		self.is_closed = False


	def close(self):
		if not self.is_closed:
			url = RecaiusAuth.baseurl + "/tokens"
			data = six.b("")
			headers = {"X-Token" : self.token}
			with MyWebHandler(url, data, headers, "DELETE") as handler:
				the_page = handler.read()
			self.is_closed = True
			#six.print_(>>sys.stderr, "Logout succeeded", file=sys.stderr)

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self.close()

class KnowledgeDB:
	# baseurl = "https://try-api.recaius.jp/asr/v2"
	baseurl = "https://api.recaius.jp/iip/v2"

	reCount = 0
	reCountBase = 0
	withJapaneseDataPath = ""


	@staticmethod
	def multipart_formdata(form_dict, boundary):
		disposition = 'Content-Disposition: form-data; name="{0}"'
		lines = []
		for k, v in six.iteritems(form_dict):
			lines.append(six.b("--" + boundary))
			lines.append(six.b(disposition.format(k)))
			lines.append(six.b(""))
			lines.append(v)
		lines.append(six.b("--" + boundary + "--"))
		lines.append(six.b(""))
		value = six.b("\r\n").join(lines)
		return value

	@staticmethod
	def multipart_formdataEx(form_dict, boundary):
		disposition = 'Content-Disposition: form-data; name="{0}"'
		lines = []
		for k, v in six.iteritems(form_dict):
			lines.append(six.b("--" + boundary))

			if k == "file":
				six.print_("START file")
				#lines.append(six.b(disposition.format(k)) + six.b('; filename="ITLaw.txt"'))
				lines.append(six.b(disposition.format(k)) + six.b('; filename=' +  BaseInfo.upfileName))

				#lines.append(six.b('Content-Type: %s' % mimetypes.guess_type('ITLaw.txt')[0]))
				lines.append(six.b('Content-Type: %s' % mimetypes.guess_type(BaseInfo.upfileName)[0]))

			else:
				six.print_("START notfile")
				lines.append(six.b(disposition.format(k)))

			lines.append(six.b(""))
			lines.append(v)

		lines.append(six.b("--" + boundary + "--"))
		lines.append(six.b(""))

		value = six.b("\r\n").join(lines)
		return value

	@staticmethod
	def multipart_formdataJson(form_dict, boundary):
		disposition = 'Content-Disposition: form-data; name="{0}"'
		lines = []
		for k, v in six.iteritems(form_dict):
			lines.append(six.b("--" + boundary))
			lines.append(six.b(disposition.format(k)))
			lines.append(six.b(""))
			lines.append(v)
		lines.append(six.b("--" + boundary + "--"))
		lines.append(six.b(""))
		value = six.b("\r\n").join(lines)
		return value



	def __init__(self, auth, uuName):
		self.auth_token = auth.token

		#追記
		self.authInstance = auth

		#six.print_("KnowledgeDB self.auth_token =" + self.auth_token)
		self._uuName = uuName
		self.is_closed = False

		self.dbid = BaseInfo.dbid

	def close(self):
		if not self.is_closed:
			self.is_closed = True

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self.close()



	#知識ベースキーワード取得
	def getDbKeywords(self, uuName):
		six.print_("知識ベースキーワード取得 START")
		values = {
			"text":six.b("It happens to be an could")
		}

		#url =  KnowledgeDB.baseurl + "/databases/" + self.dbid + "/keywords"
		url =  KnowledgeDB.baseurl + "/databases/" + self.dbid + "/keywords?count=200"
		six.print_("url =" + url)
		boundary = "--------Boundary"
		headers = {
				"Content-Type": "multipart/form-data; boundary={0}".format(boundary),
				"X-Token": self.auth_token,
				"X-User":self._uuName}
		data = KnowledgeDB.multipart_formdata(values, boundary)
		six.print_("START addText with MyWebHandler")
		data=None
		with MyWebHandler(url, data, headers, "GET") as handler:
			the_page = handler.read()
			_the_page = json.loads(the_page)
			six.print_("実行結果")
			print(_the_page)
			return _the_page


	#文書検索
	def searchDoc(self, uuName):
		six.print_("文書検索 START")

		values = {
			"text":six.b("It happens to be an could")
		}

		urlp = BaseInfo.inputForSearchDoc

		p = "query=" + urllib.parse.quote_plus(urlp ,encoding="utf-8")


		url =  KnowledgeDB.baseurl + "/databases/" + self.dbid + "?" + p
		url = url + "&count=500"

		six.print_("url addText =" + url)
		boundary = "--------Boundary"
		headers = {
				"Content-Type": "multipart/form-data; boundary={0}".format(boundary),
				"X-Token": self.auth_token,
				"X-User":self._uuName}
		data = KnowledgeDB.multipart_formdata(values, boundary)
		six.print_("START addText with MyWebHandler")
		data=None
		with MyWebHandler(url, data, headers, "GET") as handler:
			the_page = handler.read()
			_the_page = json.loads(the_page)
			#six.print_("実行結果")

			#sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
			#sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


			six.print_(_the_page)
			#print(_the_page)
			return _the_page


	#文書取得
	def getDoc(self, uuName):
		print("文書取得 START")
		values = {
			"text":six.b("It happens to be an could")
		}

		docid = BaseInfo.docid
		url =  KnowledgeDB.baseurl + "/databases/" + self.dbid + "/" + docid

		# length設定追加
		url =  url + "?" + "length=" + BaseInfo.lengthOfgetDoc


		print("url =" + url)
		boundary = "--------Boundary"
		headers = {
				"Content-Type": "multipart/form-data; boundary={0}".format(boundary),
				"X-Token": self.auth_token,
				"X-User":self._uuName}
		data = KnowledgeDB.multipart_formdata(values, boundary)
		print("START addText with MyWebHandler")
		data=None
		with MyWebHandler(url, data, headers, "GET") as handler:
			the_page = handler.read()
			_the_page = json.loads(the_page)
			print("実行結果")
			print(_the_page)
			return _the_page


	#検索語取得
	def getSearchWord(self, uuName, inputForSearchWord):
		#six.print_("◆検索語取得")
		values = {
			"text":six.b("It happens to be an could")
		}

		#urlp = BaseInfo.inputForSearchWord
		urlp = inputForSearchWord

		if six.PY2:
			p = "text=" + urllib.parse.quote_plus(urlp)
		else:
			p = "text=" + urllib.parse.quote_plus(urlp ,encoding="utf-8")


		url =  KnowledgeDB.baseurl + "/databases/" + self.dbid + "/search_words?" + p
		#six.print_("url addText =" + url)
		boundary = "--------Boundary"
		headers = {
				"Content-Type": "multipart/form-data; boundary={0}".format(boundary),
				"X-Token": self.auth_token,
				"X-User":self._uuName}

		data = KnowledgeDB.multipart_formdata(values, boundary)
		#six.print_("START addText with MyWebHandler")

		data=None
		with MyWebHandler(url, data, headers, "GET") as handler:
			#six.print_("START handler.read")
			the_page = handler.read()

			_the_page = json.loads(the_page)
			#six.print_(_the_page)
			#for element in _the_page['keywords']:
				#six.print_(element['word'] + "\t" + str(element['score']))


			#直接返す場合
			_the_page = the_page

			return _the_page



	#特徴語取得
	def getSpecificWords(self, uuName):
		print("特徴語取得処理 START")
		values = {
			"text":six.b("It happens to be an could")
		}

		p =  BaseInfo.inputForGetSpecific

		url =  KnowledgeDB.baseurl + "/databases/" + self.dbid + "/documents/specific_words?" + p +"&count=200"
		print("url addText =" + url)
		boundary = "--------Boundary"
		headers = {
				"Content-Type": "multipart/form-data; boundary={0}".format(boundary),
				"X-Token": self.auth_token,
				"X-User":self._uuName}
		data = KnowledgeDB.multipart_formdata(values, boundary)
		print("START addText with MyWebHandler")

		data=None
		with MyWebHandler(url, data, headers, "GET") as handler:
			print("START handler.read")
			the_page = handler.read()
			print("END SearchWord")
			_the_page = json.loads(the_page)
			print(_the_page)
			return _the_page



	#入力テキストキーワード(特徴づける語)取得
	def getKeywords(self, uuName):
		print("◆入力テキストキーワード")

		values = {
			"text":six.b("It happens to be an could")
		}

		#500文字以内テキスト
		urlp = BaseInfo.textDocShort

		p = "text=" + urllib.parse.quote_plus(urlp ,encoding="utf-8")

		url =  KnowledgeDB.baseurl + "/texts/keywords?" + p
		print("url getMorph =" + url)
		boundary = "--------Boundary"
		headers = {
				"Content-Type": "multipart/form-data; boundary={0}".format(boundary),
				"X-Token": self.auth_token,
				"X-User":self._uuName}

		data = KnowledgeDB.multipart_formdata(values, boundary)
		print("START getMorph with MyWebHandler")

		data=None
		with MyWebHandler(url, data, headers, "GET") as handler:
			print("START handler.read")
			the_page = handler.read()
			_the_page = json.loads(the_page)
			#six.print_("実行結果")
			#six.print_(_the_page)
			for element in _the_page['keywords']:
				six.print_(element['word'] + "\t" + str(element['score']))
			return _the_page




	########組織横断#########

	@staticmethod
	def getNeedlessWord(NeedlessWordDicFilePath):
		NeedlessWordDicFilePath = NeedlessWordDicFilePath
		NeedlessWordArray = []
		with codecs.open(NeedlessWordDicFilePath,'r','utf-8-sig') as op:
			reader = csv.reader(op, delimiter='\t')
			for row in reader:
				NeedlessWordArray.append(row[1])
		return NeedlessWordArray

	@staticmethod
	def getNeedlessWordInCode():
		NeedlessWordArray = BaseInfo.NeedlessWordList
		return NeedlessWordArray


	@staticmethod
	def compareWordAndStringArray(word, NeedlessWordArray):
		for NeedlessWord in NeedlessWordArray:
			if (KnowledgeDB.searchTextWithIGNORECASE(word, NeedlessWord) != None):
				return "true"
			else:
				continue
				#return "false"

	@staticmethod
	def searchTextWithIGNORECASE(word, text):
		#six.print_("word = " + word)
		#six.print_("text = " + text)
		result = re.compile( word, re.I ).search( text )
		#six.print_("searchTextWithIGNORECASE result = ")
		#six.print_(result)
		return result



	### 組織横断 クエリー生成
	def createQueryForSearchDoc(self, uuName, questionToCrossDept):
		try:
			NeedlessWordDicFilePath = "NeedlessWordFile.tsv"
			#NeedlessWordArray = KnowledgeDB.getNeedlessWord(NeedlessWordDicFilePath)
			NeedlessWordArray = KnowledgeDB.getNeedlessWordInCode()

			NeedlessWordSet = set(NeedlessWordArray)

			#BaseInfo.inputForSearchWord = questionToCrossDept
			inputForSearchWord = questionToCrossDept
			searchWordResult = self.getSearchWord(BaseInfo.dbname, inputForSearchWord)
			_the_page = json.loads(searchWordResult)
			#six.print_(_the_page)

			keywordListForSearchDoc = []
			finalKeywordListForSearchDoc = []

			#six.print_(questionToCrossDept)

			for element in _the_page['keywords']:
				#six.print_(element['word'] + "\t" + str(element['score']))


				elementWord = element['word']
				checkFlag = ""
				for NeedlessWord in NeedlessWordArray:
					#該当文字列部分の削除処理
					#elementWord = re.sub(NeedlessWord, "", elementWord)

					#six.print_("NeedlessWord =" + NeedlessWord)
					#six.print_("elementWord =" + elementWord)

					if KnowledgeDB.searchTextWithIGNORECASE(elementWord, NeedlessWord) != None:
						#six.print_(elementWord)
						checkFlag = "ON"
						break

				#不要語リストを用いて、フィルタリングする
				#if (element['word'] in NeedlessWordSet):
				#	continue

				if checkFlag == "ON":
					continue

				#検索語が質問文にふくまれているか文字列検索する。
				elif KnowledgeDB.searchTextWithIGNORECASE(elementWord, questionToCrossDept) == None:
					continue

				else:
					#six.print_(elementWord)
					keywordListForSearchDoc.append(elementWord)


			if len(keywordListForSearchDoc) < 4:
				for element in _the_page['keywords']:

					elementWord = element['word']

					#以下の処理は現時点では不実行設定
					#for NeedlessWord in NeedlessWordArray:
						#該当文字列部分の削除処理
						#elementWord = re.sub(NeedlessWord, "", elementWord)


					if(KnowledgeDB.searchTextWithIGNORECASE(elementWord, questionToCrossDept) == None) and (KnowledgeDB.compareWordAndStringArray(elementWord, NeedlessWordArray) != "true"):
						keywordListForSearchDoc.append(elementWord)
						if len(keywordListForSearchDoc) > 3:
							break


			if len(keywordListForSearchDoc) >= 4:
				finalKeywordListForSearchDoc.append(keywordListForSearchDoc[0])
				finalKeywordListForSearchDoc.append(keywordListForSearchDoc[1])
				finalKeywordListForSearchDoc.append(keywordListForSearchDoc[2])
				finalKeywordListForSearchDoc.append(keywordListForSearchDoc[3])

			elif len(keywordListForSearchDoc) == 3:
				finalKeywordListForSearchDoc.append(keywordListForSearchDoc[0])
				finalKeywordListForSearchDoc.append(keywordListForSearchDoc[1])
				finalKeywordListForSearchDoc.append(keywordListForSearchDoc[2])

			elif len(keywordListForSearchDoc) == 2:
				finalKeywordListForSearchDoc.append(keywordListForSearchDoc[0])
				finalKeywordListForSearchDoc.append(keywordListForSearchDoc[1])
			elif len(keywordListForSearchDoc) == 1:
				finalKeywordListForSearchDoc.append(keywordListForSearchDoc[0])

			finalKeywordListForSearchDoc = json.dumps(finalKeywordListForSearchDoc,ensure_ascii=False)
			return finalKeywordListForSearchDoc

		except Exception as e:
			finalKeywordListForSearchDoc = json.dumps([],ensure_ascii=False)
			return finalKeywordListForSearchDoc


####メイン関数###############################################################
def main():

	#d1 = datetime.datetime.today()
	#six.print_('d:', d1)

	service_id = BaseInfo.service_id
	password = BaseInfo.password

	with RecaiusAuth(service_id, password) as auth:
		with KnowledgeDB(auth, BaseInfo.uuName) as kdb:


			###組織横断用クエリー生成
			#組織横断検索クエリー生成用入力データ。ここでは内部データをセットしてるが、
			#arg経由で外部データをセットする方法でも可能。

			# questionToCrossDept = "EXCELについて詳しい人"
			questionToCrossDept = sys.argv[1]

			resultList = kdb.createQueryForSearchDoc(BaseInfo.dbname, questionToCrossDept)
			six.print_(resultList)



	#d3 = datetime.datetime.today()
	#six.print_('d:', d3)


if __name__ == "__main__":
	main()
