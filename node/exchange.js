var events = require('events');
var util = require('util');
var _ = require('underscore');
var equal = require('deep-equal');
var request = require('request');
var io = require('socket.io-client');
var ws = require('ws');
var config = require('./config');
var logger = require('./logger');


// Poller
// ------

var Poller = function (options) {
  events.EventEmitter.call(this);

  options = options || {};
  this.url = options.url;
  this.serializer = options.serializer || JSON.parse;
  this.normalizer = options.normalizer || function (tick) { return tick; };
  this.concurrency = options.concurrency || 1;
  this.comparator = options.comparator
                    || function (new_, old) { return !equal(new_, old); }
  this.label = options.label || 'Poller';
  this.last = null;
};

util.inherits(Poller, events.EventEmitter);

Poller.prototype.start = function () {
  !!this.url && _.range(this.concurrency).forEach(this._poll.bind(this));
};

Poller.prototype._poll = function () {
  var self = this;
  var poll = function () {
    logger.debug('Polling %s', self.label);

    request(self.url, function (error, response, body) {
      // TODO: Error handling
      raw = self.serializer(body);
      tick = self.normalizer(raw);
      if (!tick) {
        return;
      }

      if (!self.last || self.comparator(tick, self.last)) {
        first = !self.last;
        self.last = tick;
        !first && self.emit('tick', tick);
      }

      poll();
    });
  };

  poll();
};


// Base
// ----

var Exchange = exports.Exchange = function () {
  events.EventEmitter.call(this);

  this.exchangeCode = this.constructor.exchangeCode;
};

Exchange.prototype.start = function () {};

Exchange.prototype.normalizeQuote = function (tick) { return tick; };

Exchange.prototype.normalizeTrade = function (tick) { return tick; };

Exchange.exchangeCode = null;

util.inherits(Exchange, events.EventEmitter);


// Bitstamp
// --------

var BitstampExchange = exports.BitstampExchange = function (options) {
  Exchange.call(this);

  this.url = 'wss://ws.pusherapp.com/app/de504dc5763aeef9ff52?protocol=7\
              &client=js&version=2.1.6&flash=false'
  this.channels = ['order_book', 'live_trades'];
  this.ticker = config.tickers['bitstamp'];
};

util.inherits(BitstampExchange, Exchange);

BitstampExchange.prototype.start = function () {
  var self = this;
  var socket = new ws(this.url);
  socket.on('open', function () {
    self.channels.forEach(function (channel) {
      socket.send(JSON.stringify({
        event: 'pusher:subscribe',
        data: { channel: channel }
      }));
    });
  });
  socket.on('message', function (raw) {
    var message = JSON.parse(raw);
    if (!_.contains(self.channels, message.channel)) {
      return;
    }
    var data = JSON.parse(message.data);
    switch (message.event) {
      case 'trade': self.emit('tick', 'trade', self.normalizeTrade(data)); break;
      case 'data':  self.emit('tick', 'quote', self.normalizeQuote(data)); break;
    }
  });
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
  trade = util.isArray(tick) ? tick[0] : tick;
  return {
    ticker: this.ticker,
    id: trade['id'],
    price: trade['price'],
    quantity: trade['amount']
  }
};

BitstampExchange.exchangeCode = 'bitstamp';


// Btcchina
// --------

var BtcchinaExchange = exports.BtcchinaExchange = function (options) {
  Exchange.call(this);

  this.quotePollUrl = 'https://data.btcchina.com/data/orderbook?market=btccny&limit=10';
  this.quotePollConcurrency = 1;
  this.url = 'https://websocket.btcchina.com/';
  this.channels = ['marketdata_cnybtc'];
  this.ticker = config.tickers['btcchina'];
};

util.inherits(BtcchinaExchange, Exchange);

BtcchinaExchange.prototype.start = function () {
  var self = this;

  // Streaming
  var socket = new io(this.url);
  socket.on('connect', function () {
    socket.emit('subscribe', self.channels);
    socket.on('trade', function (message) {
      self.emit('tick', 'trade', self.normalizeTrade(message));
    });
  });

  // Polling
  (new Poller({
    label: util.format('%s %s', this.exchangeCode, 'quote'),
    url: this.quotePollUrl,
    concurrency: this.quotePollConcurrency,
    normalizer: this.normalizeQuote.bind(this),
    comparator: function (new_, old) {
      return new_.date > old.date;
    }
  })).on('tick', this.emit.bind(this, 'tick', 'quote')).start();

};

BtcchinaExchange.prototype.normalizeQuote = function (tick) {
  if (!tick || !('bids' in tick) || !('asks' in tick)) {
    return;
  }
  return {
    ticker: this.ticker,
    date: new Date(parseInt(tick['date']) * 1000),
    asks: tick['asks'],
    bids: tick['bids']
  };
};

BtcchinaExchange.prototype.normalizeTrade = function (tick) {
  if (!tick) {
    return;
  }
  return {
    ticker: this.ticker,
    date: new Date(parseInt(tick['date']) * 1000),
    id: tick['trade_id'],
    price: tick['price'],
    quantity: tick['amount'],
    type: tick['type']
  }
};

BtcchinaExchange.exchangeCode = 'btcchina';


// Korbit
// ------

var KorbitExchange = exports.KorbitExchange = function (options) {
  Exchange.call(this);

  this.quotePollUrl = 'https://api.korbit.co.kr/v1/orderbook';
  this.tradePollUrl = 'https://api.korbit.co.kr/v1/transactions';
  this.quotePollConcurrency = 2;
  this.tradePollConcurrency = 2;
  this.ticker = config.tickers['korbit'];
};

util.inherits(KorbitExchange, Exchange);

KorbitExchange.prototype.start = function () {
  (new Poller({
    label: util.format('%s %s', this.exchangeCode, 'quote'),
    url: this.quotePollUrl,
    concurrency: this.quotePollConcurrency,
    normalizer: this.normalizeQuote.bind(this)
  })).on('tick', this.emit.bind(this, 'tick', 'quote')).start();

  (new Poller({
    label: util.format('%s %s', this.exchangeCode, 'trade'),
    url: this.tradePollUrl,
    concurrency: this.tradePollConcurrency,
    normalizer: this.normalizeTrade.bind(this)
  })).on('tick', this.emit.bind(this, 'tick', 'trade')).start();
};

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
