from title import LobbyUI

if __name__ == "__main__":
    restart = True
    while restart:
        lobby_ui = LobbyUI()
        restart = lobby_ui.main()
        #
