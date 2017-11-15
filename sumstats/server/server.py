from sumstats.server.app import app

import cherrypy


def main():
    # Mount the application
    cherrypy.tree.graft(app, "/")

    # Unsuscribe the default server
    cherrypy.server.unsubscribe()

    # Instantiate a new server object
    server = cherrypy._cpserver.Server()

    server.socket_host = "0.0.0.0"
    server.socket_port = 8081
    server.socket_pool = 30

    # Subscribe this server
    server.subscribe()

    # Start the server engine (Option 1 *and* 2)
    cherrypy.engine.start()
    cherrypy.engine.block()


if __name__ == '__main__':
    main()