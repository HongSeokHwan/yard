var config = {};

config.debug = false;
config.bridgeServerPort = 9000;
config.logPath = 'bridge.log'
config.tickers = {
  bitstamp: 'BTCUSD_BITSTAMP_CURRENCY',
  korbit: 'BTCKRW_KORBIT_CURRENCY',
  btcchina: 'BTCCNY_BTCCHINA_CURRENCY',
  usdkrw: 'USDKRW_WEBSERVICEX_CURRENCY',
  cnykrw: 'CNYKRW_WEBSERVICEX_CURRENCY',
  usdcny: 'USDCNY_WEBSERVICEX_CURRENCY',
  icbit: {
    '1409': 'BTCUSD_1409_ICBIT_FUTURES',
    '1412': 'BTCUSD_1412_ICBIT_FUTURES'
  }
};

// Import local config if any
try {
  local_config = require('./local_config');
  Object.keys(local_config).forEach(function(key) {
    config[key] = local_config[key];
  });
} catch (e) {}

module.exports = config;
