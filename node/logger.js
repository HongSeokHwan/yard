var winston = require('winston');
var config = require('./config');


var logger = module.exports = new (winston.Logger)({
  transports: [
    config.debug ?
      new (winston.transports.Console)({ level: 'debug' }) :
      new (winston.transports.DailyRotateFile)({
        level: 'info', filename: config.logPath })
  ]
});
