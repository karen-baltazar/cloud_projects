import requests
import time
import threading
import logging

class ThreadedRequest():
    def __init__(self, url):
        self.url = url
        
    def make_request(self, url):
        return requests.get(url)

    def send_sequential_requests(self, url, size, thread_type: str):
        # send requests sequentially
        for i in range(size):
            try:
                resp = self.make_request(url)
                if (i+1) % 100 == 0:
                    logging.info(f"Status code for the request #{str(i + 1)} in {thread_type}: {resp.status_code}")
            except Exception as ex:
                logging.error(ex)           

    def send_sequential_requests_with_pause(self, url, thread_type: str):
        # send requests sequentially with a 1 minute sleep
        self.send_sequential_requests(url, 500, thread_type)    
        time.sleep(60)
        self.send_sequential_requests(url, 1000, thread_type)

    def send_case_scenarios(self):
        # create threads and start them  
        threads = []
        thread1 = threading.Thread(target=self.send_sequential_requests, args=(self.url,1000,"continuous thread",))
        thread2 = threading.Thread(target=self.send_sequential_requests_with_pause, args=(self.url,"thread with a pause",))
        
        thread1.start()
        threads.append(thread1)
        
        thread2.start()        
        threads.append(thread2) 
        
        # Wait for all threads to finish
        for thread in threads:
            thread.join()
