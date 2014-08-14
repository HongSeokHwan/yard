var ws = require('ws');
var config = require('./config');
var session = require('./session');


server = new ws.Server({ port: config.bridgeServerPort });
server.on('connection', function (connection) {
  new session.Session(connection);
});
