var events = require('events');
var util = require('util');
var _ = require('underscore');
var equal = require('deep-equal');
var request = require('request');
var ws = require('ws');
var config = require('./config');
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
  this.exchangeCode = this.constructor.exchangeCode;
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


// Polling
// -------

var PollingExchange = function (options) {
  Exchange.call(this, options);

  this.quotePollUrl = options.quotePollUrl;
  this.tradePollUrl = options.tradePollUrl;
  this.quotePollConcurrency = options.quotePollConcurrency || 1;
  this.tradePollConcurrency = options.tradePollConcurrency || 1;
  this.lastQuote = null;
  this.lastTrade = null;
};

util.inherits(PollingExchange, Exchange);

PollingExchange.prototype.start = function () {
  var self = this;

  !!self.quotePollUrl && _.range(self.quotePollConcurrency).forEach(function () {
    self._pollQuote();
  });
  !!self.tradePollUrl && _.range(self.tradePollConcurrency).forEach(function () {
    self._pollTrade();
  });
};
PollingExchange.prototype._pollQuote = function () {
  var self = this;
  var poll = function () {
    logger.debug('%s - Polling quote', self.exchangeCode);

    request(self.quotePollUrl, function (error, response, body) {
      // TODO: Error handling
      tick = self.serializer.loadMessage(body);
      quote = self.normalizeQuote(tick);
      if (!quote) {
        return;
      }

      if (!equal(quote, self.lastQuote)) {
        first = !!self.lastQuote;
        self.lastQuote = quote;
        !first && self.emit('tick', 'quote', quote);
      }

      poll();
    });
  };

  poll();
};
PollingExchange.prototype._pollTrade = function () {
  var self = this;
  var poll = function () {
    logger.debug('%s - Polling trade', self.exchangeCode);

    request(self.tradePollUrl, function (error, response, body) {
      // TODO: Error handling
      tick = self.serializer.loadMessage(body);
      trade = self.normalizeTrade(tick);
      if (!trade) {
        return;
      }

      if (!equal(trade, self.lastTrade)) {
        first = !!self.lastTrade;
        self.lastTrade = trade;
        !first && self.emit('tick', 'trade', trade);
      }

      poll();
    });
  };

  poll();
};


// Bitstamp
// --------

var BitstampExchange = exports.BitstampExchange = function (options) {
  WebsocketExchange.call(this, _.defaults({
    websocketUrl: 'wss://ws.pusherapp.com/app/de504dc5763aeef9ff52?protocol=7'
                  + '&client=js&version=2.1.6&flash=false'
  }, options));

  this.channels = ['order_book', 'live_trades'];
  this.ticker = config.tickers['bitstamp'];
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
    case 'trade': this.emit('tick', 'trade', this.normalizeTrade(data)); break;
    case 'data':  this.emit('tick', 'quote', this.normalizeQuote(data)); break;
  }
};

BitstampExchange.prototype.normalizeQuote = function (tick) {
  if (!tick || !('bids' in tick) || !('asks' in tick)) {
    return;
  }
  return {
    ticker: this.ticker,
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
    ticker: this.ticker,
    id: trade['id'],
    price: trade['price'],
    quantity: trade['amount']
  }
};

BitstampExchange.exchangeCode = 'bitstamp';


// Korbit
// ------

var KorbitExchange = exports.KorbitExchange = function (options) {
  PollingExchange.call(this, _.defaults({
    quotePollUrl: 'https://api.korbit.co.kr/v1/orderbook',
    tradePollUrl: 'https://api.korbit.co.kr/v1/transactions',
    quotePollConcurrency: 5,
    tradePollConcurrency: 5
  }, options));

  this.ticker = config.tickers['korbit'];
};

util.inherits(KorbitExchange, PollingExchange);

KorbitExchange.prototype.normalizeQuote = function (tick) {
  if (!tick || !('bids' in tick) || !('asks' in tick)) {
    return;
  }
  return {
    ticker: this.ticker,
    asks: tick['asks'],
    bids: tick['bids']
  };
};

KorbitExchange.prototype.normalizeTrade = function (tick) {
  if (!tick) {
    return;
  }
  trade = tick[0];
  return {
    ticker: this.ticker,
    id: trade['tid'],
    price: trade['price'],
    quantity: trade['amount']
  }
};

KorbitExchange.exchangeCode = 'korbit';
