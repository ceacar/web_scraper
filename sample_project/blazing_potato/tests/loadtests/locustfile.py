from locust import HttpLocust, TaskSet
import random
import string

def rand_str():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(1))

def save(l):
    new_key = rand_str()
    new_value = rand_str()
    l.client.post("/save", json = {"key":new_key, "value":new_value})

def save_one(l):
    new_key = "key1"
    new_value = "value1"
    l.client.post("/save", json = {"key":new_key, "value":new_value})

def get_value(l):
    new_key = rand_str()
    l.client.get("/get/{0}".format(new_key))

def get_one(l):
    new_key = "key1"
    l.client.get("/get/{0}".format(new_key))

def index(l):
    l.client.get("/")

def health(l):
    l.client.get("/health")


class UserBehavior(TaskSet):
    #tasks = {index: 1, health: 1, save: 1, get_value: 10}
    tasks = {get_one: 1}

    def on_start(self):
        save_one(self)

    #def on_stop(self):
    #    logout(self)

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 5000
    max_wait = 9000
