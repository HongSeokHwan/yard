var events = require('events');
var util = require('util');
var _ = require('underscore');
var ws = require('ws');
var logger = require('./logger');


// Serializer
// ----------

var JSONSerializer = function () {};

JSONSerializer.prototype.loadMessage = function (raw) {
  return JSON.parse(raw);
};

JSONSerializer.prototype.dumpMessage = function (message) {
  return JSON.stringify(message);
};


var XMLSerializer = function () {};

XMLSerializer.prototype.loadMessage = function (raw) {
  // FIXME: Implement
  return raw;
};

XMLSerializer.prototype.dumpMessage = function (message) {
  // FIXME: Implement
  return message;
};


// Base
// ----

var Exchange = exports.Exchange = function (options) {
  events.EventEmitter.call(this);

  options = options || {};
  this.serializer = options.serializer || new JSONSerializer();
};

Exchange.prototype.start = function () {};

Exchange.prototype.normalizeQuote = function (tick) { return tick; };

Exchange.prototype.normalizeTrade = function (tick) { return tick; };

Exchange.exchangeCode = null;

Exchange.currency = 'usd';

util.inherits(Exchange, events.EventEmitter);


// Websocket
// ---------

var WebsocketExchange = function (options) {
  Exchange.call(this, options);

  this.websocketUrl = options.websocketUrl;
  this.connection = null;
};

util.inherits(WebsocketExchange, Exchange);

WebsocketExchange.prototype.start = function () {
  var self = this;
  this.connection = new ws(this.websocketUrl);
  this.connection.on('open', this.onConnect.bind(this));
  this.connection.on('message', function (raw) {
    self.onMessage(self.serializer.loadMessage(raw));
  });
};

WebsocketExchange.prototype.onConnect = function () {};

WebsocketExchange.prototype.onMessage = function (message) {};


// Bitstamp
// --------

var BitstampExchange = exports.BitstampExchange = function (options) {
  options = options || {};
  options.websocketUrl = 'wss://ws.pusherapp.com/app/de504dc5763aeef9ff52?protocol=7&client=js&version=2.1.6&flash=false';
  WebsocketExchange.call(this, options);

  this.channels = ['order_book', 'live_trades'];
};

util.inherits(BitstampExchange, WebsocketExchange);

BitstampExchange.prototype.onConnect = function () {
  var self = this;
  this.channels.forEach(function (channel) {
    self.connection.send(self.serializer.dumpMessage({
      event: 'pusher:subscribe',
      data: { channel: channel }
    }));
  });
};

BitstampExchange.prototype.onMessage = function (message) {
  if (!_.contains(this.channels, message.channel)) {
    return;
  }
  var data = JSON.parse(message.data);

  switch (message.event) {
    case 'trade': this.emit('tick', 'trade', data); break;
    case 'data':  this.emit('tick', 'quote', data); break;
  }
};

BitstampExchange.prototype.normalizeQuote = function (tick) {
  if (!tick || !('bids' in tick) || !('asks' in tick)) {
    return;
  }
  return {
    asks: tick['asks'],
    bids: tick['bids']
  };
};

BitstampExchange.prototype.normalizeTrade = function (tick) {
  if (!tick) {
    return;
  }
  trade = tick[0];
  return {
    id: trade['id'],
    price: trade['price'],
    quantity: trade['amount']
  }
};

BitstampExchange.exchangeCode = 'bitstamp';
