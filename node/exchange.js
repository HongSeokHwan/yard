var events = require('events');
var util = require('util');
var _ = require('underscore');
var CryptoJS = require('crypto-js');
var equal = require('deep-equal');
var request = require('request');
var io = require('socket.io-client');
var ws = require('ws');
var xml = require("libxmljs");
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
  this.concurrency = options.concurrency === undefined ? 1 : options.concurrency;
  this.skipFirst = options.skipFirst === undefined ? true : options.skipFirst;
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
        if (!self.skipFirst || !first) {
          self.emit('tick', tick);
        }
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

var BitstampExchange = exports.BitstampExchange = function () {
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

var BtcchinaExchange = exports.BtcchinaExchange = function () {
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


// Icbit
// --------

var IcbitExchange = exports.IcbitExchange = function () {
  Exchange.call(this);

  this.targets = Object.keys(config.tickers.icbit);

  // For polling
  this.quotePollUrlTmpl = 'https://api.icbit.se/api/orders/book?ticker=%s'
  this.quotePollConcurrency = 2;

  // For streaming
  this.streamUrlTmpl = 'https://api.icbit.se/icbit?key=%s&signature=%s&nonce=%s';
  this.user = config.icbitUser;
  this.key = config.icbitKey;
  this.secret = config.icbitSecret;
};

util.inherits(IcbitExchange, Exchange);

IcbitExchange.prototype._buildUrl = function () {
  var tmpl = this.streamUrlTmpl;
  var user = this.user;
  var key = this.key;
  var secret = this.secret;
  var nonce = Math.round(new Date().getTime() / 1000);
  var signature = CryptoJS.HmacSHA256(nonce + user + key, secret).toString(
    CryptoJS.enc.Hex).toUpperCase();
  return util.format(tmpl, key, signature, nonce);
};

IcbitExchange.prototype.start = function () {
  var self = this;

  // Polling
  self.targets.forEach(function (target) {
    var url = util.format(self.quotePollUrlTmpl, target);
    (new Poller({
      label: util.format('%s %s (%s)', self.exchangeCode, 'quote', target),
      url: url,
      concurrency: self.quotePollConcurrency,
      normalizer: self.normalizeQuote.bind(self)
    })).on('tick', self.emit.bind(self, 'tick', 'quote')).start();
  });

  // Streaming
  var url = this._buildUrl();
  var socket = io.connect(url);
  socket.on('connect', function () {
    console.log('connected');
    socket.emit('message', {
      'op': 'subscribe',
      'channel': 'orderbook_BUU4'
    });
    socket.emit('subscribe', {
      'channel': 'orderbook_BUU4'
    });
  });
  socket.on('disconnect', function () {
    console.log('disconnected');
  });
  socket.on('error', function (raw) {
    console.log('error');
    console.log(raw);
  });
  socket.on('message', function (raw) {
    console.log('message');
    console.log(raw);
  });
};

IcbitExchange.prototype.normalizeQuote = function (tick) {
  if (!tick || !('buy' in tick) || !('sell' in tick)) {
    return;
  }
  var convertToArray = function (entry) {
    return [entry.p.toString(), entry.q.toString()];
  };

  return {
    ticker: config.tickers.icbit[tick['s']],
    asks: _.map(tick['sell'], convertToArray),
    bids: _.map(tick['buy'], convertToArray)
  };
};

IcbitExchange.prototype.normalizeTrade = function (tick) {
  if (!tick) {
    return;
  }
  return {
    ticker: this.ticker,
    id: trade['id'],
    price: trade['price'],
    quantity: trade['amount']
  }
};

IcbitExchange.exchangeCode = 'icbit';


// Korbit
// ------

var KorbitExchange = exports.KorbitExchange = function () {
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


// Webservice
// ------

var WebserviceExchange = exports.WebserviceExchange = function () {
  Exchange.call(this);

  this.tradePollUrlTmpl = 'http://www.webservicex.net/CurrencyConvertor.asmx/'
                          + 'ConversionRate?FromCurrency=%s&ToCurrency=%s';
  this.tradePollConcurrency = 1;
};

util.inherits(WebserviceExchange, Exchange);

WebserviceExchange.prototype.start = function () {
  var url = util.format(this.tradePollUrlTmpl, this.fromCurrency,
                        this.toCurrency);
  (new Poller({
    label: util.format('%s %s', this.exchangeCode, 'trade'),
    url: url,
    concurrency: this.tradePollConcurrency,
    serializer: function (raw) {
      try {
        var doc = xml.parseXml(raw);
        return doc.root().childNodes()[0].text();
      } catch (e) {
        logger.error('Failed to parse XML: ' + e);
        return null;
      }
    },
    normalizer: this.normalizeTrade.bind(this)
  })).on('tick', this.emit.bind(this, 'tick', 'trade')).start();
};

WebserviceExchange.prototype.normalizeTrade = function (tick) {
  if (!tick) {
    return;
  }
  return {
    ticker: this.ticker,
    price: tick
  }
};


// UsdToKrw
// --------

var UsdToKrwExchange = exports.UsdToKrwExchange = function () {
  WebserviceExchange.call(this);

  this.fromCurrency = 'USD';
  this.toCurrency = 'KRW';
  this.ticker = config.tickers['usdkrw'];
};

util.inherits(UsdToKrwExchange, WebserviceExchange);

UsdToKrwExchange.exchangeCode = 'usdkrw';


// CnyToKrw
// --------

var CnyToKrwExchange = exports.CnyToKrwExchange = function () {
  WebserviceExchange.call(this);

  this.fromCurrency = 'CNY';
  this.toCurrency = 'KRW';
  this.ticker = config.tickers['cnykrw'];
};

util.inherits(CnyToKrwExchange, WebserviceExchange);

CnyToKrwExchange.exchangeCode = 'cnykrw';


// UsdToCny
// --------

var UsdToCnyExchange = exports.UsdToCnyExchange = function () {
  WebserviceExchange.call(this);

  this.fromCurrency = 'USD';
  this.toCurrency = 'CNY';
  this.ticker = config.tickers['usdcny'];
};

util.inherits(UsdToCnyExchange, WebserviceExchange);

UsdToCnyExchange.exchangeCode = 'usdcny';
