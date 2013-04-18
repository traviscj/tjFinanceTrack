import sqlite3
from copy import deepcopy
import cmd
import sys

from os.path import expanduser, exists
from os import unlink


# Dropbox API keys...
from finance_track_db import *
# Include the Dropbox SDK libraries
from dropbox import client, rest
# ACCESS_TYPE should be 'dropbox' or 'app_folder' as configured for your app
ACCESS_TYPE = 'app_folder'
from DropboxStoredSession import StoredSession

class finance_track(object):
	def __init__(self):
		self.dropbox = False
		self.database = expanduser("~/Dropbox/Apps/tjFinanceTrack/fintrack.db")
		if not exists(self.database):
			sdg = self.dropbox_get()
		self.connect_db()
	def connect_db(self):
		self.conn = sqlite3.connect(self.database)
		self.cur = self.conn.cursor()
		self.printed_header = False
		self.refresh_balances()
	
	def refresh_balances(self)
		acc = self.cur.execute("SELECT * FROM accounts ;")
		self.ACC = {}
		self.ACC_NAME = {}
		self.ACC_SNAME = {}
		for a_id, a_bal, a_name, a_short in acc:
			self.ACC[a_id] = a_bal
			self.ACC_NAME[a_id] = a_name
			self.ACC_SNAME[a_id] = a_short

	def destroy(self):
		self.conn.commit()
		self.conn.close()
		if self.dropbox:
			f= open(self.database)
			response = self.api_client.put_file('/fintrack.db', f,overwrite=True)
			f.close()
			unlink(self.database)
	def dropbox_get(self):
		from tempfile import NamedTemporaryFile
		self.dropbox = True
		sess = StoredSession(APP_KEY, APP_SECRET, ACCESS_TYPE)
		sess.load_creds()
		if not sess.is_linked():
			sess.link()
			
		self.api_client = client.DropboxClient(sess)
		f, metadata = self.api_client.get_file_and_metadata('/fintrack.db')
		out = NamedTemporaryFile(mode='wb',delete=False)
		# out = open(self.database, 'wb')
		out.write(f.read())
		out.close()
		self.database = out.name
		return None
	def display(self,html=False):
		result = ""
		lengths = {}
		format = "{3:3}:{1:12} " + " ".join(["{0["+str(li)+"]:8}" for li in self.ACC.keys() if li not in [1,2]]) + " ${6:9}:{4:2}->{5:2} {2}\n"
		if html:
			format = "<tr><td>{3:3}</td><td>{2}</td><td>{1:12} </td>" + " ".join(["<td>{0["+str(li)+"]:8}</td>" for li in self.ACC.keys() if li not in [1,2]]) + "<td> ${6:9}:{4:2}->{5:2}</td></tr>\n"
		ACC = deepcopy(self.ACC)
		if not self.printed_header:
			if html: result+= "<table>"
			result+= format.format(self.ACC_SNAME,'Date','Description',' id','','','')
			result+= format.format(ACC, '','initial','','','','')
			self.printed_header = True
		tx = self.cur.execute("SELECT * FROM pending_transactions ORDER BY post_date;")
		for t_id,t_enter_date,t_post_date,from_acc,to_acc,dbal,t_desc in tx:
			ACC[from_acc] -= dbal
			ACC[to_acc] += dbal
			result+= format.format(ACC, t_post_date, t_desc, t_id, from_acc, to_acc, dbal)
		if html: 
			result+= "</table>"
			return """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
				"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
				<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">  
				<head>
				<title>travis's finances</title>
				<meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
				<style type="text/css">
				tr:nth-child(even) {{
				    background-color: #FFF;
				}}
				tr:nth-child(odd) {{
				    background-color: #EEE;
				}}
				</style>
				</head>
				<body>
				{0}
				</body>
				</html>
				""".format(result)
		return result
	def newtransaction(self, post_date, from_acc, to_acc, dbal, desc):
		T = (post_date, from_acc, to_acc, dbal, desc)
		print T
		self.cur.execute("INSERT INTO pending_transactions (enter_date, post_date,from_account,to_account,delta_balance,description) VALUES (date('now'), ?, ?, ?, ?, ?);", T)
		
	def rmtrans(self, id):
		self.cur.execute("DELETE FROM pending_transactions WHERE id=?", (id,))
	def __enter__(self):
		return self
	def __exit__(self, type, value, traceback):
		self.destroy()
	
	def cleartrans(self,id):
		pending_transaction = self.cur.execute("SELECT * FROM pending_transactions WHERE id=?;", (id,)).fetchone()
		print pending_transaction
		tid,enter_date, post_date,from_account,to_account,delta_balance,description=pending_transaction
		
		self.cur.execute("INSERT INTO settled_transactions (enter_date, post_date,from_account,to_account,delta_balance,description) VALUES (?,?,?,?,?,?);", (enter_date, post_date,from_account,to_account,delta_balance,description))
		self.cur.execute("UPDATE accounts SET balance=? WHERE a_id = ?;",(self.ACC[from_account]-delta_balance,from_account))
		self.cur.execute("UPDATE accounts SET balance=? WHERE a_id = ?;",(self.ACC[to_account]+delta_balance,to_account))
		self.rmtrans(tid)
		self.refresh_balances()
class fintrackcli(cmd.Cmd):
	def __init__(self):
		cmd.Cmd.__init__(self)
		self.prompt = 'fintrack> '
		self.ft = finance_track()
	def __enter__(self):
		return self
	def __exit__(self, type, value, traceback):
		self.ft.destroy()
	
	def do_ls(self, arg):
		print self.ft.display()
	def do_hls(self, arg):
		table = self.ft.display(html=True)
	def do_rm(self, arg):
		try:
			self.ft.rmtrans(arg)
		except Exception, err:
			print "couldn't add your spend transaction: ", arg
			print "because we encountered: ", str(err)
			
	def do_spend(self, arg):
		try:
			postdate, from_acc, dbal, desc = arg.split(' ',3)
			self.ft.newtransaction(postdate,from_acc, 1, dbal,desc)
		except Exception, err:
			print "couldn't add your spend transaction: ", arg
			print "because we encountered: ", str(err)
	def do_earn(self,arg):
		try:
			postdate, to_acc, dbal, desc = arg.split(' ',3)
			self.ft.newtransaction(postdate, 2, to_acc, dbal,desc)
		except Exception, err:
			print "couldn't add your spend transaction: ", arg
			print "because we encountered: ", str(err)
	
	def do_pay(self,arg):
		try:
			postdate, from_acc,to_acc, dbal, desc = arg.split(' ',4)
			self.ft.newtransaction(postdate, from_acc, to_acc, dbal, desc)
		except Exception, err:
			print "couldn't add your spend transaction: ", arg
			print "because we encountered: ", str(err)
	
	def do_clear(self,arg):
		self.ft.cleartrans(arg)
		try:
			pass
		except Exception, err:
			print "couldn't add your spend transaction: ", arg
			print "because we encountered: ", str(err)
	def do_quit(self,arg):
		sys.exit(0)
	def do_EOF(self,arg):
		self.do_quit(arg)

if __name__ == "__main__":
	with fintrackcli() as cli:
		if len(sys.argv)>1:
			cli.onecmd (" ".join(sys.argv[1:]))
		else:
			cli.cmdloop()
		# ftc.display()
		# ft.newtransaction(post_date = "2013-04-19",from_acc = 3,to_acc = 1,dbal = 612.5,desc = "rent for new place",)
		# ft.newtransaction(post_date = "2013-04-30",from_acc = 2,to_acc = 3,dbal = 1800,desc = "northwestern paycheck",)
		# ft.newtransaction(post_date = "2013-04-30",from_acc = 3,to_acc = 1,dbal = 425,desc = "sheridan 5240 rent may",)

