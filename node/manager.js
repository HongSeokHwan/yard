var logger = require('./logger');
var exchange = require('./exchange');


var ExchangeManager = function () {
  var self = this;

  this._subscribers = {};
  this._exchanges = {}
  this._exchangeFactories = {}

  Object.keys(exchange).forEach(function (key) {
    var value = exchange[key];
    if (value.prototype instanceof exchange.Exchange) {
      //if(value.exchangeCode != 'btcchina') return; // FIXME
      self._exchangeFactories[value.exchangeCode] = value;
    }
  });
};

ExchangeManager.prototype.subscribe = function (session, exchange) {
  var self = this;
  var exchanges = exchange ? [exchange] : Object.keys(self._exchangeFactories);
  exchanges.forEach(function (exchange) {
    logger.info('Subscribing `%s`', exchange);

    self._ensureExchange(exchange)

    if (!(exchange in self._subscribers)) {
      self._subscribers[exchange] = [];
    }
    self._subscribers[exchange].push(session)
  });
};

ExchangeManager.prototype.unsubscribe = function (session) {
  var self = this;
  Object.keys(self._subscribers).forEach(function (exchange) {
    var subscribers = self._subscribers[exchange];
    index = subscribers.indexOf(session);
    if (index >= 0) {
      logger.info('Unsubscribing %s', exchange);
      subscribers.splice(index, 1);
    }
  });
};

ExchangeManager.prototype._ensureExchange = function (exchange) {
  if (!(exchange in this._exchanges)) {
    this._exchanges[exchange] = this._createExchange(exchange);
  }
};

ExchangeManager.prototype._createExchange = function (exchange) {
  logger.info('Creating exchange: `%s`', exchange);
  instance = new (this._exchangeFactories[exchange])()
  instance.on('tick', this._onTick.bind(this, exchange));
  instance.start();
  return instance
};

ExchangeManager.prototype._onTick = function (exchange, type, tick) {
  logger.info('Received %s tick from %s', type, exchange);
  this._subscribers[exchange].forEach(function (subscriber) {
    subscriber.notifyTick(exchange, type, tick);
  });
};

module.exports = new ExchangeManager();
