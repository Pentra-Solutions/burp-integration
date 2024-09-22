from burp import IBurpExtender, IContextMenuFactory, IHttpRequestResponse
from javax.swing import JMenuItem
from java.util import ArrayList
from time import time
import threading
import json

class BurpExtender(IBurpExtender, IContextMenuFactory):

    def registerExtenderCallbacks(self, callbacks):
        self.callbacks = callbacks
        self.helpers = callbacks.getHelpers()
        callbacks.setExtensionName("Pentra")
        callbacks.registerContextMenuFactory(self)

    def createMenuItems(self, invocation):
        self.context = invocation
        menu = ArrayList()
        menu.add(JMenuItem("Send to Pentra", actionPerformed=self.save_to_file))
        return menu

    def save_to_file(self, event):
        selected_items = self.context.getSelectedMessages()
        for item in selected_items:
            request_thread = threading.Thread(target=self.get_request_with_timeout, args=(item,))
            response_thread = threading.Thread(target=self.get_response_with_timeout, args=(item,))
            request_thread.start()
            response_thread.start()
            request_thread.join(2)  # Timeout set to 1 second
            response_thread.join(2)  # Timeout set to 1 second

            self.write_to_file(self.req, self.resp)

    def get_request_with_timeout(self, item):
        try:
            request = item.getRequest()
        except Exception as e:
            request = ""
        req = [byte for byte in request]

        if request != "":
            self.req = req
        else:
            self.req = []

    def get_response_with_timeout(self, item):
        try:
            response = item.getResponse()
            self.resp = [byte for byte in response]
        except Exception as e:
            self.resp = []

    def write_to_file(self, request, response):
        file_path = "/tmp/requests_pentest_copilot.json"
        timestamp = int(time())
        try:
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
            except:
                data = []

            data.append([timestamp, {"request": request, "response": response}])

            with open(file_path, "w") as f:
                json.dump(data, f)
        except Exception as e:
            self.callbacks.issueAlert("Error writing to file: {}".format(str(e)))
