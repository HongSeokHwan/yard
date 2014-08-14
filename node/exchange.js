var util = require('util');
var logger = require('./logger');


var Exchange = exports.Exchange = function () {
};
Exchange.prototype.subscribe = function (callback) {
};
Exchange.prototype.publish = function () {
};


// Bitstamp
// --------

var BitstampExchange = exports.BitstampExchange = function () {
  Exchange.call(this);
};

util.inherits(BitstampExchange, Exchange);

BitstampExchange.prototype._private = function () {
};

BitstampExchange.exchangeCode = 'bitstamp';
