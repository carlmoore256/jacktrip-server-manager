# main class which will run the program
from session import Session
from interface import Interface
# from client_pane import ClientPane


# main class for handling session program
# eventually make inheritance so that interface does not have direct access to client
# instead, it should call on session
class JTSession():

    def __init__(self):
        self.session = Session()
        self.interface = Interface(self.session)


if __name__ == "__main__":
    jtsession = JTSession()