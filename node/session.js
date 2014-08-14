var util = require('util');
var logger = require('./logger');
var manager = require('./manager');


var Session = exports.Session = function (connection) {
  this._connection = connection;
  this._handlers = {};
  this.initialize();
};

Session.prototype.initialize = function () {
  var self = this;

  logger.info('Session opened')

  this._handlers['subscribe'] = this.handleSubscribe.bind(this);

  this._connection.on('message', function (raw) {
    self.onMessage(JSON.parse(raw));
  });
  this._connection.on('close', function () {
    self.onClose();
  });
};

Session.prototype.send = function (type, data) {
  this._connection.send(JSON.stringify({
    type: type,
    data: data || {}
  }));
};

Session.prototype.onMessage = function (message) {
  logger.debug(util.format('Message received: %j', message));
  this._handlers[message.type](message.data);
};

Session.prototype.onClose = function () {
  logger.info('Session closed');
  manager.unsubscribe(this);
};

Session.prototype.handleSubscribe = function (data) {
  manager.subscribe(this, data.exchange);
};

Session.prototype.notifyTick = function (exchange, type, tick) {
  this.send(type, {
    'exchange': exchange,
    'tick': tick
  });
};
